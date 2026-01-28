# Journey Orchestration - Bounded Context

**Document ID**: DDD-002
**Version**: 1.0
**Status**: Draft
**Created**: 2026-01-27
**Author**: Requirements Chat (P0-A2A-F1-000)

---

## 1. Bounded Context Overview

**Context Name**: Journey Orchestration

**Purpose**: Manage client progression through deployment stages (Sandbox → Pilot → Production) with automated validation and rollback capabilities.

**Ubiquitous Language**: See section 2

---

## 2. Ubiquitous Language

### Core Domain Terms

| Term | Definition | Example |
|------|------------|---------|
| **Journey** | Complete client lifecycle from Sandbox to Production | "Client-123's journey started 2026-01-15" |
| **Stage** | Distinct phase in client deployment (Sandbox, Pilot, Production) | "Client is in Pilot stage" |
| **Stage Transition** | Movement from one stage to another | "Promoted from Sandbox to Pilot" |
| **Unit of Work** | Atomic set of tasks executed during stage transition | "Sandbox setup UoW has 4 tasks" |
| **Task** | Individual action within unit of work | "Install connectors task" |
| **Exit Criteria** | Requirements that must be met before stage promotion | "Sandbox exit requires >80% search quality" |
| **Rollback** | Reverting to previous stage due to issues | "Initiated rollback from Pilot to Sandbox" |
| **Validation Gate** | Automated check preventing invalid transitions | "Exit criteria validation gate" |
| **Journey State** | Current status of client journey | "State: Pilot, duration: 8 days" |

### Process Terms

| Term | Definition |
|------|------------|
| **Promotion** | Advancing client to next stage after passing exit criteria |
| **Orchestration** | Coordinating agents to execute stage tasks |
| **Snapshot** | Point-in-time capture of journey state for rollback |
| **Progression** | Overall movement through journey stages |

---

## 3. Domain Model

### 3.1 Aggregates

#### Journey (Aggregate Root)

**Identity**: `client_id`

**Attributes**:
- `client_id: string` - Unique client identifier
- `current_stage: JourneyStage` - Current deployment stage
- `started_at: datetime` - Journey start time
- `stage_history: List[StageTransition]` - History of stage changes

**Invariants**:
- Journey must always be in exactly one stage
- Stage transitions must follow defined order (Sandbox → Pilot → Production)
- Cannot promote to next stage without passing exit criteria
- Rollback must return to previously completed stage

**Commands**:
- `start_journey(client_id)` - Begin new client journey
- `promote_to_pilot()` - Advance from Sandbox to Pilot
- `promote_to_production()` - Advance from Pilot to Production
- `initiate_rollback(reason)` - Revert to previous stage
- `cancel_journey(reason)` - Terminate journey

**Events**:
- `JourneyStarted`
- `StagePromoted`
- `RollbackInitiated`
- `RollbackCompleted`
- `JourneyCancelled`
- `JourneyCompleted`

#### UnitOfWork

**Identity**: `work_id`

**Attributes**:
- `work_id: string` - Unique UoW identifier
- `client_id: string` - Associated client
- `stage: JourneyStage` - Target stage
- `tasks: List[Task]` - Tasks to execute
- `status: WorkStatus` - Current execution status

**Invariants**:
- All task dependencies must be satisfied before execution
- Tasks must execute in topological order based on dependencies
- UoW cannot complete until all tasks succeed
- Failed tasks can retry up to max_retries

**Commands**:
- `add_task(task)` - Add task to unit of work
- `execute()` - Execute all tasks
- `retry_failed_tasks()` - Retry failed tasks
- `cancel()` - Cancel execution

**Events**:
- `UnitOfWorkCreated`
- `TaskExecutionStarted`
- `TaskExecutionCompleted`
- `TaskExecutionFailed`
- `UnitOfWorkCompleted`

### 3.2 Value Objects

#### JourneyStage

```python
class JourneyStage(Enum):
    SANDBOX = "sandbox"
    PILOT = "pilot"
    PRODUCTION = "production"
    ROLLBACK = "rollback"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
```

#### StageTransition

```python
@dataclass(frozen=True)
class StageTransition:
    from_stage: JourneyStage
    to_stage: JourneyStage
    transitioned_at: datetime
    reason: str
    exit_criteria_results: Dict[str, bool]
```

#### ExitCriteria

```python
@dataclass(frozen=True)
class ExitCriteria:
    stage: JourneyStage
    checks: List[ExitCriteriaCheck]

    def all_passed(self) -> bool:
        return all(check.passed for check in self.checks)
```

#### Task

```python
@dataclass
class Task:
    task_id: str
    name: str
    agent_id: str
    intent: str
    depends_on: List[str]
    status: TaskStatus
    retry_count: int = 0
```

---

## 4. Context Map

### 4.1 Upstream Contexts (Dependencies)

#### Agent Protocol Bridge Context

**Relationship**: Customer/Supplier

**Integration**:
- Journey Orchestration uses ProtocolBrokerAgent for message routing
- Journey Orchestration uses CapabilityDiscoveryAgent for agent discovery

**Anti-Corruption Layer**: Not needed (shared kernel pattern)

#### DataOps Context

**Relationship**: Customer/Supplier

**Integration**:
- Journey Orchestration invokes DataOps agents for dataset provisioning

**Contracts**:
- `provision_test_dataset` intent
- `teardown_dataset` intent

### 4.2 Downstream Contexts (Consumers)

#### Monitoring & Observability Context

**Relationship**: Publisher/Subscriber

**Integration**:
- Journey Orchestration publishes events to monitoring context
- Monitoring context subscribes to journey events for dashboards

**Published Events**:
- `JourneyStarted`
- `StagePromoted`
- `RollbackInitiated`

#### Notification Context

**Relationship**: Publisher/Subscriber

**Integration**:
- Journey Orchestration publishes events for customer notifications

**Published Events**:
- `StagePromoted` (notify customer of progression)
- `RollbackInitiated` (alert customer of issues)
- `JourneyCompleted` (notify customer of completion)

---

## 5. Domain Services

### JourneyOrchestrator (Domain Service)

**Responsibility**: Orchestrate journey progression through stages

**Operations**:
- `start_journey(client_id) -> Journey`
- `validate_exit_criteria(client_id, stage) -> ValidationResult`
- `execute_stage_transition(client_id, to_stage) -> TransitionResult`
- `execute_unit_of_work(uow) -> ExecutionResult`

**Collaborators**:
- JourneyStateMachine (state transitions)
- UnitOfWorkExecutor (task execution)
- ExitCriteriaValidator (gate validation)

### ExitCriteriaValidator (Domain Service)

**Responsibility**: Validate stage exit criteria before promotion

**Operations**:
- `validate(client_id, stage) -> ValidationResult`
- `get_criteria(stage) -> ExitCriteria`

**Collaborators**:
- External validation services (search quality, security)

---

## 6. Repository Interfaces

### JourneyRepository

```python
class JourneyRepository(ABC):
    """Repository for Journey aggregate"""

    @abstractmethod
    def save(self, journey: Journey) -> None:
        """Persist journey state"""

    @abstractmethod
    def find_by_client_id(self, client_id: str) -> Optional[Journey]:
        """Retrieve journey by client ID"""

    @abstractmethod
    def find_active_journeys(self) -> List[Journey]:
        """Get all non-completed journeys"""
```

### UnitOfWorkRepository

```python
class UnitOfWorkRepository(ABC):
    """Repository for UnitOfWork aggregate"""

    @abstractmethod
    def save(self, uow: UnitOfWork) -> None:
        """Persist unit of work"""

    @abstractmethod
    def find_by_id(self, work_id: str) -> Optional[UnitOfWork]:
        """Retrieve by work ID"""

    @abstractmethod
    def find_by_client_and_stage(
        self,
        client_id: str,
        stage: JourneyStage
    ) -> List[UnitOfWork]:
        """Get UoWs for client at specific stage"""
```

---

## 7. Domain Events

### Event Schema

```python
@dataclass
class JourneyStarted:
    """Journey initiated event"""
    event_id: str
    timestamp: datetime
    client_id: str
    initial_stage: JourneyStage

@dataclass
class StagePromoted:
    """Stage transition event"""
    event_id: str
    timestamp: datetime
    client_id: str
    from_stage: JourneyStage
    to_stage: JourneyStage
    exit_criteria_results: Dict[str, bool]

@dataclass
class RollbackInitiated:
    """Rollback started event"""
    event_id: str
    timestamp: datetime
    client_id: str
    from_stage: JourneyStage
    to_stage: JourneyStage
    reason: str
    initiated_by: str  # "system" or user ID
```

### Event Handlers

**Internal Handlers** (within context):
- `StagePromoted` → Create UnitOfWork for new stage
- `UnitOfWorkCompleted` → Check exit criteria
- `RollbackInitiated` → Create rollback snapshot

**External Handlers** (published to event bus):
- `StagePromoted` → Notify monitoring context
- `RollbackInitiated` → Alert notification context
- `JourneyCompleted` → Update CRM context

---

## 8. Business Rules

### 8.1 Stage Transition Rules

1. **Sequential Progression**: Stages must progress in order (Sandbox → Pilot → Production)
2. **Exit Criteria Gate**: Cannot promote without passing all exit criteria
3. **Rollback Limit**: Can only rollback to immediately previous stage
4. **No Stage Skipping**: Cannot skip stages (e.g., Sandbox → Production)

### 8.2 Validation Rules

1. **Sandbox Exit**:
   - All connectors syncing
   - Search quality >80%
   - Security scan passed
   - Demo approved by client

2. **Pilot Exit**:
   - Search quality >85%
   - User satisfaction >4.0/5.0
   - No critical bugs in 7 days
   - Performance SLA met

3. **Production Success**:
   - User adoption >70%
   - Search satisfaction >4.5/5.0
   - No P0/P1 incidents

---

## 9. Use Cases

### 9.1 Primary Use Cases

#### UC-1: Start New Journey

**Actor**: System Administrator

**Preconditions**: Client contract signed

**Flow**:
1. Admin invokes `start_journey(client_id)`
2. System creates Journey aggregate in SANDBOX stage
3. System creates initial UnitOfWork for sandbox setup
4. System publishes `JourneyStarted` event

**Postconditions**: Journey active in SANDBOX stage

#### UC-2: Promote to Pilot

**Actor**: Journey Orchestrator (automated)

**Preconditions**:
- Journey in SANDBOX stage
- All sandbox tasks completed

**Flow**:
1. System validates sandbox exit criteria
2. If all criteria pass:
   a. System transitions journey to PILOT stage
   b. System creates UnitOfWork for pilot setup
   c. System publishes `StagePromoted` event
3. If criteria fail:
   a. System logs validation failures
   b. Journey remains in SANDBOX

**Postconditions**: Journey in PILOT stage or validation failed

#### UC-3: Initiate Rollback

**Actor**: System (automatic) or Admin (manual)

**Preconditions**: Journey in PILOT or PRODUCTION stage

**Flow**:
1. Actor invokes `initiate_rollback(client_id, reason)`
2. System creates rollback snapshot
3. System transitions to ROLLBACK state
4. System executes rollback UnitOfWork
5. System transitions to previous stage
6. System publishes `RollbackCompleted` event

**Postconditions**: Journey reverted to previous stage

---

## 10. Constraints & Assumptions

### 10.1 Constraints

- **Max Concurrent Journeys**: System must support 100+ concurrent journeys
- **Stage Transition Latency**: Must complete in <5 minutes
- **Data Retention**: Journey history retained for 2 years

### 10.2 Assumptions

- Clients progress linearly through stages (no parallel pilots)
- Each client has exactly one active journey at a time
- External validation services (search quality, security) are reliable

---

## 11. Success Metrics

| Metric | Target |
|--------|--------|
| Time to Production | <30 days (baseline: 90 days) |
| Rollback Rate | <5% |
| Exit Criteria Pass Rate | >95% |
| Client Satisfaction | >4.5/5.0 |

---

## References

- **State Machine Design**: docs/designs/journey-state-machine-design.md (DES-002)
- **Integration Architecture**: docs/architecture/journey-orchestration-integration.md (ARCH-003)
- **DDD Specification**: docs/architecture/ddd-specification.md (ARCH-001)

---

**Last Updated**: 2026-01-27
**Next Review**: After implementation of P0-A2A-F1-001
