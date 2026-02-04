# Agent Implementation Guide

**Version**: 1.0.0
**Last Updated**: 2026-02-03
**Purpose**: Guide for implementing agents using dual-mode pattern

---

## Overview

This guide helps you choose and implement the right agent pattern for your use case. The a_domain platform supports two agent implementation patterns:

1. **Glean MCP Agent**: Access existing Glean agents via `mcp__glean__chat` tool
2. **XML Prompt Agent**: Create custom agents with XML prompts in `Eric-Flecher-Glean/prompts`

**Architecture Reference**: ADR-006 in `docs/architecture/ddd-specification.md`

---

## Decision Tree: Which Pattern to Use?

```
Start: Need to implement an agent
│
├─ Does the capability already exist in Glean?
│  ├─ YES → Use Glean MCP Agent ✅
│  │        - Zero implementation cost
│  │        - Battle-tested (222 customers)
│  │        - Multi-source integration built-in
│  │
│  └─ NO → Continue
│      │
│      ├─ Need rapid prototyping or custom logic?
│      │  ├─ YES → Use XML Prompt Agent ✅
│      │  │        - Minutes to implement
│      │  │        - Full control over prompts
│      │  │        - Version-controlled in Git
│      │  │
│      │  └─ NO → Re-evaluate: Consider requesting Glean agent
│
└─ Need multi-step orchestration with custom logic?
   └─ YES → Use XML Prompt Agent ✅
            - Compose multiple MCP calls
            - Custom workflow logic
            - SDLC meta-agents
```

---

## Pattern 1: Glean MCP Agent

### When to Use

✅ **Use Glean MCP Agent when:**
- Capability already exists in Glean platform
- Need multi-source data integration (Salesforce, Gong, GitHub, etc.)
- Require agentic looping for complex analysis
- Need bi-directional system integration
- Want zero implementation cost

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
- ✅ How to invoke `mcp__glean__chat` tool
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

## Pattern 2: XML Prompt Agent

### When to Use

✅ **Use XML Prompt Agent when:**
- Custom domain-specific logic needed
- Rapid prototyping or experimentation required
- Custom multi-step orchestration needed
- Building SDLC meta-agents
- Fine-grained control over prompt structure

### Quick Start

1. **Create XML Prompt**
   ```xml
   <?xml version="1.0" encoding="UTF-8"?>
   <prompt>
     <metadata>
       <name>extract-acceptance-criteria</name>
       <version>1.0.0</version>
       <domain>sdlc/requirements</domain>
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
   - Repository: `Eric-Flecher-Glean/prompts`
   - Path: `sdlc/requirements/extract-acceptance-criteria.xml`
   - Commit with semantic versioning

3. **Load and Execute**
   ```python
   # Load XML prompt
   prompt = load_xml_prompt(
       repo="Eric-Flecher-Glean/prompts",
       path="sdlc/requirements/extract-acceptance-criteria.xml"
   )

   # Execute with input
   result = execute_prompt(
       prompt=prompt,
       input_text=user_story_text
   )

   # Parse output
   acceptance_criteria = result['acceptance_criteria']
   ```

### Complete Example

**File**: `examples/xml_prompt_agent_example.py`

**What it demonstrates**:
- ✅ XML prompt structure (role, task, instructions, constraints)
- ✅ Version control with semantic versioning
- ✅ Prompt loading and execution
- ✅ Result parsing and integration

**Run it**:
```bash
uv run examples/xml_prompt_agent_example.py
```

### Full Documentation

See: `docs/guides/xml-prompt-agent-pattern.md`

---

## Comparison

| Aspect | Glean MCP Agent | XML Prompt Agent |
|--------|----------------|------------------|
| **Development Time** | 0 (already exists) | Minutes to hours |
| **Customization** | Limited (Glean config only) | Full control (edit XML) |
| **Data Sources** | Pre-configured (5+ sources) | Manual integration required |
| **Security** | Built-in (Glean platform) | Manual implementation |
| **Iteration Speed** | Slow (Glean release cycle) | Fast (edit XML, commit) |
| **Agentic Looping** | Built-in | Manual orchestration |
| **Cost** | Zero (existing investment) | Development time |
| **Use Case** | Existing capabilities | Custom logic, SDLC meta-agents |

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
   - Commit prompts to `Eric-Flecher-Glean/prompts`
   - Use semantic versioning
   - Tag releases for stable versions

3. **Test prompt variations**
   - Try different phrasings for better results
   - A/B test prompt variations
   - Measure quality metrics (precision, recall)

---

## Examples

### Example 1: Glean MCP Agent (P1-EXAMPLE-001)

**Story**: P1-EXAMPLE-001
**Pattern**: Glean MCP Agent
**Agent**: "Extract Common Pain Points"
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
- How to pass context parameters
- How to parse structured responses
- How to integrate into requirements backlog

### Example 2: XML Prompt Agent (P1-EXAMPLE-002)

**Story**: P1-EXAMPLE-002
**Pattern**: XML Prompt Agent
**Agent**: "Acceptance Criteria Extractor"
**Use Case**: Extract acceptance criteria from user story text

**Key Files**:
- Guide: `docs/guides/xml-prompt-agent-pattern.md`
- Example: `examples/xml_prompt_agent_example.py`
- Prompt: `examples/prompts/extract-acceptance-criteria.xml`

**Run it**:
```bash
uv run examples/xml_prompt_agent_example.py
```

**What you'll learn**:
- How to structure XML prompts (role, task, instructions, constraints)
- How to version control prompts in Git
- How to load and execute prompts
- How to integrate extracted results into backlog

---

## Integration with Domain Registry

Both agent patterns integrate with the Domain Registry for discovery:

```yaml
# Glean MCP Agent Registration
agent_id: "pain-point-extractor-v1"
name: "Customer Pain Point Extractor"
bounded_context: "SalesEnablement"
implementation_type: "glean_mcp"
implementation:
  mcp_tool: "mcp__glean__chat"
  glean_agent_name: "Extract Common Pain Points"
  glean_agent_version: "2.1.0"
  data_sources: ["Gong", "HubSpot", "Teams", "Salesforce", "Zoom"]

# XML Prompt Agent Registration
agent_id: "ac-extractor-v1"
name: "Acceptance Criteria Extractor"
bounded_context: "SDLC.RequirementsManagement"
implementation_type: "xml_prompt"
implementation:
  repository: "Eric-Flecher-Glean/prompts"
  prompt_path: "sdlc/requirements/extract-acceptance-criteria.xml"
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

- **ADR-006**: Dual-Mode Agent Implementation Strategy (`docs/architecture/ddd-specification.md`)
- **Glean Agent Library**: `docs/research/glean-agent-usage-categorization.md`
- **Glean MCP Pattern**: `docs/guides/glean-mcp-agent-pattern.md`
- **XML Prompt Pattern**: `docs/guides/xml-prompt-agent-pattern.md` (P1-EXAMPLE-002)
- **Domain Registry Spec**: `docs/architecture/ddd-specification.md`

---

**Last Updated**: 2026-02-03
**Version**: 1.0.0
**Related Stories**: P1-EXAMPLE-001, P1-EXAMPLE-002
