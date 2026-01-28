"""
Unit of Work Models and Executor

Defines unit of work structure for stage execution orchestration.
Based on Journey State Machine Design (DES-002).
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
import threading
import logging


logger = logging.getLogger(__name__)


class WorkStatus(Enum):
    """Unit of work execution status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    COMPENSATING = "compensating"  # Saga compensation in progress
    COMPENSATED = "compensated"    # Saga compensation completed


class TaskStatus(Enum):
    """Individual task execution status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"  # Skipped due to dependencies


@dataclass
class Task:
    """
    Individual task within unit of work.

    Represents a single agent invocation with input/output schemas
    and dependency tracking.
    """
    task_id: str
    name: str
    description: str
    agent_id: str  # Agent responsible for execution
    intent: str  # Intent to send to agent via protocol
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    depends_on: List[str]  # Task IDs that must complete first
    status: TaskStatus = TaskStatus.PENDING
    retry_count: int = 0
    max_retries: int = 3
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    result: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Serialize task to dictionary"""
        return {
            "task_id": self.task_id,
            "name": self.name,
            "description": self.description,
            "agent_id": self.agent_id,
            "intent": self.intent,
            "input_schema": self.input_schema,
            "output_schema": self.output_schema,
            "depends_on": self.depends_on,
            "status": self.status.value,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "error": self.error,
            "result": self.result
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Task":
        """Deserialize task from dictionary"""
        return cls(
            task_id=data["task_id"],
            name=data["name"],
            description=data["description"],
            agent_id=data["agent_id"],
            intent=data["intent"],
            input_schema=data["input_schema"],
            output_schema=data["output_schema"],
            depends_on=data["depends_on"],
            status=TaskStatus(data["status"]),
            retry_count=data.get("retry_count", 0),
            max_retries=data.get("max_retries", 3),
            started_at=datetime.fromisoformat(data["started_at"]) if data.get("started_at") else None,
            completed_at=datetime.fromisoformat(data["completed_at"]) if data.get("completed_at") else None,
            error=data.get("error"),
            result=data.get("result")
        )


@dataclass
class UnitOfWork:
    """
    Unit of work - atomic set of tasks for stage execution.

    Represents a complete workflow with multiple tasks that must
    execute in dependency order. Supports saga compensation on failure.
    """
    work_id: str
    stage: str  # Journey stage this UoW belongs to
    client_id: str
    tasks: List[Task]
    status: WorkStatus = WorkStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Saga state tracking
    compensation_tasks: List[Task] = field(default_factory=list)
    failed_task_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Serialize unit of work to dictionary"""
        return {
            "work_id": self.work_id,
            "stage": self.stage,
            "client_id": self.client_id,
            "tasks": [t.to_dict() for t in self.tasks],
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "metadata": self.metadata,
            "compensation_tasks": [t.to_dict() for t in self.compensation_tasks],
            "failed_task_id": self.failed_task_id
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UnitOfWork":
        """Deserialize unit of work from dictionary"""
        return cls(
            work_id=data["work_id"],
            stage=data["stage"],
            client_id=data["client_id"],
            tasks=[Task.from_dict(t) for t in data["tasks"]],
            status=WorkStatus(data["status"]),
            created_at=datetime.fromisoformat(data["created_at"]),
            started_at=datetime.fromisoformat(data["started_at"]) if data.get("started_at") else None,
            completed_at=datetime.fromisoformat(data["completed_at"]) if data.get("completed_at") else None,
            metadata=data.get("metadata", {}),
            compensation_tasks=[Task.from_dict(t) for t in data.get("compensation_tasks", [])],
            failed_task_id=data.get("failed_task_id")
        )

    def get_task(self, task_id: str) -> Optional[Task]:
        """Get task by ID"""
        for task in self.tasks:
            if task.task_id == task_id:
                return task
        return None

    def get_pending_tasks(self) -> List[Task]:
        """Get all tasks that are pending"""
        return [t for t in self.tasks if t.status == TaskStatus.PENDING]

    def get_completed_tasks(self) -> List[Task]:
        """Get all completed tasks"""
        return [t for t in self.tasks if t.status == TaskStatus.COMPLETED]

    def get_failed_tasks(self) -> List[Task]:
        """Get all failed tasks"""
        return [t for t in self.tasks if t.status == TaskStatus.FAILED]

    def get_runnable_tasks(self) -> List[Task]:
        """
        Get tasks that can run now (all dependencies completed).

        Returns:
            List of tasks with PENDING status and all dependencies completed
        """
        runnable = []
        completed_ids = {t.task_id for t in self.get_completed_tasks()}

        for task in self.get_pending_tasks():
            # Check if all dependencies are completed
            if all(dep_id in completed_ids for dep_id in task.depends_on):
                runnable.append(task)

        return runnable

    def has_circular_dependencies(self) -> bool:
        """
        Check for circular dependencies in task graph.

        Returns:
            True if circular dependencies detected, False otherwise
        """
        # Build adjacency list
        graph = {t.task_id: t.depends_on for t in self.tasks}

        # Detect cycles using DFS
        visited = set()
        rec_stack = set()

        def has_cycle(node_id: str) -> bool:
            visited.add(node_id)
            rec_stack.add(node_id)

            for dep_id in graph.get(node_id, []):
                if dep_id not in visited:
                    if has_cycle(dep_id):
                        return True
                elif dep_id in rec_stack:
                    return True

            rec_stack.remove(node_id)
            return False

        for task_id in graph:
            if task_id not in visited:
                if has_cycle(task_id):
                    return True

        return False

    def get_execution_duration_seconds(self) -> Optional[float]:
        """Get total execution duration in seconds"""
        if not self.started_at:
            return None

        end_time = self.completed_at or datetime.utcnow()
        return (end_time - self.started_at).total_seconds()


@dataclass
class ExecutionResult:
    """Result of unit of work execution"""
    success: bool
    work_id: str
    status: WorkStatus
    completed_tasks: List[str]
    failed_tasks: List[str]
    task_results: Dict[str, Any]
    error: Optional[str] = None
    duration_seconds: Optional[float] = None
    compensation_executed: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "work_id": self.work_id,
            "status": self.status.value,
            "completed_tasks": self.completed_tasks,
            "failed_tasks": self.failed_tasks,
            "task_results": self.task_results,
            "error": self.error,
            "duration_seconds": self.duration_seconds,
            "compensation_executed": self.compensation_executed
        }
