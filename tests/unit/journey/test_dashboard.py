"""
Unit tests for Glean Dashboard Integration

Tests journey publishing, notifications, and alerts.
Validates AC1, AC2, AC3, and AC4 of P1-A2A-F1-003.
"""

import pytest
from datetime import datetime, timedelta

from a_domain.journey.dashboard import (
    MockGleanPublisher,
    JourneyDashboardService
)
from a_domain.journey.state_machine import (
    JourneyStage,
    JourneyState
)
from a_domain.journey.unit_of_work import (
    UnitOfWork,
    Task,
    TaskStatus,
    WorkStatus
)


class TestMockGleanPublisher:
    """Test mock Glean publisher"""

    def setup_method(self):
        """Create publisher for each test"""
        self.publisher = MockGleanPublisher()

    def test_publish_journey_status(self):
        """Test publishing journey status"""
        journey_state = JourneyState(
            client_id="client-123",
            current_stage=JourneyStage.SANDBOX,
            previous_stage=None,
            started_at=datetime.utcnow(),
            stage_started_at=datetime.utcnow(),
            completed_stages=[],
            stage_history=[],
            metadata={"contract": "c-456"}
        )

        result = self.publisher.publish_journey_status(
            "client-123",
            journey_state,
            {"duration": 5.0}
        )

        assert result is True
        updates = self.publisher.get_journey_updates("client-123")
        assert len(updates) == 1
        assert updates[0]["client_id"] == "client-123"
        assert updates[0]["current_stage"] == "sandbox"

    def test_publish_stage_transition(self):
        """Test publishing stage transition"""
        result = self.publisher.publish_stage_transition(
            "client-123",
            JourneyStage.SANDBOX,
            JourneyStage.PILOT,
            "Exit criteria met"
        )

        assert result is True
        transitions = self.publisher.get_transitions("client-123")
        assert len(transitions) == 1
        assert transitions[0]["from_stage"] == "sandbox"
        assert transitions[0]["to_stage"] == "pilot"
        assert transitions[0]["reason"] == "Exit criteria met"

    def test_publish_alert(self):
        """Test publishing alert"""
        result = self.publisher.publish_alert(
            alert_type="sla_violation",
            client_id="client-123",
            message="Stage exceeded SLA",
            severity="high",
            metadata={"duration": 20.0}
        )

        assert result is True
        alerts = self.publisher.get_alerts("client-123")
        assert len(alerts) == 1
        assert alerts[0]["alert_type"] == "sla_violation"
        assert alerts[0]["severity"] == "high"

    def test_filter_by_client(self):
        """Test filtering by client_id"""
        journey1 = JourneyState(
            client_id="client-1",
            current_stage=JourneyStage.SANDBOX,
            previous_stage=None,
            started_at=datetime.utcnow(),
            stage_started_at=datetime.utcnow(),
            completed_stages=[],
            stage_history=[],
            metadata={}
        )

        journey2 = JourneyState(
            client_id="client-2",
            current_stage=JourneyStage.PILOT,
            previous_stage=JourneyStage.SANDBOX,
            started_at=datetime.utcnow(),
            stage_started_at=datetime.utcnow(),
            completed_stages=[],
            stage_history=[],
            metadata={}
        )

        self.publisher.publish_journey_status("client-1", journey1, {})
        self.publisher.publish_journey_status("client-2", journey2, {})

        client1_updates = self.publisher.get_journey_updates("client-1")
        assert len(client1_updates) == 1
        assert client1_updates[0]["client_id"] == "client-1"

    def test_clear(self):
        """Test clearing all data"""
        journey = JourneyState(
            client_id="client-123",
            current_stage=JourneyStage.SANDBOX,
            previous_stage=None,
            started_at=datetime.utcnow(),
            stage_started_at=datetime.utcnow(),
            completed_stages=[],
            stage_history=[],
            metadata={}
        )

        self.publisher.publish_journey_status("client-123", journey, {})
        self.publisher.publish_stage_transition(
            "client-123",
            JourneyStage.SANDBOX,
            JourneyStage.PILOT,
            "test"
        )
        self.publisher.publish_alert("test", "client-123", "msg", "low")

        self.publisher.clear()

        assert len(self.publisher.get_journey_updates()) == 0
        assert len(self.publisher.get_transitions()) == 0
        assert len(self.publisher.get_alerts()) == 0


class TestJourneyDashboardService:
    """Test journey dashboard service"""

    def setup_method(self):
        """Create service for each test"""
        self.publisher = MockGleanPublisher()
        self.service = JourneyDashboardService(self.publisher)

    def test_publish_journey_update(self):
        """Test publishing journey update to dashboard (AC1)"""
        journey_state = JourneyState(
            client_id="client-123",
            current_stage=JourneyStage.SANDBOX,
            previous_stage=None,
            started_at=datetime.utcnow(),
            stage_started_at=datetime.utcnow(),
            completed_stages=[],
            stage_history=[],
            metadata={"key": "value"}
        )

        exit_criteria = {
            "connectors_syncing": True,
            "search_quality": True
        }

        result = self.service.publish_journey_update(
            "client-123",
            journey_state,
            exit_criteria
        )

        assert result is True
        updates = self.publisher.get_journey_updates("client-123")
        assert len(updates) == 1
        assert updates[0]["metrics"]["exit_criteria_status"] == exit_criteria

    def test_publish_transition_notification(self):
        """Test publishing stage transition (AC2)"""
        result = self.service.publish_transition(
            "client-123",
            JourneyStage.SANDBOX,
            JourneyStage.PILOT,
            "Sandbox exit criteria met"
        )

        assert result is True
        transitions = self.publisher.get_transitions("client-123")
        assert len(transitions) == 1
        assert transitions[0]["from_stage"] == "sandbox"
        assert transitions[0]["to_stage"] == "pilot"

    def test_sla_violation_alert(self):
        """Test SLA violation alert is triggered (AC3)"""
        # Create journey that has been in stage for 20 days
        past_date = datetime.utcnow() - timedelta(days=20)
        journey_state = JourneyState(
            client_id="client-123",
            current_stage=JourneyStage.SANDBOX,
            previous_stage=None,
            started_at=past_date,
            stage_started_at=past_date,
            completed_stages=[],
            stage_history=[],
            metadata={}
        )

        # Set SLA threshold to 15 days
        self.service.set_sla_threshold(JourneyStage.SANDBOX, 15.0)

        # Publish update should trigger SLA alert
        self.service.publish_journey_update("client-123", journey_state)

        alerts = self.publisher.get_alerts("client-123")
        assert len(alerts) == 1
        assert alerts[0]["alert_type"] == "sla_violation"
        assert alerts[0]["severity"] == "high"
        assert "exceeded SLA threshold" in alerts[0]["message"]

    def test_no_sla_alert_within_threshold(self):
        """Test no SLA alert when within threshold"""
        journey_state = JourneyState(
            client_id="client-123",
            current_stage=JourneyStage.SANDBOX,
            previous_stage=None,
            started_at=datetime.utcnow(),
            stage_started_at=datetime.utcnow(),
            completed_stages=[],
            stage_history=[],
            metadata={}
        )

        self.service.set_sla_threshold(JourneyStage.SANDBOX, 15.0)
        self.service.publish_journey_update("client-123", journey_state)

        alerts = self.publisher.get_alerts("client-123")
        assert len(alerts) == 0

    def test_publish_uow_metrics(self):
        """Test publishing UoW metrics with labor cost (AC4)"""
        task1 = Task(
            task_id="task-1",
            name="Task 1",
            description="",
            agent_id="agent-1",
            intent="intent-1",
            input_schema={},
            output_schema={},
            depends_on=[]
        )
        task1.status = TaskStatus.COMPLETED

        uow = UnitOfWork(
            work_id="uow-1",
            stage="sandbox",
            client_id="client-123",
            tasks=[task1],
            status=WorkStatus.COMPLETED
        )
        uow.started_at = datetime.utcnow()
        uow.completed_at = datetime.utcnow()

        result = self.service.publish_uow_metrics(
            "client-123",
            uow,
            labor_cost=150.00
        )

        assert result is True

    def test_bottleneck_alert_for_failed_tasks(self):
        """Test bottleneck alert when UoW has failed tasks (AC3)"""
        task1 = Task(
            task_id="task-1",
            name="Task 1",
            description="",
            agent_id="agent-1",
            intent="intent-1",
            input_schema={},
            output_schema={},
            depends_on=[]
        )
        task1.status = TaskStatus.FAILED

        uow = UnitOfWork(
            work_id="uow-1",
            stage="sandbox",
            client_id="client-123",
            tasks=[task1],
            status=WorkStatus.FAILED
        )
        uow.started_at = datetime.utcnow()
        uow.completed_at = datetime.utcnow()

        self.service.publish_uow_metrics("client-123", uow)

        alerts = self.publisher.get_alerts("client-123")
        assert len(alerts) == 1
        assert alerts[0]["alert_type"] == "bottleneck"
        assert "failed tasks" in alerts[0]["message"]

    def test_bottleneck_alert_for_long_execution(self):
        """Test bottleneck alert for long UoW execution (AC3)"""
        task1 = Task(
            task_id="task-1",
            name="Task 1",
            description="",
            agent_id="agent-1",
            intent="intent-1",
            input_schema={},
            output_schema={},
            depends_on=[]
        )
        task1.status = TaskStatus.COMPLETED

        uow = UnitOfWork(
            work_id="uow-1",
            stage="sandbox",
            client_id="client-123",
            tasks=[task1],
            status=WorkStatus.COMPLETED
        )
        # Simulate 2-hour execution
        uow.started_at = datetime.utcnow() - timedelta(hours=2)
        uow.completed_at = datetime.utcnow()

        self.service.publish_uow_metrics("client-123", uow)

        alerts = self.publisher.get_alerts("client-123")
        assert len(alerts) == 1
        assert alerts[0]["alert_type"] == "bottleneck"
        assert "exceeded 1 hour" in alerts[0]["message"]

    def test_get_journey_summary(self):
        """Test getting comprehensive journey summary (AC1)"""
        past_date = datetime.utcnow() - timedelta(days=5)
        journey_state = JourneyState(
            client_id="client-123",
            current_stage=JourneyStage.PILOT,
            previous_stage=JourneyStage.SANDBOX,
            started_at=past_date,
            stage_started_at=datetime.utcnow() - timedelta(days=2),
            completed_stages=[JourneyStage.SANDBOX],
            stage_history=[],
            metadata={"contract": "c-456"}
        )

        summary = self.service.get_journey_summary("client-123", journey_state)

        assert summary["client_id"] == "client-123"
        assert summary["current_stage"] == "pilot"
        assert summary["previous_stage"] == "sandbox"
        assert summary["stage_duration_days"] >= 2.0
        assert summary["total_duration_days"] >= 5.0
        assert summary["completed_stages"] == ["sandbox"]
        assert summary["metadata"]["contract"] == "c-456"
        assert summary["is_terminal"] is False

    def test_terminal_state_detection(self):
        """Test terminal state detection in summary"""
        journey_state = JourneyState(
            client_id="client-123",
            current_stage=JourneyStage.COMPLETED,
            previous_stage=JourneyStage.PRODUCTION,
            started_at=datetime.utcnow(),
            stage_started_at=datetime.utcnow(),
            completed_stages=[],
            stage_history=[],
            metadata={}
        )

        summary = self.service.get_journey_summary("client-123", journey_state)
        assert summary["is_terminal"] is True

    def test_set_sla_threshold(self):
        """Test setting custom SLA thresholds"""
        self.service.set_sla_threshold(JourneyStage.SANDBOX, 20.0)
        self.service.set_sla_threshold(JourneyStage.PILOT, 25.0)

        # Create journey just under threshold
        past_date = datetime.utcnow() - timedelta(days=19)
        journey_state = JourneyState(
            client_id="client-123",
            current_stage=JourneyStage.SANDBOX,
            previous_stage=None,
            started_at=past_date,
            stage_started_at=past_date,
            completed_stages=[],
            stage_history=[],
            metadata={}
        )

        self.service.publish_journey_update("client-123", journey_state)

        # Should not trigger alert (19 days < 20 day threshold)
        alerts = self.publisher.get_alerts("client-123")
        assert len(alerts) == 0

    def test_multiple_clients_tracking(self):
        """Test tracking multiple clients independently"""
        journey1 = JourneyState(
            client_id="client-1",
            current_stage=JourneyStage.SANDBOX,
            previous_stage=None,
            started_at=datetime.utcnow(),
            stage_started_at=datetime.utcnow(),
            completed_stages=[],
            stage_history=[],
            metadata={}
        )

        journey2 = JourneyState(
            client_id="client-2",
            current_stage=JourneyStage.PILOT,
            previous_stage=JourneyStage.SANDBOX,
            started_at=datetime.utcnow(),
            stage_started_at=datetime.utcnow(),
            completed_stages=[],
            stage_history=[],
            metadata={}
        )

        self.service.publish_journey_update("client-1", journey1)
        self.service.publish_journey_update("client-2", journey2)

        client1_updates = self.publisher.get_journey_updates("client-1")
        client2_updates = self.publisher.get_journey_updates("client-2")

        assert len(client1_updates) == 1
        assert len(client2_updates) == 1
        assert client1_updates[0]["current_stage"] == "sandbox"
        assert client2_updates[0]["current_stage"] == "pilot"

    def test_exit_criteria_included_in_metrics(self):
        """Test exit criteria status included in published metrics"""
        journey_state = JourneyState(
            client_id="client-123",
            current_stage=JourneyStage.SANDBOX,
            previous_stage=None,
            started_at=datetime.utcnow(),
            stage_started_at=datetime.utcnow(),
            completed_stages=[],
            stage_history=[],
            metadata={}
        )

        exit_criteria = {
            "connectors_syncing": True,
            "search_quality": False,
            "security_scan": True,
            "demo_approved": False
        }

        self.service.publish_journey_update("client-123", journey_state, exit_criteria)

        updates = self.publisher.get_journey_updates("client-123")
        assert updates[0]["metrics"]["exit_criteria_status"] == exit_criteria
