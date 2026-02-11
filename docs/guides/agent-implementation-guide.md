# Agent Implementation Guide

**Version**: 2.0.0
**Last Updated**: 2026-02-04
**Purpose**: Guide for implementing agents using Glean MCP with optional XML prompt templates

---

## Overview

This guide explains how to leverage existing Glean agents via the `mcp__glean__chat` tool, with optional XML prompt templates to structure your messages for consistency and reusability.

**Key Concept**: All agents in this system use the `mcp__glean__chat` tool to access existing Glean capabilities. XML prompts are **not** standalone agents—they are templates that structure the messages you send to Glean agents.

**Architecture Reference**: ADR-006 in `docs/architecture/ddd-specification.md`

---

## Decision Tree: Should You Use an XML Prompt Template?

```
Start: Need to invoke a Glean agent via mcp__glean__chat
│
├─ Is this a one-time or ad-hoc query?
│  ├─ YES → Use direct mcp__glean__chat call ✅
│  │        - Simple message parameter
│  │        - No template needed
│  │        - Quick and straightforward
│  │
│  └─ NO → Continue
│      │
│      ├─ Do you need repeatable, structured invocation?
│      │  ├─ YES → Use XML Prompt Template ✅
│      │  │        - Define role, task, instructions
│      │  │        - Version control in Git
│      │  │        - Reusable across team
│      │  │        - Consistent formatting
│      │  │
│      │  └─ NO → Use direct mcp__glean__chat call ✅
│
└─ Note: Both approaches call the SAME Glean agents via mcp__glean__chat
          Templates just structure the input message
```

---

## Approach 1: Direct Invocation (No Template)

### When to Use

✅ **Use direct mcp__glean__chat invocation when:**
- Simple, ad-hoc query to a Glean agent
- One-off exploration or prototyping
- Message structure is straightforward
- No need for version-controlled prompts

### Quick Start

1. **Identify Glean Agent**
   - Review: `docs/research/glean-agent-usage-categorization.md`
   - 50+ pre-built agents available
   - Examples: "Extract Common Pain Points", "Deal Strategy", "PR Review"

2. **Invoke via MCP**
   ```python
   # Example: Extract customer pain points
   from mcp.tools import mcp__glean__chat

   response = mcp__glean__chat(
       message="Extract customer pain points from Q1 2026 calls",
       context=[
           "industry: healthcare",
           "customer_segment: enterprise"
       ]
   )
   ```

3. **Parse Response**
   ```python
   pain_points = response['pain_points']
   for pain_point in pain_points:
       print(f"- {pain_point['description']}")
       print(f"  Impact: {pain_point['impact_score']}")
   ```

### Complete Example

**File**: `examples/glean_mcp_agent_example.py`

**What it demonstrates**:
- ✅ How to invoke `mcp__glean__chat` tool directly
- ✅ How to pass context parameters
- ✅ How to parse structured responses
- ✅ How to integrate results into backlog

**Run it**:
```bash
uv run examples/glean_mcp_agent_example.py
```

**Expected output**:
```
✅ Pain points extracted successfully!
📊 Summary: 6 pain points identified across 32 mentions
🔴 Pain Points Identified:
1. Manual data entry taking 10+ hours/week per user
   Frequency: high, Impact: productivity (score: 0.90)
   ...
```

### Full Documentation

See: `docs/guides/glean-mcp-agent-pattern.md`

---

## Approach 2: With XML Prompt Template

### When to Use

✅ **Use XML prompt template when:**
- Repeatable invocation pattern needed
- Complex message structure (role, instructions, constraints)
- Need version control of prompt format
- Want to share/reuse prompt across team
- Building SDLC workflows requiring consistent structure

**Note**: The XML template structures the message sent TO a Glean agent via `mcp__glean__chat`. It's not a separate agent.

### Quick Start

1. **Create XML Prompt Template**
   ```xml
   <?xml version="1.0" encoding="UTF-8"?>
   <prompt>
     <metadata>
       <name>extract-acceptance-criteria</name>
       <version>1.0.0</version>
       <domain>sdlc/requirements</domain>
       <glean_agent>Extract Requirements</glean_agent>
     </metadata>

     <role>
       You are a requirements analyst extracting acceptance criteria from user stories.
     </role>

     <task>
       Extract testable acceptance criteria from the given user story text.
     </task>

     <instructions>
       <step1>Read the user story carefully</step1>
       <step2>Identify concrete, measurable outcomes</step2>
       <step3>Format each as "AC#: [description]"</step3>
     </instructions>

     <output_format>
       <section name="Acceptance Criteria">
         List of extracted AC items
       </section>
     </output_format>

     <constraints>
       <constraint>Each AC must be testable</constraint>
       <constraint>Use "AC#:" prefix for numbering</constraint>
     </constraints>
   </prompt>
   ```

2. **Store in Repository**
   - Repository: `sdlc/prompts`
   - Path: `sdlc/requirements/extract-acceptance-criteria.xml`
   - Commit with semantic versioning

3. **Load Template and Invoke Glean Agent**
   ```python
   # Load XML template
   template = load_xml_template(
       repo="../../sdlc/prompts",
       path="sdlc/requirements/extract-acceptance-criteria.xml"
   )

   # Template formats the message for mcp__glean__chat
   formatted_message = template.format(
       user_story=user_story_text
   )

   # Invoke Glean agent with formatted message
   response = mcp__glean__chat(
       message=formatted_message,
       context=template.get_context()
   )

   # Parse output
   acceptance_criteria = response['acceptance_criteria']
   ```

### Complete Example

**File**: `examples/xml_prompt_agent_example.py`

**What it demonstrates**:
- ✅ XML template structure (role, task, instructions, constraints)
- ✅ How template formats message for `mcp__glean__chat`
- ✅ Version control with semantic versioning
- ✅ Template loading and Glean agent invocation
- ✅ Result parsing and integration

**Run it**:
```bash
uv run examples/xml_prompt_agent_example.py
```

### Full Documentation

See: `docs/guides/xml-prompt-agent-pattern.md`

---

## Comparison

**Important**: Both approaches use the SAME Glean agents via `mcp__glean__chat`. The difference is in how you structure the input message.

| Aspect | Direct Invocation | With XML Template |
|--------|------------------|-------------------|
| **Glean Agent** | ✅ Uses mcp__glean__chat | ✅ Uses mcp__glean__chat |
| **Setup Time** | Immediate | Minutes (create template) |
| **Message Structure** | Ad-hoc string | Structured (role, task, instructions) |
| **Version Control** | Not versioned | Git-tracked XML |
| **Reusability** | Copy-paste code | Import template |
| **Consistency** | Manual | Enforced by template |
| **Best For** | One-off queries | Repeatable workflows |
| **Data Sources** | Glean platform (5+ sources) | Glean platform (5+ sources) |
| **Security** | Glean platform | Glean platform |
| **Agentic Looping** | Glean platform | Glean platform |

---

## Best Practices

### For Both Patterns

1. **Document intent contracts**
   - Input schema (what parameters are required)
   - Output schema (what structure is returned)
   - Example invocations

2. **Register in Domain Registry**
   ```yaml
   agent_id: "pain-point-extractor-v1"
   name: "Customer Pain Point Extractor"
   bounded_context: "SalesEnablement"
   implementation_type: "glean_mcp"  # or "xml_prompt"
   ```

3. **Version your agents**
   - Glean MCP: Track Glean agent version
   - XML Prompt: Use semantic versioning (1.0.0, 1.1.0, 2.0.0)

4. **Test your agents**
   - Unit tests for parsing logic
   - Integration tests with real/mock data
   - Validate against acceptance criteria

### Glean MCP Specific

1. **Understand data source permissions**
   - Glean enforces permissions at data source level
   - Users only see data they have access to
   - Test with different permission levels

2. **Monitor usage metrics**
   - Glean tracks agent invocations
   - Review usage patterns via Glean dashboard
   - Optimize based on actual usage

3. **Handle rate limits**
   - Glean may have rate limits per agent
   - Implement retry logic with exponential backoff
   - Cache results where appropriate

### XML Prompt Specific

1. **Use structured XML format**
   - Always include metadata (name, version, domain)
   - Define role, task, instructions clearly
   - Specify output format and constraints

2. **Version control best practices**
   - Commit prompts to `sdlc/prompts`
   - Use semantic versioning
   - Tag releases for stable versions

3. **Test prompt variations**
   - Try different phrasings for better results
   - A/B test prompt variations
   - Measure quality metrics (precision, recall)

---

## Examples

### Example 1: Direct Invocation (P1-EXAMPLE-001)

**Story**: P1-EXAMPLE-001
**Approach**: Direct `mcp__glean__chat` invocation
**Glean Agent**: "Extract Common Pain Points"
**Use Case**: Extract customer pain points from Gong call transcripts

**Key Files**:
- Guide: `docs/guides/glean-mcp-agent-pattern.md`
- Example: `examples/glean_mcp_agent_example.py`

**Run it**:
```bash
uv run examples/glean_mcp_agent_example.py
```

**What you'll learn**:
- How to invoke Glean agents via `mcp__glean__chat`
- How to pass context parameters directly
- How to parse structured responses
- How to integrate into requirements backlog

### Example 2: With XML Template (P1-EXAMPLE-002)

**Story**: P1-EXAMPLE-002
**Approach**: XML template + `mcp__glean__chat` invocation
**Glean Agent**: Glean requirements agent
**Use Case**: Extract acceptance criteria from user story text using structured template

**Key Files**:
- Guide: `docs/guides/xml-prompt-agent-pattern.md`
- Example: `examples/xml_prompt_agent_example.py`
- Template: `examples/prompts/extract-acceptance-criteria.xml`

**Run it**:
```bash
uv run examples/xml_prompt_agent_example.py
```

**What you'll learn**:
- How to structure XML templates (role, task, instructions, constraints)
- How template formats message for `mcp__glean__chat`
- How to version control templates in Git
- How to load templates and invoke Glean agents
- How to integrate extracted results into backlog

---

## Integration with Domain Registry

All agent invocations use Glean MCP via `mcp__glean__chat`. Registry tracks whether an XML template is used:

```yaml
# Direct Invocation (No Template)
agent_id: "pain-point-extractor-v1"
name: "Customer Pain Point Extractor"
bounded_context: "SalesEnablement"
implementation:
  tool: "mcp__glean__chat"
  glean_agent_name: "Extract Common Pain Points"
  glean_agent_version: "2.1.0"
  data_sources: ["Gong", "HubSpot", "Teams", "Salesforce", "Zoom"]

# With XML Template
agent_id: "ac-extractor-v1"
name: "Acceptance Criteria Extractor"
bounded_context: "SDLC.RequirementsManagement"
implementation:
  tool: "mcp__glean__chat"
  glean_agent_name: "Extract Requirements"  # Which Glean agent to use
  message_template:
    repository: "sdlc/prompts"
    path: "sdlc/requirements/extract-acceptance-criteria.xml"
    version: "1.0.0"
```

---

## Troubleshooting

### Glean MCP Agent Issues

**Problem**: Agent not found
- **Solution**: Verify agent name exactly matches Glean agent template
- **Check**: `docs/research/glean-agent-usage-categorization.md`

**Problem**: Empty results
- **Solution**: Check user permissions to data sources
- **Solution**: Verify context parameters are valid

**Problem**: Timeout errors
- **Solution**: Reduce scope with more specific context
- **Solution**: Check Glean platform status

### XML Prompt Agent Issues

**Problem**: Prompt not loading
- **Solution**: Verify repository path and file exists
- **Solution**: Check XML is well-formed (no syntax errors)

**Problem**: Poor quality results
- **Solution**: Refine prompt instructions and constraints
- **Solution**: Add examples in prompt
- **Solution**: Test with different input variations

---

## Next Steps

1. **Choose your pattern** based on use case
2. **Review the appropriate guide**:
   - Glean MCP: `docs/guides/glean-mcp-agent-pattern.md`
   - XML Prompt: `docs/guides/xml-prompt-agent-pattern.md` (P1-EXAMPLE-002)
3. **Run the examples**:
   - `uv run examples/glean_mcp_agent_example.py`
   - `uv run examples/xml_prompt_agent_example.py` (coming in P1-EXAMPLE-002)
4. **Implement your agent** following the pattern
5. **Register in Domain Registry** for discoverability

---

## Related Documentation

- **ADR-006**: Glean MCP Agent Integration with XML Prompt Templates (`docs/architecture/ddd-specification.md`)
- **Glean Agent Library**: `docs/research/glean-agent-usage-categorization.md`
- **Direct Invocation Guide**: `docs/guides/glean-mcp-agent-pattern.md`
- **XML Template Pattern**: `docs/guides/xml-prompt-agent-pattern.md`
- **Domain Registry Spec**: `docs/architecture/ddd-specification.md`

---

**Last Updated**: 2026-02-04
**Version**: 2.0.0
**Related Stories**: P1-EXAMPLE-001, P1-EXAMPLE-002
