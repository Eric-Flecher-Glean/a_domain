# Core Architectural Principles

**Version:** 1.0
**Last Updated:** 2026-02-11
**Status:** Active

---

## Overview

This document defines **non-negotiable architectural constraints** that apply to all features, components, and implementations within this system. These principles ensure:

- **Security:** Controlled access patterns and audit trails
- **Cost Control:** Centralized resource usage tracking
- **Consistency:** Single source of truth for critical capabilities
- **Compliance:** Regulatory and organizational policy adherence

### Scope

These principles apply to:
- All features (P0, P1, P2+)
- All architecture documents and designs
- All implementation code and configurations
- All third-party integrations

### Violation Policy

**Violations are NOT permitted under any circumstances.**

- ❌ No exceptions granted without executive approval
- ❌ No "temporary" or "prototype" violations
- ❌ No "we'll fix it later" deferrals

All architecture reviews MUST validate compliance using [ARCHITECTURE-REVIEW-CHECKLIST.md](./ARCHITECTURE-REVIEW-CHECKLIST.md).

---

## Principle 1: Centralized LLM Compute via Authenticated Sessions

### Statement

**REQUIRED:** All Large Language Model (LLM) compute operations MUST be executed through one of the following approved patterns:

1. **Glean MCP Chat Tool** (`mcp__glean__chat`)
2. **Claude Code Commands/Agents** (Task tool with appropriate subagent)

**PROHIBITED:** Direct usage of Anthropic API or any other LLM provider APIs is explicitly forbidden.

### Rationale

#### Security
- **No API Key Sprawl:** Eliminates need for ANTHROPIC_API_KEY distribution across services
- **Centralized Access Control:** All LLM access controlled through authenticated platform sessions
- **Audit Trail:** Complete visibility into all LLM usage through platform logs
- **Credential Rotation:** No embedded credentials to rotate or manage

#### Cost Control
- **Usage Tracking:** All LLM calls tracked through authenticated user sessions
- **Budget Enforcement:** Platform-level controls prevent runaway costs
- **Attribution:** Usage directly attributed to users/sessions for accountability

#### Reliability
- **Managed Infrastructure:** Platform handles rate limiting, retries, failover
- **No Client-Side Failures:** No network issues from direct API calls
- **Consistent Performance:** SLA-backed service availability

#### Consistency
- **Single Integration Point:** One pattern for all LLM needs
- **Standardized Interfaces:** Uniform tool calling across features
- **Simplified Maintenance:** Updates to LLM capabilities handled at platform level

### Approved Pattern 1: Glean MCP Chat

**Use Case:** Analyze, synthesize, or reason about enterprise knowledge with LLM capabilities.

**Implementation:**

```yaml
# In agent configuration
agent_invocation:
  tool: mcp__glean__chat
  message: "Analyze the requirements document and extract user stories"
  context:
    - "Previous conversation context if needed"
```

**Example - Requirements Analysis:**

```yaml
# sdlc/requirements/analyze-requirements.yaml
analysis_step:
  tool: mcp__glean__chat
  message: |
    Extract functional requirements from this product specification:

    {document_content}

    Format as YAML with:
    - requirement_id
    - description
    - acceptance_criteria
    - priority
```

**Example - Design Generation:**

```python
# In Python agent
from mcp_client import MCPClient

client = MCPClient()
response = client.call_tool(
    "mcp__glean__chat",
    {
        "message": "Generate Figma component specifications for user dashboard",
        "context": [
            "Reference existing design system patterns",
            "Follow Material Design 3 guidelines"
        ]
    }
)
```

#### Two Invocation Modes

Glean MCP supports two modes for agent invocation:

**Mode 1: Explicit Agent Invocation** (Deterministic)

Directly specify which Glean agent to use:

```python
response = client.call_tool(
    "mcp__glean__chat",
    {
        "agent": "Extract Common Pain Points",  # Explicit agent name
        "message": "Extract pain points from Q1 sales calls",
        "context": ["industry: healthcare", "timeframe: Q1 2026"]
    }
)
```

**Agent Discovery:**

Use the [Glean Agent Registry](../glean/AGENT-REGISTRY.yaml) to discover available agents:
- **52+ production-ready agents** organized by domain
- Comprehensive specifications with input/output schemas
- Usage examples and data source integrations
- Agent capabilities and deployment statistics

See [AGENT-REGISTRY-GUIDE.md](../glean/AGENT-REGISTRY-GUIDE.md) for discovery workflows and validation patterns.

**Use when:**
- Building deterministic workflows with known agent sequences
- Agent selection is part of orchestration logic
- Need consistent, repeatable behavior
- Implementing multi-step pipelines (Agent A → Agent B → Agent C)

**Mode 2: Auto-Routing** (Intelligent)

Let Glean's platform analyze the message and route to the best agent:

```python
response = client.call_tool(
    "mcp__glean__chat",
    {
        "message": "Extract pain points from Q1 sales calls",
        "context": ["industry: healthcare", "timeframe: Q1 2026"]
    }
    # No 'agent' parameter - Glean's AI routes automatically
)
```

**Use when:**
- Building conversational interfaces or user-driven queries
- Want Glean's AI to select the most appropriate agent
- Exploratory analysis with unpredictable requests
- Simplifying implementation (fewer decisions in code)

**Recommendation:** Start with Mode 2 (auto-routing) for simplicity. Use Mode 1 (explicit) when you need deterministic workflows or have identified the optimal agent sequence through experimentation.

### Approved Pattern 1B: Glean MCP with XML Prompt Templates

**Use Case:** Structure repeatable invocations of Glean agents using version-controlled XML message templates.

**Note:** XML templates are NOT standalone agents—they format messages sent to Glean agents via `mcp__glean__chat`. All agent capabilities come from the Glean platform.

**Implementation:**

```yaml
# In agent configuration with XML template
agent_invocation:
  tool: mcp__glean__chat
  message_template:
    repository: "sdlc/prompts"
    path: "sdlc/requirements/extract-acceptance-criteria.xml"
    version: "1.0.0"
  inputs:
    user_story: "{story_text}"
```

**Example XML Template Structure** (`sdlc/requirements/extract-acceptance-criteria.xml`):

```xml
<?xml version="1.0" encoding="UTF-8"?>
<prompt>
  <metadata>
    <name>extract-acceptance-criteria</name>
    <version>1.0.0</version>
    <domain>sdlc/requirements</domain>
  </metadata>

  <role>
    You are an expert requirements analyst extracting testable acceptance criteria.
  </role>

  <task>
    Extract clear, testable acceptance criteria from user story text.
    Number each as AC1, AC2, AC3, etc.
  </task>

  <instructions>
    <step1>Read the user story carefully</step1>
    <step2>Identify all requirements (explicit and implicit)</step2>
    <step3>Formulate each as testable criterion</step3>
    <step4>Validate criteria are INVEST compliant</step4>
  </instructions>

  <output_format>
    <section name="Acceptance Criteria">
      AC#: [Description]
      Type: [Functional|Non-functional|Edge Case]
      Priority: [P0|P1|P2]
    </section>
  </output_format>

  <constraints>
    <constraint>Each criterion must be testable</constraint>
    <constraint>Use AC# prefix (AC1, AC2, etc.)</constraint>
    <constraint>Include at least one edge case</constraint>
  </constraints>
</prompt>
```

**Example - Loading and Executing XML Template:**

```python
# Load template from version-controlled repository
from xml_prompt_loader import XMLPromptLoader

template = XMLPromptLoader.load_from_repository(
    repo="../../sdlc/prompts",
    path="sdlc/requirements/extract-acceptance-criteria.xml",
    version="1.0.0"
)

# Format message using template
message = template.format(user_story=story_text)

# Send formatted message to Glean agent via mcp__glean__chat
from mcp_client import MCPClient

client = MCPClient()
response = client.call_tool(
    "mcp__glean__chat",
    {
        "message": message,
        "context": template.context
    }
)
```

**Benefits:**
- **Version Control:** All prompts tracked in Git with semantic versioning
- **Reusability:** Share templates across projects and teams
- **Consistency:** Enforced structure (role, task, instructions, output format)
- **Rapid Iteration:** Edit XML, commit, re-run (no deployment needed)
- **Documentation:** Self-documenting with metadata and examples

**Template Repository:** ../../sdlc/prompts

### Approved Pattern 2: Claude Code Commands

**Use Case:** Execute multi-step agentic tasks requiring file operations, code analysis, or complex workflows.

**Implementation:**

```yaml
# In task orchestration
task_execution:
  tool: Task
  subagent_type: general-purpose
  prompt: |
    Review the API implementation in src/api/ and:
    1. Identify missing error handling
    2. Suggest improvements
    3. Generate test cases
```

**Example - Code Review:**

```python
# In orchestration script
from claude_code import execute_task

result = execute_task(
    subagent_type="general-purpose",
    description="Perform code review",
    prompt="""
    Analyze the authentication module:
    - Check for security vulnerabilities
    - Validate error handling patterns
    - Ensure test coverage > 80%
    """
)
```

**Example - Documentation Generation:**

```bash
# Via CLI
claude-code task \
  --type general-purpose \
  --description "Generate API docs" \
  --prompt "Create OpenAPI spec from FastAPI routes in src/api/"
```

### Prohibited Patterns

The following patterns are **EXPLICITLY FORBIDDEN**:

#### ❌ Anti-Pattern 1: Direct Anthropic API Client

```python
# PROHIBITED - DO NOT USE
from anthropic import Anthropic

client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
message = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Analyze this data"}]
)
```

**Why Prohibited:**
- Requires API key distribution
- No usage tracking or attribution
- Bypasses platform security controls
- No audit trail

#### ❌ Anti-Pattern 2: Environment Variable for API Keys

```yaml
# PROHIBITED - DO NOT USE
environment:
  - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}  # VIOLATION
  - OPENAI_API_KEY=${OPENAI_API_KEY}        # VIOLATION
```

**Why Prohibited:**
- Security risk (key exposure in configs)
- No centralized key management
- Difficult to rotate or revoke

#### ❌ Anti-Pattern 3: Model Configuration in Code

```yaml
# PROHIBITED - DO NOT USE
llm_config:
  model: claude-sonnet-4-5        # VIOLATION
  temperature: 0.3
  max_tokens: 2048
  fallback_model: claude-opus-4-6  # VIOLATION
```

**Why Prohibited:**
- Implies direct API usage
- Bypasses platform capabilities
- No centralized model management

#### ❌ Anti-Pattern 4: Third-Party LLM Libraries

```python
# PROHIBITED - DO NOT USE
import openai
import anthropic
import langchain  # If used for direct LLM calls

# These libraries should NOT be in dependencies
# requirements.txt:
# anthropic==0.20.0  # VIOLATION
# openai==1.10.0     # VIOLATION
```

**Why Prohibited:**
- Indicates intent to bypass approved patterns
- Creates maintenance burden
- No platform integration

### Migration Path

If you encounter existing code with prohibited patterns:

1. **Identify the LLM Operation:**
   - What is the LLM being asked to do?
   - What inputs does it receive?
   - What outputs are expected?

2. **Choose Approved Pattern:**
   - **Glean MCP:** For analysis, synthesis, knowledge retrieval
   - **Claude Code:** For multi-step workflows, file operations, code tasks

3. **Refactor Implementation:**
   ```python
   # BEFORE (Prohibited)
   from anthropic import Anthropic
   client = Anthropic(api_key=key)
   response = client.messages.create(
       model="claude-sonnet-4-5",
       messages=[{"role": "user", "content": prompt}]
   )

   # AFTER (Approved)
   from mcp_client import MCPClient
   client = MCPClient()
   response = client.call_tool(
       "mcp__glean__chat",
       {"message": prompt}
   )
   ```

4. **Update Dependencies:**
   - Remove `anthropic`, `openai`, etc. from `requirements.txt`
   - Add MCP client library if needed
   - Update environment variables

5. **Validate Compliance:**
   - Run validation checklist (see ARCHITECTURE-REVIEW-CHECKLIST.md)
   - Verify no prohibited patterns remain
   - Test functionality with approved pattern

### Validation Checklist

Before submitting any architecture document or code for review:

- [ ] **No ANTHROPIC_API_KEY** in environment configurations
- [ ] **No anthropic client library** in dependencies
- [ ] **No openai or other LLM libraries** in dependencies
- [ ] **No model specifications** (`claude-sonnet-4-5`, `gpt-4`, etc.) in configs
- [ ] **No fallback_model** configurations
- [ ] **All LLM operations** use `mcp__glean__chat` or Claude Code Task tool
- [ ] **XML prompt templates** (if used) stored in version-controlled repository (sdlc/prompts)
- [ ] **Prompt templates** reference Glean agents via `mcp__glean__chat` (not standalone agents)
- [ ] **Environment variables** use `GLEAN_MCP_CONFIG` (not API keys)

**Automated Validation:**

```bash
# Search for violations (should return NO matches)
grep -rn "ANTHROPIC_API_KEY\|OPENAI_API_KEY" .
grep -rn "from anthropic import\|import anthropic" .
grep -rn "model.*claude-\|model.*gpt-" --include="*.yaml" --include="*.yml" .
grep -rn "fallback_model" --include="*.yaml" --include="*.yml" .
```

### Exceptions

**NONE PERMITTED.**

All LLM compute must flow through approved patterns. If a use case cannot be satisfied by Glean MCP or Claude Code:

1. Contact architecture team to evaluate if platform enhancement is needed
2. Do NOT implement workaround using direct API access
3. If critical, escalate to executive level for policy exception review

### References

**Internal Guides:**
- [Glean Agent Registry](../glean/AGENT-REGISTRY.yaml) - Catalog of 52+ available Glean agents with specifications
- [Glean Agent Registry Guide](../glean/AGENT-REGISTRY-GUIDE.md) - How to discover and use agents from registry
- [Glean MCP Agent Pattern Guide](../guides/glean-mcp-agent-pattern.md) - Direct invocation of Glean agents
- [XML Prompt Template Pattern Guide](../guides/xml-prompt-agent-pattern.md) - Structured message templates for Glean agents
- [Agent Implementation Guide](../guides/agent-implementation-guide.md) - Master guide for agent patterns

**Architecture Documents:**
- [ADR-006: Glean MCP Agent Integration](./ddd-specification.md#adr-006-glean-mcp-agent-integration-with-xml-prompt-templates) - Dual-mode agent implementation strategy
- [Implementation Specification](../product/implementation-specification.md)
- [Architecture Review Checklist](./ARCHITECTURE-REVIEW-CHECKLIST.md)

**External Documentation:**
- [Using Agents as MCP Tools - Glean Help Center](https://docs.glean.com/administration/platform/mcp/agents-as-tools)
- [Glean Developer Platform](https://developers.glean.com/)
- [Glean's MCP servers announcement](https://www.glean.com/blog/mcp-servers-septdrop-2025)
- [Claude Code Documentation](https://claude.com/claude-code)

---

## Principle 2: [Future Principle]

_Placeholder for next core principle._

---

## Principle 3: [Future Principle]

_Placeholder for next core principle._

---

## Document Maintenance

### Changelog

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2026-02-11 | Initial creation with Principle 1 (LLM Compute) | Architecture Team |

### Review Schedule

This document must be reviewed:
- **Quarterly:** Validate principles remain relevant
- **Before Major Releases:** Ensure compliance with current architecture
- **When Violations Detected:** Update examples and validation rules

### Amendment Process

1. Propose amendment via architecture review board
2. Evaluate impact on existing implementations
3. Update validation checklist
4. Communicate changes to all teams
5. Update version and changelog
