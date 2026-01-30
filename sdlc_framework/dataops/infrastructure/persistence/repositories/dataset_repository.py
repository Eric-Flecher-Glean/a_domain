"""Dataset repository implementation."""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ....domain.entities import Dataset, DataQualityCheck
from ....domain.types import DatasetType, Stage, DatasetStatus, DataSource
from ....domain.value_objects import DatasetMetadata, QualityScore
from ..models import DatasetModel, DataQualityCheckModel
from .base_repository import BaseRepository


class DatasetRepository(BaseRepository[DatasetModel]):
    """Repository for Dataset aggregate."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, DatasetModel)

    async def find_by_client_and_stage(
        self,
        client_id: UUID,
        stage: Stage,
        dataset_type: Optional[DatasetType] = None,
        status: Optional[DatasetStatus] = None
    ) -> List[Dataset]:
        """Find datasets for a client and stage."""
        conditions = [
            DatasetModel.client_id == client_id,
            DatasetModel.stage == stage
        ]

        if dataset_type:
            conditions.append(DatasetModel.dataset_type == dataset_type)

        if status:
            conditions.append(DatasetModel.status == status)

        result = await self.session.execute(
            select(DatasetModel)
            .where(and_(*conditions))
            .options(selectinload(DatasetModel.quality_checks))
        )

        models = result.scalars().all()
        return [self._to_domain(model) for model in models]

    async def find_by_journey(self, journey_id: UUID) -> List[Dataset]:
        """Find all datasets for a journey."""
        result = await self.session.execute(
            select(DatasetModel)
            .where(DatasetModel.journey_id == journey_id)
            .options(selectinload(DatasetModel.quality_checks))
        )

        models = result.scalars().all()
        return [self._to_domain(model) for model in models]

    async def find_active_by_type(
        self,
        client_id: UUID,
        stage: Stage,
        dataset_type: DatasetType
    ) -> Optional[Dataset]:
        """Find active dataset for client/stage/type (enforces uniqueness)."""
        result = await self.session.execute(
            select(DatasetModel)
            .where(
                and_(
                    DatasetModel.client_id == client_id,
                    DatasetModel.stage == stage,
                    DatasetModel.dataset_type == dataset_type,
                    DatasetModel.status.notin_([
                        DatasetStatus.ARCHIVED,
                        DatasetStatus.FAILED
                    ])
                )
            )
            .options(selectinload(DatasetModel.quality_checks))
        )

        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def save_dataset(self, dataset: Dataset) -> Dataset:
        """Save dataset entity (insert or update)."""
        # Check if exists
        existing = await self.get_by_id(dataset.dataset_id)

        if existing:
            # Update existing
            model = existing
            self._update_model_from_domain(model, dataset)
        else:
            # Create new
            model = self._to_model(dataset)

        model = await self.save(model)
        return self._to_domain(model)

    def _to_model(self, dataset: Dataset) -> DatasetModel:
        """Convert domain entity to SQLAlchemy model."""
        return DatasetModel(
            id=dataset.dataset_id,
            name=dataset.name,
            dataset_type=dataset.dataset_type,
            stage=dataset.stage,
            client_id=dataset.client_id,
            journey_id=dataset.journey_id,
            status=dataset.status,
            created_at=dataset.created_at,
            ready_at=dataset.ready_at,
            archived_at=dataset.archived_at,
            data_source=dataset.data_source,
            record_count=dataset.record_count,
            size_bytes=dataset.size_bytes,
            quality_score=dataset.quality_score.overall_score if dataset.quality_score else None,
            connector_id=dataset.connector_id,
            template_id=dataset.template_id,
            metadata_json=self._metadata_to_json(dataset.metadata) if dataset.metadata else {}
        )

    def _update_model_from_domain(self, model: DatasetModel, dataset: Dataset) -> None:
        """Update model fields from domain entity."""
        model.name = dataset.name
        model.status = dataset.status
        model.ready_at = dataset.ready_at
        model.archived_at = dataset.archived_at
        model.record_count = dataset.record_count
        model.size_bytes = dataset.size_bytes
        model.quality_score = dataset.quality_score.overall_score if dataset.quality_score else None
        model.connector_id = dataset.connector_id
        model.metadata_json = self._metadata_to_json(dataset.metadata) if dataset.metadata else {}

    def _to_domain(self, model: DatasetModel) -> Dataset:
        """Convert SQLAlchemy model to domain entity."""
        # Convert quality checks
        quality_checks = [
            self._check_to_domain(check) for check in model.quality_checks
        ]

        # Recreate QualityScore if available
        quality_score = None
        if model.quality_score is not None and quality_checks:
            # Try to rebuild from checks
            schema_score = next((c.score for c in quality_checks if c.check_type.value == 'schema_validation'), 0.0)
            completeness_score = next((c.score for c in quality_checks if c.check_type.value == 'data_completeness'), 0.0)
            connector_score = next((c.score for c in quality_checks if c.check_type.value == 'connector_health'), 0.0)
            query_score = next((c.score for c in quality_checks if c.check_type.value == 'sample_query_success'), 0.0)

            quality_score = QualityScore.from_check_scores(
                schema_score, completeness_score, connector_score, query_score
            )

        # Recreate metadata
        metadata = self._json_to_metadata(model.metadata_json, model.data_source, model.stage)

        return Dataset(
            dataset_id=model.id,
            name=model.name,
            dataset_type=model.dataset_type,
            stage=model.stage,
            client_id=model.client_id,
            journey_id=model.journey_id,
            status=model.status,
            created_at=model.created_at,
            ready_at=model.ready_at,
            archived_at=model.archived_at,
            data_source=model.data_source,
            record_count=model.record_count,
            size_bytes=model.size_bytes,
            quality_score=quality_score,
            connector_id=model.connector_id,
            template_id=model.template_id,
            metadata=metadata,
            quality_checks=quality_checks
        )

    def _check_to_domain(self, model: DataQualityCheckModel) -> DataQualityCheck:
        """Convert quality check model to domain entity."""
        return DataQualityCheck(
            check_id=model.id,
            dataset_id=model.dataset_id,
            check_type=model.check_type,
            status=model.status,
            score=model.score,
            threshold=model.threshold,
            executed_at=model.executed_at,
            result=model.result,
            error_message=model.error_message
        )

    def _metadata_to_json(self, metadata: DatasetMetadata) -> dict:
        """Convert DatasetMetadata to JSON dict."""
        return {
            'industry': metadata.industry.value if metadata.industry else None,
            'use_case': metadata.use_case,
            'data_type': metadata.data_type.value,
            'stage': metadata.stage.value,
            'tags': metadata.tags,
            'custom_fields': metadata.custom_fields
        }

    def _json_to_metadata(self, json_data: dict, data_source: DataSource, stage: Stage) -> DatasetMetadata:
        """Convert JSON dict to DatasetMetadata."""
        from ....domain.types import Industry

        industry = None
        if json_data.get('industry'):
            try:
                industry = Industry(json_data['industry'])
            except ValueError:
                pass

        return DatasetMetadata(
            industry=industry,
            use_case=json_data.get('use_case'),
            data_type=data_source,
            stage=stage,
            tags=json_data.get('tags', []),
            custom_fields=json_data.get('custom_fields', {})
        )
