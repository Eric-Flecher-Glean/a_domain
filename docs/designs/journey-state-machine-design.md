# Journey Orchestration - State Machine Design

**Document ID**: DES-002
**Version**: 1.0
**Status**: Draft
**Created**: 2026-01-27
**Author**: Requirements Chat (P0-A2A-F1-000)

---

## Executive Summary

This document defines the state machine design for the Client Journey Orchestration Engine, which automates client progression through Sandbox → Pilot → Production stages.

**Business Impact**:
- Reduces time-to-production from 90 days to 30 days (-67%)
- Automates stage transitions with validation gates
- Enables rollback to previous stages if issues detected
- Tracks client satisfaction and rollback rates

**Key Components**:
- Journey state machine with 3 primary stages
- Unit of work executor for stage-specific tasks
- Exit criteria validation engine
- Glean dashboard for journey visibility

---

## 1. Journey Stages

### 1.1 Stage Definitions

```
┌─────────────┐       ┌─────────────┐       ┌─────────────┐
│   SANDBOX   │──────>│    PILOT    │──────>│ PRODUCTION  │
│   (Stage 1) │       │  (Stage 2)  │       │  (Stage 3)  │
└─────────────┘       └─────────────┘       └─────────────┘
      │                     │                      │
      │                     │                      │
      └─────────────────────┴──────────────────────┘
                    ROLLBACK (any stage)
```

#### Stage 1: Sandbox

**Purpose**: Initial client setup and validation in isolated environment

**Duration**: 10-15 days (baseline: 30 days)

**Entry Criteria**:
- Client contract signed
- Infrastructure provisioned
- Initial data sources identified

**Activities**:
- Connector installation (Glean agents for data sources)
- Test dataset provisioning (via DataOps agent)
- Initial search quality validation
- Security audit pass

**Exit Criteria**:
- ✅ All connectors installed and syncing
- ✅ Test queries return relevant results (>80% precision)
- ✅ Security scan passes (no critical vulnerabilities)
- ✅ Client stakeholder demo approved

**Rollback Triggers**:
- Security vulnerabilities detected
- Data quality below threshold
- Client requests pause

#### Stage 2: Pilot

**Purpose**: Limited production deployment with real users

**Duration**: 10-15 days (baseline: 30 days)

**Entry Criteria**:
- Sandbox exit criteria met
- Pilot user cohort identified (typically 10-50 users)
- Production infrastructure ready

**Activities**:
- Deploy to production with limited user access
- Monitor search quality metrics
- Collect user feedback via Glean surveys
- Performance testing under real load

**Exit Criteria**:
- ✅ Search quality metrics stable (>85% precision)
- ✅ User satisfaction score >4.0/5.0
- ✅ No critical bugs in 7-day window
- ✅ Performance meets SLA (P95 latency <500ms)

**Rollback Triggers**:
- User satisfaction score drops below 3.5/5.0
- Critical bugs discovered
- Performance degradation >20%

#### Stage 3: Production

**Purpose**: Full deployment to all users

**Duration**: Ongoing

**Entry Criteria**:
- Pilot exit criteria met
- Full user rollout plan approved
- Monitoring and alerting configured

**Activities**:
- Gradual user rollout (10% → 50% → 100%)
- Continuous monitoring of metrics
- Ongoing optimization based on usage patterns

**Success Metrics**:
- User adoption >70% within 30 days
- Search satisfaction >4.5/5.0
- Query volume growth >20% month-over-month

**Rollback Triggers**:
- Major incidents (P0/P1 severity)
- User satisfaction drops below 4.0/5.0
- System instability

---

## 2. State Machine Implementation

### 2.1 State Model

```python
from enum import Enum
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from datetime import datetime

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
class JourneyState:
    """Current state of a client journey"""
    client_id: str
    current_stage: JourneyStage
    previous_stage: Optional[JourneyStage]
    started_at: datetime
    stage_started_at: datetime
    completed_stages: List[JourneyStage]
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "client_id": self.client_id,
            "current_stage": self.current_stage.value,
            "previous_stage": self.previous_stage.value if self.previous_stage else None,
            "started_at": self.started_at.isoformat(),
            "stage_started_at": self.stage_started_at.isoformat(),
            "completed_stages": [s.value for s in self.completed_stages],
            "metadata": self.metadata
        }
```

### 2.2 State Transition Rules

```python
class JourneyStateMachine:
    """
    State machine for client journey orchestration.

    Implements state transitions with validation.
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

        # Rollback completion (returns to previous stage)
        (JourneyStage.ROLLBACK, TransitionEvent.COMPLETE_ROLLBACK): None,  # Dynamic

        # Cancellation (from any state)
        (JourneyStage.SANDBOX, TransitionEvent.CANCEL_JOURNEY): JourneyStage.CANCELLED,
        (JourneyStage.PILOT, TransitionEvent.CANCEL_JOURNEY): JourneyStage.CANCELLED,
        (JourneyStage.PRODUCTION, TransitionEvent.CANCEL_JOURNEY): JourneyStage.CANCELLED,
    }

    def transition(
        self,
        state: JourneyState,
        event: TransitionEvent,
        metadata: Optional[Dict[str, Any]] = None
    ) -> JourneyState:
        """
        Execute state transition with validation.

        Args:
            state: Current journey state
            event: Transition event
            metadata: Additional context for transition

        Returns:
            New journey state

        Raises:
            InvalidTransitionError: If transition not allowed
        """
        current_stage = state.current_stage

        # Check if transition is valid
        if (current_stage, event) not in self.TRANSITIONS:
            raise InvalidTransitionError(
                f"Invalid transition: {current_stage} + {event}"
            )

        # Get target stage
        target_stage = self.TRANSITIONS[(current_stage, event)]

        # Special handling for rollback completion
        if event == TransitionEvent.COMPLETE_ROLLBACK:
            target_stage = state.previous_stage

        # Create new state
        new_state = JourneyState(
            client_id=state.client_id,
            current_stage=target_stage,
            previous_stage=current_stage,
            started_at=state.started_at,
            stage_started_at=datetime.utcnow(),
            completed_stages=state.completed_stages + [current_stage],
            metadata={**state.metadata, **(metadata or {})}
        )

        return new_state
```

---

## 3. Unit of Work Structure

### 3.1 Unit of Work Definition

A **Unit of Work** is an atomic set of tasks executed during a stage transition.

```python
@dataclass
class UnitOfWork:
    """
    Defines a unit of work for stage execution.
    """
    work_id: str
    stage: JourneyStage
    client_id: str
    tasks: List['Task']
    status: str  # pending, in_progress, completed, failed
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]

@dataclass
class Task:
    """Individual task within unit of work"""
    task_id: str
    name: str
    description: str
    agent_id: str  # Agent responsible for execution
    intent: str  # Intent to send to agent
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    depends_on: List[str]  # Task IDs that must complete first
    status: str  # pending, in_progress, completed, failed
    retry_count: int = 0
    max_retries: int = 3
```

### 3.2 Example: Sandbox Setup Unit of Work

```yaml
unit_of_work:
  work_id: "uow-client-123-sandbox-setup"
  stage: sandbox
  client_id: "client-123"
  status: pending

  tasks:
    - task_id: "task-1-provision-infra"
      name: "Provision Infrastructure"
      agent_id: "infrastructure-provisioning-agent"
      intent: "provision_sandbox_environment"
      input_schema:
        client_id: "string"
        data_sources: "array"
      output_schema:
        environment_id: "string"
        status: "string"
      depends_on: []

    - task_id: "task-2-install-connectors"
      name: "Install Glean Connectors"
      agent_id: "connector-installation-agent"
      intent: "install_connectors"
      input_schema:
        environment_id: "string"
        connectors: "array"
      output_schema:
        installed_connectors: "array"
      depends_on: ["task-1-provision-infra"]

    - task_id: "task-3-provision-test-data"
      name: "Provision Test Dataset"
      agent_id: "dataset-provisioning-agent"
      intent: "provision_test_dataset"
      input_schema:
        environment_id: "string"
        data_sources: "array"
      output_schema:
        dataset_id: "string"
        record_count: "number"
      depends_on: ["task-2-install-connectors"]

    - task_id: "task-4-run-security-scan"
      name: "Security Audit"
      agent_id: "security-audit-agent"
      intent: "run_security_scan"
      input_schema:
        environment_id: "string"
      output_schema:
        scan_result: "object"
        vulnerabilities: "array"
      depends_on: ["task-3-provision-test-data"]
```

---

## 4. Exit Criteria Validation

### 4.1 Validation Engine

```python
class ExitCriteriaValidator:
    """
    Validates exit criteria for stage transitions.
    """

    def validate_sandbox_exit(self, client_id: str) -> ValidationResult:
        """
        Validate Sandbox → Pilot transition criteria.

        Checks:
        1. All connectors installed and syncing
        2. Test query precision >80%
        3. Security scan passes
        4. Client demo approved
        """
        results = []

        # Check 1: Connectors
        connectors = self.get_connectors(client_id)
        all_syncing = all(c.status == "syncing" for c in connectors)
        results.append(ValidationCheck(
            name="connectors_syncing",
            passed=all_syncing,
            message=f"{len(connectors)} connectors syncing" if all_syncing else "Some connectors not syncing"
        ))

        # Check 2: Search quality
        precision = self.get_search_precision(client_id)
        results.append(ValidationCheck(
            name="search_quality",
            passed=precision > 0.80,
            message=f"Precision: {precision:.2%}"
        ))

        # Check 3: Security
        scan = self.get_latest_security_scan(client_id)
        no_critical = scan.critical_count == 0
        results.append(ValidationCheck(
            name="security_scan",
            passed=no_critical,
            message=f"{scan.critical_count} critical vulnerabilities"
        ))

        # Check 4: Demo approval
        demo_approved = self.get_demo_approval(client_id)
        results.append(ValidationCheck(
            name="demo_approved",
            passed=demo_approved,
            message="Demo approved" if demo_approved else "Demo not approved"
        ))

        return ValidationResult(
            stage="sandbox",
            passed=all(r.passed for r in results),
            checks=results
        )

    def validate_pilot_exit(self, client_id: str) -> ValidationResult:
        """
        Validate Pilot → Production transition criteria.

        Checks:
        1. Search quality >85%
        2. User satisfaction >4.0/5.0
        3. No critical bugs in 7-day window
        4. Performance SLA met
        """
        # Implementation similar to sandbox validation
        pass
```

---

## 5. Rollback Mechanisms

### 5.1 Rollback Triggers

**Automatic Rollback** (system-initiated):
- Critical security vulnerability detected
- Performance degradation >50%
- Data loss incident
- Service outage >1 hour

**Manual Rollback** (user-initiated):
- Client requests pause/rollback
- Business decision to delay
- Stakeholder concerns

### 5.2 Rollback Process

```python
class RollbackManager:
    """
    Manages journey rollbacks to previous stages.
    """

    def initiate_rollback(
        self,
        client_id: str,
        reason: str,
        rollback_to: Optional[JourneyStage] = None
    ) -> RollbackResult:
        """
        Initiate rollback to previous stage.

        Process:
        1. Pause current stage activities
        2. Create rollback snapshot
        3. Execute stage-specific rollback tasks
        4. Validate rollback success
        5. Notify stakeholders
        """
        state = self.get_journey_state(client_id)

        # Determine rollback target
        target_stage = rollback_to or state.previous_stage

        # Create rollback plan
        rollback_plan = self.create_rollback_plan(
            client_id=client_id,
            from_stage=state.current_stage,
            to_stage=target_stage,
            reason=reason
        )

        # Execute rollback
        result = self.execute_rollback(rollback_plan)

        # Update state machine
        if result.success:
            self.state_machine.transition(
                state,
                TransitionEvent.COMPLETE_ROLLBACK
            )

        return result
```

---

## 6. Integration with Agent Protocol

### 6.1 Agent Communication Pattern

```python
class JourneyOrchestrator:
    """
    Orchestrates client journeys using agent protocol.
    """

    def __init__(self, protocol_broker: ProtocolBrokerAgent):
        self.broker = protocol_broker
        self.state_machine = JourneyStateMachine()
        self.validator = ExitCriteriaValidator()

    def execute_unit_of_work(self, uow: UnitOfWork) -> ExecutionResult:
        """
        Execute unit of work by orchestrating agents.

        Process:
        1. Resolve task dependencies
        2. For each task:
           a. Discover agent via CapabilityDiscoveryAgent
           b. Send message via ProtocolBrokerAgent
           c. Wait for response
           d. Validate output
        3. Aggregate results
        """
        # Topological sort tasks by dependencies
        ordered_tasks = self.resolve_dependencies(uow.tasks)

        results = {}
        for task in ordered_tasks:
            # Discover agent
            matches = self.broker.discover_by_intent(task.intent)
            if not matches:
                return ExecutionResult(
                    success=False,
                    error=f"No agent found for intent: {task.intent}"
                )

            agent = matches[0]  # Take first match

            # Build input from previous task outputs
            task_input = self.build_task_input(task, results)

            # Send message
            message = ProtocolMessage(
                source_agent=Agent(agent_id="journey-orchestrator", domain="a_domain", version="1.0.0"),
                target_agent=Agent(agent_id=agent.agent_id, domain=agent.domain, version=agent.version),
                message_type="request",
                intent=task.intent,
                payload=task_input,
                security=Security(auth_token="...")
            )

            response = self.broker.route_message(message)

            # Store result
            results[task.task_id] = response.payload

        return ExecutionResult(success=True, results=results)
```

---

## 7. Metrics & Monitoring

### 7.1 Journey Metrics

**Stage Duration Metrics**:
- Sandbox duration (target: <15 days)
- Pilot duration (target: <15 days)
- Total time-to-production (target: <30 days)

**Quality Metrics**:
- Stage rollback rate (target: <5%)
- Exit criteria pass rate (target: >95%)
- Client satisfaction score (target: >4.5/5.0)

**Operational Metrics**:
- Active journeys by stage
- Average tasks per unit of work
- Task failure rate (target: <2%)

### 7.2 Glean Dashboard Integration

```python
class GleanDashboardPublisher:
    """
    Publishes journey metrics to Glean dashboard.
    """

    def publish_journey_status(self, client_id: str):
        """
        Publish current journey status to Glean.

        Creates/updates dashboard card with:
        - Current stage
        - Stage progress (% tasks complete)
        - Exit criteria status
        - Recent activities
        """
        state = self.get_journey_state(client_id)

        dashboard_card = {
            "client_id": client_id,
            "current_stage": state.current_stage.value,
            "started_at": state.started_at.isoformat(),
            "stage_duration_days": (datetime.utcnow() - state.stage_started_at).days,
            "exit_criteria": self.validator.validate_exit(client_id).to_dict(),
            "recent_activities": self.get_recent_activities(client_id)
        }

        self.glean_client.publish_card(dashboard_card)
```

---

## 8. Success Criteria

### 8.1 Functional Requirements

- ✅ State machine handles all stage transitions (Sandbox → Pilot → Production)
- ✅ Unit of work executor orchestrates agents for stage tasks
- ✅ Exit criteria validation prevents premature stage promotion
- ✅ Rollback mechanism reverts to previous stage on issues

### 8.2 Non-Functional Requirements

- **Performance**: Stage transitions complete in <5 minutes
- **Reliability**: Rollback success rate >99%
- **Observability**: All state changes logged to Glean dashboard
- **Scalability**: Support 100+ concurrent client journeys

---

## 9. Implementation Stories

This design supports the following implementation stories:

- **P0-A2A-F1-001**: Journey Orchestration - State Machine & Stage Management
- **P0-A2A-F1-002**: Journey Orchestration - Unit of Work Executor
- **P1-A2A-F1-003**: Journey Orchestration - Glean Dashboard Integration
- **P2-A2A-F1-004**: Journey Orchestration - Metrics & Reporting

---

## 10. Open Questions

1. **Rollback Data Retention**: How long should we retain rollback snapshots?
2. **Concurrent Journeys**: Can a client have multiple active journeys?
3. **Stage Skipping**: Should we allow Sandbox → Production (skip Pilot)?

---

## References

- **Story**: P0-A2A-F1-000 in IMPLEMENTATION_BACKLOG.yaml
- **Architecture**: docs/architecture/journey-orchestration-integration.md (ARCH-003)
- **DDD Context**: docs/ddd/journey-orchestration-bounded-context.md (DDD-002)
- **Features Document**: docs/concepts/inital-agents-a2a-features.md

---

**Last Updated**: 2026-01-27
**Next Review**: After implementation of P0-A2A-F1-001
