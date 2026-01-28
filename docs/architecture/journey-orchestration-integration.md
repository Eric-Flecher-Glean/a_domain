# Integration Architecture - Journey Orchestration

**Document ID**: ARCH-003
**Version**: 1.0
**Status**: Draft
**Created**: 2026-01-27
**Author**: Requirements Chat (P0-A2A-F1-000)

---

## Executive Summary

This document defines the integration architecture for the Client Journey Orchestration Engine within the a_domain agent-to-agent platform.

**Purpose**: Enable automated client progression through deployment stages (Sandbox → Pilot → Production) via agent orchestration.

**Key Integration Points**:
- Agent Protocol Bridge (message routing, discovery)
- DataOps Lifecycle Agent (dataset provisioning)
- Glean Platform (dashboard, metrics publishing)
- External systems (customer CRM, notification services)

---

## 1. System Context

```
┌────────────────────────────────────────────────────────────────┐
│                    a_domain Platform                            │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │         Journey Orchestration Engine                     │  │
│  │                                                          │  │
│  │  ┌────────────────┐      ┌────────────────┐            │  │
│  │  │  State Machine │      │  UoW Executor  │            │  │
│  │  └────────────────┘      └────────────────┘            │  │
│  │          │                       │                      │  │
│  │          └───────────┬───────────┘                      │  │
│  │                      │                                  │  │
│  └──────────────────────┼──────────────────────────────────┘  │
│                         │                                      │
│                         ▼                                      │
│  ┌────────────────────────────────────────────────────────┐  │
│  │         Agent Protocol Bridge                          │  │
│  │                                                        │  │
│  │  ┌────────────────┐      ┌────────────────┐          │  │
│  │  │ Protocol Broker│      │  Discovery     │          │  │
│  │  └────────────────┘      └────────────────┘          │  │
│  └──────────────────────┬─────────────────────┬──────────┘  │
│                         │                     │              │
│                         ▼                     ▼              │
│  ┌──────────────────┐  ┌──────────────────┐  ┌───────────┐ │
│  │ DataOps Agent    │  │  Security Agent  │  │  ... +10  │ │
│  └──────────────────┘  └──────────────────┘  └───────────┘ │
└─────────────────────────────────┬──────────────────────────┘
                                  │
                         ┌────────┴────────┐
                         ▼                 ▼
                  ┌────────────┐    ┌────────────┐
                  │   Glean    │    │  External  │
                  │  Platform  │    │  Systems   │
                  └────────────┘    └────────────┘
```

---

## 2. Component Architecture

### 2.1 Journey Orchestration Components

#### JourneyStateMachine
- **Responsibility**: Manage stage transitions with validation
- **Interfaces**:
  - `transition(state, event) -> new_state`
  - `validate_transition(state, event) -> bool`
- **Dependencies**: None (pure state management)

#### UnitOfWorkExecutor
- **Responsibility**: Execute stage tasks by orchestrating agents
- **Interfaces**:
  - `execute(uow) -> ExecutionResult`
  - `monitor_progress(uow_id) -> ProgressStatus`
- **Dependencies**:
  - ProtocolBrokerAgent (message routing)
  - CapabilityDiscoveryAgent (agent discovery)

#### ExitCriteriaValidator
- **Responsibility**: Validate stage exit criteria before promotion
- **Interfaces**:
  - `validate_sandbox_exit(client_id) -> ValidationResult`
  - `validate_pilot_exit(client_id) -> ValidationResult`
- **Dependencies**:
  - Metrics collection agents
  - External validation services

#### RollbackManager
- **Responsibility**: Handle rollback to previous stages
- **Interfaces**:
  - `initiate_rollback(client_id, reason) -> RollbackResult`
  - `create_rollback_snapshot(client_id) -> Snapshot`
- **Dependencies**:
  - State persistence layer
  - Agent coordination for rollback tasks

---

## 3. Integration Patterns

### 3.1 Agent Discovery & Routing

**Pattern**: Intent-based agent discovery via CapabilityDiscoveryAgent

```python
# Journey Orchestrator discovers agents for tasks
matches = discovery_agent.discover_by_intent("provision_test_dataset")

# Select agent (e.g., DataOps Provisioning Agent)
agent = matches[0]

# Route message via Protocol Broker
message = ProtocolMessage(
    source_agent=Agent(agent_id="journey-orchestrator", ...),
    target_agent=Agent(agent_id=agent.agent_id, ...),
    intent="provision_test_dataset",
    payload={"client_id": "client-123", "data_sources": [...]}
)

response = protocol_broker.route_message(message)
```

**Benefits**:
- Decouples orchestrator from specific agent implementations
- Enables agent substitution without code changes
- Supports dynamic agent scaling

### 3.2 State Persistence

**Pattern**: Event-sourced state persistence

```python
class JourneyEventStore:
    """
    Stores journey events for state reconstruction.
    """

    def append_event(self, event: JourneyEvent):
        """Store event (immutable log)"""
        self.events.append({
            "event_id": uuid.uuid4(),
            "client_id": event.client_id,
            "event_type": event.event_type,
            "timestamp": datetime.utcnow(),
            "data": event.data
        })

    def reconstruct_state(self, client_id: str) -> JourneyState:
        """Rebuild current state from event history"""
        events = self.get_events(client_id)
        state = JourneyState.initial()

        for event in events:
            state = state.apply_event(event)

        return state
```

**Benefits**:
- Complete audit trail of stage transitions
- Enables time-travel debugging
- Supports rollback by replaying events

### 3.3 Metrics Publishing

**Pattern**: Asynchronous metrics publishing to Glean

```python
class GleanMetricsPublisher:
    """
    Publishes journey metrics to Glean dashboard.
    """

    async def publish_stage_transition(self, event: StageTransitionEvent):
        """
        Publish stage transition to Glean.

        Creates dashboard card showing:
        - Stage progression timeline
        - Current stage status
        - Exit criteria checklist
        """
        card = {
            "type": "journey_status",
            "client_id": event.client_id,
            "from_stage": event.from_stage,
            "to_stage": event.to_stage,
            "timestamp": event.timestamp,
            "exit_criteria": event.exit_criteria_results
        }

        await self.glean_client.create_card(card)
```

**Benefits**:
- Real-time visibility into client journeys
- Searchable journey history in Glean
- Integration with Glean alerts

---

## 4. Data Flow

### 4.1 Stage Transition Flow

```
1. Exit Criteria Validation
   ┌─────────────────────────┐
   │ ExitCriteriaValidator   │
   │                         │
   │ - Check connectors      │
   │ - Check search quality  │
   │ - Check security        │
   │ - Check demo approval   │
   └──────────┬──────────────┘
              │ ValidationResult
              ▼
2. State Transition
   ┌─────────────────────────┐
   │  JourneyStateMachine    │
   │                         │
   │ - Validate transition   │
   │ - Update state          │
   │ - Persist event         │
   └──────────┬──────────────┘
              │ NewState
              ▼
3. Unit of Work Execution
   ┌─────────────────────────┐
   │  UnitOfWorkExecutor     │
   │                         │
   │ - Create UoW for stage  │
   │ - Resolve dependencies  │
   │ - Execute tasks         │
   └──────────┬──────────────┘
              │ ExecutionResult
              ▼
4. Metrics Publishing
   ┌─────────────────────────┐
   │ GleanMetricsPublisher   │
   │                         │
   │ - Publish to dashboard  │
   │ - Update timeline       │
   │ - Send notifications    │
   └─────────────────────────┘
```

### 4.2 Task Execution Flow

```
┌──────────────────────────────────────────────────────┐
│              Unit of Work Executor                    │
└───────────────┬──────────────────────────────────────┘
                │
                │ 1. Discover agent
                ▼
    ┌───────────────────────────┐
    │ CapabilityDiscoveryAgent  │
    │  discover_by_intent(...)  │
    └───────────┬───────────────┘
                │ AgentMatch
                │ 2. Route message
                ▼
    ┌───────────────────────────┐
    │   ProtocolBrokerAgent     │
    │  route_message(...)       │
    └───────────┬───────────────┘
                │ ProtocolMessage
                │ 3. Execute task
                ▼
    ┌───────────────────────────┐
    │   Target Agent            │
    │  (e.g., DataOps Agent)    │
    └───────────┬───────────────┘
                │ Response
                │ 4. Return result
                ▼
    ┌───────────────────────────┐
    │  UnitOfWorkExecutor       │
    │  (aggregate results)      │
    └───────────────────────────┘
```

---

## 5. External Integrations

### 5.1 Glean Platform Integration

**Integration Type**: REST API + Webhooks

**Capabilities**:
- Dashboard card creation/updates
- Metrics publishing
- Alert configuration
- Search integration

**API Endpoints**:
```
POST /api/v1/cards
GET  /api/v1/cards/{card_id}
POST /api/v1/metrics
POST /api/v1/alerts
```

**Authentication**: OAuth 2.0 with service account

### 5.2 Customer CRM Integration

**Integration Type**: Webhook notifications

**Events Published**:
- `journey.stage_transition` - Stage change notification
- `journey.rollback_initiated` - Rollback alert
- `journey.completed` - Journey completion

**Payload Example**:
```json
{
  "event_type": "journey.stage_transition",
  "client_id": "client-123",
  "from_stage": "sandbox",
  "to_stage": "pilot",
  "timestamp": "2026-01-27T10:30:00Z",
  "metadata": {
    "exit_criteria_passed": true,
    "user_satisfaction": 4.2
  }
}
```

---

## 6. Security & Compliance

### 6.1 Authentication & Authorization

**Agent-to-Agent Auth**: JWT tokens via Protocol Broker
**External API Auth**: OAuth 2.0
**State Encryption**: AES-256 for persisted state

### 6.2 Audit Trail

All state transitions logged with:
- Timestamp
- Actor (user/system)
- Reason for transition
- Validation results

**Retention**: 2 years for compliance

---

## 7. Scalability Considerations

### 7.1 Concurrent Journey Support

**Target**: 100+ concurrent client journeys

**Strategies**:
- Stateless orchestrator design
- Event-driven architecture for async tasks
- Horizontal scaling via Kubernetes

### 7.2 Performance Targets

| Metric | Target |
|--------|--------|
| Stage transition latency | <5 minutes |
| UoW task execution | <2 minutes per task |
| Exit criteria validation | <30 seconds |
| Rollback initiation | <10 minutes |

---

## 8. Deployment Architecture

```
┌───────────────────────────────────────────────────────────┐
│                  Kubernetes Cluster                        │
│                                                            │
│  ┌──────────────────────────────────────────────────┐    │
│  │  Journey Orchestration Namespace                 │    │
│  │                                                   │    │
│  │  ┌────────────────────┐  ┌──────────────────┐   │    │
│  │  │ Orchestrator Pod   │  │  State Store     │   │    │
│  │  │ (3 replicas)       │  │  (PostgreSQL)    │   │    │
│  │  └────────────────────┘  └──────────────────┘   │    │
│  │                                                   │    │
│  │  ┌────────────────────┐  ┌──────────────────┐   │    │
│  │  │ Metrics Publisher  │  │  Event Store     │   │    │
│  │  │ (2 replicas)       │  │  (EventStoreDB)  │   │    │
│  │  └────────────────────┘  └──────────────────┘   │    │
│  └──────────────────────────────────────────────────┘    │
│                                                            │
│  ┌──────────────────────────────────────────────────┐    │
│  │  Agent Protocol Namespace                        │    │
│  │  (ProtocolBrokerAgent, DiscoveryAgent)           │    │
│  └──────────────────────────────────────────────────┘    │
└───────────────────────────────────────────────────────────┘
```

---

## 9. Error Handling & Resilience

### 9.1 Task Retry Logic

```python
class ResilientTaskExecutor:
    """
    Executes tasks with retry and circuit breaker.
    """

    def execute_with_retry(self, task: Task) -> TaskResult:
        """
        Execute task with exponential backoff.
        """
        for attempt in range(task.max_retries):
            try:
                result = self.execute_task(task)
                return result
            except RetryableError as e:
                if attempt < task.max_retries - 1:
                    sleep_time = 2 ** attempt  # Exponential backoff
                    time.sleep(sleep_time)
                else:
                    raise TaskExecutionError(f"Max retries exceeded: {e}")
```

### 9.2 Circuit Breaker Pattern

For external integrations (Glean, CRM):
- Open circuit after 5 consecutive failures
- Half-open state after 60 seconds
- Close circuit after 3 successful requests

---

## 10. Monitoring & Alerting

### 10.1 Key Metrics

**Journey Metrics**:
- Active journeys by stage
- Average stage duration
- Rollback rate
- Exit criteria pass rate

**System Metrics**:
- Task execution latency (P50, P99)
- Message throughput (messages/sec)
- Error rate by error type

### 10.2 Alerts

| Alert | Condition | Severity |
|-------|-----------|----------|
| High rollback rate | >5% in 24h window | P2 |
| Stage transition failure | Any transition fails | P1 |
| Exit criteria degradation | Pass rate <90% | P2 |
| System throughput low | <50% of target | P2 |

---

## 11. Testing Strategy

### 11.1 Integration Tests

```python
class TestJourneyIntegration:
    """
    Integration tests for journey orchestration.
    """

    def test_sandbox_to_pilot_transition(self):
        """
        Test complete Sandbox → Pilot transition.

        Verifies:
        - Exit criteria validation
        - State transition
        - UoW execution
        - Metrics publishing
        """
        # Setup
        client_id = "test-client-123"
        orchestrator = JourneyOrchestrator(...)

        # Execute
        result = orchestrator.promote_to_pilot(client_id)

        # Verify
        assert result.success
        state = orchestrator.get_state(client_id)
        assert state.current_stage == JourneyStage.PILOT
```

### 11.2 Load Tests

**Scenarios**:
- 100 concurrent journeys
- 1000 UoW tasks/minute
- Sustained load for 1 hour

**Success Criteria**:
- Latency <5 minutes for stage transitions
- Error rate <1%
- No resource exhaustion

---

## 12. Migration & Rollout

### 12.1 Rollout Plan

**Phase 1 (Week 1-2)**:
- Deploy to staging environment
- Test with 5 pilot clients

**Phase 2 (Week 3-4)**:
- Gradual production rollout (10% → 50% → 100%)
- Monitor metrics closely

**Phase 3 (Week 5+)**:
- Full production deployment
- Continuous optimization

### 12.2 Rollback Plan

If issues detected:
1. Route new journeys to legacy system
2. Complete in-flight journeys in new system
3. Investigate and fix issues
4. Resume gradual rollout

---

## References

- **State Machine Design**: docs/designs/journey-state-machine-design.md (DES-002)
- **DDD Context**: docs/ddd/journey-orchestration-bounded-context.md (DDD-002)
- **Configuration Guide**: docs/technical/journey-orchestration-config.md (TECH-003)
- **Features Document**: docs/concepts/inital-agents-a2a-features.md

---

**Last Updated**: 2026-01-27
**Next Review**: After P0-A2A-F1-001 implementation
