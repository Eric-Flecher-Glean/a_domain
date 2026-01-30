"""Create dataset tables

Revision ID: 001
Revises:
Create Date: 2026-01-28 12:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create dataset_templates table
    op.create_table(
        'dataset_templates',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('dataset_type', sa.Enum(
            'confluence_pages', 'github_repos', 'slack_messages', 'jira_issues', 'custom',
            name='datasettype'
        ), nullable=False),
        sa.Column('industry', sa.Enum(
            'fintech', 'healthcare', 'enterprise', 'manufacturing', 'retail',
            name='industry'
        ), nullable=True),
        sa.Column('use_case', sa.String(length=255), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('source_path', sa.String(length=512), nullable=True),
        sa.Column('schema_definition', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('default_record_count', sa.Integer(), nullable=False),
        sa.Column('metadata_template', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('quality_rules', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_template_type_industry', 'dataset_templates', ['dataset_type', 'industry'])
    op.create_index('idx_template_use_case', 'dataset_templates', ['use_case'])

    # Create datasets table
    op.create_table(
        'datasets',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('dataset_type', sa.Enum(
            'confluence_pages', 'github_repos', 'slack_messages', 'jira_issues', 'custom',
            name='datasettype'
        ), nullable=False),
        sa.Column('stage', sa.Enum('sandbox', 'pilot', 'production', name='stage'), nullable=False),
        sa.Column('client_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('journey_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('status', sa.Enum(
            'provisioning', 'validating', 'ready', 'failed', 'teardown', 'archived',
            name='datasetstatus'
        ), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('ready_at', sa.DateTime(), nullable=True),
        sa.Column('archived_at', sa.DateTime(), nullable=True),
        sa.Column('data_source', sa.Enum(
            'mock_template', 'sanitized_production', 'custom',
            name='datasource'
        ), nullable=False),
        sa.Column('record_count', sa.Integer(), nullable=False),
        sa.Column('size_bytes', sa.Integer(), nullable=False),
        sa.Column('quality_score', sa.Float(), nullable=True),
        sa.Column('connector_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('template_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('metadata_json', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.ForeignKeyConstraint(['template_id'], ['dataset_templates.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('client_id', 'stage', 'dataset_type', name='uq_dataset_per_client_stage')
    )
    op.create_index('idx_client_stage', 'datasets', ['client_id', 'stage'])
    op.create_index('idx_journey', 'datasets', ['journey_id'])
    op.create_index('idx_status', 'datasets', ['status'])
    op.create_index('idx_connector', 'datasets', ['connector_id'])

    # Create data_quality_checks table
    op.create_table(
        'data_quality_checks',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('dataset_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('check_type', sa.Enum(
            'schema_validation', 'data_completeness', 'connector_health', 'sample_query_success',
            name='checktype'
        ), nullable=False),
        sa.Column('status', sa.Enum('pending', 'running', 'passed', 'failed', name='checkstatus'), nullable=False),
        sa.Column('score', sa.Float(), nullable=False),
        sa.Column('threshold', sa.Float(), nullable=False),
        sa.Column('executed_at', sa.DateTime(), nullable=True),
        sa.Column('result', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['dataset_id'], ['datasets.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_check_dataset', 'data_quality_checks', ['dataset_id'])
    op.create_index('idx_check_type', 'data_quality_checks', ['check_type'])


def downgrade() -> None:
    op.drop_index('idx_check_type', table_name='data_quality_checks')
    op.drop_index('idx_check_dataset', table_name='data_quality_checks')
    op.drop_table('data_quality_checks')

    op.drop_index('idx_connector', table_name='datasets')
    op.drop_index('idx_status', table_name='datasets')
    op.drop_index('idx_journey', table_name='datasets')
    op.drop_index('idx_client_stage', table_name='datasets')
    op.drop_table('datasets')

    op.drop_index('idx_template_use_case', table_name='dataset_templates')
    op.drop_index('idx_template_type_industry', table_name='dataset_templates')
    op.drop_table('dataset_templates')

    # Drop enums
    sa.Enum(name='checkstatus').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='checktype').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='datasource').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='datasetstatus').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='stage').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='datasettype').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='industry').drop(op.get_bind(), checkfirst=True)
