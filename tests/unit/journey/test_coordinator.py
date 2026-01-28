"""
Unit tests for Journey Coordinator

Tests journey lifecycle management and thread safety.
Validates AC2 and AC4 of P0-A2A-F1-001.
"""

import pytest
from threading import Thread
from time import sleep

from a_domain.journey.coordinator import JourneyCoordinator
from a_domain.journey.state_machine import (
    JourneyStage,
    TransitionEvent,
    InvalidTransitionError
)


class TestJourneyCoordinator:
    """Test journey coordinator operations"""

    def setup_method(self):
        """Create coordinator instance for each test"""
        self.coordinator = JourneyCoordinator()

    def test_start_journey(self):
        """Test starting new journey (AC2)"""
        state = self.coordinator.start_journey(
            "client-123",
            metadata={"contract_id": "c-456", "contact": "john@example.com"}
        )

        assert state.client_id == "client-123"
        assert state.current_stage == JourneyStage.SANDBOX
        assert state.metadata["contract_id"] == "c-456"

    def test_start_journey_duplicate_raises_error(self):
        """Test starting duplicate journey raises ValueError"""
        self.coordinator.start_journey("client-123")

        with pytest.raises(ValueError) as exc_info:
            self.coordinator.start_journey("client-123")

        assert "already exists" in str(exc_info.value)

    def test_get_journey_state(self):
        """Test retrieving journey state"""
        self.coordinator.start_journey("client-123")

        state = self.coordinator.get_journey_state("client-123")
        assert state is not None
        assert state.client_id == "client-123"

        # Non-existent journey returns None
        assert self.coordinator.get_journey_state("client-999") is None

    def test_promote_to_pilot(self):
        """Test promoting from SANDBOX to PILOT (AC2)"""
        self.coordinator.start_journey("client-123")

        criteria_results = {
            "connectors_syncing": True,
            "search_quality": True,
            "security_scan": True,
            "demo_approved": True
        }

        new_state = self.coordinator.promote_to_pilot(
            "client-123",
            reason="All sandbox criteria met",
            exit_criteria_results=criteria_results
        )

        assert new_state.current_stage == JourneyStage.PILOT
        assert new_state.previous_stage == JourneyStage.SANDBOX

    def test_promote_to_production(self):
        """Test promoting from PILOT to PRODUCTION (AC2)"""
        self.coordinator.start_journey("client-123")
        self.coordinator.promote_to_pilot("client-123")

        criteria_results = {
            "search_quality": True,
            "user_satisfaction": True,
            "no_critical_bugs": True,
            "performance_sla": True
        }

        new_state = self.coordinator.promote_to_production(
            "client-123",
            reason="Pilot success",
            exit_criteria_results=criteria_results
        )

        assert new_state.current_stage == JourneyStage.PRODUCTION
        assert new_state.previous_stage == JourneyStage.PILOT

    def test_mark_complete(self):
        """Test marking journey as COMPLETED (AC2)"""
        self.coordinator.start_journey("client-123")
        self.coordinator.promote_to_pilot("client-123")
        self.coordinator.promote_to_production("client-123")

        final_state = self.coordinator.mark_complete(
            "client-123",
            reason="Production success metrics achieved"
        )

        assert final_state.current_stage == JourneyStage.COMPLETED

    def test_full_journey_lifecycle(self):
        """Test complete journey: SANDBOX → PILOT → PRODUCTION → COMPLETED (AC2)"""
        # Start journey
        state1 = self.coordinator.start_journey("client-123")
        assert state1.current_stage == JourneyStage.SANDBOX

        # Promote to pilot
        state2 = self.coordinator.promote_to_pilot("client-123")
        assert state2.current_stage == JourneyStage.PILOT

        # Promote to production
        state3 = self.coordinator.promote_to_production("client-123")
        assert state3.current_stage == JourneyStage.PRODUCTION

        # Mark complete
        state4 = self.coordinator.mark_complete("client-123")
        assert state4.current_stage == JourneyStage.COMPLETED

        # Verify history
        assert len(state4.stage_history) == 4
        assert JourneyStage.SANDBOX in state4.completed_stages
        assert JourneyStage.PILOT in state4.completed_stages
        assert JourneyStage.PRODUCTION in state4.completed_stages

    def test_initiate_rollback(self):
        """Test initiating rollback from current stage"""
        self.coordinator.start_journey("client-123")
        self.coordinator.promote_to_pilot("client-123")

        rollback_state = self.coordinator.initiate_rollback(
            "client-123",
            reason="Critical security vulnerability detected"
        )

        assert rollback_state.current_stage == JourneyStage.ROLLBACK
        assert rollback_state.previous_stage == JourneyStage.PILOT

    def test_complete_rollback(self):
        """Test completing rollback returns to previous stage"""
        self.coordinator.start_journey("client-123")
        self.coordinator.promote_to_pilot("client-123")
        self.coordinator.initiate_rollback("client-123", "Test rollback")

        restored_state = self.coordinator.complete_rollback(
            "client-123",
            reason="Issues resolved"
        )

        assert restored_state.current_stage == JourneyStage.PILOT
        assert restored_state.previous_stage == JourneyStage.ROLLBACK

    def test_cancel_journey(self):
        """Test cancelling journey"""
        self.coordinator.start_journey("client-123")

        cancelled_state = self.coordinator.cancel_journey(
            "client-123",
            reason="Contract terminated"
        )

        assert cancelled_state.current_stage == JourneyStage.CANCELLED

    def test_get_active_journeys(self):
        """Test filtering active (non-terminal) journeys"""
        # Create 3 journeys in different states
        self.coordinator.start_journey("client-1")  # SANDBOX (active)
        self.coordinator.start_journey("client-2")
        self.coordinator.promote_to_pilot("client-2")  # PILOT (active)

        self.coordinator.start_journey("client-3")
        self.coordinator.cancel_journey("client-3", "Test")  # CANCELLED (terminal)

        active = self.coordinator.get_active_journeys()
        assert len(active) == 2
        assert all(j.client_id in ["client-1", "client-2"] for j in active)

    def test_get_journeys_in_stage(self):
        """Test filtering journeys by stage"""
        self.coordinator.start_journey("client-1")  # SANDBOX
        self.coordinator.start_journey("client-2")
        self.coordinator.promote_to_pilot("client-2")  # PILOT
        self.coordinator.start_journey("client-3")  # SANDBOX

        sandbox_journeys = self.coordinator.get_journeys_in_stage(JourneyStage.SANDBOX)
        assert len(sandbox_journeys) == 2
        assert all(j.client_id in ["client-1", "client-3"] for j in sandbox_journeys)

        pilot_journeys = self.coordinator.get_journeys_in_stage(JourneyStage.PILOT)
        assert len(pilot_journeys) == 1
        assert pilot_journeys[0].client_id == "client-2"

    def test_get_available_transitions(self):
        """Test getting available transitions for journey"""
        self.coordinator.start_journey("client-123")

        available = self.coordinator.get_available_transitions("client-123")
        assert TransitionEvent.PROMOTE_TO_PILOT in available
        assert TransitionEvent.INITIATE_ROLLBACK in available
        assert TransitionEvent.CANCEL_JOURNEY in available

    def test_get_available_transitions_not_found(self):
        """Test getting transitions for non-existent journey raises error"""
        with pytest.raises(ValueError) as exc_info:
            self.coordinator.get_available_transitions("client-999")

        assert "not found" in str(exc_info.value)

    def test_invalid_transition_raises_error(self):
        """Test invalid transition raises InvalidTransitionError"""
        self.coordinator.start_journey("client-123")

        # Cannot promote directly to production from sandbox
        with pytest.raises(InvalidTransitionError):
            self.coordinator.promote_to_production("client-123")

    def test_transition_nonexistent_journey_raises_error(self):
        """Test operations on non-existent journey raise ValueError"""
        with pytest.raises(ValueError):
            self.coordinator.promote_to_pilot("client-999")

        with pytest.raises(ValueError):
            self.coordinator.promote_to_production("client-999")

        with pytest.raises(ValueError):
            self.coordinator.mark_complete("client-999")

    def test_get_journey_summary(self):
        """Test getting journey summary with progress"""
        self.coordinator.start_journey("client-123", metadata={"key": "value"})
        self.coordinator.promote_to_pilot("client-123")

        summary = self.coordinator.get_journey_summary("client-123")

        assert summary["client_id"] == "client-123"
        assert summary["current_stage"] == "pilot"
        assert summary["previous_stage"] == "sandbox"
        assert summary["stage_duration_days"] >= 0
        assert summary["total_duration_days"] >= 0
        assert "sandbox" in summary["completed_stages"]
        assert summary["is_terminal"] is False
        assert summary["stage_history_count"] == 2
        assert summary["metadata"]["key"] == "value"

    def test_persist_and_restore_state(self):
        """Test state persistence and restoration"""
        # Create journey
        self.coordinator.start_journey("client-123", metadata={"test": "data"})
        self.coordinator.promote_to_pilot("client-123")

        # Persist state
        state_data = self.coordinator.persist_state("client-123")
        assert state_data["client_id"] == "client-123"
        assert state_data["current_stage"] == "pilot"

        # Create new coordinator and restore
        new_coordinator = JourneyCoordinator()
        restored_state = new_coordinator.restore_state(state_data)

        assert restored_state.client_id == "client-123"
        assert restored_state.current_stage == JourneyStage.PILOT
        assert restored_state.metadata["test"] == "data"

    def test_restore_duplicate_state_raises_error(self):
        """Test restoring duplicate journey raises error"""
        self.coordinator.start_journey("client-123")
        state_data = self.coordinator.persist_state("client-123")

        with pytest.raises(ValueError) as exc_info:
            self.coordinator.restore_state(state_data)

        assert "already exists" in str(exc_info.value)

    def test_thread_safety_concurrent_journeys(self):
        """Test thread-safe concurrent journey management (AC4)"""
        results = []
        errors = []

        def create_and_promote_journey(client_id):
            try:
                coordinator = JourneyCoordinator()
                coordinator.start_journey(client_id)
                state = coordinator.promote_to_pilot(client_id)
                results.append(state)
            except Exception as e:
                errors.append(e)

        # Create 20 concurrent journeys
        threads = []
        for i in range(20):
            t = Thread(target=create_and_promote_journey, args=(f"client-{i}",))
            threads.append(t)
            t.start()

        # Wait for all threads
        for t in threads:
            t.join()

        # All should succeed
        assert len(errors) == 0
        assert len(results) == 20
        assert all(s.current_stage == JourneyStage.PILOT for s in results)

    def test_thread_safety_shared_coordinator(self):
        """Test thread-safe operations on shared coordinator instance (AC4)"""
        errors = []

        def perform_operations(client_id):
            try:
                self.coordinator.start_journey(client_id)
                sleep(0.001)  # Small delay to increase concurrency
                self.coordinator.promote_to_pilot(client_id)
                sleep(0.001)
                state = self.coordinator.get_journey_state(client_id)
                assert state.current_stage == JourneyStage.PILOT
            except Exception as e:
                errors.append(e)

        # 10 concurrent operations on shared coordinator
        threads = []
        for i in range(10):
            t = Thread(target=perform_operations, args=(f"client-{i}",))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        # All should succeed
        assert len(errors) == 0
        assert len(self.coordinator.get_active_journeys()) == 10

    def test_concurrent_reads_during_writes(self):
        """Test concurrent reads during write operations (AC4)"""
        self.coordinator.start_journey("client-123")

        read_results = []
        errors = []

        def read_state():
            try:
                for _ in range(50):
                    state = self.coordinator.get_journey_state("client-123")
                    if state:
                        read_results.append(state.current_stage)
            except Exception as e:
                errors.append(e)

        def write_state():
            try:
                sleep(0.01)
                self.coordinator.promote_to_pilot("client-123")
            except Exception as e:
                errors.append(e)

        # Start read threads
        read_threads = [Thread(target=read_state) for _ in range(5)]
        for t in read_threads:
            t.start()

        # Start write thread
        write_thread = Thread(target=write_state)
        write_thread.start()

        # Wait for all
        for t in read_threads:
            t.join()
        write_thread.join()

        # No errors
        assert len(errors) == 0
        # Reads should have seen both SANDBOX and PILOT stages
        assert JourneyStage.SANDBOX in read_results or JourneyStage.PILOT in read_results

    def test_multiple_journeys_independent(self):
        """Test multiple journeys operate independently"""
        # Create 3 journeys at different stages
        self.coordinator.start_journey("client-1")
        self.coordinator.start_journey("client-2")
        self.coordinator.promote_to_pilot("client-2")
        self.coordinator.start_journey("client-3")
        self.coordinator.promote_to_pilot("client-3")
        self.coordinator.promote_to_production("client-3")

        # Verify each is in correct stage
        state1 = self.coordinator.get_journey_state("client-1")
        state2 = self.coordinator.get_journey_state("client-2")
        state3 = self.coordinator.get_journey_state("client-3")

        assert state1.current_stage == JourneyStage.SANDBOX
        assert state2.current_stage == JourneyStage.PILOT
        assert state3.current_stage == JourneyStage.PRODUCTION

    def test_rollback_lifecycle(self):
        """Test complete rollback lifecycle"""
        # Create journey and promote
        self.coordinator.start_journey("client-123")
        self.coordinator.promote_to_pilot("client-123")
        self.coordinator.promote_to_production("client-123")

        # Initiate rollback from production
        rollback_state = self.coordinator.initiate_rollback(
            "client-123",
            reason="P0 incident detected"
        )
        assert rollback_state.current_stage == JourneyStage.ROLLBACK
        assert rollback_state.previous_stage == JourneyStage.PRODUCTION

        # Complete rollback
        restored_state = self.coordinator.complete_rollback(
            "client-123",
            reason="Incident resolved"
        )
        assert restored_state.current_stage == JourneyStage.PRODUCTION

        # Can still progress after rollback
        final_state = self.coordinator.mark_complete("client-123")
        assert final_state.current_stage == JourneyStage.COMPLETED
