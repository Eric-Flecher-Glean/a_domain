"""Quality Score value object."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class QualityScore:
    """Immutable quality score calculated from validation checks.

    Represents the weighted average of 4 quality check types:
    - Schema Validation (30% weight)
    - Data Completeness (30% weight)
    - Connector Health (25% weight)
    - Sample Query Success (15% weight)

    A dataset requires overall_score >= 95.0 to be marked READY.
    """

    overall_score: float
    schema_validation_score: float
    data_completeness_score: float
    connector_health_score: float
    query_success_score: float
    calculated_at: datetime
    threshold: float = 95.0

    # Weights for score calculation
    SCHEMA_WEIGHT = 0.30
    COMPLETENESS_WEIGHT = 0.30
    CONNECTOR_WEIGHT = 0.25
    QUERY_WEIGHT = 0.15

    def __post_init__(self):
        """Validate scores on creation."""
        # Validate score ranges
        for score_name in ['overall_score', 'schema_validation_score',
                          'data_completeness_score', 'connector_health_score',
                          'query_success_score']:
            score_value = getattr(self, score_name)
            if not (0.0 <= score_value <= 100.0):
                raise ValueError(f"{score_name} must be between 0.0 and 100.0, got {score_value}")

        # Verify calculated score matches weighted average
        expected = self._calculate_weighted_score()
        if abs(self.overall_score - expected) > 0.1:  # Allow small floating point diff
            raise ValueError(
                f"Overall score {self.overall_score} doesn't match calculated "
                f"weighted average {expected:.2f}"
            )

    def _calculate_weighted_score(self) -> float:
        """Calculate weighted average of individual scores."""
        return (
            self.schema_validation_score * self.SCHEMA_WEIGHT +
            self.data_completeness_score * self.COMPLETENESS_WEIGHT +
            self.connector_health_score * self.CONNECTOR_WEIGHT +
            self.query_success_score * self.QUERY_WEIGHT
        )

    @property
    def meets_threshold(self) -> bool:
        """Check if quality score meets the ready threshold."""
        return self.overall_score >= self.threshold

    @classmethod
    def from_check_scores(
        cls,
        schema_score: float,
        completeness_score: float,
        connector_score: float,
        query_score: float,
        threshold: float = 95.0
    ) -> "QualityScore":
        """Create quality score from individual check scores.

        Automatically calculates weighted average as overall_score.
        """
        overall = (
            schema_score * cls.SCHEMA_WEIGHT +
            completeness_score * cls.COMPLETENESS_WEIGHT +
            connector_score * cls.CONNECTOR_WEIGHT +
            query_score * cls.QUERY_WEIGHT
        )

        return cls(
            overall_score=overall,
            schema_validation_score=schema_score,
            data_completeness_score=completeness_score,
            connector_health_score=connector_score,
            query_success_score=query_score,
            calculated_at=datetime.utcnow(),
            threshold=threshold
        )

    def __str__(self) -> str:
        """Human-readable quality score representation."""
        status = "✅ MEETS THRESHOLD" if self.meets_threshold else "❌ BELOW THRESHOLD"
        return (
            f"Quality Score: {self.overall_score:.1f}% {status}\n"
            f"  Schema: {self.schema_validation_score:.1f}% (30% weight)\n"
            f"  Completeness: {self.data_completeness_score:.1f}% (30% weight)\n"
            f"  Connector: {self.connector_health_score:.1f}% (25% weight)\n"
            f"  Queries: {self.query_success_score:.1f}% (15% weight)"
        )
