"""SQLAlchemy models for DataOps persistence."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    Column, String, Integer, Float, DateTime, Text, Index,
    UniqueConstraint, ForeignKey, JSON, Enum as SQLEnum
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship

from ...domain.types import (
    DatasetType, Stage, DatasetStatus, DataSource,
    CheckType, CheckStatus, Industry
)
from .database import Base


class DatasetTemplateModel(Base):
    """SQLAlchemy model for DatasetTemplate entity."""

    __tablename__ = "dataset_templates"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False)
    dataset_type = Column(SQLEnum(DatasetType), nullable=False)
    industry = Column(SQLEnum(Industry), nullable=True)
    use_case = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    source_path = Column(String(512), nullable=True)
    schema_definition = Column(JSON, nullable=False, default=dict)
    default_record_count = Column(Integer, nullable=False, default=100)
    metadata_template = Column(JSON, nullable=False, default=dict)
    quality_rules = Column(JSON, nullable=False, default=list)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    datasets = relationship("DatasetModel", back_populates="template")

    __table_args__ = (
        Index("idx_template_type_industry", "dataset_type", "industry"),
        Index("idx_template_use_case", "use_case"),
    )


class DatasetModel(Base):
    """SQLAlchemy model for Dataset entity."""

    __tablename__ = "datasets"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False)
    dataset_type = Column(SQLEnum(DatasetType), nullable=False)
    stage = Column(SQLEnum(Stage), nullable=False)
    client_id = Column(PGUUID(as_uuid=True), nullable=False)
    journey_id = Column(PGUUID(as_uuid=True), nullable=False)
    status = Column(SQLEnum(DatasetStatus), nullable=False, default=DatasetStatus.PROVISIONING)

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    ready_at = Column(DateTime, nullable=True)
    archived_at = Column(DateTime, nullable=True)

    # Data characteristics
    data_source = Column(SQLEnum(DataSource), nullable=False, default=DataSource.MOCK_TEMPLATE)
    record_count = Column(Integer, nullable=False, default=0)
    size_bytes = Column(Integer, nullable=False, default=0)

    # Quality and connectors
    quality_score = Column(Float, nullable=True)
    connector_id = Column(PGUUID(as_uuid=True), nullable=True)
    template_id = Column(PGUUID(as_uuid=True), ForeignKey("dataset_templates.id"), nullable=True)

    # Metadata
    metadata_json = Column(JSON, nullable=False, default=dict)

    # Relationships
    template = relationship("DatasetTemplateModel", back_populates="datasets")
    quality_checks = relationship(
        "DataQualityCheckModel",
        back_populates="dataset",
        cascade="all, delete-orphan"
    )

    __table_args__ = (
        # Enforce uniqueness: one active dataset per client/stage/type
        UniqueConstraint(
            "client_id", "stage", "dataset_type",
            name="uq_dataset_per_client_stage",
            # Note: This should ideally include a WHERE clause for active statuses
            # but that requires a partial index which varies by DB
        ),
        Index("idx_client_stage", "client_id", "stage"),
        Index("idx_journey", "journey_id"),
        Index("idx_status", "status"),
        Index("idx_connector", "connector_id"),
    )


class DataQualityCheckModel(Base):
    """SQLAlchemy model for DataQualityCheck entity."""

    __tablename__ = "data_quality_checks"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    dataset_id = Column(PGUUID(as_uuid=True), ForeignKey("datasets.id"), nullable=False)
    check_type = Column(SQLEnum(CheckType), nullable=False)
    status = Column(SQLEnum(CheckStatus), nullable=False, default=CheckStatus.PENDING)
    score = Column(Float, nullable=False, default=0.0)
    threshold = Column(Float, nullable=False, default=95.0)
    executed_at = Column(DateTime, nullable=True)
    result = Column(JSON, nullable=False, default=dict)
    error_message = Column(Text, nullable=True)

    # Relationships
    dataset = relationship("DatasetModel", back_populates="quality_checks")

    __table_args__ = (
        Index("idx_check_dataset", "dataset_id"),
        Index("idx_check_type", "check_type"),
    )
