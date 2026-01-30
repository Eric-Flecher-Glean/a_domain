"""Dataset Metadata value object."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from ..types import Industry, DataSource, Stage


@dataclass(frozen=True)
class DatasetMetadata:
    """Immutable metadata describing dataset characteristics.

    Value object containing industry, use case, and categorization
    information for datasets and templates.
    """

    industry: Optional[Industry]
    use_case: Optional[str]
    data_type: DataSource
    stage: Stage
    tags: List[str] = field(default_factory=list)
    custom_fields: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        """Validate metadata on creation."""
        # Ensure tags is a list
        if not isinstance(self.tags, list):
            object.__setattr__(self, 'tags', list(self.tags) if self.tags else [])

        # Ensure custom_fields is a dict
        if not isinstance(self.custom_fields, dict):
            object.__setattr__(self, 'custom_fields', {})

    def with_tag(self, tag: str) -> "DatasetMetadata":
        """Return new metadata with additional tag."""
        new_tags = self.tags + [tag]
        return DatasetMetadata(
            industry=self.industry,
            use_case=self.use_case,
            data_type=self.data_type,
            stage=self.stage,
            tags=new_tags,
            custom_fields=self.custom_fields
        )

    def with_custom_field(self, key: str, value: str) -> "DatasetMetadata":
        """Return new metadata with additional custom field."""
        new_fields = {**self.custom_fields, key: value}
        return DatasetMetadata(
            industry=self.industry,
            use_case=self.use_case,
            data_type=self.data_type,
            stage=self.stage,
            tags=self.tags,
            custom_fields=new_fields
        )
