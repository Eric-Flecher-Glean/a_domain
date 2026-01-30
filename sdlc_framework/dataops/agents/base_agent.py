"""Base agent class for DataOps agents."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


@dataclass
class AgentExecutionContext:
    """Context for agent execution."""
    execution_id: UUID
    started_at: datetime
    agent_name: str
    triggered_by: str = "manual"
    metadata: dict = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class BaseAgent(ABC):
    """Base class for all DataOps agents.

    Provides common infrastructure for logging, error handling,
    and execution tracking.
    """

    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.current_execution: Optional[AgentExecutionContext] = None

    def start_execution(self, triggered_by: str = "manual") -> AgentExecutionContext:
        """Begin agent execution with tracking context."""
        self.current_execution = AgentExecutionContext(
            execution_id=uuid4(),
            started_at=datetime.utcnow(),
            agent_name=self.agent_name,
            triggered_by=triggered_by
        )
        return self.current_execution

    def end_execution(self) -> None:
        """End current execution."""
        self.current_execution = None

    @abstractmethod
    async def execute(self, **kwargs):
        """Execute agent logic. Must be implemented by subclasses."""
        pass

    def log(self, message: str, level: str = "INFO") -> None:
        """Log agent activity."""
        timestamp = datetime.utcnow().isoformat()
        execution_id = self.current_execution.execution_id if self.current_execution else "N/A"
        print(f"[{timestamp}] [{level}] [{self.agent_name}] [{execution_id}] {message}")
