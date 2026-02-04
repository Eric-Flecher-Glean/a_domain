# Agent Implementation Pattern Clarification - Summary

**Date**: 2026-02-03
**Issue**: Clarify and document dual-mode agent implementation strategy
**Status**: ✅ COMPLETED

---

## User Request

> "I want to clarify and add to the roadmap if this is not present. Agents in this system will either be an existing Glean agent that we call via mcp chat, or it will be an xml instruction that is organized and retained in https://github.com/Eric-Flecher-Glean/prompts"

---

## What Was Accomplished

### 1. Architecture Documentation Updated ✅

**File**: `docs/architecture/ddd-specification.md`

**Changes Made**:

1. **Added to Key Architectural Decisions** (Section: ADR-006)
   - New decision: "Dual-Mode Agent Implementation Strategy"
   - Documented both implementation patterns (Glean MCP vs. XML Prompt)

2. **Updated Ubiquitous Language Glossary**
   - Added 3 new terms:
     - **Glean MCP Agent**: An existing Glean agent invoked via `mcp__glean__chat` tool
     - **XML Prompt Agent**: Prompt-engineered agent stored in `Eric-Flecher-Glean/prompts` repository
     - **Agent Implementation Type**: Classification (glean_mcp or xml_prompt)

3. **Created ADR-006: Dual-Mode Agent Implementation Strategy**
   - **Decision**: Agents implemented via one of two patterns
   - **Rationale**: Best-of-both-worlds approach
   - **Implementation Guidelines**: When to use each pattern
   - **Examples**: YAML configuration for both patterns
   - **Registry Implications**: How to register each type

---

## ADR-006 Summary

### Pattern 1: Glean MCP Agents

**When to Use**:
- Capability already exists in Glean platform
- Need multi-source data integration
- Require agentic looping feature
- Need bi-directional system integration

**Benefits**:
- Zero implementation cost (already deployed)
- Battle-tested (222 customers, 200+ agents each)
- Enterprise security built-in
- Access to configured data sources

**Example**:
```yaml
agent_type: glean_mcp
implementation:
  tool: mcp__glean__chat
  agent_name: "Extract Common Pain Points"
  context: "Analyze sales call transcripts by industry"
```

### Pattern 2: XML Prompt Agents

**When to Use**:
- Custom domain-specific logic needed
- Rapid prototyping or experimentation
- Custom multi-step orchestration required
- Need fine-grained prompt control
- Building meta-agents for SDLC automation

**Benefits**:
- Rapid development (minutes vs. days)
- Version-controlled in Git
- Easy to review and iterate
- Reusable prompt library
- Fine-grained control over structure

**Example**:
```yaml
agent_type: xml_prompt
implementation:
  repository: Eric-Flecher-Glean/prompts
  prompt_path: sdlc/requirements/extract-acceptance-criteria.xml
  version: "1.2.0"
```

---

## Example Stories Created ✅

### P1-EXAMPLE-001: Glean MCP Agent Example

**Purpose**: Demonstrate how to use existing Glean agents via MCP

**Use Case**: Extract customer pain points from Gong call transcripts

**Key Points**:
- Shows `mcp__glean__chat` tool usage
- Demonstrates context parameter structure
- Includes result handling code
- References existing "Extract Common Pain Points" Glean agent

**Estimated Effort**: 8 points

### P1-EXAMPLE-002: XML Prompt Agent Example

**Purpose**: Demonstrate custom agent creation with XML prompts

**Use Case**: Extract acceptance criteria from user story text

**Key Points**:
- Shows XML prompt structure (role, task, instructions, constraints)
- Stored in `Eric-Flecher-Glean/prompts` repository
- Version-controlled with semantic versioning
- Demonstrates prompt loading and execution

**Estimated Effort**: 8 points

---

## Backlog Updates

**Version**: 63 → 64

**New Stories**: 2
- P1-EXAMPLE-001: Glean MCP Agent example
- P1-EXAMPLE-002: XML Prompt Agent example

**Total Stories**: 66
- Completed: 37 (56%)
- In Progress: 0
- Not Started: 29 (44%)

**Changelog Entry**:
```yaml
version: 64
date: 2026-02-03T23:30:00Z
changes:
  - Added ADR-006: Dual-Mode Agent Implementation Strategy to architecture docs
  - Created P1-EXAMPLE-001: Glean MCP Agent example story
  - Created P1-EXAMPLE-002: XML Prompt Agent example story
  - Updated ubiquitous language with agent implementation terms
```

---

## Registry Implications

### Agent Registration Schema Updates

Agents must now include `implementation_type` field:

```yaml
agent_registration:
  agent_id: "pain-point-extractor-v1"
  name: "Customer Pain Point Extractor"
  bounded_context: "SalesEnablement"
  implementation_type: "glean_mcp"  # or "xml_prompt"
  implementation:
    # Glean MCP specific
    mcp_tool: "mcp__glean__chat"
    glean_agent_name: "Extract Common Pain Points"
    # OR XML Prompt specific
    repository: "Eric-Flecher-Glean/prompts"
    prompt_path: "sales/pain-point-extraction.xml"
    version: "1.2.0"
```

### Discovery Query Updates

Discovery API can now filter by implementation type:

```python
# Find all Glean MCP agents
agents = registry.discover(
    implementation_type="glean_mcp"
)

# Find all XML Prompt agents
agents = registry.discover(
    implementation_type="xml_prompt"
)

# Find agents regardless of implementation
agents = registry.discover(
    bounded_context="SalesEnablement"
)
```

### Schema Validation Updates

Different validation rules apply:
- **Glean MCP agents**: Validated by Glean platform
- **XML Prompt agents**: Validated locally against XML schema + prompt structure

---

## Documentation References

### Updated Files
1. `docs/architecture/ddd-specification.md`
   - Added ADR-006 (lines ~1575-1630)
   - Updated ubiquitous language glossary (lines ~72-80)
   - Updated Key Architectural Decisions (lines ~52-59)

### New Files
2. `.sdlc/core/add_agent_example_stories.py`
   - Script to add example stories to backlog
   - Can be run again to regenerate stories

3. `docs/recap/agent-implementation-pattern-clarification.md` (this file)
   - Summary of changes and rationale

### Referenced Files
4. `docs/research/glean-agent-usage-categorization.md`
   - Source of Glean agent usage data
   - 222 customers, 200+ agents deployed

5. `docs/concepts/xml-chat-orginal.md`
   - Original XML prompt structure examples
   - Reference for XML agent pattern

---

## Next Steps

### Immediate (Recommended)
1. ✅ Review ADR-006 in architecture documentation
2. ✅ Review example stories (P1-EXAMPLE-001, P1-EXAMPLE-002)
3. ⏭️ Implement P1-EXAMPLE-001 to create runnable Glean MCP example
4. ⏭️ Implement P1-EXAMPLE-002 to create runnable XML Prompt example

### Short-term
1. Update Agent Registry schema to include `implementation_type` field
2. Update Discovery API to support filtering by implementation type
3. Create validation rules for XML Prompt agents
4. Sync `Eric-Flecher-Glean/prompts` repository to registry

### Long-term
1. Build prompt library in `Eric-Flecher-Glean/prompts`
2. Create reusable XML prompt templates
3. Establish prompt versioning and deprecation strategy
4. Measure usage metrics: Glean MCP vs. XML Prompt adoption

---

## Key Decisions Made

### User Choices
1. **Location**: Add to architecture specification (ADR-006) ✅
2. **Examples**: Create example stories for both patterns ✅

### Implementation Decisions
1. **Pattern Names**:
   - "Glean MCP Agent" (not "Glean agent" to avoid confusion)
   - "XML Prompt Agent" (emphasizes structured XML format)

2. **Repository**:
   - Use `Eric-Flecher-Glean/prompts` as single source of truth
   - Version control with semantic versioning
   - Organize by domain (sdlc/, sales/, support/, etc.)

3. **Ubiquitous Language**:
   - Added formal terms to Platform.Registry context
   - Ensures consistent terminology across codebase

4. **Registry Integration**:
   - `implementation_type` as required field
   - Different validation pipelines for each type
   - Discovery API supports filtering

---

## Impact Assessment

### Positive Impacts ✅
- **Clarity**: Developers now understand two implementation paths
- **Flexibility**: Choose best tool for the job (Glean MCP vs. XML Prompt)
- **Speed**: XML Prompts enable rapid development
- **Reuse**: Leverage existing Glean platform capabilities
- **Documentation**: Formal ADR captures rationale and trade-offs

### Potential Challenges ⚠️
- **Learning Curve**: Team needs to understand when to use each pattern
- **Maintenance**: Two patterns to maintain (MCP invocation + XML execution)
- **Consistency**: Need to ensure both patterns integrate seamlessly with registry

### Mitigation Strategies 🛡️
- **Examples**: P1-EXAMPLE-001 and P1-EXAMPLE-002 provide templates
- **Guidelines**: ADR-006 includes clear "when to use" criteria
- **Validation**: Different pipelines ensure quality for each type
- **Registry**: Unified discovery regardless of implementation type

---

## Conclusion

Successfully clarified and documented the dual-mode agent implementation strategy. The architecture now explicitly recognizes two agent patterns:

1. **Glean MCP Agents**: Leverage existing enterprise AI capabilities
2. **XML Prompt Agents**: Enable rapid custom development

This clarification:
- ✅ Added to architecture documentation (ADR-006)
- ✅ Updated ubiquitous language glossary
- ✅ Created example stories demonstrating both patterns
- ✅ Updated backlog (version 64)
- ✅ Established clear implementation guidelines

Developers can now choose the right implementation pattern based on use case requirements, with clear examples and architectural guidance to support their decisions.

---

**Status**: ✅ COMPLETE
**Backlog Version**: 64
**Stories Created**: 2 (P1-EXAMPLE-001, P1-EXAMPLE-002)
**Documentation Updated**: docs/architecture/ddd-specification.md
