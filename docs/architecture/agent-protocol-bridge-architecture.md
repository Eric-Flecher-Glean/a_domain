# Agent Protocol Bridge - System Architecture

**Feature ID**: F7
**Document ID**: ARCH-002
**Status**: Draft
**Created**: 2026-01-27
**Related Stories**: P0-A2A-F7-000, P0-A2A-F7-001, P0-A2A-F7-002, P0-A2A-F7-003, P0-A2A-F7-004

---

## System Overview

The Agent Protocol Bridge provides a standardized infrastructure for agent-to-agent communication across all domains in the a_domain platform.

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     a_domain (Unified Interface)                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────────┐  ┌─────────────────────────────────────┐ │
│  │ Capability       │  │   ProtocolBrokerAgent                │ │
│  │ DiscoveryAgent   │  │   - Handshake management            │ │
│  │                  │  │   - Contract negotiation            │ │
│  │ - Registry       │  │   - Message routing                 │ │
│  │ - Intent queries │  │                                     │ │
│  └────────┬─────────┘  └────────┬──────────────────────┬─────┘ │
│           │                     │                       │       │
│           │    ┌────────────────┴─────────┐             │       │
│           │    │ ContractValidatorAgent   │             │       │
│           │    │ - Schema validation      │             │       │
│           │    │ - Security policy        │             │       │
│           │    └──────────────────────────┘             │       │
│           │                                             │       │
│           │                 ┌───────────────────────────┴─────┐ │
│           │                 │  SandboxExecutionAgent          │ │
│           │                 │  (Hyperlight Integration)       │ │
│           │                 └─────────────────────────────────┘ │
│           │                                                       │
└───────────┼───────────────────────────────────────────────────────┘
            │
    ┌───────┴────────┐
    │                │
┌───▼───┐  ┌────▼────┐  ┌─────▼──────┐  ┌────▼─────┐
│ SDLC  │  │Medtronic│  │ Knowledge  │  │  Glean   │
│Domain │  │ POC     │  │ Labor Obs  │  │ Domain   │
└───────┘  └─────────┘  └────────────┘  └──────────┘
```

---

## Component Architecture

### 1. ProtocolBrokerAgent

**Location**: `src/a_domain/protocol/broker_agent.py`

**Responsibilities**:
- Central message router for all agent-to-agent communication
- Manages handshake lifecycle
- Negotiates and stores contracts
- Ensures reliable message delivery

**Key Components**:

```python
class ProtocolBrokerAgent:
    def __init__(self):
        self.handshake_manager = HandshakeManager()
        self.contract_store = ContractStore()
        self.message_router = MessageRouter()
        self.auth_service = AuthService()

    # Core methods
    def initiate_handshake(...)
    def negotiate_contract(...)
    def route_message(...)
    def terminate_collaboration(...)
```

**Dependencies**:
- Redis: In-memory handshake state
- PostgreSQL: Contract persistence
- JWT library: Token validation
- Message queue (RabbitMQ): Async message delivery

### 2. CapabilityDiscoveryAgent

**Location**: `src/a_domain/protocol/discovery_agent.py`

**Responsibilities**:
- Maintain registry of agent capabilities
- Support intent-based queries
- Manage capability versioning
- Track compatibility matrix

**Data Model**:

```python
class CapabilitySpec:
    agent_id: str
    domain: str
    version: str
    intents: List[str]  # e.g., ["provision_test_dataset", "validate_data"]
    input_schema: Dict
    output_schema: Dict
    requires: List[str]  # Required capabilities from other agents
    provides: List[str]  # Capabilities this agent offers

class CompatibilityMatrix:
    agent_a: str
    agent_b: str
    compatible: bool
    schema_version: str
    last_validated: datetime
```

**Storage**:
- PostgreSQL: Capability registry (persistent)
- Redis: Fast capability lookup cache
- Schema registry: Versioned capability schemas

### 3. ContractValidatorAgent

**Location**: `src/a_domain/protocol/validator_agent.py`

**Responsibilities**:
- Validate contracts before execution
- Enforce security policies
- Verify schema compatibility
- Check agent permissions

**Validation Pipeline**:

```python
def validate_contract(contract: Contract) -> ValidationResult:
    # Step 1: Verify both agents exist and are active
    if not agents_exist(contract.participants):
        return ValidationResult(valid=False, error="Agent not found")

    # Step 2: Check schema compatibility
    if not schemas_compatible(contract.input_schema, contract.output_schema):
        return ValidationResult(valid=False, error="Schema mismatch")

    # Step 3: Enforce security policies
    if not security_policy_allows(contract):
        return ValidationResult(valid=False, error="Security policy violation")

    # Step 4: Verify permissions
    if not permissions_sufficient(contract):
        return ValidationResult(valid=False, error="Insufficient permissions")

    return ValidationResult(valid=True)
```

**Security Policies**:
- PII handling: Contracts involving PII must use encryption
- Cross-domain access: Restricted unless explicitly allowed
- Resource limits: Max execution time, memory, CPU
- Network isolation: Sandboxed agents cannot make outbound calls

### 4. SandboxExecutionAgent

**Location**: `src/a_domain/protocol/sandbox_agent.py`

**Responsibilities**:
- Execute untrusted agent code in isolated environment
- Monitor resource usage
- Enforce sandbox policies
- Terminate on policy violations

**Hyperlight Integration**:

```python
class SandboxExecutionAgent:
    def __init__(self):
        self.hyperlight = HyperlightRuntime()
        self.policy_engine = SandboxPolicyEngine()

    def execute_in_sandbox(
        self,
        agent_code: str,
        input_data: Dict,
        timeout: int = 30
    ) -> ExecutionResult:
        # 1. Validate sandbox policy
        policy = self.policy_engine.get_policy(agent_id)

        # 2. Create Hyperlight VM
        vm = self.hyperlight.create_vm(
            memory_mb=policy.max_memory,
            cpu_limit=policy.max_cpu,
            network_isolation=True
        )

        # 3. Execute with monitoring
        result = vm.execute(
            code=agent_code,
            input=input_data,
            timeout=timeout,
            on_syscall=self.syscall_filter
        )

        # 4. Cleanup
        vm.terminate()

        return result
```

**Hyperlight Features Used**:
- Copy-on-write memory management
- ARM64/macOS support
- Secure syscall filtering
- Network isolation
- Resource monitoring

---

## Data Flow

### Successful Agent Collaboration Flow

```
1. SDLCTestAgent wants dataset from DatasetProvisioningAgent

   [SDLCTestAgent]
         │
         │ 1. Discover capability: "provision_test_dataset"
         ▼
   [CapabilityDiscoveryAgent]
         │
         │ 2. Returns: ["DatasetProvisioningAgent"]
         ▼
   [ProtocolBrokerAgent]
         │
         │ 3. Initiate handshake
         ▼
   [ContractValidatorAgent]
         │
         │ 4. Validate contract
         │    ✓ Schema compatible
         │    ✓ Security policy OK
         │    ✓ Permissions sufficient
         ▼
   [ProtocolBrokerAgent]
         │
         │ 5. Route message to DatasetProvisioningAgent
         ▼
   [SandboxExecutionAgent] (if untrusted)
         │
         │ 6. Execute in Hyperlight VM
         ▼
   [DatasetProvisioningAgent]
         │
         │ 7. Provision dataset
         │ 8. Return connection string
         ▼
   [ProtocolBrokerAgent]
         │
         │ 9. Route response to SDLCTestAgent
         ▼
   [SDLCTestAgent]
         │
         │ 10. Receive dataset, validate schema
         ✓ Collaboration successful
```

### Contract Rejection Flow

```
1. Agent requests collaboration with incompatible schema

   [AgentA]
         │
         │ Request: "intent:validate_data"
         ▼
   [CapabilityDiscoveryAgent]
         │
         │ Returns: ["DataValidationAgent"]
         ▼
   [ProtocolBrokerAgent]
         │
         │ Initiate handshake
         ▼
   [ContractValidatorAgent]
         │
         │ Validate contract
         │ ✗ Schema mismatch detected
         │   - AgentA expects output: {"valid": bool}
         │   - DataValidationAgent returns: {"result": str}
         ▼
   [ProtocolBrokerAgent]
         │
         │ Return error response
         ▼
   [AgentA]
         │
         │ Error: SCHEMA_MISMATCH
         │ Details: "Output schema incompatible"
         ✗ Collaboration rejected
```

---

## Deployment Architecture

### Infrastructure Requirements

**Services**:
```yaml
services:
  protocol-broker:
    image: a_domain/protocol-broker:latest
    replicas: 3
    ports: [8080]
    env:
      - REDIS_URL=redis://redis:6379
      - POSTGRES_URL=postgresql://db:5432/protocol
      - RABBITMQ_URL=amqp://rabbitmq:5672
    resources:
      cpu: 2
      memory: 4Gi

  capability-discovery:
    image: a_domain/capability-discovery:latest
    replicas: 2
    ports: [8081]
    env:
      - REDIS_URL=redis://redis:6379
      - POSTGRES_URL=postgresql://db:5432/capabilities

  contract-validator:
    image: a_domain/contract-validator:latest
    replicas: 2
    ports: [8082]

  sandbox-execution:
    image: a_domain/sandbox-execution:latest
    replicas: 5
    privileged: true  # Required for Hyperlight
    env:
      - HYPERLIGHT_MEMORY_LIMIT=512M
      - HYPERLIGHT_CPU_LIMIT=1
```

**Databases**:
- PostgreSQL: Contracts, capabilities, audit logs
- Redis: Handshake state, capability cache
- RabbitMQ: Async message queue

**Monitoring**:
- Prometheus: Metrics (message throughput, latency)
- Grafana: Dashboards
- Jaeger: Distributed tracing

---

## Performance Characteristics

### Throughput

- **Target**: 100+ messages/sec per broker instance
- **Scaling**: Horizontal (add more broker replicas)
- **Bottleneck**: Contract validation (CPU-bound)

### Latency

- **Handshake initiation**: <50ms (p50), <100ms (p99)
- **Contract validation**: <30ms (p50), <80ms (p99)
- **Message routing**: <20ms (p50), <50ms (p99)
- **Total collaboration latency**: <100ms (p50), <250ms (p99)

### Resource Usage

- **ProtocolBrokerAgent**: 2 CPU, 4Gi RAM per replica
- **CapabilityDiscoveryAgent**: 1 CPU, 2Gi RAM per replica
- **ContractValidatorAgent**: 1 CPU, 2Gi RAM per replica
- **SandboxExecutionAgent**: 2 CPU, 8Gi RAM per replica (Hyperlight overhead)

---

## Security Architecture

### Authentication & Authorization

**JWT Token Flow**:
```
1. Agent requests token from a_domain auth service
   - Provides agent_id, domain, requested capabilities
2. Auth service validates agent registration
3. Issues JWT with capabilities claim
4. Agent includes JWT in all protocol messages
5. Broker validates JWT on every message
```

**Capability-Based Access Control**:
- Each agent has list of capabilities (e.g., `read:datasets`, `write:test_scenarios`)
- Contracts require matching capabilities
- Tokens scoped to specific target agents (audience claim)

### Sandbox Security

**Hyperlight Isolation**:
- No file system access (except explicitly mounted volumes)
- No outbound network calls
- Syscall filtering (only allowed: memory allocation, logging)
- Resource limits enforced (CPU, memory, execution time)

**Threat Model**:
- **Malicious agent code**: Contained in Hyperlight VM, cannot escape
- **Data exfiltration**: Network isolation prevents unauthorized data transfer
- **Resource exhaustion**: CPU/memory limits prevent DoS
- **Contract manipulation**: Validator ensures schema and policy compliance

---

## Observability

### Metrics

**Protocol Metrics**:
- `protocol_messages_total{source_domain, target_domain, status}`: Counter
- `protocol_handshake_duration_seconds`: Histogram
- `protocol_contract_validation_duration_seconds`: Histogram
- `protocol_active_collaborations`: Gauge

**Agent Metrics**:
- `agent_capability_registrations_total{domain}`: Counter
- `agent_discovery_queries_total{intent}`: Counter
- `agent_sandbox_executions_total{status}`: Counter

### Tracing

**Distributed Tracing**:
- Trace ID propagated through all protocol messages
- Spans: handshake, contract_validation, message_routing, sandbox_execution
- Jaeger integration for visualization

### Logging

**Structured Logs**:
```json
{
  "timestamp": "2026-01-27T14:30:00Z",
  "level": "info",
  "component": "protocol-broker",
  "event": "handshake_initiated",
  "source_agent": "sdlc-test-agent",
  "target_agent": "dataset-provisioning-agent",
  "intent": "provision_test_dataset",
  "trace_id": "trace-uuid"
}
```

---

## Scalability Strategy

### Horizontal Scaling

**Stateless Components** (scale easily):
- ProtocolBrokerAgent: Load balance across replicas
- ContractValidatorAgent: Stateless validation
- SandboxExecutionAgent: Independent sandbox instances

**Stateful Components** (careful scaling):
- CapabilityDiscoveryAgent: Redis cache requires coordination
- Contract persistence: PostgreSQL read replicas for queries

### Load Balancing

- Round-robin for handshake initiation
- Sticky sessions for active collaborations (same broker instance)
- Circuit breakers for failing agents

---

## References

- **Design Document**: docs/designs/agent-protocol-bridge-design.md
- **Feature Specification**: docs/concepts/inital-agents-a2a-features.md (Feature 7)
- **DDD Specification**: docs/architecture/ddd-specification.md
- **Hyperlight Documentation**: https://github.com/hyperlight-dev/hyperlight

---

*This architecture document defines the system design for the Agent Protocol Bridge.*
