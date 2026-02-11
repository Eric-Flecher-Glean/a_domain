# Glean Agent Registry Usage Guide

**Version:** 1.0.0
**Last Updated:** 2026-02-11
**Purpose:** How to discover, validate, and invoke Glean agents using the Agent Registry

---

## Table of Contents

1. [Overview](#overview)
2. [Exception Classes](#exception-classes)
3. [Quick Start](#quick-start)
4. [Agent Discovery Workflows](#agent-discovery-workflows)
5. [Agent Invocation Patterns](#agent-invocation-patterns)
   - [Pattern 1: Basic Invocation](#pattern-1-basic-invocation)
   - [Pattern 2: Invocation with Context](#pattern-2-invocation-with-context)
   - [Pattern 3: Validated Invocation](#pattern-3-validated-invocation)
   - [Pattern 4: Workflow Chain](#pattern-4-workflow-chain-multi-agent)
6. [Input/Output Schema Validation](#inputoutput-schema-validation)
7. [Error Handling](#error-handling)
8. [Integration with Domain Registry](#integration-with-domain-registry)
9. [Best Practices](#best-practices)
10. [FAQ](#faq)
11. [Related Documentation](#related-documentation)
12. [Appendix: Registry Schema](#appendix-registry-schema)

---

## Overview

The **Glean Agent Registry** ([AGENT-REGISTRY.yaml](./AGENT-REGISTRY.yaml)) is a comprehensive catalog of 52+ production-ready Glean agents organized by domain. This guide shows you how to:

1. **Discover** available agents for your use case
2. **Validate** agent names and capabilities
3. **Invoke** agents using the correct parameters
4. **Integrate** agents into your workflows

---

## Exception Classes

For production use, import these custom exception classes for proper error handling:

```python
"""Custom exception classes for Glean Agent Registry operations."""


class AgentRegistryError(Exception):
    """Base exception for all agent registry operations."""
    pass


class AgentNotFoundError(AgentRegistryError):
    """Raised when an agent cannot be found in the registry."""
    def __init__(self, agent_name, domain=None):
        self.agent_name = agent_name
        self.domain = domain
        if domain:
            msg = f"Agent '{agent_name}' not found in domain '{domain}'"
        else:
            msg = f"Agent '{agent_name}' not found in registry"
        super().__init__(msg)


class RegistryLoadError(AgentRegistryError):
    """Raised when the registry file cannot be loaded."""
    def __init__(self, file_path, original_error):
        self.file_path = file_path
        self.original_error = original_error
        msg = f"Failed to load registry from '{file_path}': {original_error}"
        super().__init__(msg)


class AgentStatusError(AgentRegistryError):
    """Raised when agent status is invalid for invocation."""
    def __init__(self, agent_name, status):
        self.agent_name = agent_name
        self.status = status
        msg = f"Agent '{agent_name}' cannot be invoked (status: {status})"
        super().__init__(msg)


class AgentInvocationError(AgentRegistryError):
    """Raised when agent invocation fails."""
    def __init__(self, agent_name, original_error):
        self.agent_name = agent_name
        self.original_error = original_error
        msg = f"Failed to invoke agent '{agent_name}': {original_error}"
        super().__init__(msg)


class SchemaValidationError(AgentRegistryError):
    """Raised when response doesn't match expected output schema."""
    def __init__(self, agent_name, missing_properties):
        self.agent_name = agent_name
        self.missing_properties = missing_properties
        msg = f"Response from '{agent_name}' missing properties: {', '.join(missing_properties)}"
        super().__init__(msg)


class RequiredActionError(AgentRegistryError):
    """Raised when required actions are not configured."""
    def __init__(self, agent_name, missing_actions):
        self.agent_name = agent_name
        self.missing_actions = missing_actions
        msg = f"Agent '{agent_name}' requires unconfigured actions: {', '.join(missing_actions)}"
        super().__init__(msg)
```

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
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
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

    logger.info(f"Successfully invoked agent. Response keys: {response.keys()}")

except AgentInvocationError as e:
    logger.error(f"Agent invocation failed: {e}")
    raise
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    raise AgentInvocationError("Extract Common Pain Points", e)
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
import logging

logger = logging.getLogger(__name__)

def invoke_agent_basic(agent_name, message):
    """Invoke agent with basic error handling."""
    try:
        client = MCPClient()

        # Simple message with no context
        response = client.call_tool(
            "mcp__glean__chat",
            {
                "agent": agent_name,
                "message": message
            }
        )

        logger.info(f"Agent '{agent_name}' invoked successfully")
        return response

    except ConnectionError as e:
        logger.error(f"MCP connection failed: {e}")
        raise AgentInvocationError(agent_name, e)
    except Exception as e:
        logger.error(f"Unexpected error invoking '{agent_name}': {e}")
        raise AgentInvocationError(agent_name, e)


# Usage
try:
    response = invoke_agent_basic(
        "Customer Sentiment Scorer",
        "Assess sentiment for Memorial Hospital account"
    )
    print(response)
except AgentInvocationError as e:
    print(f"Failed to invoke agent: {e}")
```

### Pattern 2: Invocation with Context

```python
import logging

logger = logging.getLogger(__name__)

def invoke_agent_with_context(agent_name, message, context):
    """Invoke agent with context and error handling."""
    try:
        # Validate context format
        if not isinstance(context, list):
            raise ValueError("Context must be a list of strings")

        if not all(isinstance(item, str) for item in context):
            raise ValueError("All context items must be strings")

        client = MCPClient()

        # Message with additional context parameters
        response = client.call_tool(
            "mcp__glean__chat",
            {
                "agent": agent_name,
                "message": message,
                "context": context
            }
        )

        logger.info(f"Agent '{agent_name}' invoked with {len(context)} context params")
        return response

    except ValueError as e:
        logger.error(f"Invalid context format: {e}")
        raise
    except Exception as e:
        logger.error(f"Failed to invoke agent '{agent_name}': {e}")
        raise AgentInvocationError(agent_name, e)


# Usage
try:
    response = invoke_agent_with_context(
        "Extract Common Pain Points",
        "Extract pain points from Q1 sales calls",
        [
            "industry: healthcare",
            "timeframe: Q1 2026",
            "segment: enterprise"
        ]
    )
except (ValueError, AgentInvocationError) as e:
    logger.error(f"Invocation failed: {e}")
```

### Pattern 3: Validated Invocation

```python
import yaml
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def load_registry(registry_path='docs/glean/AGENT-REGISTRY.yaml'):
    """Load registry with error handling."""
    try:
        path = Path(registry_path)
        if not path.exists():
            raise FileNotFoundError(f"Registry file not found: {registry_path}")

        with open(path, 'r') as f:
            registry = yaml.safe_load(f)

        if not registry:
            raise ValueError("Registry file is empty")

        logger.info(f"Loaded registry from {registry_path}")
        return registry

    except yaml.YAMLError as e:
        raise RegistryLoadError(registry_path, e)
    except Exception as e:
        raise RegistryLoadError(registry_path, e)


def get_agent_spec(registry, agent_name, domain=None):
    """Find agent spec in registry with error handling."""
    try:
        if domain:
            # Search specific domain
            if domain not in registry:
                raise AgentNotFoundError(agent_name, domain)

            domain_agents = registry.get(domain, {}).get('agents', [])
            for agent in domain_agents:
                if agent['name'] == agent_name:
                    logger.info(f"Found agent '{agent_name}' in domain '{domain}'")
                    return agent
        else:
            # Search all domains
            for domain_key in registry:
                if domain_key in ['metadata', 'statistics', 'usage_guidelines', 'references']:
                    continue
                domain_agents = registry[domain_key].get('agents', [])
                for agent in domain_agents:
                    if agent['name'] == agent_name:
                        logger.info(f"Found agent '{agent_name}' in domain '{domain_key}'")
                        return agent

        raise AgentNotFoundError(agent_name, domain)

    except AgentNotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error searching registry: {e}")
        raise AgentRegistryError(f"Failed to search registry: {e}")


def validate_agent_status(agent_spec):
    """Validate agent is active and ready to invoke."""
    agent_name = agent_spec['name']
    status = agent_spec.get('status', 'unknown')

    if status != 'active':
        raise AgentStatusError(agent_name, status)

    logger.info(f"Agent '{agent_name}' is active")


def invoke_validated_agent(agent_spec, message, context=None):
    """Invoke agent after validation."""
    agent_name = agent_spec['name']

    try:
        client = MCPClient()

        params = {
            "agent": agent_name,
            "message": message
        }

        if context:
            params["context"] = context

        response = client.call_tool("mcp__glean__chat", params)

        # Validate output matches expected schema
        validate_output_schema(response, agent_spec)

        logger.info(f"Successfully invoked and validated '{agent_name}'")
        return response

    except Exception as e:
        raise AgentInvocationError(agent_name, e)


def validate_output_schema(response, agent_spec):
    """Validate response matches agent output schema."""
    agent_name = agent_spec['name']
    schema = agent_spec.get('output_schema', {})

    if not schema or 'properties' not in schema:
        logger.warning(f"No output schema defined for '{agent_name}'")
        return

    expected_keys = schema['properties'].keys()
    missing_keys = [key for key in expected_keys if key not in response]

    if missing_keys:
        logger.warning(f"Missing keys in response from '{agent_name}': {missing_keys}")
        # Note: Warning only, not raising exception as optional fields may be missing
    else:
        logger.info(f"Output schema validated for '{agent_name}'")


# Complete workflow with error handling
try:
    # Load registry
    registry = load_registry()

    # Find and validate agent
    agent_name = "Extract Common Pain Points"
    agent_spec = get_agent_spec(registry, agent_name, domain='sales_enablement')

    # Check status
    validate_agent_status(agent_spec)

    # Invoke with validation
    response = invoke_validated_agent(
        agent_spec,
        "Extract pain points from Q1 sales calls",
        context=["industry: healthcare"]
    )

    print(f"Success: {response}")

except RegistryLoadError as e:
    logger.error(f"Registry load failed: {e}")
    logger.error(f"Original error: {e.original_error}")
except AgentNotFoundError as e:
    logger.error(f"Agent not found: {e}")
    logger.info(f"Available domains: {list(registry.keys())}")
except AgentStatusError as e:
    logger.error(f"Agent status invalid: {e}")
    logger.info(f"Try auto-routing instead")
except AgentInvocationError as e:
    logger.error(f"Invocation failed: {e}")
    logger.error(f"Original error: {e.original_error}")
except Exception as e:
    logger.error(f"Unexpected error: {e}")
```

### Pattern 4: Workflow Chain (Multi-Agent)

```python
import logging

logger = logging.getLogger(__name__)

def run_agent_workflow(workflow_steps):
    """Execute multi-agent workflow with error handling and state tracking."""
    results = {}
    completed_steps = []

    try:
        client = MCPClient()

        for step_name, step_config in workflow_steps.items():
            logger.info(f"Executing step: {step_name}")

            try:
                # Prepare parameters (may reference previous results)
                params = {
                    "agent": step_config['agent'],
                    "message": step_config['message'].format(**results)
                }

                if 'context' in step_config:
                    # Format context with previous results
                    params['context'] = [
                        ctx.format(**results) for ctx in step_config['context']
                    ]

                # Invoke agent
                response = client.call_tool("mcp__glean__chat", params)

                # Store result
                results[step_name] = response
                completed_steps.append(step_name)

                logger.info(f"Step '{step_name}' completed successfully")

            except Exception as e:
                logger.error(f"Step '{step_name}' failed: {e}")
                raise AgentInvocationError(step_config['agent'], e)

        logger.info(f"Workflow completed: {len(completed_steps)} steps")
        return results

    except Exception as e:
        logger.error(f"Workflow failed after {len(completed_steps)} steps: {completed_steps}")
        raise


# Define workflow
workflow = {
    "extract_pain_points": {
        "agent": "Extract Common Pain Points",
        "message": "Extract pain points from Q1 healthcare sales calls"
    },
    "generate_strategy": {
        "agent": "Deal Strategy",
        "message": "Generate deal strategy addressing these pain points: {extract_pain_points[pain_points]}",
        "context": ["opportunity_id: OPP-12345"]
    },
    "find_references": {
        "agent": "Find Potential Customer References",
        "message": "Find references that addressed similar pain points",
        "context": [
            "industry: healthcare",
            "use_case: {extract_pain_points[pain_points][0][description]}"
        ]
    }
}

# Execute workflow with error handling
try:
    results = run_agent_workflow(workflow)

    pain_points = results['extract_pain_points']
    strategy = results['generate_strategy']
    references = results['find_references']

    logger.info("Workflow completed successfully")
    logger.info(f"Pain points: {len(pain_points.get('pain_points', []))}")
    logger.info(f"Strategy: {strategy.get('summary', 'N/A')}")
    logger.info(f"References: {len(references.get('references', []))}")

except AgentInvocationError as e:
    logger.error(f"Agent invocation failed in workflow: {e}")
    logger.info("Consider implementing retry logic or fallback agents")
except KeyError as e:
    logger.error(f"Missing expected key in workflow results: {e}")
    logger.info("Check agent output schemas match workflow expectations")
except Exception as e:
    logger.error(f"Unexpected workflow error: {e}")
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
import logging

logger = logging.getLogger(__name__)

def validate_response(response, agent_spec):
    """Validate response matches agent output schema with comprehensive error handling."""
    agent_name = agent_spec.get('name', 'Unknown')

    try:
        schema = agent_spec.get('output_schema')

        if not schema:
            logger.warning(f"No output schema defined for agent '{agent_name}'")
            return True

        # Check type
        expected_type = schema.get('type', 'object')
        if expected_type == 'object' and not isinstance(response, dict):
            raise SchemaValidationError(
                agent_name,
                [f"Expected object response, got {type(response).__name__}"]
            )

        # Check required properties
        properties = schema.get('properties', {})
        missing_props = []

        for prop in properties:
            if prop not in response:
                missing_props.append(prop)

        if missing_props:
            logger.warning(f"Missing properties in '{agent_name}' response: {missing_props}")
            # Note: Some properties may be optional, so warning instead of error

        logger.info(f"Response validated for agent '{agent_name}'")
        return True

    except SchemaValidationError:
        raise
    except Exception as e:
        logger.error(f"Validation error for agent '{agent_name}': {e}")
        raise AgentRegistryError(f"Schema validation failed: {e}")


# Use validation with error handling
try:
    is_valid = validate_response(response, agent_spec)

    if is_valid:
        logger.info("Response validation passed")
        # Process response
        process_agent_response(response)

except SchemaValidationError as e:
    logger.error(f"Schema validation failed: {e}")
    logger.error(f"Missing properties: {e.missing_properties}")
    # Handle validation failure (e.g., retry, use partial data, alert)
except AgentRegistryError as e:
    logger.error(f"Validation error: {e}")
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
import logging

logger = logging.getLogger(__name__)

# ❌ BAD: Hard-coded string with no validation
try:
    response = client.call_tool("mcp__glean__chat", {
        "agent": "Extract Pain Points",  # Typo, will fail
        "message": "..."
    })
except Exception as e:
    logger.error(f"Failed: {e}")
    # No way to recover - agent name was wrong

# ✅ GOOD: Load from registry and validate
try:
    registry = load_registry()
    agent_spec = get_agent_spec(registry, "Extract Common Pain Points")

    if not agent_spec:
        raise AgentNotFoundError("Extract Common Pain Points")

    validate_agent_status(agent_spec)

    response = client.call_tool("mcp__glean__chat", {
        "agent": agent_spec['name'],
        "message": "..."
    })

    logger.info(f"Successfully invoked '{agent_spec['name']}'")

except AgentNotFoundError as e:
    logger.error(f"Agent not found: {e}")
    # Could fall back to auto-routing or suggest similar agents
    logger.info("Falling back to auto-routing mode")
    response = client.call_tool("mcp__glean__chat", {
        "message": "..."  # Let Glean auto-select agent
    })
except AgentStatusError as e:
    logger.error(f"Agent not active: {e}")
    # Handle deprecated/experimental agents
except AgentInvocationError as e:
    logger.error(f"Invocation failed: {e}")
```

### 2. Check Agent Status

```python
import logging

logger = logging.getLogger(__name__)

def invoke_with_status_check(agent_spec, message, context=None):
    """Invoke agent only if status is active, with fallback handling."""
    agent_name = agent_spec['name']
    status = agent_spec.get('status', 'unknown')

    try:
        # Check status
        if status != 'active':
            logger.warning(f"Agent '{agent_name}' status is '{status}', falling back to auto-routing")
            raise AgentStatusError(agent_name, status)

        # Invoke active agent
        client = MCPClient()
        params = {"agent": agent_name, "message": message}

        if context:
            params["context"] = context

        response = client.call_tool("mcp__glean__chat", params)
        logger.info(f"Successfully invoked active agent '{agent_name}'")
        return response

    except AgentStatusError:
        # Fall back to auto-routing
        logger.info("Attempting auto-routing as fallback")
        try:
            params = {"message": message}
            if context:
                params["context"] = context

            response = client.call_tool("mcp__glean__chat", params)
            logger.info("Auto-routing succeeded")
            return response

        except Exception as e:
            logger.error(f"Auto-routing also failed: {e}")
            raise AgentInvocationError("auto-routing", e)


# Usage
try:
    response = invoke_with_status_check(
        agent_spec,
        "Extract pain points from Q1 sales calls",
        context=["industry: healthcare"]
    )
except AgentInvocationError as e:
    logger.error(f"All invocation methods failed: {e}")
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

Track agent usage and performance with comprehensive metrics:

```python
import time
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class AgentMetrics:
    """Track agent invocation metrics."""

    def __init__(self):
        self.invocations = []

    def record_invocation(self, agent_name, duration, status, error=None):
        """Record agent invocation metrics."""
        metric = {
            "agent": agent_name,
            "timestamp": datetime.now().isoformat(),
            "duration_seconds": duration,
            "status": status,
            "error": str(error) if error else None
        }
        self.invocations.append(metric)
        logger.info(f"Recorded metric: {metric}")

    def get_summary(self):
        """Get summary of agent performance."""
        if not self.invocations:
            return {"total": 0}

        total = len(self.invocations)
        successful = sum(1 for m in self.invocations if m['status'] == 'success')
        failed = total - successful
        avg_duration = sum(m['duration_seconds'] for m in self.invocations) / total

        return {
            "total_invocations": total,
            "successful": successful,
            "failed": failed,
            "success_rate": successful / total * 100,
            "avg_duration_seconds": avg_duration
        }


# Initialize metrics tracker
metrics = AgentMetrics()

def invoke_with_metrics(agent_name, message, context=None):
    """Invoke agent and track performance metrics."""
    start_time = time.time()
    status = "failed"
    error = None

    try:
        client = MCPClient()

        params = {"agent": agent_name, "message": message}
        if context:
            params["context"] = context

        response = client.call_tool("mcp__glean__chat", params)

        status = "success"
        duration = time.time() - start_time

        logger.info(f"Agent '{agent_name}' completed in {duration:.2f}s")
        return response

    except Exception as e:
        error = e
        logger.error(f"Agent '{agent_name}' failed: {e}")
        raise AgentInvocationError(agent_name, e)

    finally:
        duration = time.time() - start_time
        metrics.record_invocation(agent_name, duration, status, error)


# Usage
try:
    response = invoke_with_metrics(
        "Extract Common Pain Points",
        "Extract pain points from Q1 sales calls",
        context=["industry: healthcare"]
    )

    # Periodically log summary
    summary = metrics.get_summary()
    logger.info(f"Agent metrics summary: {summary}")

except AgentInvocationError as e:
    logger.error(f"Invocation failed: {e}")

    # Check if this agent has reliability issues
    summary = metrics.get_summary()
    if summary.get('success_rate', 100) < 80:
        logger.warning(f"Agent success rate below 80%: {summary['success_rate']:.1f}%")
        logger.warning("Consider switching to alternative agent or auto-routing")
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
