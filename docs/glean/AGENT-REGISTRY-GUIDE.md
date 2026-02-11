# Glean Agent Registry Usage Guide

**Version:** 1.0.0
**Last Updated:** 2026-02-11
**Purpose:** How to discover, validate, and invoke Glean agents using the Agent Registry

---

## Overview

The **Glean Agent Registry** ([AGENT-REGISTRY.yaml](./AGENT-REGISTRY.yaml)) is a comprehensive catalog of 52+ production-ready Glean agents organized by domain. This guide shows you how to:

1. **Discover** available agents for your use case
2. **Validate** agent names and capabilities
3. **Invoke** agents using the correct parameters
4. **Integrate** agents into your workflows

---

## Quick Start

### 1. Browse Available Agents

```bash
# View all agents
cat docs/glean/AGENT-REGISTRY.yaml

# Search for specific domain
grep -A 20 "sales_enablement:" docs/glean/AGENT-REGISTRY.yaml
```

### 2. Find Agent by Use Case

| Use Case | Agent Name | Domain |
|----------|------------|--------|
| Analyze customer pain points | `Extract Common Pain Points` | Sales Enablement |
| Generate deal strategies | `Deal Strategy` | Sales Enablement |
| Review pull requests | `Pull Request Review` | SDLC/Engineering |
| Debug CI/CD failures | `CI/CD GitHub Logs Debugger` | SDLC/Engineering |
| Assess customer sentiment | `Customer Sentiment Scorer` | Customer Support |
| Extract meeting action items | `Extract Meeting Action Items` | Productivity |
| Generate work summaries | `Weekly Work Report` | Productivity |

### 3. Invoke Agent

```python
from mcp_client import MCPClient

client = MCPClient()

# Explicit invocation (recommended for production)
response = client.call_tool(
    "mcp__glean__chat",
    {
        "agent": "Extract Common Pain Points",  # From registry
        "message": "Extract pain points from Q1 sales calls",
        "context": ["industry: healthcare", "timeframe: Q1 2026"]
    }
)
```

---

## Agent Discovery Workflows

### Workflow 1: Browse by Domain

**Step 1:** Identify your domain in the registry:

- `sales_enablement` - Deal management, prospecting, customer intelligence
- `sdlc_engineering` - Code review, CI/CD, implementation automation
- `customer_support` - Ticket management, sentiment analysis, customer 360
- `knowledge_management` - Documentation, Q&A chatbots, KB articles
- `journey_orchestration` - Meeting summaries, work reports, action items

**Step 2:** Review agents in that domain:

```yaml
# Example: SDLC/Engineering domain
sdlc_engineering:
  agents:
    - name: "Pull Request Review"
      description: "Performs comprehensive code review..."
      capabilities:
        - Code quality assessment
        - Security vulnerability detection
```

**Step 3:** Check agent status and deployment:

```yaml
status: active  # Must be 'active' to use
deployed_customers: 222
avg_weekly_runs: 550000
```

### Workflow 2: Search by Capability

```bash
# Find all agents with agentic looping
grep -B 5 "Agentic looping enabled" docs/glean/AGENT-REGISTRY.yaml

# Find agents that integrate multiple data sources
grep -B 3 "Multi-source" docs/glean/AGENT-REGISTRY.yaml

# Find agents requiring specific actions
grep -B 5 "required_actions:" docs/glean/AGENT-REGISTRY.yaml
```

### Workflow 3: Match by Data Source

```bash
# Find agents that access Gong
grep -B 10 "Gong" docs/glean/AGENT-REGISTRY.yaml

# Find agents that access Salesforce
grep -B 10 "Salesforce" docs/glean/AGENT-REGISTRY.yaml
```

---

## Agent Invocation Patterns

### Pattern 1: Basic Invocation

```python
from mcp_client import MCPClient

client = MCPClient()

# Simple message with no context
response = client.call_tool(
    "mcp__glean__chat",
    {
        "agent": "Customer Sentiment Scorer",
        "message": "Assess sentiment for Memorial Hospital account"
    }
)

print(response)
```

### Pattern 2: Invocation with Context

```python
# Message with additional context parameters
response = client.call_tool(
    "mcp__glean__chat",
    {
        "agent": "Extract Common Pain Points",
        "message": "Extract pain points from Q1 sales calls",
        "context": [
            "industry: healthcare",
            "timeframe: Q1 2026",
            "segment: enterprise"
        ]
    }
)
```

### Pattern 3: Validated Invocation

```python
import yaml

# Load registry
with open('docs/glean/AGENT-REGISTRY.yaml', 'r') as f:
    registry = yaml.safe_load(f)

def get_agent_spec(agent_name, domain=None):
    """Find agent spec in registry."""
    if domain:
        # Search specific domain
        domain_agents = registry.get(domain, {}).get('agents', [])
        for agent in domain_agents:
            if agent['name'] == agent_name:
                return agent
    else:
        # Search all domains
        for domain_key in registry:
            if domain_key in ['metadata', 'statistics', 'usage_guidelines', 'references']:
                continue
            domain_agents = registry[domain_key].get('agents', [])
            for agent in domain_agents:
                if agent['name'] == agent_name:
                    return agent
    return None

# Validate before invoking
agent_name = "Extract Common Pain Points"
agent_spec = get_agent_spec(agent_name, domain='sales_enablement')

if not agent_spec:
    raise ValueError(f"Agent '{agent_name}' not found in registry")

if agent_spec['status'] != 'active':
    raise ValueError(f"Agent '{agent_name}' is not active (status: {agent_spec['status']})")

# Invoke validated agent
response = client.call_tool(
    "mcp__glean__chat",
    {
        "agent": agent_spec['name'],
        "message": "Extract pain points from Q1 sales calls",
        "context": ["industry: healthcare"]
    }
)

# Validate output matches expected schema
expected_keys = agent_spec['output_schema']['properties'].keys()
for key in expected_keys:
    if key not in response:
        print(f"Warning: Expected key '{key}' missing from response")
```

### Pattern 4: Workflow Chain (Multi-Agent)

```python
# Step 1: Extract pain points
pain_points_response = client.call_tool(
    "mcp__glean__chat",
    {
        "agent": "Extract Common Pain Points",
        "message": "Extract pain points from Q1 healthcare sales calls"
    }
)

# Step 2: Generate deal strategy based on pain points
deal_strategy_response = client.call_tool(
    "mcp__glean__chat",
    {
        "agent": "Deal Strategy",
        "message": f"Generate deal strategy addressing these pain points: {pain_points_response['pain_points']}",
        "context": ["opportunity_id: OPP-12345"]
    }
)

# Step 3: Find customer references
references_response = client.call_tool(
    "mcp__glean__chat",
    {
        "agent": "Find Potential Customer References",
        "message": "Find references that addressed similar pain points",
        "context": [
            "industry: healthcare",
            f"use_case: {pain_points_response['pain_points'][0]['description']}"
        ]
    }
)
```

---

## Input/Output Schema Validation

### Understanding Input Schemas

Each agent in the registry defines its expected inputs:

```yaml
input_schema:
  message:
    type: string
    required: true
    example: "Extract pain points from Q1 sales calls"
  context:
    type: array
    required: false
    items:
      - industry: string
      - timeframe: string
```

**Best Practices:**
- Always provide the `message` parameter (required)
- Use `context` for filtering and scoping (optional but recommended)
- Match context parameter names to schema (e.g., `industry`, `timeframe`)
- Check `example` field for proper formatting

### Understanding Output Schemas

Output schemas define the structure of agent responses:

```yaml
output_schema:
  type: object
  properties:
    pain_points:
      type: array
      items:
        description: string
        frequency: enum[high, medium, low]
        impact: string
        source: string
        customer: string
    summary: string
    recommendations: array[string]
```

**Validation Example:**

```python
def validate_response(response, agent_spec):
    """Validate response matches agent output schema."""
    schema = agent_spec['output_schema']

    # Check type
    if schema['type'] == 'object' and not isinstance(response, dict):
        raise ValueError("Expected object response")

    # Check required properties
    for prop in schema['properties']:
        if prop not in response:
            print(f"Warning: Missing property '{prop}' in response")

    return True

# Use validation
validate_response(response, agent_spec)
```

---

## Error Handling

### Common Errors

**1. Agent Not Found**

```python
# Error: Unknown agent name
response = client.call_tool(
    "mcp__glean__chat",
    {
        "agent": "Extract Pain Point",  # ❌ Wrong name (missing 's')
        "message": "..."
    }
)
# Result: Error or auto-routing fallback

# Fix: Use exact name from registry
response = client.call_tool(
    "mcp__glean__chat",
    {
        "agent": "Extract Common Pain Points",  # ✅ Correct
        "message": "..."
    }
)
```

**2. Invalid Context Parameters**

```python
# Error: Incorrect context format
response = client.call_tool(
    "mcp__glean__chat",
    {
        "agent": "Extract Common Pain Points",
        "message": "Extract pain points",
        "context": "industry=healthcare"  # ❌ Wrong format
    }
)

# Fix: Use array of strings
response = client.call_tool(
    "mcp__glean__chat",
    {
        "agent": "Extract Common Pain Points",
        "message": "Extract pain points",
        "context": ["industry: healthcare"]  # ✅ Correct
    }
)
```

**3. Missing Required Actions**

Some agents require specific actions to be configured (e.g., GitHub PR creation, document generation).

```yaml
# Check registry for required_actions
required_actions:
  - GitHub PR creation
  - AI coding assistant
```

Ensure these integrations are set up before invoking the agent.

---

## Integration with Domain Registry

When registering agents in the Platform.Registry, reference the Glean Agent Registry:

```yaml
# Platform.Registry - Agent Registration
bounded_contexts:
  SDLC.RequirementsManagement:
    agents:
      - agent_id: "pain-point-analyzer-v1"
        name: "Pain Point Analyzer"
        description: "Analyzes customer pain points for requirements prioritization"

        implementation:
          type: "glean_mcp_agent"
          glean_agent_ref: "Extract Common Pain Points"  # Links to AGENT-REGISTRY.yaml
          mode: "explicit"  # or "auto_routing"

        input_schema:
          # Inherit from Glean agent + add domain-specific fields
          extends: "glean://sales_enablement/Extract Common Pain Points/input_schema"
          additional_fields:
            priority_threshold: number

        output_schema:
          # Inherit from Glean agent
          extends: "glean://sales_enablement/Extract Common Pain Points/output_schema"
```

---

## Best Practices

### 1. Always Validate Agent Names

```python
# ❌ BAD: Hard-coded string with no validation
response = client.call_tool("mcp__glean__chat", {
    "agent": "Extract Pain Points",  # Typo, will fail
    "message": "..."
})

# ✅ GOOD: Load from registry and validate
agent_spec = get_agent_spec("Extract Common Pain Points")
if not agent_spec:
    raise ValueError("Agent not found")

response = client.call_tool("mcp__glean__chat", {
    "agent": agent_spec['name'],
    "message": "..."
})
```

### 2. Check Agent Status

```python
# Only invoke active agents
if agent_spec['status'] != 'active':
    # Fall back to auto-routing or alternative agent
    response = client.call_tool("mcp__glean__chat", {
        "message": "..."  # Let Glean auto-route
    })
```

### 3. Use Example Invocations

Each agent includes an `example_invocation` field:

```yaml
example_invocation:
  agent: "Extract Common Pain Points"
  message: "Extract pain points from Q1 sales calls"
  context:
    - "industry: healthcare"
    - "timeframe: Q1 2026"
```

Use this as a template for your invocations.

### 4. Document Agent Selection

When using explicit agent invocation in production code, document why that agent was chosen:

```python
# Pain point analysis for healthcare vertical
# Using "Extract Common Pain Points" because:
# - Multi-source data integration (Gong, HubSpot, Salesforce)
# - Agentic looping for iterative refinement
# - Industry-specific pattern recognition
# See: docs/glean/AGENT-REGISTRY.yaml#sales_enablement
response = client.call_tool("mcp__glean__chat", {
    "agent": "Extract Common Pain Points",
    "message": "..."
})
```

### 5. Monitor Agent Performance

Track agent usage and performance:

```python
import time

start_time = time.time()

response = client.call_tool("mcp__glean__chat", {
    "agent": "Extract Common Pain Points",
    "message": "..."
})

duration = time.time() - start_time

# Log metrics
logger.info(f"Agent: Extract Common Pain Points, Duration: {duration}s, Status: success")
```

---

## FAQ

**Q: What happens if I specify an invalid agent name?**

A: Behavior depends on Glean platform configuration. It may:
- Return an error
- Fall back to auto-routing mode
- Suggest similar agent names

Always validate against the registry to avoid runtime issues.

**Q: Can I add custom agents to the registry?**

A: Yes, if you build custom Glean agents in your organization:

1. Add agent spec to appropriate domain section in AGENT-REGISTRY.yaml
2. Follow the same schema structure as existing agents
3. Set `status: experimental` until validated in production
4. Update `metadata.total_agents` count

**Q: How often is the registry updated?**

A: Update the registry when:
- New Glean agents are deployed to your organization
- Existing agents are deprecated or updated
- Agent capabilities or schemas change

Check `metadata.last_updated` for registry version.

**Q: Should I use explicit invocation or auto-routing?**

A: **Recommendation:**

- **Development/Exploration:** Use auto-routing (no `agent` parameter)
- **Production/Workflows:** Use explicit invocation (validate against registry)
- **Conversational UI:** Use auto-routing (user intent unpredictable)
- **Deterministic Pipelines:** Use explicit invocation (consistent behavior)

**Q: What if an agent requires actions I haven't configured?**

A: Check the `required_actions` field in the agent spec:

```yaml
required_actions:
  - GitHub PR creation
  - AI coding assistant
```

Ensure these integrations are set up in your Glean platform before invoking.

---

## Related Documentation

- [CORE-PRINCIPLES.md](../architecture/CORE-PRINCIPLES.md) - LLM compute principle with Glean MCP patterns
- [AGENT-REGISTRY.yaml](./AGENT-REGISTRY.yaml) - Complete agent catalog
- [glean-mcp-agent-pattern.md](../guides/glean-mcp-agent-pattern.md) - Glean MCP integration guide
- [ARCHITECTURE-REVIEW-CHECKLIST.md](../architecture/ARCHITECTURE-REVIEW-CHECKLIST.md) - Agent name validation rules

---

## Appendix: Registry Schema

### Agent Entry Structure

```yaml
- name: string              # Exact agent name (case-sensitive)
  id: string                # Unique identifier
  status: enum              # active | deprecated | experimental
  deployed_customers: int   # Number of customers using this agent (optional)
  avg_weekly_runs: int      # Average runs per week (optional)

  description: string       # What the agent does

  capabilities: array       # Key features/capabilities
    - string

  data_sources: array       # Integrated data sources
    - string

  required_actions: array   # Actions that must be configured (optional)
    - string

  input_schema: object      # Expected input structure
    message: object
    context: object

  output_schema: object     # Expected output structure
    type: string
    properties: object

  example_invocation: object  # Example usage
    agent: string
    message: string
    context: array

  use_cases: array          # Common use cases (optional)
    - string
```

---

**Last Updated:** 2026-02-11
**Registry Version:** 1.0.0
**Total Agents:** 52
