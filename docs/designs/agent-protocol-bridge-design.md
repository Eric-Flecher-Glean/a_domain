# Agent Protocol Bridge - Technical Design

**Feature ID**: F7
**Document ID**: DES-001
**Status**: Draft
**Created**: 2026-01-27
**Related Stories**: P0-A2A-F7-000, P0-A2A-F7-001, P0-A2A-F7-002, P0-A2A-F7-003, P0-A2A-F7-004

---

## Overview

### Purpose

The Agent Protocol Bridge implements a standardized agent-to-agent communication protocol enabling agents from different domains to discover, negotiate, and collaborate autonomously without hard-coded integrations.

### Problem Statement

**Current State**:
- Agents from different domains cannot communicate without hard-coded integrations
- No standard interface for agent discovery, capability negotiation, or data exchange
- Custom integration code required for every agent collaboration
- Security risks from direct agent-to-agent communication

**Pain Points**:
- Integration development time: Days per new agent collaboration
- Brittle integrations that break when agents change
- No visibility into agent interaction patterns
- Unable to sandbox untrusted agent code

### Solution Approach

Implement a protocol infrastructure that provides:
1. **Standard Message Format**: JSON-based protocol for all agent communications
2. **Capability Discovery**: Registry for agents to publish and query capabilities
3. **Contract Negotiation**: Automated handshake and contract validation
4. **Secure Execution**: Hyperlight-based sandboxing for untrusted agents
5. **Message Routing**: Central broker for reliable message delivery

### Primary Domain

**a_domain** (Unified Agent Interface) - This is infrastructure that all domains consume.

---

## Architecture

### Required Agents

#### 1. ProtocolBrokerAgent

**Responsibilities**:
- Manage agent-to-agent handshakes
- Negotiate communication contracts
- Route messages between agents
- Track active collaborations

**Key Methods**:
```python
def initiate_handshake(source_agent: str, target_agent: str, intent: str) -> HandshakeResult
def negotiate_contract(participants: List[str], contract_spec: Dict) -> Contract
def route_message(message: ProtocolMessage) -> DeliveryReceipt
def terminate_collaboration(collaboration_id: str) -> None
```

**State Management**:
- Active handshakes (in-memory with Redis backup)
- Validated contracts (persisted to contract_store)
- Message routing table (in-memory, refresh from registry)

#### 2. CapabilityDiscoveryAgent

**Responsibilities**:
- Publish agent capabilities in standard format
- Allow agents to query for collaborators by intent
- Maintain compatibility matrix between agents
- Version capability schemas

**Key Methods**:
```python
def register_capability(agent_id: str, capability: CapabilitySpec) -> None
def discover_by_intent(intent: str) -> List[AgentMatch]
def check_compatibility(agent_a: str, agent_b: str) -> CompatibilityResult
def get_capability_schema(agent_id: str, version: str) -> Schema
```

**Discovery Patterns**:
- **Intent-based**: `intent:provision_test_dataset` → returns agents that can provision datasets
- **Capability-based**: `capability:data_validation` → returns validation agents
- **Domain-based**: `domain:medtronic_poc` → returns all medtronic domain agents

#### 3. ContractValidatorAgent

**Responsibilities**:
- Validate inter-agent contracts before execution
- Ensure schema compatibility between input/output
- Enforce security policies (e.g., PII handling)
- Verify agent permissions

**Key Methods**:
```python
def validate_contract(contract: Contract) -> ValidationResult
def check_schema_compatibility(input_schema: Schema, output_schema: Schema) -> bool
def enforce_security_policy(contract: Contract, policy: SecurityPolicy) -> PolicyResult
def verify_permissions(agent_id: str, requested_capability: str) -> bool
```

**Validation Rules**:
- Input schema must match provider's expected input
- Output schema must satisfy consumer's requirements
- Both agents must have valid authentication tokens
- Contract must not violate domain security policies

#### 4. SandboxExecutionAgent

**Responsibilities**:
- Run untrusted agent code in Hyperlight VM
- Isolate agent interactions from host system
- Prevent malicious behavior (file access, network calls)
- Monitor resource usage (CPU, memory)

**Key Methods**:
```python
def execute_in_sandbox(agent_code: str, input_data: Dict, timeout: int) -> ExecutionResult
def validate_sandbox_policy(agent_id: str) -> SandboxPolicy
def monitor_resource_usage(sandbox_id: str) -> ResourceMetrics
def terminate_sandbox(sandbox_id: str, reason: str) -> None
```

**Hyperlight Integration**:
- ARM64/macOS support (per Hyperlight PR reference)
- Copy-on-write memory management for efficiency
- Secure syscall filtering
- Network isolation (no outbound calls allowed)

---

## Protocol Specification

### Message Format

All agent-to-agent messages follow this JSON schema:

```json
{
  "protocol_version": "1.0",
  "message_id": "msg-uuid-v4",
  "timestamp": "2026-01-27T14:30:00Z",
  "source_agent": {
    "agent_id": "sdlc-test-agent",
    "domain": "a_domain",
    "version": "1.2.3"
  },
  "target_agent": {
    "agent_id": "dataset-provisioning-agent",
    "domain": "medtronic_poc",
    "version": "2.1.0"
  },
  "message_type": "request|response|event|error",
  "intent": "provision_test_dataset",
  "payload": {
    "input": {...},
    "contract_id": "contract-uuid",
    "correlation_id": "correlation-uuid"
  },
  "security": {
    "auth_token": "jwt-token-here",
    "encryption": "none|aes256"
  }
}
```

### Authentication

**JWT Token Structure**:
```json
{
  "sub": "sdlc-test-agent",
  "iss": "a_domain-auth-service",
  "aud": "dataset-provisioning-agent",
  "exp": 1706371800,
  "iat": 1706371200,
  "capabilities": ["read:datasets", "write:test_scenarios"],
  "domain": "a_domain"
}
```

**Token Validation**:
- Issued by a_domain auth service
- Not expired (exp > current_time)
- Audience matches target agent
- Capabilities sufficient for requested intent

### Error Handling

**Error Response Format**:
```json
{
  "protocol_version": "1.0",
  "message_id": "msg-error-uuid",
  "message_type": "error",
  "error": {
    "code": "CAPABILITY_NOT_FOUND|SCHEMA_MISMATCH|AUTH_FAILED|TIMEOUT|INTERNAL_ERROR",
    "message": "Human-readable error description",
    "details": {...},
    "retry_after": 300
  }
}
```

**Error Codes**:
- `CAPABILITY_NOT_FOUND`: Target agent doesn't support requested intent
- `SCHEMA_MISMATCH`: Input/output schemas incompatible
- `AUTH_FAILED`: Authentication token invalid or insufficient permissions
- `TIMEOUT`: Target agent didn't respond within timeout
- `INTERNAL_ERROR`: Unexpected broker or agent failure

---

## Unit of Work Definition

**Example Scenario**: SDLCTestAgent needs dataset from DatasetProvisioningAgent

```json
{
  "unit_of_work_id": "uow-agent-collaboration",
  "work_type": "agent_to_agent_workflow",
  "steps": [
    {
      "step": 1,
      "agent": "SDLCTestAgent",
      "action": "discover_capability",
      "query": "intent:provision_test_dataset"
    },
    {
      "step": 2,
      "agent": "CapabilityDiscoveryAgent",
      "output": "matching_agents",
      "result": ["DatasetProvisioningAgent"]
    },
    {
      "step": 3,
      "agent": "ProtocolBrokerAgent",
      "action": "initiate_handshake",
      "participants": ["SDLCTestAgent", "DatasetProvisioningAgent"]
    },
    {
      "step": 4,
      "agent": "ContractValidatorAgent",
      "action": "validate_contract",
      "contract": {
        "input": "test_scenario_id",
        "output": "dataset_connection_string"
      }
    },
    {
      "step": 5,
      "agent": "DatasetProvisioningAgent",
      "action": "execute_provision",
      "execution_environment": "hyperlight_sandbox"
    },
    {
      "step": 6,
      "agent": "SDLCTestAgent",
      "action": "receive_dataset",
      "validates": "schema_matches"
    }
  ],
  "exit_criteria": {
    "collaboration_successful": true,
    "contract_satisfied": true
  }
}
```

---

## Success Metrics

### Primary Metrics

1. **Inter-agent collaborations per day**: 500+
   - Baseline: 0 (no protocol exists)
   - Target: 500+ successful collaborations/day
   - Measurement: Count of completed handshakes → contract execution → success

2. **Integration development time**: <1 hour (vs. days for custom code)
   - Baseline: 2-3 days per new agent integration
   - Target: <1 hour (agent registers capability → discoverable)
   - Measurement: Time from capability registration to first successful collaboration

3. **Security incidents from agent interactions**: 0
   - Baseline: N/A (no agent interactions yet)
   - Target: 0 security incidents (sandbox breaches, unauthorized data access)
   - Measurement: Count of security violations detected by ContractValidator or sandbox

4. **Protocol adoption across domains**: 100%
   - Baseline: 0% (protocol doesn't exist)
   - Target: 100% of domains using protocol for agent collaboration
   - Measurement: % of domains with at least 1 agent registered in capability registry

### Secondary Metrics

- Message throughput: 100+ messages/sec
- Average handshake latency: <100ms
- Contract validation success rate: >95%
- Sandbox execution overhead: <10% vs. native execution

---

## Value Proposition

### Benefits

1. **Zero-code integrations**: Agents collaborate without custom integration code
2. **Security**: Sandboxed execution prevents malicious agents
3. **Scalability**: Add new agents without breaking existing workflows
4. **Standard protocol**: Industry-standard agent communication pattern
5. **Observability**: Every interaction tracked and measurable

### ROI Calculation

**Time Savings**:
- Before: 2-3 days per agent integration × 10 integrations/month = 20-30 days/month
- After: <1 hour per integration × 10 integrations/month = 10 hours/month
- **Savings**: ~90% reduction in integration effort

**Risk Reduction**:
- Security incidents avoided: Sandboxing prevents malicious code execution
- Integration failures: Contract validation catches incompatibilities before execution

---

## Integration Points

### Producer/Consumer Relationships

**Consumes from**:
- All domains (all agents register capabilities in discovery registry)

**Provides to**:
- All domains (protocol for inter-agent communication)

**Integration with**:
- Hyperlight: Sandboxed agent execution for security
- knowledge_labor_observability_metrics: Every unit of work emits events for tracking

### Client Journey Stages Supported

**All stages** (this is infrastructure) - enables agent collaboration across:
- Discovery (Pre-Sandbox)
- Sandbox
- Pilot
- Production
- Optimization (Continuous)

---

## Technical Decisions

### Key Decisions

| Decision | Rationale |
|----------|-----------|
| JSON-based protocol | Industry standard, human-readable, well-supported |
| JWT authentication | Stateless, standard, supports capability-based permissions |
| Hyperlight for sandboxing | ARM64/macOS support, copy-on-write efficiency, security isolation |
| Central broker pattern | Simplifies routing, enables observability, single point for policy enforcement |
| Intent-based discovery | More flexible than capability-based (e.g., "provision dataset" vs. "DatasetProvisioningAgent") |

### Alternative Approaches Considered

1. **gRPC instead of JSON**:
   - Pro: Better performance, schema validation
   - Con: Less human-readable, requires code generation
   - Decision: Start with JSON, migrate to gRPC if performance becomes issue

2. **Direct agent-to-agent vs. broker**:
   - Pro: Lower latency, simpler architecture
   - Con: No central observability, harder to enforce policies
   - Decision: Use broker for observability and policy enforcement

3. **Docker containers vs. Hyperlight**:
   - Pro: More mature, wider ecosystem
   - Con: Heavier weight, slower startup
   - Decision: Hyperlight for lightweight, fast sandboxing

---

## Open Questions

1. **Versioning Strategy**: How to handle protocol version upgrades when agents are on different versions?
   - Proposal: Support backward compatibility for 2 major versions

2. **Rate Limiting**: Should broker enforce rate limits per agent?
   - Proposal: Start with 1000 requests/min per agent, adjust based on metrics

3. **Message Persistence**: Should messages be persisted for replay/audit?
   - Proposal: Persist only contract negotiations and errors, not all messages

4. **Multi-region Support**: How to route messages across regions?
   - Proposal: Start single-region, add federation later

---

## References

- **Feature Specification**: docs/concepts/inital-agents-a2a-features.md (Feature 7)
- **Hyperlight Documentation**: https://github.com/hyperlight-dev/hyperlight
- **Related Stories**: P0-A2A-F7-001, P0-A2A-F7-002, P0-A2A-F7-003, P0-A2A-F7-004

---

*This design document serves as the foundation for implementing the Agent Protocol Bridge feature.*
