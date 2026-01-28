"""
Unit tests for Unit of Work models

Tests task and UoW data structures, serialization, and dependency analysis.
Validates AC1 of P0-A2A-F1-002.
"""

import pytest
from datetime import datetime

from a_domain.journey.unit_of_work import (
    WorkStatus,
    TaskStatus,
    Task,
    UnitOfWork,
    ExecutionResult
)


class TestWorkStatus:
    """Test work status enumeration"""

    def test_all_statuses_defined(self):
        """Test all 6 work statuses are defined"""
        statuses = list(WorkStatus)
        assert len(statuses) == 6
        assert WorkStatus.PENDING in statuses
        assert WorkStatus.IN_PROGRESS in statuses
        assert WorkStatus.COMPLETED in statuses
        assert WorkStatus.FAILED in statuses
        assert WorkStatus.COMPENSATING in statuses
        assert WorkStatus.COMPENSATED in statuses


class TestTaskStatus:
    """Test task status enumeration"""

    def test_all_statuses_defined(self):
        """Test all 5 task statuses are defined"""
        statuses = list(TaskStatus)
        assert len(statuses) == 5
        assert TaskStatus.PENDING in statuses
        assert TaskStatus.IN_PROGRESS in statuses
        assert TaskStatus.COMPLETED in statuses
        assert TaskStatus.FAILED in statuses
        assert TaskStatus.SKIPPED in statuses


class TestTask:
    """Test task data structure"""

    def test_create_task(self):
        """Test creating task with all fields"""
        task = Task(
            task_id="task-1",
            name="Provision Infrastructure",
            description="Provision sandbox environment",
            agent_id="infra-agent",
            intent="provision_sandbox",
            input_schema={"client_id": "string"},
            output_schema={"environment_id": "string"},
            depends_on=[],
            max_retries=3
        )

        assert task.task_id == "task-1"
        assert task.status == TaskStatus.PENDING
        assert task.retry_count == 0
        assert task.max_retries == 3
        assert task.result is None

    def test_task_serialization(self):
        """Test task to_dict serialization"""
        task = Task(
            task_id="task-1",
            name="Test Task",
            description="Test description",
            agent_id="test-agent",
            intent="test_intent",
            input_schema={},
            output_schema={},
            depends_on=["task-0"]
        )

        data = task.to_dict()
        assert data["task_id"] == "task-1"
        assert data["status"] == "pending"
        assert data["depends_on"] == ["task-0"]

    def test_task_deserialization(self):
        """Test task from_dict deserialization"""
        data = {
            "task_id": "task-1",
            "name": "Test Task",
            "description": "Test",
            "agent_id": "test-agent",
            "intent": "test_intent",
            "input_schema": {},
            "output_schema": {},
            "depends_on": [],
            "status": "completed",
            "retry_count": 0,
            "max_retries": 3,
            "started_at": "2026-01-27T00:00:00",
            "completed_at": "2026-01-27T00:01:00",
            "error": None,
            "result": {"status": "success"}
        }

        task = Task.from_dict(data)
        assert task.task_id == "task-1"
        assert task.status == TaskStatus.COMPLETED
        assert task.result == {"status": "success"}


class TestUnitOfWork:
    """Test unit of work data structure"""

    def setup_method(self):
        """Create sample tasks for testing"""
        self.task1 = Task(
            task_id="task-1",
            name="Task 1",
            description="First task",
            agent_id="agent-1",
            intent="intent-1",
            input_schema={},
            output_schema={},
            depends_on=[]
        )

        self.task2 = Task(
            task_id="task-2",
            name="Task 2",
            description="Second task",
            agent_id="agent-2",
            intent="intent-2",
            input_schema={},
            output_schema={},
            depends_on=["task-1"]
        )

        self.task3 = Task(
            task_id="task-3",
            name="Task 3",
            description="Third task",
            agent_id="agent-3",
            intent="intent-3",
            input_schema={},
            output_schema={},
            depends_on=["task-1", "task-2"]
        )

    def test_create_uow(self):
        """Test creating unit of work"""
        uow = UnitOfWork(
            work_id="uow-1",
            stage="sandbox",
            client_id="client-123",
            tasks=[self.task1, self.task2]
        )

        assert uow.work_id == "uow-1"
        assert uow.stage == "sandbox"
        assert uow.status == WorkStatus.PENDING
        assert len(uow.tasks) == 2

    def test_get_task(self):
        """Test retrieving task by ID"""
        uow = UnitOfWork(
            work_id="uow-1",
            stage="sandbox",
            client_id="client-123",
            tasks=[self.task1, self.task2]
        )

        task = uow.get_task("task-1")
        assert task is not None
        assert task.task_id == "task-1"

        assert uow.get_task("task-999") is None

    def test_get_pending_tasks(self):
        """Test filtering pending tasks"""
        self.task1.status = TaskStatus.COMPLETED
        uow = UnitOfWork(
            work_id="uow-1",
            stage="sandbox",
            client_id="client-123",
            tasks=[self.task1, self.task2, self.task3]
        )

        pending = uow.get_pending_tasks()
        assert len(pending) == 2
        assert all(t.status == TaskStatus.PENDING for t in pending)

    def test_get_completed_tasks(self):
        """Test filtering completed tasks"""
        self.task1.status = TaskStatus.COMPLETED
        self.task2.status = TaskStatus.COMPLETED
        uow = UnitOfWork(
            work_id="uow-1",
            stage="sandbox",
            client_id="client-123",
            tasks=[self.task1, self.task2, self.task3]
        )

        completed = uow.get_completed_tasks()
        assert len(completed) == 2
        assert all(t.status == TaskStatus.COMPLETED for t in completed)

    def test_get_failed_tasks(self):
        """Test filtering failed tasks"""
        self.task2.status = TaskStatus.FAILED
        uow = UnitOfWork(
            work_id="uow-1",
            stage="sandbox",
            client_id="client-123",
            tasks=[self.task1, self.task2, self.task3]
        )

        failed = uow.get_failed_tasks()
        assert len(failed) == 1
        assert failed[0].task_id == "task-2"

    def test_get_runnable_tasks(self):
        """Test identifying runnable tasks based on dependencies (AC1)"""
        uow = UnitOfWork(
            work_id="uow-1",
            stage="sandbox",
            client_id="client-123",
            tasks=[self.task1, self.task2, self.task3]
        )

        # Initially only task1 is runnable (no dependencies)
        runnable = uow.get_runnable_tasks()
        assert len(runnable) == 1
        assert runnable[0].task_id == "task-1"

        # After task1 completes, task2 is runnable
        self.task1.status = TaskStatus.COMPLETED
        runnable = uow.get_runnable_tasks()
        assert len(runnable) == 1
        assert runnable[0].task_id == "task-2"

        # After task2 completes, task3 is runnable
        self.task2.status = TaskStatus.COMPLETED
        runnable = uow.get_runnable_tasks()
        assert len(runnable) == 1
        assert runnable[0].task_id == "task-3"

    def test_has_circular_dependencies_false(self):
        """Test circular dependency detection - valid DAG"""
        uow = UnitOfWork(
            work_id="uow-1",
            stage="sandbox",
            client_id="client-123",
            tasks=[self.task1, self.task2, self.task3]
        )

        assert not uow.has_circular_dependencies()

    def test_has_circular_dependencies_true(self):
        """Test circular dependency detection - cycle detected"""
        # Create circular dependency: task1 → task2 → task3 → task1
        task1 = Task(
            task_id="task-1",
            name="Task 1",
            description="",
            agent_id="agent-1",
            intent="intent-1",
            input_schema={},
            output_schema={},
            depends_on=["task-3"]  # Circular!
        )

        task2 = Task(
            task_id="task-2",
            name="Task 2",
            description="",
            agent_id="agent-2",
            intent="intent-2",
            input_schema={},
            output_schema={},
            depends_on=["task-1"]
        )

        task3 = Task(
            task_id="task-3",
            name="Task 3",
            description="",
            agent_id="agent-3",
            intent="intent-3",
            input_schema={},
            output_schema={},
            depends_on=["task-2"]
        )

        uow = UnitOfWork(
            work_id="uow-1",
            stage="sandbox",
            client_id="client-123",
            tasks=[task1, task2, task3]
        )

        assert uow.has_circular_dependencies()

    def test_get_execution_duration(self):
        """Test calculating execution duration"""
        uow = UnitOfWork(
            work_id="uow-1",
            stage="sandbox",
            client_id="client-123",
            tasks=[]
        )

        # No duration before started
        assert uow.get_execution_duration_seconds() is None

        # Duration after started
        uow.started_at = datetime.utcnow()
        uow.completed_at = datetime.utcnow()
        duration = uow.get_execution_duration_seconds()
        assert duration is not None
        assert duration >= 0

    def test_uow_serialization(self):
        """Test UoW to_dict serialization"""
        uow = UnitOfWork(
            work_id="uow-1",
            stage="sandbox",
            client_id="client-123",
            tasks=[self.task1],
            metadata={"key": "value"}
        )

        data = uow.to_dict()
        assert data["work_id"] == "uow-1"
        assert data["stage"] == "sandbox"
        assert data["status"] == "pending"
        assert len(data["tasks"]) == 1
        assert data["metadata"]["key"] == "value"

    def test_uow_deserialization(self):
        """Test UoW from_dict deserialization"""
        data = {
            "work_id": "uow-1",
            "stage": "sandbox",
            "client_id": "client-123",
            "tasks": [self.task1.to_dict()],
            "status": "completed",
            "created_at": "2026-01-27T00:00:00",
            "started_at": "2026-01-27T00:00:00",
            "completed_at": "2026-01-27T00:01:00",
            "metadata": {},
            "compensation_tasks": [],
            "failed_task_id": None
        }

        uow = UnitOfWork.from_dict(data)
        assert uow.work_id == "uow-1"
        assert uow.status == WorkStatus.COMPLETED
        assert len(uow.tasks) == 1


class TestExecutionResult:
    """Test execution result data structure"""

    def test_create_result(self):
        """Test creating execution result"""
        result = ExecutionResult(
            success=True,
            work_id="uow-1",
            status=WorkStatus.COMPLETED,
            completed_tasks=["task-1", "task-2"],
            failed_tasks=[],
            task_results={"task-1": {"status": "success"}},
            duration_seconds=5.5
        )

        assert result.success is True
        assert result.work_id == "uow-1"
        assert len(result.completed_tasks) == 2
        assert result.duration_seconds == 5.5

    def test_result_serialization(self):
        """Test execution result to_dict"""
        result = ExecutionResult(
            success=True,
            work_id="uow-1",
            status=WorkStatus.COMPLETED,
            completed_tasks=["task-1"],
            failed_tasks=[],
            task_results={},
            compensation_executed=False
        )

        data = result.to_dict()
        assert data["success"] is True
        assert data["work_id"] == "uow-1"
        assert data["status"] == "completed"
        assert data["compensation_executed"] is False
