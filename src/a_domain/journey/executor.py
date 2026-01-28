"""
Unit of Work Executor

Executes multi-agent workflows with dependency resolution and compensation.
Based on Journey State Machine Design (DES-002).
"""

from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
import threading
import logging

from .unit_of_work import (
    UnitOfWork,
    Task,
    WorkStatus,
    TaskStatus,
    ExecutionResult
)


logger = logging.getLogger(__name__)


class DependencyCycleError(Exception):
    """Raised when circular dependencies detected in task graph"""
    pass


class AgentNotFoundError(Exception):
    """Raised when no agent found for task intent"""
    pass


class UnitOfWorkExecutor:
    """
    Executes unit of work by orchestrating agent tasks.

    Responsibilities:
    - Resolve task dependencies (topological sort)
    - Execute tasks via agent protocol
    - Handle task failures and retries
    - Manage saga compensation on failure
    - Track execution metrics

    Thread-safe for concurrent UoW execution.
    """

    def __init__(
        self,
        agent_invoker: Optional[Callable[[Task, Dict[str, Any]], Dict[str, Any]]] = None
    ):
        """
        Initialize executor.

        Args:
            agent_invoker: Function to invoke agents (task, task_results) -> result
                          If None, uses mock implementation for testing
        """
        self._agent_invoker = agent_invoker or self._mock_agent_invoke
        self._lock = threading.Lock()
        self._execution_metrics: Dict[str, Dict[str, Any]] = {}

    def execute(self, uow: UnitOfWork) -> ExecutionResult:
        """
        Execute unit of work.

        Args:
            uow: Unit of work to execute

        Returns:
            Execution result with success status and task results

        Raises:
            DependencyCycleError: If circular dependencies detected
        """
        with self._lock:
            # Validate dependencies
            if uow.has_circular_dependencies():
                raise DependencyCycleError(
                    f"Circular dependencies detected in UoW {uow.work_id}"
                )

            # Update status
            uow.status = WorkStatus.IN_PROGRESS
            uow.started_at = datetime.utcnow()

            logger.info(
                f"Starting UoW execution: {uow.work_id}",
                extra={"work_id": uow.work_id, "task_count": len(uow.tasks)}
            )

        # Execute tasks (release lock for long-running operations)
        task_results = {}
        completed_tasks = []
        failed_tasks = []

        try:
            while True:
                with self._lock:
                    runnable = uow.get_runnable_tasks()

                    if not runnable:
                        # Check if all tasks completed
                        pending = uow.get_pending_tasks()
                        if not pending:
                            break  # All done

                        # Some tasks blocked by failed dependencies
                        logger.warning(
                            f"No runnable tasks but {len(pending)} still pending",
                            extra={"work_id": uow.work_id}
                        )
                        break

                # Execute runnable tasks
                for task in runnable:
                    success = self._execute_task(task, task_results, uow)

                    with self._lock:
                        if success:
                            # Only add to completed once
                            if task.task_id not in completed_tasks:
                                completed_tasks.append(task.task_id)
                        elif task.status == TaskStatus.FAILED:
                            # Only add to failed if truly failed (not retrying)
                            if task.task_id not in failed_tasks:
                                failed_tasks.append(task.task_id)
                            uow.failed_task_id = task.task_id

                            # Initiate compensation if saga enabled
                            if uow.compensation_tasks:
                                logger.info(
                                    f"Task failed, initiating compensation",
                                    extra={"work_id": uow.work_id, "failed_task": task.task_id}
                                )
                                self._execute_compensation(uow, task_results)
                                uow.status = WorkStatus.COMPENSATED
                                break

            # Determine final status
            with self._lock:
                if failed_tasks:
                    uow.status = WorkStatus.FAILED if not uow.compensation_tasks else WorkStatus.COMPENSATED
                else:
                    uow.status = WorkStatus.COMPLETED

                uow.completed_at = datetime.utcnow()
                duration = uow.get_execution_duration_seconds()

                # Record metrics
                self._record_metrics(uow, completed_tasks, failed_tasks, duration)

                logger.info(
                    f"UoW execution completed: {uow.work_id}",
                    extra={
                        "work_id": uow.work_id,
                        "status": uow.status.value,
                        "completed": len(completed_tasks),
                        "failed": len(failed_tasks),
                        "duration_seconds": duration
                    }
                )

                return ExecutionResult(
                    success=(uow.status == WorkStatus.COMPLETED),
                    work_id=uow.work_id,
                    status=uow.status,
                    completed_tasks=completed_tasks,
                    failed_tasks=failed_tasks,
                    task_results=task_results,
                    error=uow.failed_task_id,
                    duration_seconds=duration,
                    compensation_executed=(uow.status == WorkStatus.COMPENSATED)
                )

        except Exception as e:
            with self._lock:
                uow.status = WorkStatus.FAILED
                uow.completed_at = datetime.utcnow()

                logger.error(
                    f"UoW execution failed with exception: {uow.work_id}",
                    extra={"work_id": uow.work_id, "error": str(e)},
                    exc_info=True
                )

                return ExecutionResult(
                    success=False,
                    work_id=uow.work_id,
                    status=WorkStatus.FAILED,
                    completed_tasks=completed_tasks,
                    failed_tasks=failed_tasks,
                    task_results=task_results,
                    error=str(e)
                )

    def _execute_task(
        self,
        task: Task,
        task_results: Dict[str, Any],
        uow: UnitOfWork
    ) -> bool:
        """
        Execute individual task.

        Args:
            task: Task to execute
            task_results: Results from previous tasks
            uow: Parent unit of work

        Returns:
            True if success, False if failed
        """
        task.status = TaskStatus.IN_PROGRESS
        task.started_at = datetime.utcnow()

        logger.info(
            f"Executing task: {task.task_id}",
            extra={
                "work_id": uow.work_id,
                "task_id": task.task_id,
                "agent_id": task.agent_id,
                "intent": task.intent
            }
        )

        try:
            # Invoke agent via protocol
            result = self._agent_invoker(task, task_results)

            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.utcnow()
            task.result = result
            task_results[task.task_id] = result

            logger.info(
                f"Task completed: {task.task_id}",
                extra={"work_id": uow.work_id, "task_id": task.task_id}
            )

            return True

        except Exception as e:
            task.error = str(e)
            task.retry_count += 1

            # Retry logic
            if task.retry_count < task.max_retries:
                logger.warning(
                    f"Task failed, retrying ({task.retry_count}/{task.max_retries})",
                    extra={
                        "work_id": uow.work_id,
                        "task_id": task.task_id,
                        "error": str(e)
                    }
                )

                # Reset status for retry
                task.status = TaskStatus.PENDING
                task.started_at = None
                return False

            else:
                logger.error(
                    f"Task failed after {task.retry_count} retries",
                    extra={
                        "work_id": uow.work_id,
                        "task_id": task.task_id,
                        "error": str(e)
                    },
                    exc_info=True
                )

                task.status = TaskStatus.FAILED
                task.completed_at = datetime.utcnow()
                return False

    def _execute_compensation(
        self,
        uow: UnitOfWork,
        task_results: Dict[str, Any]
    ):
        """
        Execute saga compensation tasks.

        Args:
            uow: Unit of work with failed task
            task_results: Results from completed tasks
        """
        uow.status = WorkStatus.COMPENSATING

        logger.info(
            f"Executing compensation for UoW: {uow.work_id}",
            extra={
                "work_id": uow.work_id,
                "compensation_task_count": len(uow.compensation_tasks)
            }
        )

        # Execute compensation tasks in reverse order
        for comp_task in reversed(uow.compensation_tasks):
            try:
                comp_task.status = TaskStatus.IN_PROGRESS
                comp_task.started_at = datetime.utcnow()

                result = self._agent_invoker(comp_task, task_results)

                comp_task.status = TaskStatus.COMPLETED
                comp_task.completed_at = datetime.utcnow()
                comp_task.result = result

                logger.info(
                    f"Compensation task completed: {comp_task.task_id}",
                    extra={"work_id": uow.work_id, "task_id": comp_task.task_id}
                )

            except Exception as e:
                logger.error(
                    f"Compensation task failed: {comp_task.task_id}",
                    extra={
                        "work_id": uow.work_id,
                        "task_id": comp_task.task_id,
                        "error": str(e)
                    },
                    exc_info=True
                )

                comp_task.status = TaskStatus.FAILED
                comp_task.error = str(e)
                comp_task.completed_at = datetime.utcnow()

    def _record_metrics(
        self,
        uow: UnitOfWork,
        completed_tasks: List[str],
        failed_tasks: List[str],
        duration_seconds: Optional[float]
    ):
        """Record execution metrics for analysis"""
        self._execution_metrics[uow.work_id] = {
            "work_id": uow.work_id,
            "stage": uow.stage,
            "client_id": uow.client_id,
            "status": uow.status.value,
            "task_count": len(uow.tasks),
            "completed_count": len(completed_tasks),
            "failed_count": len(failed_tasks),
            "duration_seconds": duration_seconds,
            "compensation_executed": (uow.status == WorkStatus.COMPENSATED),
            "timestamp": datetime.utcnow().isoformat()
        }

    def get_metrics(self, work_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get execution metrics.

        Args:
            work_id: Specific UoW ID, or None for all metrics

        Returns:
            Metrics dictionary
        """
        with self._lock:
            if work_id:
                return self._execution_metrics.get(work_id, {})
            return self._execution_metrics.copy()

    def _mock_agent_invoke(
        self,
        task: Task,
        task_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Mock agent invocation for testing.

        Real implementation would use ProtocolBrokerAgent to:
        1. Discover agent by intent
        2. Send ProtocolMessage
        3. Receive response
        4. Validate output schema
        """
        logger.debug(
            f"Mock invoke: {task.agent_id}.{task.intent}",
            extra={"task_id": task.task_id}
        )

        # Build input from dependencies
        input_data = {}
        for dep_id in task.depends_on:
            if dep_id in task_results:
                input_data[dep_id] = task_results[dep_id]

        # Mock result matching output schema
        return {
            "status": "success",
            "task_id": task.task_id,
            "input": input_data,
            "timestamp": datetime.utcnow().isoformat()
        }
