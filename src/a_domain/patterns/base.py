#!/usr/bin/env -S uv run --quiet --script
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

"""
Base Pattern for A/B Agent Collaboration

Defines the abstract interface for all A/B collaboration patterns.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Callable
from datetime import datetime
from uuid import uuid4
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../.."))

from src.a_domain.protocol import ProtocolMessage, ProtocolBrokerAgent


@dataclass
class ABWorkflowContext:
    """
    Context for A/B workflow execution.

    Captures state, inputs, outputs, and observability data.
    """
    workflow_id: str = field(default_factory=lambda: f"ab-workflow-{uuid4()}")
    started_at: datetime = field(default_factory=datetime.utcnow)

    # Inputs
    input_data: Dict[str, Any] = field(default_factory=dict)

    # State
    current_iteration: int = 0
    max_iterations: int = 3
    is_complete: bool = False

    # Outputs
    final_output: Optional[Any] = None
    iteration_history: List[Dict[str, Any]] = field(default_factory=list)

    # Observability
    messages_exchanged: int = 0
    total_duration_ms: float = 0.0

    def record_iteration(self, iteration_data: Dict[str, Any]) -> None:
        """Record data from a completed iteration."""
        self.iteration_history.append({
            "iteration": self.current_iteration,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            **iteration_data
        })
        self.current_iteration += 1

    def should_continue(self) -> bool:
        """Check if workflow should continue iterating."""
        return (
            not self.is_complete and
            self.current_iteration < self.max_iterations
        )


class ABPattern(ABC):
    """
    Abstract base class for A/B collaboration patterns.

    All A/B patterns must implement:
    - Pattern name and description
    - Agent roles (Agent A, Agent B, etc.)
    - Execution logic
    - Observability hooks
    """

    def __init__(
        self,
        broker: ProtocolBrokerAgent,
        observer: Optional[Callable] = None
    ):
        """
        Initialize pattern with broker and optional observer.

        Args:
            broker: Protocol broker for agent communication
            observer: Optional callback for observability events
        """
        self.broker = broker
        self.observer = observer
        self.context: Optional[ABWorkflowContext] = None

    @property
    @abstractmethod
    def pattern_name(self) -> str:
        """Return the name of this pattern."""
        pass

    @property
    @abstractmethod
    def pattern_description(self) -> str:
        """Return a description of what this pattern does."""
        pass

    @property
    @abstractmethod
    def agent_roles(self) -> List[str]:
        """Return list of agent roles required for this pattern."""
        pass

    @abstractmethod
    def execute(
        self,
        input_data: Dict[str, Any],
        max_iterations: int = 3
    ) -> ABWorkflowContext:
        """
        Execute the A/B collaboration pattern.

        Args:
            input_data: Input data for the workflow
            max_iterations: Maximum iterations to run

        Returns:
            Workflow context with results and history
        """
        pass

    def _observe(self, event: str, data: Dict[str, Any]) -> None:
        """
        Send observability event to observer if configured.

        Args:
            event: Event name
            data: Event data
        """
        if self.observer:
            self.observer(event, {
                "pattern": self.pattern_name,
                "workflow_id": self.context.workflow_id if self.context else None,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                **data
            })

    def get_pattern_info(self) -> Dict[str, Any]:
        """Get metadata about this pattern."""
        return {
            "name": self.pattern_name,
            "description": self.pattern_description,
            "roles": self.agent_roles,
            "class": self.__class__.__name__
        }


if __name__ == "__main__":
    # Test base pattern structure
    print("A/B Pattern Base Classes")
    print("=" * 60)
    print("\nABWorkflowContext:")
    ctx = ABWorkflowContext(input_data={"test": "data"})
    print(f"  Workflow ID: {ctx.workflow_id}")
    print(f"  Max iterations: {ctx.max_iterations}")
    print(f"  Should continue: {ctx.should_continue()}")

    ctx.record_iteration({"result": "success"})
    print(f"  After iteration: {ctx.current_iteration}")
    print(f"  History length: {len(ctx.iteration_history)}")
