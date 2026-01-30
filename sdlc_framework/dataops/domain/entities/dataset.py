"""Dataset entity."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from ..types import DatasetType, DatasetStatus, DataSource, Stage
from ..value_objects import DatasetMetadata, QualityScore
from .data_quality_check import DataQualityCheck


@dataclass
class Dataset:
    """Entity representing a provisioned dataset in a client journey stage.

    Aggregates all information about a dataset including its lifecycle state,
    quality metrics, connector configuration, and relationships to templates
    and quality checks.

    Invariants:
    - Quality score must be ≥95% before status can be READY
    - Only one active dataset per client/stage/type combination
    - Archived datasets are immutable
    """

    dataset_id: UUID = field(default_factory=uuid4)
    name: str = field(default="")
    dataset_type: DatasetType = field(default=None)
    stage: Stage = field(default=None)
    client_id: UUID = field(default=None)
    journey_id: UUID = field(default=None)
    status: DatasetStatus = field(default=DatasetStatus.PROVISIONING)
    created_at: datetime = field(default_factory=datetime.utcnow)
    ready_at: Optional[datetime] = None
    archived_at: Optional[datetime] = None
    data_source: DataSource = field(default=DataSource.MOCK_TEMPLATE)
    record_count: int = 0
    size_bytes: int = 0
    quality_score: Optional[QualityScore] = None
    connector_id: Optional[UUID] = None
    template_id: Optional[UUID] = None
    metadata: Optional[DatasetMetadata] = None
    quality_checks: List[DataQualityCheck] = field(default_factory=list)

    def __post_init__(self):
        """Validate dataset on creation."""
        if not self.name:
            raise ValueError("Dataset name cannot be empty")

        if self.dataset_type is None:
            raise ValueError("Dataset type is required")

        if self.stage is None:
            raise ValueError("Stage is required")

        if self.client_id is None:
            raise ValueError("Client ID is required")

        if self.journey_id is None:
            raise ValueError("Journey ID is required")

        if self.record_count < 0:
            raise ValueError("Record count must be non-negative")

        if self.size_bytes < 0:
            raise ValueError("Size bytes must be non-negative")

    def can_mark_ready(self) -> bool:
        """Check if dataset can transition to READY status.

        Requirements:
        - Status must be VALIDATING
        - Quality score must be ≥95%
        - All 4 quality checks must have passed
        - Dataset must not be archived
        """
        if self.status == DatasetStatus.ARCHIVED:
            return False

        if self.status != DatasetStatus.VALIDATING:
            return False

        if not self.quality_score or not self.quality_score.meets_threshold:
            return False

        # Verify all 4 quality checks passed
        if len(self.quality_checks) < 4:
            return False

        return all(check.passed for check in self.quality_checks)

    def mark_ready(self) -> None:
        """Transition dataset to READY status.

        Raises:
            ValueError: If dataset cannot be marked ready
        """
        if not self.can_mark_ready():
            raise ValueError(
                f"Dataset {self.dataset_id} cannot be marked ready. "
                f"Status: {self.status}, Quality: {self.quality_score.overall_score if self.quality_score else 'None'}"
            )

        self.status = DatasetStatus.READY
        self.ready_at = datetime.utcnow()

    def update_quality_score(self, score: QualityScore) -> None:
        """Update dataset quality score.

        If quality drops below threshold while dataset is READY,
        reverts to VALIDATING status.
        """
        self.quality_score = score

        # Revert to validating if quality drops
        if self.status == DatasetStatus.READY and not score.meets_threshold:
            self.status = DatasetStatus.VALIDATING
            self.ready_at = None

    def add_quality_check(self, check: DataQualityCheck) -> None:
        """Add a quality check to this dataset."""
        if check.dataset_id != self.dataset_id:
            raise ValueError(
                f"Quality check dataset_id {check.dataset_id} doesn't match "
                f"dataset {self.dataset_id}"
            )

        self.quality_checks.append(check)

    def start_validation(self) -> None:
        """Transition from PROVISIONING to VALIDATING."""
        if self.status != DatasetStatus.PROVISIONING:
            raise ValueError(
                f"Cannot start validation from status {self.status}"
            )

        self.status = DatasetStatus.VALIDATING

    def mark_failed(self, reason: str) -> None:
        """Mark dataset as FAILED with reason."""
        self.status = DatasetStatus.FAILED
        # Store reason in metadata
        if self.metadata:
            self.metadata = self.metadata.with_custom_field("failure_reason", reason)

    def start_teardown(self) -> None:
        """Initiate dataset teardown process."""
        if self.status == DatasetStatus.ARCHIVED:
            raise ValueError("Cannot teardown already archived dataset")

        self.status = DatasetStatus.TEARDOWN

    def archive(self) -> None:
        """Mark dataset as archived (immutable final state)."""
        if self.status != DatasetStatus.TEARDOWN:
            raise ValueError(
                f"Cannot archive dataset from status {self.status}. "
                "Must be in TEARDOWN status first."
            )

        self.status = DatasetStatus.ARCHIVED
        self.archived_at = datetime.utcnow()

    def validate_invariants(self) -> List[str]:
        """Validate all dataset invariants.

        Returns:
            List of invariant violations (empty if all valid)
        """
        violations = []

        # Quality threshold invariant
        if self.status == DatasetStatus.READY:
            if not self.quality_score or not self.quality_score.meets_threshold:
                violations.append(
                    "READY dataset must have quality score ≥95%"
                )

        # Immutability invariant
        if self.status == DatasetStatus.ARCHIVED and self.archived_at is None:
            violations.append(
                "ARCHIVED dataset must have archived_at timestamp"
            )

        return violations

    def __str__(self) -> str:
        """Human-readable representation."""
        quality_str = f" ({self.quality_score.overall_score:.1f}%)" if self.quality_score else ""
        return (
            f"{self.name} [{self.status.value}]{quality_str} - "
            f"{self.dataset_type.value} ({self.stage.value})"
        )
