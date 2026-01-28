"""
Client Journey Orchestration Engine

Automates client progression through deployment stages (Sandbox → Pilot → Production).
Based on System Architecture (ARCH-003) and State Machine Design (DES-002).
"""

from .state_machine import (
    JourneyStage,
    TransitionEvent,
    JourneyState,
    StageTransition,
    JourneyStateMachine,
    InvalidTransitionError
)

from .coordinator import JourneyCoordinator

__version__ = "1.0.0"

__all__ = [
    "JourneyStage",
    "TransitionEvent",
    "JourneyState",
    "StageTransition",
    "JourneyStateMachine",
    "InvalidTransitionError",
    "JourneyCoordinator",
]
