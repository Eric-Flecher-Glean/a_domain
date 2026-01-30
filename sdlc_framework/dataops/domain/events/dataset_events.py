"""Domain events for dataset lifecycle."""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from ..types import Stage


@dataclass(frozen=True)
class DatasetProvisionRequested:
    """Event: Client requests dataset provisioning for journey stage."""

    event_id: UUID
    journey_id: UUID
    client_id: UUID
    stage: Stage
    dataset_types: List[str]
    requested_at: datetime
    requested_by: str

    @classmethod
    def create(
        cls,
        journey_id: UUID,
        client_id: UUID,
        stage: Stage,
        dataset_types: List[str],
        requested_by: str = "system"
    ) -> "DatasetProvisionRequested":
        """Create new provision requested event."""
        return cls(
            event_id=uuid4(),
            journey_id=journey_id,
            client_id=client_id,
            stage=stage,
            dataset_types=dataset_types,
            requested_at=datetime.utcnow(),
            requested_by=requested_by
        )


@dataclass(frozen=True)
class DatasetProvisioningStarted:
    """Event: Dataset provisioning has begun."""

    event_id: UUID
    dataset_id: UUID
    journey_id: UUID
    template_id: UUID
    stage: Stage
    started_at: datetime

    @classmethod
    def create(
        cls,
        dataset_id: UUID,
        journey_id: UUID,
        template_id: UUID,
        stage: Stage
    ) -> "DatasetProvisioningStarted":
        """Create new provisioning started event."""
        return cls(
            event_id=uuid4(),
            dataset_id=dataset_id,
            journey_id=journey_id,
            template_id=template_id,
            stage=stage,
            started_at=datetime.utcnow()
        )


@dataclass(frozen=True)
class DatasetProvisionCompleted:
    """Event: Dataset provisioning completed successfully."""

    event_id: UUID
    dataset_id: UUID
    journey_id: UUID
    quality_score: float
    record_count: int
    connector_id: UUID
    completed_at: datetime
    duration_minutes: int

    @classmethod
    def create(
        cls,
        dataset_id: UUID,
        journey_id: UUID,
        quality_score: float,
        record_count: int,
        connector_id: UUID,
        started_at: datetime
    ) -> "DatasetProvisionCompleted":
        """Create new provision completed event."""
        completed_at = datetime.utcnow()
        duration = (completed_at - started_at).total_seconds() / 60

        return cls(
            event_id=uuid4(),
            dataset_id=dataset_id,
            journey_id=journey_id,
            quality_score=quality_score,
            record_count=record_count,
            connector_id=connector_id,
            completed_at=completed_at,
            duration_minutes=int(duration)
        )


@dataclass(frozen=True)
class DatasetValidationFailed:
    """Event: Dataset quality validation failed."""

    event_id: UUID
    dataset_id: UUID
    journey_id: UUID
    failed_checks: List[str]
    error_message: str
    failed_at: datetime

    @classmethod
    def create(
        cls,
        dataset_id: UUID,
        journey_id: UUID,
        failed_checks: List[str],
        error_message: str
    ) -> "DatasetValidationFailed":
        """Create new validation failed event."""
        return cls(
            event_id=uuid4(),
            dataset_id=dataset_id,
            journey_id=journey_id,
            failed_checks=failed_checks,
            error_message=error_message,
            failed_at=datetime.utcnow()
        )


@dataclass(frozen=True)
class DatasetReady:
    """Event: Dataset is ready for use."""

    event_id: UUID
    dataset_id: UUID
    journey_id: UUID
    quality_score: float
    ready_at: datetime

    @classmethod
    def create(
        cls,
        dataset_id: UUID,
        journey_id: UUID,
        quality_score: float
    ) -> "DatasetReady":
        """Create new dataset ready event."""
        return cls(
            event_id=uuid4(),
            dataset_id=dataset_id,
            journey_id=journey_id,
            quality_score=quality_score,
            ready_at=datetime.utcnow()
        )


@dataclass(frozen=True)
class DatasetTeardownStarted:
    """Event: Dataset teardown initiated."""

    event_id: UUID
    dataset_id: UUID
    journey_id: UUID
    reason: str
    started_at: datetime

    @classmethod
    def create(
        cls,
        dataset_id: UUID,
        journey_id: UUID,
        reason: str = "stage_transition"
    ) -> "DatasetTeardownStarted":
        """Create new teardown started event."""
        return cls(
            event_id=uuid4(),
            dataset_id=dataset_id,
            journey_id=journey_id,
            reason=reason,
            started_at=datetime.utcnow()
        )


@dataclass(frozen=True)
class DatasetArchived:
    """Event: Dataset archived (final state)."""

    event_id: UUID
    dataset_id: UUID
    journey_id: UUID
    archive_location: str
    archived_at: datetime
    original_size_bytes: int

    @classmethod
    def create(
        cls,
        dataset_id: UUID,
        journey_id: UUID,
        archive_location: str,
        original_size_bytes: int
    ) -> "DatasetArchived":
        """Create new dataset archived event."""
        return cls(
            event_id=uuid4(),
            dataset_id=dataset_id,
            journey_id=journey_id,
            archive_location=archive_location,
            archived_at=datetime.utcnow(),
            original_size_bytes=original_size_bytes
        )
