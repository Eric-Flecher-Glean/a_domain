"""Dataset Template repository implementation."""

from pathlib import Path
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from ....domain.entities import DatasetTemplate
from ....domain.types import DatasetType, Industry
from ..models import DatasetTemplateModel
from .base_repository import BaseRepository


class TemplateRepository(BaseRepository[DatasetTemplateModel]):
    """Repository for DatasetTemplate entities."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, DatasetTemplateModel)

    async def find_by_criteria(
        self,
        industry: Optional[Industry] = None,
        use_case: Optional[str] = None,
        dataset_type: Optional[DatasetType] = None
    ) -> List[DatasetTemplate]:
        """Find templates matching search criteria."""
        conditions = []

        if industry:
            conditions.append(DatasetTemplateModel.industry == industry)

        if use_case:
            conditions.append(DatasetTemplateModel.use_case == use_case)

        if dataset_type:
            conditions.append(DatasetTemplateModel.dataset_type == dataset_type)

        query = select(DatasetTemplateModel)
        if conditions:
            query = query.where(and_(*conditions))

        result = await self.session.execute(query)
        models = result.scalars().all()

        return [self._to_domain(model) for model in models]

    async def save_template(self, template: DatasetTemplate) -> DatasetTemplate:
        """Save template entity (insert or update)."""
        # Check if exists
        existing = await self.get_by_id(template.template_id)

        if existing:
            # Update existing
            model = existing
            self._update_model_from_domain(model, template)
        else:
            # Create new
            model = self._to_model(template)

        model = await self.save(model)
        return self._to_domain(model)

    def _to_model(self, template: DatasetTemplate) -> DatasetTemplateModel:
        """Convert domain entity to SQLAlchemy model."""
        return DatasetTemplateModel(
            id=template.template_id,
            name=template.name,
            dataset_type=template.dataset_type,
            industry=template.industry,
            use_case=template.use_case,
            description=template.description,
            source_path=str(template.source_path) if template.source_path else None,
            schema_definition=template.schema_definition,
            default_record_count=template.default_record_count,
            metadata_template=template.metadata_template,
            quality_rules=template.quality_rules
        )

    def _update_model_from_domain(
        self,
        model: DatasetTemplateModel,
        template: DatasetTemplate
    ) -> None:
        """Update model fields from domain entity."""
        model.name = template.name
        model.description = template.description
        model.schema_definition = template.schema_definition
        model.default_record_count = template.default_record_count
        model.metadata_template = template.metadata_template
        model.quality_rules = template.quality_rules

    def _to_domain(self, model: DatasetTemplateModel) -> DatasetTemplate:
        """Convert SQLAlchemy model to domain entity."""
        return DatasetTemplate(
            template_id=model.id,
            name=model.name,
            dataset_type=model.dataset_type,
            industry=model.industry,
            use_case=model.use_case,
            description=model.description,
            source_path=Path(model.source_path) if model.source_path else None,
            schema_definition=model.schema_definition,
            default_record_count=model.default_record_count,
            metadata_template=model.metadata_template,
            quality_rules=model.quality_rules
        )
