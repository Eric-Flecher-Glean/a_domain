"""
Journey State Machine Implementation

Manages client journey state transitions with validation.
Based on State Machine Design (DES-002).
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import threading


class JourneyStage(Enum):
    """Journey stage enumeration"""
    SANDBOX = "sandbox"
    PILOT = "pilot"
    PRODUCTION = "production"
    ROLLBACK = "rollback"  # Temporary state during rollback
    COMPLETED = "completed"  # Final state (success)
    CANCELLED = "cancelled"  # Final state (failure)


class TransitionEvent(Enum):
    """Events that trigger state transitions"""
    START_JOURNEY = "start_journey"
    PROMOTE_TO_PILOT = "promote_to_pilot"
    PROMOTE_TO_PRODUCTION = "promote_to_production"
    INITIATE_ROLLBACK = "initiate_rollback"
    COMPLETE_ROLLBACK = "complete_rollback"
    CANCEL_JOURNEY = "cancel_journey"
    MARK_COMPLETE = "mark_complete"


@dataclass
class StageTransition:
    """Record of a stage transition"""
    from_stage: Optional[JourneyStage]
    to_stage: JourneyStage
    transitioned_at: datetime
    reason: str
    exit_criteria_results: Optional[Dict[str, bool]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "from_stage": self.from_stage.value if self.from_stage else None,
            "to_stage": self.to_stage.value,
            "transitioned_at": self.transitioned_at.isoformat(),
            "reason": self.reason,
            "exit_criteria_results": self.exit_criteria_results or {}
        }


@dataclass
class JourneyState:
    """Current state of a client journey"""
    client_id: str
    current_stage: JourneyStage
    previous_stage: Optional[JourneyStage]
    started_at: datetime
    stage_started_at: datetime
    completed_stages: List[JourneyStage] = field(default_factory=list)
    stage_history: List[StageTransition] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "client_id": self.client_id,
            "current_stage": self.current_stage.value,
            "previous_stage": self.previous_stage.value if self.previous_stage else None,
            "started_at": self.started_at.isoformat(),
            "stage_started_at": self.stage_started_at.isoformat(),
            "completed_stages": [s.value for s in self.completed_stages],
            "stage_history": [t.to_dict() for t in self.stage_history],
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "JourneyState":
        """Create JourneyState from dictionary"""
        return cls(
            client_id=data["client_id"],
            current_stage=JourneyStage(data["current_stage"]),
            previous_stage=JourneyStage(data["previous_stage"]) if data.get("previous_stage") else None,
            started_at=datetime.fromisoformat(data["started_at"]),
            stage_started_at=datetime.fromisoformat(data["stage_started_at"]),
            completed_stages=[JourneyStage(s) for s in data.get("completed_stages", [])],
            stage_history=[],  # Simplified for now
            metadata=data.get("metadata", {})
        )

    def get_stage_duration_days(self) -> float:
        """Get duration in current stage (days)"""
        duration = datetime.utcnow() - self.stage_started_at
        return duration.total_seconds() / 86400

    def get_total_duration_days(self) -> float:
        """Get total journey duration (days)"""
        duration = datetime.utcnow() - self.started_at
        return duration.total_seconds() / 86400


class InvalidTransitionError(Exception):
    """Raised when an invalid state transition is attempted"""
    pass


class JourneyStateMachine:
    """
    State machine for client journey orchestration.

    Implements state transitions with validation.
    Thread-safe for concurrent journey management.
    """

    # Valid transitions map: (from_state, event) -> to_state
    TRANSITIONS = {
        (None, TransitionEvent.START_JOURNEY): JourneyStage.SANDBOX,
        (JourneyStage.SANDBOX, TransitionEvent.PROMOTE_TO_PILOT): JourneyStage.PILOT,
        (JourneyStage.PILOT, TransitionEvent.PROMOTE_TO_PRODUCTION): JourneyStage.PRODUCTION,
        (JourneyStage.PRODUCTION, TransitionEvent.MARK_COMPLETE): JourneyStage.COMPLETED,

        # Rollback transitions (from any active stage)
        (JourneyStage.SANDBOX, TransitionEvent.INITIATE_ROLLBACK): JourneyStage.ROLLBACK,
        (JourneyStage.PILOT, TransitionEvent.INITIATE_ROLLBACK): JourneyStage.ROLLBACK,
        (JourneyStage.PRODUCTION, TransitionEvent.INITIATE_ROLLBACK): JourneyStage.ROLLBACK,

        # Rollback completion (returns to previous stage) - handled dynamically
        (JourneyStage.ROLLBACK, TransitionEvent.COMPLETE_ROLLBACK): None,  # Dynamic

        # Cancellation (from any state)
        (JourneyStage.SANDBOX, TransitionEvent.CANCEL_JOURNEY): JourneyStage.CANCELLED,
        (JourneyStage.PILOT, TransitionEvent.CANCEL_JOURNEY): JourneyStage.CANCELLED,
        (JourneyStage.PRODUCTION, TransitionEvent.CANCEL_JOURNEY): JourneyStage.CANCELLED,
        (JourneyStage.ROLLBACK, TransitionEvent.CANCEL_JOURNEY): JourneyStage.CANCELLED,
    }

    def __init__(self):
        self._lock = threading.Lock()

    def start_journey(self, client_id: str, metadata: Optional[Dict[str, Any]] = None) -> JourneyState:
        """
        Start a new client journey.

        Args:
            client_id: Unique client identifier
            metadata: Additional journey metadata

        Returns:
            Initial journey state (SANDBOX)
        """
        with self._lock:
            now = datetime.utcnow()

            state = JourneyState(
                client_id=client_id,
                current_stage=JourneyStage.SANDBOX,
                previous_stage=None,
                started_at=now,
                stage_started_at=now,
                completed_stages=[],
                stage_history=[
                    StageTransition(
                        from_stage=None,
                        to_stage=JourneyStage.SANDBOX,
                        transitioned_at=now,
                        reason="Journey started"
                    )
                ],
                metadata=metadata or {}
            )

            return state

    def transition(
        self,
        state: JourneyState,
        event: TransitionEvent,
        reason: str = "",
        exit_criteria_results: Optional[Dict[str, bool]] = None
    ) -> JourneyState:
        """
        Execute state transition with validation.

        Args:
            state: Current journey state
            event: Transition event
            reason: Reason for transition
            exit_criteria_results: Exit criteria validation results

        Returns:
            New journey state

        Raises:
            InvalidTransitionError: If transition not allowed
        """
        with self._lock:
            current_stage = state.current_stage

            # Check if transition is valid
            transition_key = (current_stage, event)
            if transition_key not in self.TRANSITIONS:
                raise InvalidTransitionError(
                    f"Invalid transition: {current_stage.value} + {event.value}"
                )

            # Get target stage
            target_stage = self.TRANSITIONS[transition_key]

            # Special handling for rollback completion (return to previous stage)
            if event == TransitionEvent.COMPLETE_ROLLBACK:
                if not state.previous_stage:
                    raise InvalidTransitionError(
                        "Cannot complete rollback: no previous stage recorded"
                    )
                target_stage = state.previous_stage

            # Create stage transition record
            transition = StageTransition(
                from_stage=current_stage,
                to_stage=target_stage,
                transitioned_at=datetime.utcnow(),
                reason=reason or f"Transition to {target_stage.value}",
                exit_criteria_results=exit_criteria_results
            )

            # Update completed stages (only for forward progression)
            completed = state.completed_stages.copy()
            if event in (TransitionEvent.PROMOTE_TO_PILOT, TransitionEvent.PROMOTE_TO_PRODUCTION, TransitionEvent.MARK_COMPLETE):
                completed.append(current_stage)

            # Create new state
            new_state = JourneyState(
                client_id=state.client_id,
                current_stage=target_stage,
                previous_stage=current_stage,
                started_at=state.started_at,
                stage_started_at=datetime.utcnow(),
                completed_stages=completed,
                stage_history=state.stage_history + [transition],
                metadata=state.metadata.copy()
            )

            return new_state

    def can_transition(self, state: JourneyState, event: TransitionEvent) -> bool:
        """
        Check if transition is allowed without executing it.

        Args:
            state: Current journey state
            event: Transition event

        Returns:
            True if transition is valid, False otherwise
        """
        transition_key = (state.current_stage, event)
        return transition_key in self.TRANSITIONS

    def get_available_transitions(self, state: JourneyState) -> List[TransitionEvent]:
        """
        Get list of available transition events for current state.

        Args:
            state: Current journey state

        Returns:
            List of valid transition events
        """
        available = []
        for (from_stage, event), to_stage in self.TRANSITIONS.items():
            if from_stage == state.current_stage:
                available.append(event)
        return available

    def is_terminal_state(self, state: JourneyState) -> bool:
        """
        Check if journey is in terminal state (completed or cancelled).

        Args:
            state: Journey state to check

        Returns:
            True if terminal, False otherwise
        """
        return state.current_stage in (JourneyStage.COMPLETED, JourneyStage.CANCELLED)
