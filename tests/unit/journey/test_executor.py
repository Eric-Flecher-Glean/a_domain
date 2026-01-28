"""
Unit tests for Unit of Work Executor

Tests workflow execution, compensation, and metrics tracking.
Validates AC2, AC3, and AC4 of P0-A2A-F1-002.
"""

import pytest
from threading import Thread
from time import sleep

from a_domain.journey.unit_of_work import (
    WorkStatus,
    TaskStatus,
    Task,
    UnitOfWork
)
from a_domain.journey.executor import (
    UnitOfWorkExecutor,
    DependencyCycleError
)


class TestUnitOfWorkExecutor:
    """Test unit of work executor"""

    def setup_method(self):
        """Create executor and sample tasks"""
        self.executor = UnitOfWorkExecutor()

        self.task1 = Task(
            task_id="task-1",
            name="Provision Infrastructure",
            description="Provision sandbox",
            agent_id="infra-agent",
            intent="provision_sandbox",
            input_schema={},
            output_schema={"environment_id": "string"},
            depends_on=[]
        )

        self.task2 = Task(
            task_id="task-2",
            name="Install Connectors",
            description="Install Glean connectors",
            agent_id="connector-agent",
            intent="install_connectors",
            input_schema={"environment_id": "string"},
            output_schema={"connectors": "array"},
            depends_on=["task-1"]
        )

        self.task3 = Task(
            task_id="task-3",
            name="Provision Data",
            description="Provision test dataset",
            agent_id="data-agent",
            intent="provision_dataset",
            input_schema={"environment_id": "string"},
            output_schema={"dataset_id": "string"},
            depends_on=["task-1", "task-2"]
        )

    def test_execute_simple_workflow(self):
        """Test executing single-task workflow (AC2)"""
        uow = UnitOfWork(
            work_id="uow-1",
            stage="sandbox",
            client_id="client-123",
            tasks=[self.task1]
        )

        result = self.executor.execute(uow)

        assert result.success is True
        assert result.status == WorkStatus.COMPLETED
        assert len(result.completed_tasks) == 1
        assert len(result.failed_tasks) == 0
        assert uow.status == WorkStatus.COMPLETED

    def test_execute_multi_task_workflow(self):
        """Test executing multi-task workflow with dependencies (AC2)"""
        uow = UnitOfWork(
            work_id="uow-1",
            stage="sandbox",
            client_id="client-123",
            tasks=[self.task1, self.task2, self.task3]
        )

        result = self.executor.execute(uow)

        assert result.success is True
        assert result.status == WorkStatus.COMPLETED
        assert len(result.completed_tasks) == 3
        assert "task-1" in result.completed_tasks
        assert "task-2" in result.completed_tasks
        assert "task-3" in result.completed_tasks

        # Verify all tasks completed
        assert self.task1.status == TaskStatus.COMPLETED
        assert self.task2.status == TaskStatus.COMPLETED
        assert self.task3.status == TaskStatus.COMPLETED

    def test_execute_respects_dependencies(self):
        """Test tasks execute in dependency order (AC2)"""
        execution_order = []

        def track_invoke(task, task_results):
            execution_order.append(task.task_id)
            return {"status": "success", "task_id": task.task_id}

        executor = UnitOfWorkExecutor(agent_invoker=track_invoke)

        uow = UnitOfWork(
            work_id="uow-1",
            stage="sandbox",
            client_id="client-123",
            tasks=[self.task1, self.task2, self.task3]
        )

        executor.execute(uow)

        # task-1 must execute before task-2 and task-3
        assert execution_order.index("task-1") < execution_order.index("task-2")
        assert execution_order.index("task-1") < execution_order.index("task-3")
        # task-2 must execute before task-3
        assert execution_order.index("task-2") < execution_order.index("task-3")

    def test_circular_dependency_raises_error(self):
        """Test circular dependencies are detected"""
        task1 = Task(
            task_id="task-1",
            name="Task 1",
            description="",
            agent_id="agent-1",
            intent="intent-1",
            input_schema={},
            output_schema={},
            depends_on=["task-2"]
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

        uow = UnitOfWork(
            work_id="uow-1",
            stage="sandbox",
            client_id="client-123",
            tasks=[task1, task2]
        )

        with pytest.raises(DependencyCycleError) as exc_info:
            self.executor.execute(uow)

        assert "Circular dependencies" in str(exc_info.value)

    def test_task_failure_stops_workflow(self):
        """Test workflow stops on task failure"""
        def failing_invoke(task, task_results):
            if task.task_id == "task-2":
                raise Exception("Task 2 failed")
            return {"status": "success"}

        executor = UnitOfWorkExecutor(agent_invoker=failing_invoke)

        uow = UnitOfWork(
            work_id="uow-1",
            stage="sandbox",
            client_id="client-123",
            tasks=[self.task1, self.task2, self.task3]
        )

        result = executor.execute(uow)

        assert result.success is False
        assert result.status == WorkStatus.FAILED
        assert "task-2" in result.failed_tasks
        assert "task-3" not in result.completed_tasks  # task-3 blocked

    def test_task_retry_on_failure(self):
        """Test tasks retry up to max_retries"""
        invoke_count = {}

        def counting_invoke(task, task_results):
            count = invoke_count.get(task.task_id, 0)
            invoke_count[task.task_id] = count + 1

            if task.task_id == "task-1" and count < 2:
                raise Exception("Temporary failure")

            return {"status": "success"}

        executor = UnitOfWorkExecutor(agent_invoker=counting_invoke)

        self.task1.max_retries = 3

        uow = UnitOfWork(
            work_id="uow-1",
            stage="sandbox",
            client_id="client-123",
            tasks=[self.task1]
        )

        result = executor.execute(uow)

        # Should succeed after retries
        assert result.success is True
        assert invoke_count["task-1"] == 3  # Initial + 2 retries
        assert self.task1.retry_count == 2

    def test_task_fails_after_max_retries(self):
        """Test task fails after max_retries exceeded"""
        def always_fail(task, task_results):
            raise Exception("Persistent failure")

        executor = UnitOfWorkExecutor(agent_invoker=always_fail)

        self.task1.max_retries = 2

        uow = UnitOfWork(
            work_id="uow-1",
            stage="sandbox",
            client_id="client-123",
            tasks=[self.task1]
        )

        result = executor.execute(uow)

        assert result.success is False
        assert self.task1.status == TaskStatus.FAILED
        assert self.task1.retry_count == 2
        assert self.task1.error is not None

    def test_saga_compensation_on_failure(self):
        """Test saga compensation executes on failure (AC3)"""
        def failing_at_task2(task, task_results):
            if task.task_id == "task-2":
                raise Exception("Task 2 failed")
            return {"status": "success"}

        executor = UnitOfWorkExecutor(agent_invoker=failing_at_task2)

        # Add compensation task
        comp_task = Task(
            task_id="comp-1",
            name="Rollback Infrastructure",
            description="Rollback provisioning",
            agent_id="infra-agent",
            intent="rollback_provision",
            input_schema={},
            output_schema={},
            depends_on=[]
        )

        uow = UnitOfWork(
            work_id="uow-1",
            stage="sandbox",
            client_id="client-123",
            tasks=[self.task1, self.task2],
            compensation_tasks=[comp_task]
        )

        result = executor.execute(uow)

        # Should execute compensation
        assert result.success is False
        assert result.compensation_executed is True
        assert uow.status == WorkStatus.COMPENSATED
        assert comp_task.status == TaskStatus.COMPLETED
        assert uow.failed_task_id == "task-2"

    def test_compensation_not_executed_on_success(self):
        """Test compensation skipped on successful workflow"""
        comp_task = Task(
            task_id="comp-1",
            name="Rollback",
            description="",
            agent_id="agent-1",
            intent="rollback",
            input_schema={},
            output_schema={},
            depends_on=[]
        )

        uow = UnitOfWork(
            work_id="uow-1",
            stage="sandbox",
            client_id="client-123",
            tasks=[self.task1],
            compensation_tasks=[comp_task]
        )

        result = self.executor.execute(uow)

        assert result.success is True
        assert result.compensation_executed is False
        assert comp_task.status == TaskStatus.PENDING  # Not executed

    def test_metrics_tracking(self):
        """Test execution metrics are tracked (AC4)"""
        uow = UnitOfWork(
            work_id="uow-1",
            stage="sandbox",
            client_id="client-123",
            tasks=[self.task1, self.task2]
        )

        result = self.executor.execute(uow)

        # Get metrics
        metrics = self.executor.get_metrics("uow-1")

        assert metrics["work_id"] == "uow-1"
        assert metrics["stage"] == "sandbox"
        assert metrics["client_id"] == "client-123"
        assert metrics["status"] == "completed"
        assert metrics["task_count"] == 2
        assert metrics["completed_count"] == 2
        assert metrics["failed_count"] == 0
        assert metrics["duration_seconds"] is not None
        assert metrics["duration_seconds"] >= 0

    def test_metrics_all_workflows(self):
        """Test retrieving all workflow metrics (AC4)"""
        uow1 = UnitOfWork(
            work_id="uow-1",
            stage="sandbox",
            client_id="client-1",
            tasks=[self.task1]
        )

        uow2 = UnitOfWork(
            work_id="uow-2",
            stage="pilot",
            client_id="client-2",
            tasks=[self.task1]
        )

        self.executor.execute(uow1)
        self.executor.execute(uow2)

        all_metrics = self.executor.get_metrics()

        assert len(all_metrics) == 2
        assert "uow-1" in all_metrics
        assert "uow-2" in all_metrics

    def test_thread_safety_concurrent_execution(self):
        """Test thread-safe concurrent UoW execution"""
        results = []
        errors = []

        def execute_uow(work_id):
            try:
                uow = UnitOfWork(
                    work_id=work_id,
                    stage="sandbox",
                    client_id=f"client-{work_id}",
                    tasks=[
                        Task(
                            task_id=f"{work_id}-task-1",
                            name="Task",
                            description="",
                            agent_id="agent",
                            intent="test",
                            input_schema={},
                            output_schema={},
                            depends_on=[]
                        )
                    ]
                )
                result = self.executor.execute(uow)
                results.append(result)
            except Exception as e:
                errors.append(e)

        # Execute 10 UoWs concurrently
        threads = []
        for i in range(10):
            t = Thread(target=execute_uow, args=(f"uow-{i}",))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        # All should succeed
        assert len(errors) == 0
        assert len(results) == 10
        assert all(r.success for r in results)

    def test_execution_duration_tracking(self):
        """Test execution duration is tracked"""
        uow = UnitOfWork(
            work_id="uow-1",
            stage="sandbox",
            client_id="client-123",
            tasks=[self.task1]
        )

        result = self.executor.execute(uow)

        assert result.duration_seconds is not None
        assert result.duration_seconds >= 0
        assert uow.started_at is not None
        assert uow.completed_at is not None

    def test_complex_dependency_graph(self):
        """Test executing complex multi-level dependency graph"""
        # Create diamond dependency:
        #     task1
        #    /     \
        # task2   task3
        #    \     /
        #     task4

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
            depends_on=["task-1"]
        )

        task4 = Task(
            task_id="task-4",
            name="Task 4",
            description="",
            agent_id="agent-4",
            intent="intent-4",
            input_schema={},
            output_schema={},
            depends_on=["task-2", "task-3"]
        )

        uow = UnitOfWork(
            work_id="uow-1",
            stage="sandbox",
            client_id="client-123",
            tasks=[task1, task2, task3, task4]
        )

        result = self.executor.execute(uow)

        assert result.success is True
        assert len(result.completed_tasks) == 4
        # All tasks should complete
        assert task1.status == TaskStatus.COMPLETED
        assert task2.status == TaskStatus.COMPLETED
        assert task3.status == TaskStatus.COMPLETED
        assert task4.status == TaskStatus.COMPLETED

    def test_task_results_passed_to_dependents(self):
        """Test task results are passed to dependent tasks"""
        captured_inputs = {}

        def capture_invoke(task, task_results):
            captured_inputs[task.task_id] = task_results.copy()
            return {"status": "success", "output": f"{task.task_id}-result"}

        executor = UnitOfWorkExecutor(agent_invoker=capture_invoke)

        uow = UnitOfWork(
            work_id="uow-1",
            stage="sandbox",
            client_id="client-123",
            tasks=[self.task1, self.task2]
        )

        executor.execute(uow)

        # task-2 should receive task-1's results
        assert "task-1" in captured_inputs["task-2"]
        assert captured_inputs["task-2"]["task-1"]["output"] == "task-1-result"
