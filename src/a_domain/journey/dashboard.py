"""
Glean Dashboard Integration

Publishes journey status and metrics to Glean dashboard.
Based on Journey State Machine Design (DES-002).
"""

from typing import Dict, Any, Optional, List, Protocol
from datetime import datetime
import logging
from abc import ABC, abstractmethod

from .state_machine import JourneyState, JourneyStage
from .unit_of_work import UnitOfWork, WorkStatus


logger = logging.getLogger(__name__)


class GleanPublisher(ABC):
    """
    Abstract publisher for Glean dashboard integration.

    Real implementation would use Glean API to publish cards/notifications.
    This interface allows for testing with mock implementation.
    """

    @abstractmethod
    def publish_journey_status(
        self,
        client_id: str,
        journey_state: JourneyState,
        metrics: Dict[str, Any]
    ) -> bool:
        """
        Publish journey status to Glean dashboard.

        Args:
            client_id: Client identifier
            journey_state: Current journey state
            metrics: Journey metrics (duration, stage progress, etc.)

        Returns:
            True if published successfully, False otherwise
        """
        pass

    @abstractmethod
    def publish_stage_transition(
        self,
        client_id: str,
        from_stage: JourneyStage,
        to_stage: JourneyStage,
        reason: str
    ) -> bool:
        """
        Publish stage transition notification.

        Args:
            client_id: Client identifier
            from_stage: Previous stage
            to_stage: New stage
            reason: Transition reason

        Returns:
            True if published successfully, False otherwise
        """
        pass

    @abstractmethod
    def publish_alert(
        self,
        alert_type: str,
        client_id: str,
        message: str,
        severity: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Publish alert to Glean.

        Args:
            alert_type: Type of alert (bottleneck, sla_violation, etc.)
            client_id: Client identifier
            message: Alert message
            severity: Severity level (low, medium, high, critical)
            metadata: Additional alert metadata

        Returns:
            True if published successfully, False otherwise
        """
        pass


class MockGleanPublisher(GleanPublisher):
    """
    Mock Glean publisher for testing.

    Stores published data in memory for verification.
    """

    def __init__(self):
        self._journey_updates: List[Dict[str, Any]] = []
        self._transitions: List[Dict[str, Any]] = []
        self._alerts: List[Dict[str, Any]] = []

    def publish_journey_status(
        self,
        client_id: str,
        journey_state: JourneyState,
        metrics: Dict[str, Any]
    ) -> bool:
        """Store journey status update"""
        self._journey_updates.append({
            "client_id": client_id,
            "current_stage": journey_state.current_stage.value,
            "previous_stage": journey_state.previous_stage.value if journey_state.previous_stage else None,
            "stage_duration_days": journey_state.get_stage_duration_days(),
            "total_duration_days": journey_state.get_total_duration_days(),
            "metrics": metrics,
            "timestamp": datetime.utcnow().isoformat()
        })
        logger.info(
            f"[MOCK] Published journey status for {client_id}: {journey_state.current_stage.value}",
            extra={"client_id": client_id}
        )
        return True

    def publish_stage_transition(
        self,
        client_id: str,
        from_stage: JourneyStage,
        to_stage: JourneyStage,
        reason: str
    ) -> bool:
        """Store transition notification"""
        self._transitions.append({
            "client_id": client_id,
            "from_stage": from_stage.value,
            "to_stage": to_stage.value,
            "reason": reason,
            "timestamp": datetime.utcnow().isoformat()
        })
        logger.info(
            f"[MOCK] Published transition: {client_id} {from_stage.value} → {to_stage.value}",
            extra={"client_id": client_id}
        )
        return True

    def publish_alert(
        self,
        alert_type: str,
        client_id: str,
        message: str,
        severity: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Store alert"""
        self._alerts.append({
            "alert_type": alert_type,
            "client_id": client_id,
            "message": message,
            "severity": severity,
            "metadata": metadata or {},
            "timestamp": datetime.utcnow().isoformat()
        })
        logger.warning(
            f"[MOCK] Published alert: {alert_type} for {client_id} ({severity})",
            extra={"client_id": client_id, "severity": severity}
        )
        return True

    def get_journey_updates(self, client_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get journey status updates"""
        if client_id:
            return [u for u in self._journey_updates if u["client_id"] == client_id]
        return self._journey_updates.copy()

    def get_transitions(self, client_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get stage transitions"""
        if client_id:
            return [t for t in self._transitions if t["client_id"] == client_id]
        return self._transitions.copy()

    def get_alerts(self, client_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get alerts"""
        if client_id:
            return [a for a in self._alerts if a["client_id"] == client_id]
        return self._alerts.copy()

    def clear(self):
        """Clear all stored data"""
        self._journey_updates.clear()
        self._transitions.clear()
        self._alerts.clear()


class JourneyDashboardService:
    """
    Service for publishing journey data to Glean dashboard.

    Coordinates journey state updates, stage transitions, and alerts.
    """

    def __init__(self, publisher: GleanPublisher):
        """
        Initialize dashboard service.

        Args:
            publisher: Glean publisher implementation
        """
        self._publisher = publisher
        self._sla_thresholds = {
            JourneyStage.SANDBOX: 15.0,  # days
            JourneyStage.PILOT: 15.0,
            JourneyStage.PRODUCTION: 30.0
        }

    def set_sla_threshold(self, stage: JourneyStage, days: float):
        """Set SLA threshold for stage (in days)"""
        self._sla_thresholds[stage] = days

    def publish_journey_update(
        self,
        client_id: str,
        journey_state: JourneyState,
        exit_criteria_status: Optional[Dict[str, bool]] = None
    ) -> bool:
        """
        Publish journey status update to dashboard (AC1).

        Args:
            client_id: Client identifier
            journey_state: Current journey state
            exit_criteria_status: Exit criteria validation results

        Returns:
            True if published successfully
        """
        # Build metrics
        metrics = {
            "stage_duration_days": journey_state.get_stage_duration_days(),
            "total_duration_days": journey_state.get_total_duration_days(),
            "completed_stages": [s.value for s in journey_state.completed_stages],
            "exit_criteria_status": exit_criteria_status or {},
            "metadata": journey_state.metadata
        }

        # Check for SLA violations (AC3)
        self._check_sla_violation(client_id, journey_state)

        return self._publisher.publish_journey_status(
            client_id,
            journey_state,
            metrics
        )

    def publish_transition(
        self,
        client_id: str,
        from_stage: JourneyStage,
        to_stage: JourneyStage,
        reason: str
    ) -> bool:
        """
        Publish stage transition notification (AC2).

        Args:
            client_id: Client identifier
            from_stage: Previous stage
            to_stage: New stage
            reason: Transition reason

        Returns:
            True if published successfully
        """
        return self._publisher.publish_stage_transition(
            client_id,
            from_stage,
            to_stage,
            reason
        )

    def publish_uow_metrics(
        self,
        client_id: str,
        uow: UnitOfWork,
        labor_cost: Optional[float] = None
    ) -> bool:
        """
        Publish unit of work execution metrics (AC4).

        Args:
            client_id: Client identifier
            uow: Unit of work
            labor_cost: Labor cost for UoW execution

        Returns:
            True if published successfully
        """
        duration = uow.get_execution_duration_seconds()

        metrics = {
            "work_id": uow.work_id,
            "stage": uow.stage,
            "status": uow.status.value,
            "task_count": len(uow.tasks),
            "completed_tasks": len(uow.get_completed_tasks()),
            "failed_tasks": len(uow.get_failed_tasks()),
            "duration_seconds": duration,
            "labor_cost": labor_cost
        }

        # Check for bottlenecks (AC3)
        self._check_bottleneck(client_id, uow)

        logger.info(
            f"Published UoW metrics for {client_id}",
            extra={"client_id": client_id, "work_id": uow.work_id}
        )

        return True

    def _check_sla_violation(
        self,
        client_id: str,
        journey_state: JourneyState
    ):
        """Check if stage duration exceeds SLA threshold"""
        stage = journey_state.current_stage
        if stage not in self._sla_thresholds:
            return

        threshold = self._sla_thresholds[stage]
        duration = journey_state.get_stage_duration_days()

        if duration > threshold:
            self._publisher.publish_alert(
                alert_type="sla_violation",
                client_id=client_id,
                message=f"Stage {stage.value} exceeded SLA threshold ({duration:.1f} days > {threshold} days)",
                severity="high",
                metadata={
                    "stage": stage.value,
                    "duration_days": duration,
                    "threshold_days": threshold,
                    "overage_days": duration - threshold
                }
            )

    def _check_bottleneck(
        self,
        client_id: str,
        uow: UnitOfWork
    ):
        """Check if UoW execution indicates bottleneck"""
        # Bottleneck indicators:
        # 1. Failed tasks
        # 2. Long execution time (>1 hour)
        # 3. High retry count

        failed_count = len(uow.get_failed_tasks())
        if failed_count > 0:
            self._publisher.publish_alert(
                alert_type="bottleneck",
                client_id=client_id,
                message=f"UoW {uow.work_id} has {failed_count} failed tasks",
                severity="medium",
                metadata={
                    "work_id": uow.work_id,
                    "stage": uow.stage,
                    "failed_tasks": [t.task_id for t in uow.get_failed_tasks()]
                }
            )

        duration = uow.get_execution_duration_seconds()
        if duration and duration > 3600:  # >1 hour
            self._publisher.publish_alert(
                alert_type="bottleneck",
                client_id=client_id,
                message=f"UoW {uow.work_id} execution exceeded 1 hour ({duration/3600:.1f} hours)",
                severity="low",
                metadata={
                    "work_id": uow.work_id,
                    "stage": uow.stage,
                    "duration_hours": duration / 3600
                }
            )

    def get_journey_summary(
        self,
        client_id: str,
        journey_state: JourneyState
    ) -> Dict[str, Any]:
        """
        Get comprehensive journey summary for dashboard display (AC1).

        Args:
            client_id: Client identifier
            journey_state: Current journey state

        Returns:
            Journey summary dictionary
        """
        return {
            "client_id": client_id,
            "current_stage": journey_state.current_stage.value,
            "previous_stage": journey_state.previous_stage.value if journey_state.previous_stage else None,
            "started_at": journey_state.started_at.isoformat(),
            "stage_started_at": journey_state.stage_started_at.isoformat(),
            "stage_duration_days": journey_state.get_stage_duration_days(),
            "total_duration_days": journey_state.get_total_duration_days(),
            "completed_stages": [s.value for s in journey_state.completed_stages],
            "stage_history_count": len(journey_state.stage_history),
            "metadata": journey_state.metadata,
            "sla_threshold_days": self._sla_thresholds.get(journey_state.current_stage),
            "is_terminal": journey_state.current_stage in (JourneyStage.COMPLETED, JourneyStage.CANCELLED)
        }
