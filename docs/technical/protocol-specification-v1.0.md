# Protocol Specification v1.0

**Feature ID**: F7
**Document ID**: TECH-001
**Status**: Draft
**Version**: 1.0.0
**Created**: 2026-01-27
**Related Stories**: P0-A2A-F7-000, P0-A2A-F7-001

---

## Overview

This document defines the Agent-to-Agent Communication Protocol (A2ACP) v1.0, a JSON-based message format for standardized agent collaboration across all domains in the a_domain platform.

---

## Message Format

### Base Message Schema

All protocol messages MUST conform to this JSON schema:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["protocol_version", "message_id", "timestamp", "source_agent", "target_agent", "message_type"],
  "properties": {
    "protocol_version": {
      "type": "string",
      "pattern": "^\\d+\\.\\d+$",
      "description": "Protocol version (e.g., '1.0')"
    },
    "message_id": {
      "type": "string",
      "format": "uuid",
      "description": "Unique message identifier (UUID v4)"
    },
    "timestamp": {
      "type": "string",
      "format": "date-time",
      "description": "ISO 8601 timestamp (UTC)"
    },
    "source_agent": {
      "$ref": "#/definitions/Agent"
    },
    "target_agent": {
      "$ref": "#/definitions/Agent"
    },
    "message_type": {
      "type": "string",
      "enum": ["request", "response", "event", "error"]
    },
    "intent": {
      "type": "string",
      "description": "Agent intent (e.g., 'provision_test_dataset')"
    },
    "payload": {
      "type": "object",
      "description": "Message-specific data"
    },
    "security": {
      "$ref": "#/definitions/Security"
    }
  },
  "definitions": {
    "Agent": {
      "type": "object",
      "required": ["agent_id", "domain", "version"],
      "properties": {
        "agent_id": {
          "type": "string",
          "description": "Unique agent identifier"
        },
        "domain": {
          "type": "string",
          "description": "Domain this agent belongs to"
        },
        "version": {
          "type": "string",
          "pattern": "^\\d+\\.\\d+\\.\\d+$",
          "description": "Semantic version (e.g., '1.2.3')"
        }
      }
    },
    "Security": {
      "type": "object",
      "required": ["auth_token"],
      "properties": {
        "auth_token": {
          "type": "string",
          "description": "JWT authentication token"
        },
        "encryption": {
          "type": "string",
          "enum": ["none", "aes256"],
          "default": "none"
        }
      }
    }
  }
}
```

### Example Messages

#### Request Message

```json
{
  "protocol_version": "1.0",
  "message_id": "550e8400-e29b-41d4-a716-446655440000",
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
  "message_type": "request",
  "intent": "provision_test_dataset",
  "payload": {
    "test_scenario_id": "scenario-123",
    "dataset_type": "patient_demographics",
    "record_count": 1000,
    "contract_id": "contract-456",
    "correlation_id": "correlation-789"
  },
  "security": {
    "auth_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "encryption": "none"
  }
}
```

#### Response Message

```json
{
  "protocol_version": "1.0",
  "message_id": "660f9500-f39c-52e5-b827-557766551111",
  "timestamp": "2026-01-27T14:30:05Z",
  "source_agent": {
    "agent_id": "dataset-provisioning-agent",
    "domain": "medtronic_poc",
    "version": "2.1.0"
  },
  "target_agent": {
    "agent_id": "sdlc-test-agent",
    "domain": "a_domain",
    "version": "1.2.3"
  },
  "message_type": "response",
  "intent": "provision_test_dataset",
  "payload": {
    "dataset_id": "dataset-abc",
    "connection_string": "postgresql://test-db:5432/scenario_123",
    "record_count": 1000,
    "schema_version": "1.0",
    "correlation_id": "correlation-789"
  },
  "security": {
    "auth_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "encryption": "none"
  }
}
```

#### Error Message

```json
{
  "protocol_version": "1.0",
  "message_id": "770g0600-g40d-63f6-c938-668877662222",
  "timestamp": "2026-01-27T14:30:05Z",
  "source_agent": {
    "agent_id": "protocol-broker-agent",
    "domain": "a_domain",
    "version": "1.0.0"
  },
  "target_agent": {
    "agent_id": "sdlc-test-agent",
    "domain": "a_domain",
    "version": "1.2.3"
  },
  "message_type": "error",
  "payload": {
    "error": {
      "code": "SCHEMA_MISMATCH",
      "message": "Input schema incompatible with target agent's expected schema",
      "details": {
        "expected_schema": {"test_scenario_id": "string", "dataset_type": "string"},
        "received_schema": {"scenario_id": "string", "type": "string"}
      },
      "retry_after": 0,
      "correlation_id": "correlation-789"
    }
  },
  "security": {
    "auth_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "encryption": "none"
  }
}
```

---

## Authentication

### JWT Token Structure

All messages MUST include a JWT authentication token in the `security.auth_token` field.

**Token Claims**:

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

**Required Claims**:
- `sub` (subject): Source agent ID
- `iss` (issuer): Must be `a_domain-auth-service`
- `aud` (audience): Target agent ID
- `exp` (expiration): Unix timestamp (token expires after this time)
- `iat` (issued at): Unix timestamp (token creation time)
- `capabilities`: Array of granted capabilities
- `domain`: Source agent's domain

### Token Validation Rules

The ProtocolBrokerAgent MUST validate tokens before routing messages:

1. **Signature verification**: Token signed by a_domain auth service
2. **Expiration check**: `exp > current_time`
3. **Audience match**: `aud == target_agent.agent_id`
4. **Capability check**: Required capabilities present for requested intent
5. **Issuer verification**: `iss == "a_domain-auth-service"`

### Token Acquisition

Agents acquire tokens by calling the a_domain auth service:

```http
POST /auth/token
Content-Type: application/json

{
  "agent_id": "sdlc-test-agent",
  "target_agent_id": "dataset-provisioning-agent",
  "requested_capabilities": ["read:datasets", "write:test_scenarios"],
  "ttl": 3600
}

Response:
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_at": "2026-01-27T15:30:00Z"
}
```

---

## Error Codes

### Standard Error Codes

| Code | Description | Retry? | Typical Cause |
|------|-------------|--------|---------------|
| `CAPABILITY_NOT_FOUND` | Target agent doesn't support requested intent | No | Agent not registered or intent misspelled |
| `SCHEMA_MISMATCH` | Input/output schemas incompatible | No | Contract negotiation failed |
| `AUTH_FAILED` | Authentication token invalid or insufficient permissions | No | Expired token or missing capabilities |
| `TIMEOUT` | Target agent didn't respond within timeout | Yes | Agent overloaded or unresponsive |
| `INTERNAL_ERROR` | Unexpected broker or agent failure | Yes | System issue |
| `RATE_LIMIT_EXCEEDED` | Agent exceeded message rate limit | Yes (after delay) | Too many requests |
| `CONTRACT_VIOLATION` | Agent violated contract terms | No | Implementation bug |
| `SECURITY_POLICY_VIOLATION` | Security policy doesn't allow this collaboration | No | Unauthorized cross-domain access |

### Error Response Format

Error messages MUST include:
- `error.code`: Error code from table above
- `error.message`: Human-readable description
- `error.details`: Additional context (optional)
- `error.retry_after`: Seconds to wait before retry (0 = don't retry)

---

## Message Lifecycle

### Handshake Flow

```
1. Source agent sends handshake request
   - Type: "request"
   - Intent: "initiate_handshake"
   - Payload: { "target_agent_id": "...", "requested_intent": "..." }

2. Broker validates handshake
   - Check authentication
   - Verify target agent exists
   - Confirm capability compatibility

3. Broker sends handshake to target agent
   - Type: "request"
   - Intent: "accept_handshake"

4. Target agent accepts or rejects
   - Type: "response"
   - Payload: { "accepted": true|false, "reason": "..." }

5. Broker notifies source agent
   - Type: "response"
   - Payload: { "collaboration_id": "...", "contract": {...} }
```

### Contract Negotiation

```
1. Broker generates contract from handshake
   - Input schema: From source agent capability spec
   - Output schema: From target agent capability spec
   - Security policy: Based on domain policies

2. ContractValidatorAgent validates contract
   - Schema compatibility check
   - Security policy enforcement
   - Permission verification

3. Contract stored in contract_store
   - contract_id assigned
   - Both agents notified

4. Messages reference contract_id
   - Broker validates messages against contract
   - Ensures schema compliance
```

### Message Routing

```
1. Source agent sends message with contract_id

2. Broker validates message
   - Check authentication
   - Verify contract exists and is valid
   - Validate payload against contract schema

3. Broker routes message to target agent
   - Lookup target agent endpoint
   - Deliver message (sync or async)

4. Target agent processes and responds
   - Response includes same contract_id
   - Response payload validated against contract

5. Broker routes response to source agent
```

---

## Versioning

### Protocol Versioning

- Protocol version follows semantic versioning: `MAJOR.MINOR`
- Current version: `1.0`
- Backward compatibility: Support N-1 major versions

### Agent Versioning

- Agent version follows semantic versioning: `MAJOR.MINOR.PATCH`
- Capability schemas versioned independently
- Breaking changes require major version bump

### Compatibility Rules

1. **Same major version**: Full compatibility
2. **Different major versions**: Broker attempts compatibility translation
3. **Incompatible versions**: Contract validation fails with `SCHEMA_MISMATCH`

---

## Performance Requirements

### Message Size Limits

- **Maximum message size**: 1 MB
- **Maximum payload size**: 900 KB (to allow for headers)
- **Recommended message size**: <100 KB (for best performance)

### Timeout Values

- **Handshake timeout**: 5 seconds
- **Contract validation timeout**: 2 seconds
- **Message routing timeout**: 30 seconds (default, configurable per intent)
- **Sandbox execution timeout**: 60 seconds (default, configurable)

### Rate Limits

- **Per agent**: 1000 messages/minute (default)
- **Per collaboration**: 100 messages/minute
- **Global**: 10,000 messages/minute (broker capacity)

---

## Security Considerations

### Encryption

- **TLS**: All transport encrypted with TLS 1.3
- **Payload encryption**: Optional AES-256 for sensitive data
  - Set `security.encryption = "aes256"`
  - Keys exchanged during handshake

### PII Handling

- Messages containing PII MUST set `security.encryption = "aes256"`
- Contract validator enforces encryption for PII intents
- PII audit log maintained for compliance

### Sandbox Execution

- Untrusted agents MUST execute in Hyperlight sandbox
- Sandbox policy enforced by SandboxExecutionAgent
- No file system or network access (except explicitly allowed)

---

## Examples

### Complete Collaboration Example

See `examples/agent-collaboration-flow.json` for a complete example of:
1. Capability discovery
2. Handshake initiation
3. Contract negotiation and validation
4. Request/response exchange
5. Collaboration termination

### Error Handling Example

See `examples/error-handling-flow.json` for examples of:
1. Authentication failures
2. Schema mismatches
3. Timeouts
4. Rate limit errors

---

## References

- **Design Document**: docs/designs/agent-protocol-bridge-design.md
- **Architecture Document**: docs/architecture/agent-protocol-bridge-architecture.md
- **Feature Specification**: docs/concepts/inital-agents-a2a-features.md (Feature 7)

---

*This protocol specification defines the contract for all agent-to-agent communication in the a_domain platform.*
