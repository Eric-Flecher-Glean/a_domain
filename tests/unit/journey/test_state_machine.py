"""
Unit tests for Journey State Machine

Tests state transitions, validation, and thread safety.
Validates AC1 and AC4 of P0-A2A-F1-001.
"""

import pytest
from datetime import datetime
from threading import Thread
from time import sleep

from a_domain.journey.state_machine import (
    JourneyStage,
    TransitionEvent,
    JourneyState,
    StageTransition,
    JourneyStateMachine,
    InvalidTransitionError
)


class TestJourneyStage:
    """Test journey stage enumeration"""

    def test_all_stages_defined(self):
        """Test all 6 journey stages are defined"""
        stages = list(JourneyStage)
        assert len(stages) == 6
        assert JourneyStage.SANDBOX in stages
        assert JourneyStage.PILOT in stages
        assert JourneyStage.PRODUCTION in stages
        assert JourneyStage.ROLLBACK in stages
        assert JourneyStage.COMPLETED in stages
        assert JourneyStage.CANCELLED in stages

    def test_stage_values(self):
        """Test stage enum values"""
        assert JourneyStage.SANDBOX.value == "sandbox"
        assert JourneyStage.PILOT.value == "pilot"
        assert JourneyStage.PRODUCTION.value == "production"
        assert JourneyStage.ROLLBACK.value == "rollback"
        assert JourneyStage.COMPLETED.value == "completed"
        assert JourneyStage.CANCELLED.value == "cancelled"


class TestTransitionEvent:
    """Test transition event enumeration"""

    def test_all_events_defined(self):
        """Test all 7 transition events are defined"""
        events = list(TransitionEvent)
        assert len(events) == 7
        assert TransitionEvent.START_JOURNEY in events
        assert TransitionEvent.PROMOTE_TO_PILOT in events
        assert TransitionEvent.PROMOTE_TO_PRODUCTION in events
        assert TransitionEvent.INITIATE_ROLLBACK in events
        assert TransitionEvent.COMPLETE_ROLLBACK in events
        assert TransitionEvent.CANCEL_JOURNEY in events
        assert TransitionEvent.MARK_COMPLETE in events


class TestStageTransition:
    """Test stage transition record"""

    def test_create_transition(self):
        """Test creating stage transition record"""
        transition = StageTransition(
            from_stage=JourneyStage.SANDBOX,
            to_stage=JourneyStage.PILOT,
            transitioned_at=datetime.utcnow(),
            reason="Sandbox exit criteria met",
            exit_criteria_results={"connectors": True, "search_quality": True}
        )

        assert transition.from_stage == JourneyStage.SANDBOX
        assert transition.to_stage == JourneyStage.PILOT
        assert transition.reason == "Sandbox exit criteria met"
        assert transition.exit_criteria_results["connectors"] is True

    def test_transition_to_dict(self):
        """Test transition serialization"""
        now = datetime.utcnow()
        transition = StageTransition(
            from_stage=JourneyStage.SANDBOX,
            to_stage=JourneyStage.PILOT,
            transitioned_at=now,
            reason="Test",
            exit_criteria_results={"check1": True}
        )

        data = transition.to_dict()
        assert data["from_stage"] == "sandbox"
        assert data["to_stage"] == "pilot"
        assert data["transitioned_at"] == now.isoformat()
        assert data["reason"] == "Test"
        assert data["exit_criteria_results"]["check1"] is True


class TestJourneyState:
    """Test journey state data class"""

    def test_create_state(self):
        """Test creating journey state"""
        now = datetime.utcnow()
        state = JourneyState(
            client_id="client-123",
            current_stage=JourneyStage.SANDBOX,
            previous_stage=None,
            started_at=now,
            stage_started_at=now,
            completed_stages=[],
            stage_history=[],
            metadata={"contract_id": "contract-456"}
        )

        assert state.client_id == "client-123"
        assert state.current_stage == JourneyStage.SANDBOX
        assert state.previous_stage is None
        assert state.metadata["contract_id"] == "contract-456"

    def test_state_to_dict(self):
        """Test state serialization"""
        now = datetime.utcnow()
        state = JourneyState(
            client_id="client-123",
            current_stage=JourneyStage.PILOT,
            previous_stage=JourneyStage.SANDBOX,
            started_at=now,
            stage_started_at=now,
            completed_stages=[JourneyStage.SANDBOX],
            stage_history=[],
            metadata={"key": "value"}
        )

        data = state.to_dict()
        assert data["client_id"] == "client-123"
        assert data["current_stage"] == "pilot"
        assert data["previous_stage"] == "sandbox"
        assert data["completed_stages"] == ["sandbox"]
        assert data["metadata"]["key"] == "value"

    def test_state_from_dict(self):
        """Test state deserialization"""
        data = {
            "client_id": "client-123",
            "current_stage": "pilot",
            "previous_stage": "sandbox",
            "started_at": "2026-01-01T00:00:00",
            "stage_started_at": "2026-01-15T00:00:00",
            "completed_stages": ["sandbox"],
            "metadata": {"key": "value"}
        }

        state = JourneyState.from_dict(data)
        assert state.client_id == "client-123"
        assert state.current_stage == JourneyStage.PILOT
        assert state.previous_stage == JourneyStage.SANDBOX
        assert JourneyStage.SANDBOX in state.completed_stages
        assert state.metadata["key"] == "value"

    def test_get_stage_duration_days(self):
        """Test calculating stage duration"""
        past_time = datetime.utcnow()
        # Sleep briefly to ensure duration > 0
        sleep(0.01)

        state = JourneyState(
            client_id="client-123",
            current_stage=JourneyStage.SANDBOX,
            previous_stage=None,
            started_at=past_time,
            stage_started_at=past_time,
            completed_stages=[],
            stage_history=[],
            metadata={}
        )

        duration = state.get_stage_duration_days()
        assert duration >= 0  # Should be a small positive number

    def test_get_total_duration_days(self):
        """Test calculating total journey duration"""
        past_time = datetime.utcnow()
        sleep(0.01)

        state = JourneyState(
            client_id="client-123",
            current_stage=JourneyStage.PILOT,
            previous_stage=JourneyStage.SANDBOX,
            started_at=past_time,
            stage_started_at=datetime.utcnow(),
            completed_stages=[JourneyStage.SANDBOX],
            stage_history=[],
            metadata={}
        )

        duration = state.get_total_duration_days()
        assert duration >= 0


class TestJourneyStateMachine:
    """Test state machine transitions"""

    def setup_method(self):
        """Create state machine instance for each test"""
        self.sm = JourneyStateMachine()

    def test_start_journey(self):
        """Test starting new journey creates SANDBOX state"""
        state = self.sm.start_journey("client-123", {"contract": "c-456"})

        assert state.client_id == "client-123"
        assert state.current_stage == JourneyStage.SANDBOX
        assert state.previous_stage is None
        assert state.metadata["contract"] == "c-456"
        assert len(state.stage_history) == 1
        assert state.stage_history[0].to_stage == JourneyStage.SANDBOX

    def test_promote_sandbox_to_pilot(self):
        """Test valid transition from SANDBOX to PILOT"""
        state = self.sm.start_journey("client-123")

        new_state = self.sm.transition(
            state,
            TransitionEvent.PROMOTE_TO_PILOT,
            reason="Exit criteria met"
        )

        assert new_state.current_stage == JourneyStage.PILOT
        assert new_state.previous_stage == JourneyStage.SANDBOX
        assert JourneyStage.SANDBOX in new_state.completed_stages
        assert len(new_state.stage_history) == 2

    def test_promote_pilot_to_production(self):
        """Test valid transition from PILOT to PRODUCTION"""
        state = self.sm.start_journey("client-123")
        state = self.sm.transition(state, TransitionEvent.PROMOTE_TO_PILOT)

        new_state = self.sm.transition(
            state,
            TransitionEvent.PROMOTE_TO_PRODUCTION,
            reason="Pilot success"
        )

        assert new_state.current_stage == JourneyStage.PRODUCTION
        assert new_state.previous_stage == JourneyStage.PILOT
        assert JourneyStage.PILOT in new_state.completed_stages

    def test_mark_production_complete(self):
        """Test marking production as COMPLETED"""
        state = self.sm.start_journey("client-123")
        state = self.sm.transition(state, TransitionEvent.PROMOTE_TO_PILOT)
        state = self.sm.transition(state, TransitionEvent.PROMOTE_TO_PRODUCTION)

        new_state = self.sm.transition(
            state,
            TransitionEvent.MARK_COMPLETE,
            reason="Production success metrics met"
        )

        assert new_state.current_stage == JourneyStage.COMPLETED
        assert self.sm.is_terminal_state(new_state)

    def test_invalid_transition_raises_error(self):
        """Test invalid transition raises InvalidTransitionError"""
        state = self.sm.start_journey("client-123")

        # Cannot go directly from SANDBOX to PRODUCTION
        with pytest.raises(InvalidTransitionError) as exc_info:
            self.sm.transition(state, TransitionEvent.PROMOTE_TO_PRODUCTION)

        assert "Invalid transition" in str(exc_info.value)

    def test_initiate_rollback_from_pilot(self):
        """Test initiating rollback from PILOT stage"""
        state = self.sm.start_journey("client-123")
        state = self.sm.transition(state, TransitionEvent.PROMOTE_TO_PILOT)

        rollback_state = self.sm.transition(
            state,
            TransitionEvent.INITIATE_ROLLBACK,
            reason="Critical issue detected"
        )

        assert rollback_state.current_stage == JourneyStage.ROLLBACK
        assert rollback_state.previous_stage == JourneyStage.PILOT

    def test_complete_rollback_returns_to_previous_stage(self):
        """Test completing rollback returns to previous stage"""
        state = self.sm.start_journey("client-123")
        state = self.sm.transition(state, TransitionEvent.PROMOTE_TO_PILOT)
        rollback_state = self.sm.transition(state, TransitionEvent.INITIATE_ROLLBACK)

        restored_state = self.sm.transition(
            rollback_state,
            TransitionEvent.COMPLETE_ROLLBACK,
            reason="Issues resolved"
        )

        assert restored_state.current_stage == JourneyStage.PILOT
        assert restored_state.previous_stage == JourneyStage.ROLLBACK

    def test_cancel_journey_from_any_stage(self):
        """Test cancelling journey from different stages"""
        # Cancel from SANDBOX
        state = self.sm.start_journey("client-123")
        cancelled = self.sm.transition(state, TransitionEvent.CANCEL_JOURNEY, "Contract cancelled")
        assert cancelled.current_stage == JourneyStage.CANCELLED
        assert self.sm.is_terminal_state(cancelled)

        # Cancel from PILOT
        state2 = self.sm.start_journey("client-456")
        state2 = self.sm.transition(state2, TransitionEvent.PROMOTE_TO_PILOT)
        cancelled2 = self.sm.transition(state2, TransitionEvent.CANCEL_JOURNEY, "Client withdrawn")
        assert cancelled2.current_stage == JourneyStage.CANCELLED

    def test_can_transition_validates_event(self):
        """Test can_transition checks without executing"""
        state = self.sm.start_journey("client-123")

        assert self.sm.can_transition(state, TransitionEvent.PROMOTE_TO_PILOT)
        assert not self.sm.can_transition(state, TransitionEvent.PROMOTE_TO_PRODUCTION)
        assert self.sm.can_transition(state, TransitionEvent.INITIATE_ROLLBACK)
        assert self.sm.can_transition(state, TransitionEvent.CANCEL_JOURNEY)

    def test_get_available_transitions(self):
        """Test getting list of available transitions"""
        state = self.sm.start_journey("client-123")

        available = self.sm.get_available_transitions(state)
        assert TransitionEvent.PROMOTE_TO_PILOT in available
        assert TransitionEvent.INITIATE_ROLLBACK in available
        assert TransitionEvent.CANCEL_JOURNEY in available
        assert TransitionEvent.PROMOTE_TO_PRODUCTION not in available

    def test_is_terminal_state(self):
        """Test terminal state detection"""
        state = self.sm.start_journey("client-123")
        assert not self.sm.is_terminal_state(state)

        completed_state = JourneyState(
            client_id="client-456",
            current_stage=JourneyStage.COMPLETED,
            previous_stage=JourneyStage.PRODUCTION,
            started_at=datetime.utcnow(),
            stage_started_at=datetime.utcnow(),
            completed_stages=[],
            stage_history=[],
            metadata={}
        )
        assert self.sm.is_terminal_state(completed_state)

        cancelled_state = JourneyState(
            client_id="client-789",
            current_stage=JourneyStage.CANCELLED,
            previous_stage=JourneyStage.SANDBOX,
            started_at=datetime.utcnow(),
            stage_started_at=datetime.utcnow(),
            completed_stages=[],
            stage_history=[],
            metadata={}
        )
        assert self.sm.is_terminal_state(cancelled_state)

    def test_exit_criteria_results_stored(self):
        """Test exit criteria results are stored in transition history"""
        state = self.sm.start_journey("client-123")

        criteria_results = {
            "connectors_syncing": True,
            "search_quality": True,
            "security_scan": True,
            "demo_approved": True
        }

        new_state = self.sm.transition(
            state,
            TransitionEvent.PROMOTE_TO_PILOT,
            reason="All criteria passed",
            exit_criteria_results=criteria_results
        )

        latest_transition = new_state.stage_history[-1]
        assert latest_transition.exit_criteria_results == criteria_results

    def test_thread_safety_concurrent_transitions(self):
        """Test thread-safe state transitions (AC4)"""
        results = []
        errors = []

        def transition_journey(client_id):
            try:
                sm = JourneyStateMachine()
                state = sm.start_journey(client_id)
                state = sm.transition(state, TransitionEvent.PROMOTE_TO_PILOT)
                results.append(state)
            except Exception as e:
                errors.append(e)

        # Create 10 concurrent journeys
        threads = []
        for i in range(10):
            t = Thread(target=transition_journey, args=(f"client-{i}",))
            threads.append(t)
            t.start()

        # Wait for all threads
        for t in threads:
            t.join()

        # All should succeed without errors
        assert len(errors) == 0
        assert len(results) == 10
        assert all(s.current_stage == JourneyStage.PILOT for s in results)

    def test_rollback_without_previous_stage_fails(self):
        """Test rollback fails if no previous stage recorded"""
        # Create state in ROLLBACK with no previous stage
        state = JourneyState(
            client_id="client-123",
            current_stage=JourneyStage.ROLLBACK,
            previous_stage=None,
            started_at=datetime.utcnow(),
            stage_started_at=datetime.utcnow(),
            completed_stages=[],
            stage_history=[],
            metadata={}
        )

        with pytest.raises(InvalidTransitionError) as exc_info:
            self.sm.transition(state, TransitionEvent.COMPLETE_ROLLBACK)

        assert "no previous stage" in str(exc_info.value)
