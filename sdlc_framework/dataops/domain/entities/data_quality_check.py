"""Data Quality Check entity."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Optional
from uuid import UUID, uuid4

from ..types import CheckType, CheckStatus


@dataclass
class DataQualityCheck:
    """Entity representing a quality validation check on a dataset.

    Each check validates one aspect of dataset quality:
    - Schema validation: All records match expected schema
    - Data completeness: Required fields populated, record count met
    - Connector health: Connection working, auth valid, responsive
    - Sample queries: Test queries return expected results
    """

    check_id: UUID = field(default_factory=uuid4)
    dataset_id: UUID = field(default=None)
    check_type: CheckType = field(default=None)
    status: CheckStatus = field(default=CheckStatus.PENDING)
    score: float = field(default=0.0)
    threshold: float = field(default=95.0)
    executed_at: Optional[datetime] = None
    result: Dict = field(default_factory=dict)
    error_message: Optional[str] = None

    def __post_init__(self):
        """Validate check on creation."""
        if self.score < 0.0 or self.score > 100.0:
            raise ValueError(f"Score must be 0-100, got {self.score}")

        if self.threshold < 0.0 or self.threshold > 100.0:
            raise ValueError(f"Threshold must be 0-100, got {self.threshold}")

    @property
    def passed(self) -> bool:
        """Whether this check passed its threshold."""
        return self.status == CheckStatus.PASSED and self.score >= self.threshold

    def execute(self, score: float, result: Dict) -> None:
        """Mark check as executed with results.

        Args:
            score: Calculated score (0-100)
            result: Detailed check results (check-specific structure)
        """
        if score < 0.0 or score > 100.0:
            raise ValueError(f"Score must be 0-100, got {score}")

        self.score = score
        self.result = result
        self.executed_at = datetime.utcnow()

        # Determine pass/fail based on threshold
        if score >= self.threshold:
            self.status = CheckStatus.PASSED
        else:
            self.status = CheckStatus.FAILED
            self.error_message = (
                f"{self.check_type.value} failed: score {score:.1f}% "
                f"below threshold {self.threshold:.1f}%"
            )

    def fail(self, error: str) -> None:
        """Mark check as failed with error message."""
        self.status = CheckStatus.FAILED
        self.error_message = error
        self.executed_at = datetime.utcnow()
        self.score = 0.0

    def __str__(self) -> str:
        """Human-readable representation."""
        status_icon = {
            CheckStatus.PENDING: "⏳",
            CheckStatus.RUNNING: "⏳",
            CheckStatus.PASSED: "✅",
            CheckStatus.FAILED: "❌"
        }.get(self.status, "❓")

        return f"{status_icon} {self.check_type.value}: {self.score:.1f}% ({self.status.value})"
