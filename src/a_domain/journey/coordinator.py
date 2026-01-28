"""
Journey Coordinator Implementation

Orchestrates client journey progression through deployment stages.
Based on Journey State Machine Design (DES-002).
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
import threading
import logging

from .state_machine import (
    JourneyStage,
    TransitionEvent,
    JourneyState,
    JourneyStateMachine,
    InvalidTransitionError
)


logger = logging.getLogger(__name__)


class JourneyCoordinator:
    """
    Coordinates client journey orchestration.

    Responsibilities:
    - Manage journey lifecycle (start, promote, rollback, cancel)
    - Execute state transitions via state machine
    - Track journey history and metadata
    - Provide journey state queries

    Thread-safe for concurrent journey management.
    """

    def __init__(self):
        self._state_machine = JourneyStateMachine()
        self._journeys: Dict[str, JourneyState] = {}
        self._lock = threading.Lock()

    def start_journey(
        self,
        client_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> JourneyState:
        """
        Start a new client journey in SANDBOX stage.

        Args:
            client_id: Unique client identifier
            metadata: Additional journey metadata (e.g., contact info, contract details)

        Returns:
            Initial journey state

        Raises:
            ValueError: If journey already exists for client_id
        """
        with self._lock:
            if client_id in self._journeys:
                raise ValueError(f"Journey already exists for client {client_id}")

            state = self._state_machine.start_journey(client_id, metadata)
            self._journeys[client_id] = state

            logger.info(
                f"Started journey for client {client_id}",
                extra={
                    "client_id": client_id,
                    "stage": state.current_stage.value,
                    "started_at": state.started_at.isoformat()
                }
            )

            return state

    def get_journey_state(self, client_id: str) -> Optional[JourneyState]:
        """
        Get current state of client journey.

        Args:
            client_id: Client identifier

        Returns:
            Journey state if exists, None otherwise
        """
        with self._lock:
            return self._journeys.get(client_id)

    def promote_to_pilot(
        self,
        client_id: str,
        reason: str = "",
        exit_criteria_results: Optional[Dict[str, bool]] = None
    ) -> JourneyState:
        """
        Promote client from SANDBOX to PILOT stage.

        Args:
            client_id: Client identifier
            reason: Reason for promotion
            exit_criteria_results: Exit criteria validation results

        Returns:
            New journey state

        Raises:
            ValueError: If journey not found
            InvalidTransitionError: If not in SANDBOX stage
        """
        return self._execute_transition(
            client_id,
            TransitionEvent.PROMOTE_TO_PILOT,
            reason or "Sandbox exit criteria met, promoting to Pilot",
            exit_criteria_results
        )

    def promote_to_production(
        self,
        client_id: str,
        reason: str = "",
        exit_criteria_results: Optional[Dict[str, bool]] = None
    ) -> JourneyState:
        """
        Promote client from PILOT to PRODUCTION stage.

        Args:
            client_id: Client identifier
            reason: Reason for promotion
            exit_criteria_results: Exit criteria validation results

        Returns:
            New journey state

        Raises:
            ValueError: If journey not found
            InvalidTransitionError: If not in PILOT stage
        """
        return self._execute_transition(
            client_id,
            TransitionEvent.PROMOTE_TO_PRODUCTION,
            reason or "Pilot exit criteria met, promoting to Production",
            exit_criteria_results
        )

    def mark_complete(
        self,
        client_id: str,
        reason: str = ""
    ) -> JourneyState:
        """
        Mark journey as COMPLETED (successful completion).

        Args:
            client_id: Client identifier
            reason: Reason for completion

        Returns:
            New journey state

        Raises:
            ValueError: If journey not found
            InvalidTransitionError: If not in PRODUCTION stage
        """
        return self._execute_transition(
            client_id,
            TransitionEvent.MARK_COMPLETE,
            reason or "Production success criteria met, journey complete"
        )

    def initiate_rollback(
        self,
        client_id: str,
        reason: str
    ) -> JourneyState:
        """
        Initiate rollback to ROLLBACK state.

        Args:
            client_id: Client identifier
            reason: Reason for rollback (e.g., "Critical security vulnerability")

        Returns:
            New journey state in ROLLBACK stage

        Raises:
            ValueError: If journey not found
            InvalidTransitionError: If in terminal state
        """
        return self._execute_transition(
            client_id,
            TransitionEvent.INITIATE_ROLLBACK,
            reason
        )

    def complete_rollback(
        self,
        client_id: str,
        reason: str = ""
    ) -> JourneyState:
        """
        Complete rollback and return to previous stage.

        Args:
            client_id: Client identifier
            reason: Reason for rollback completion

        Returns:
            New journey state (reverted to previous stage)

        Raises:
            ValueError: If journey not found
            InvalidTransitionError: If not in ROLLBACK stage
        """
        return self._execute_transition(
            client_id,
            TransitionEvent.COMPLETE_ROLLBACK,
            reason or "Rollback completed, returning to previous stage"
        )

    def cancel_journey(
        self,
        client_id: str,
        reason: str
    ) -> JourneyState:
        """
        Cancel journey (terminal failure state).

        Args:
            client_id: Client identifier
            reason: Reason for cancellation

        Returns:
            New journey state in CANCELLED stage

        Raises:
            ValueError: If journey not found
        """
        return self._execute_transition(
            client_id,
            TransitionEvent.CANCEL_JOURNEY,
            reason
        )

    def get_active_journeys(self) -> List[JourneyState]:
        """
        Get all active (non-terminal) journeys.

        Returns:
            List of journey states not in COMPLETED or CANCELLED
        """
        with self._lock:
            return [
                state for state in self._journeys.values()
                if not self._state_machine.is_terminal_state(state)
            ]

    def get_journeys_in_stage(self, stage: JourneyStage) -> List[JourneyState]:
        """
        Get all journeys currently in specified stage.

        Args:
            stage: Journey stage to filter by

        Returns:
            List of journey states in the specified stage
        """
        with self._lock:
            return [
                state for state in self._journeys.values()
                if state.current_stage == stage
            ]

    def get_available_transitions(self, client_id: str) -> List[TransitionEvent]:
        """
        Get available transition events for client journey.

        Args:
            client_id: Client identifier

        Returns:
            List of valid transition events

        Raises:
            ValueError: If journey not found
        """
        with self._lock:
            state = self._journeys.get(client_id)
            if not state:
                raise ValueError(f"Journey not found for client {client_id}")

            return self._state_machine.get_available_transitions(state)

    def _execute_transition(
        self,
        client_id: str,
        event: TransitionEvent,
        reason: str,
        exit_criteria_results: Optional[Dict[str, bool]] = None
    ) -> JourneyState:
        """
        Execute state transition with validation.

        Args:
            client_id: Client identifier
            event: Transition event
            reason: Reason for transition
            exit_criteria_results: Exit criteria validation results

        Returns:
            New journey state

        Raises:
            ValueError: If journey not found
            InvalidTransitionError: If transition not allowed
        """
        with self._lock:
            current_state = self._journeys.get(client_id)
            if not current_state:
                raise ValueError(f"Journey not found for client {client_id}")

            # Execute transition via state machine
            new_state = self._state_machine.transition(
                current_state,
                event,
                reason,
                exit_criteria_results
            )

            # Update stored state
            self._journeys[client_id] = new_state

            logger.info(
                f"Journey transition for client {client_id}",
                extra={
                    "client_id": client_id,
                    "from_stage": current_state.current_stage.value,
                    "to_stage": new_state.current_stage.value,
                    "event": event.value,
                    "reason": reason
                }
            )

            return new_state

    def get_journey_summary(self, client_id: str) -> Dict[str, Any]:
        """
        Get summary of journey progress.

        Args:
            client_id: Client identifier

        Returns:
            Journey summary with stage durations and progress

        Raises:
            ValueError: If journey not found
        """
        with self._lock:
            state = self._journeys.get(client_id)
            if not state:
                raise ValueError(f"Journey not found for client {client_id}")

            return {
                "client_id": client_id,
                "current_stage": state.current_stage.value,
                "previous_stage": state.previous_stage.value if state.previous_stage else None,
                "stage_duration_days": state.get_stage_duration_days(),
                "total_duration_days": state.get_total_duration_days(),
                "completed_stages": [s.value for s in state.completed_stages],
                "is_terminal": self._state_machine.is_terminal_state(state),
                "available_transitions": [e.value for e in self.get_available_transitions(client_id)],
                "stage_history_count": len(state.stage_history),
                "metadata": state.metadata
            }

    def persist_state(self, client_id: str) -> Dict[str, Any]:
        """
        Get serialized journey state for persistence.

        Args:
            client_id: Client identifier

        Returns:
            Serialized journey state

        Raises:
            ValueError: If journey not found
        """
        with self._lock:
            state = self._journeys.get(client_id)
            if not state:
                raise ValueError(f"Journey not found for client {client_id}")

            return state.to_dict()

    def restore_state(self, state_data: Dict[str, Any]) -> JourneyState:
        """
        Restore journey state from serialized data.

        Args:
            state_data: Serialized journey state

        Returns:
            Restored journey state

        Raises:
            ValueError: If journey already exists
        """
        with self._lock:
            state = JourneyState.from_dict(state_data)

            if state.client_id in self._journeys:
                raise ValueError(f"Journey already exists for client {state.client_id}")

            self._journeys[state.client_id] = state

            logger.info(
                f"Restored journey for client {state.client_id}",
                extra={
                    "client_id": state.client_id,
                    "stage": state.current_stage.value
                }
            )

            return state
