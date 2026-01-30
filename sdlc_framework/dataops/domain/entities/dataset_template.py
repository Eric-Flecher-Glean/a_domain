"""Dataset Template entity."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional
from uuid import UUID, uuid4

from ..types import DatasetType, Industry


@dataclass
class DatasetTemplate:
    """Entity representing a reusable dataset template.

    Templates define schemas, default configurations, and source data
    paths for creating datasets of a specific type for a specific
    industry/use-case combination.
    """

    template_id: UUID = field(default_factory=uuid4)
    name: str = field(default="")
    dataset_type: DatasetType = field(default=None)
    industry: Optional[Industry] = None
    use_case: Optional[str] = None
    description: str = ""
    source_path: Optional[Path] = None
    schema_definition: Dict = field(default_factory=dict)
    default_record_count: int = 100
    metadata_template: Dict = field(default_factory=dict)
    quality_rules: List[Dict] = field(default_factory=list)

    def __post_init__(self):
        """Validate template on creation."""
        if not self.name:
            raise ValueError("Template name cannot be empty")

        if self.dataset_type is None:
            raise ValueError("Dataset type is required")

        if self.default_record_count < 0:
            raise ValueError("Default record count must be non-negative")

        # Convert string path to Path if needed
        if isinstance(self.source_path, str):
            self.source_path = Path(self.source_path)

    @property
    def estimated_size_mb(self) -> float:
        """Estimate dataset size in MB based on schema and record count.

        This is a rough estimate - actual size depends on data content.
        """
        # Rough estimate: 1KB per record for typical document datasets
        bytes_per_record = 1024
        total_bytes = self.default_record_count * bytes_per_record
        return total_bytes / (1024 * 1024)

    def matches_criteria(
        self,
        industry: Optional[Industry] = None,
        use_case: Optional[str] = None,
        dataset_type: Optional[DatasetType] = None
    ) -> bool:
        """Check if template matches search criteria."""
        if industry and self.industry != industry:
            return False

        if use_case and self.use_case != use_case:
            return False

        if dataset_type and self.dataset_type != dataset_type:
            return False

        return True

    def __str__(self) -> str:
        """Human-readable representation."""
        industry_str = f" ({self.industry.value})" if self.industry else ""
        return f"{self.name}{industry_str} - {self.dataset_type.value}"
