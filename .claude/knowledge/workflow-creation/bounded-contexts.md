# Bounded Contexts Reference

This document describes all bounded contexts in the document-driven agent orchestration system. Use this to guide users in selecting the appropriate context for their workflow.

## Core Domains (Business-Critical, High Complexity)

### PromptEngineering
**Purpose:** XML prompt generation and validation for Anthropic-style prompts

**Responsibilities:**
- Transform natural language requests into structured XML prompts
- Validate prompt quality, structure, and completeness
- Generate actionable feedback for refinement
- Apply Anthropic's hierarchical methodology
- Handle iterative refinement loops

**Existing Agents:**
- `prompt-generator-001` - XML prompt generation
- `prompt-validator-001` - Quality validation and feedback

**Existing Workflows:**
- `prompt-generation` - 2-stage validation workflow

**When to Use:**
- User wants to generate XML prompts
- Task involves prompt engineering or validation
- Need to transform natural language into structured formats
- Working with LLM prompt optimization

**Domain Events:**
- PromptGenerationRequested
- PromptGenerated
- ValidationCompleted
- FeedbackProvided
- PromptRefined

---

### WorkflowOrchestration
**Purpose:** Coordinate agent interactions, feedback loops, and quality gates

**Responsibilities:**
- Manage multi-agent workflows
- Orchestrate staged validation patterns
- Handle feedback loops and retry logic
- Track quality scores and metrics
- Escalate failures appropriately
- Manage state passing between stages

**Existing Agents:**
- None (orchestration is handled by the workflow engine itself)

**Existing Workflows:**
- All workflows use this context for orchestration logic

**When to Use:**
- Building meta-workflows that coordinate other workflows
- Creating new orchestration patterns
- Managing complex agent collaborations
- Implementing new validation or feedback strategies

**Domain Events:**
- WorkflowStarted
- StageCompleted
- ValidationFailed
- FeedbackLoopInitiated
- WorkflowCompleted
- WorkflowFailed

---

## Supporting Domains (Provide Essential Support)

### ContextDiscovery
**Purpose:** Analyze tasks to identify required inputs and context sources

**Responsibilities:**
- Parse user requests to identify data requirements
- Map inputs to appropriate sources (user input, Glean, APIs)
- Identify which Glean MCP tools are needed
- Generate input specifications for prompts
- Discover context sources from enterprise knowledge

**Existing Agents:**
- Context analysis is built into `prompt-generator-001` (NEW capability)

**Existing Workflows:**
- Integrated into `prompt-generation` workflow

**When to Use:**
- Task requires understanding what inputs are needed
- Need to map data sources for a workflow
- Building workflows that integrate with Glean
- Analyzing requirements before execution

**Domain Events:**
- ContextAnalysisRequested
- InputsIdentified
- SourcesMapped
- GleanToolsDiscovered

---

## Generic Subdomains (Common Functionality)

### GleanIntegration
**Purpose:** Integration with Glean MCP services and enterprise knowledge

**Responsibilities:**
- Execute Glean MCP tool calls
- Query enterprise documents and knowledge
- Search code repositories
- Access meeting transcripts
- Retrieve people and org information

**Existing Agents:**
- None (Glean tools accessed via MCP server)

**Existing Workflows:**
- Used as supporting infrastructure for workflows that need enterprise context

**When to Use:**
- Workflow needs to access enterprise knowledge
- Task requires searching documents, code, or meetings
- Need to retrieve company-specific information
- Building integrations with Glean services

**Domain Events:**
- GleanQueryExecuted
- DocumentsRetrieved
- SearchCompleted
- ContextFetched

---

## Bounded Context Selection Guide

### Questions to Ask:

1. **What is the primary business capability?**
   - Prompt engineering? → PromptEngineering
   - Agent coordination? → WorkflowOrchestration
   - Requirement analysis? → ContextDiscovery
   - Knowledge retrieval? → GleanIntegration

2. **Does this workflow coordinate other workflows?**
   - Yes → WorkflowOrchestration
   - No → Continue to next question

3. **What type of data does it process?**
   - XML prompts → PromptEngineering
   - Task specifications → ContextDiscovery
   - Enterprise knowledge → GleanIntegration
   - Agent outputs → WorkflowOrchestration

4. **What is the primary output?**
   - Structured prompt → PromptEngineering
   - Input specification → ContextDiscovery
   - Retrieved documents → GleanIntegration
   - Workflow result → WorkflowOrchestration

5. **Is this a new domain?**
   - If the workflow doesn't fit any existing context, it may require a new bounded context
   - New contexts should be justified by unique:
     - Business capabilities
     - Domain language/ubiquitous language
     - Data models
     - Business rules

### Creating New Bounded Contexts

Only create a new bounded context if:
1. The capability doesn't fit any existing context
2. It has a distinct ubiquitous language
3. It has different business rules and constraints
4. It represents a separate business capability
5. It would be awkward to force into existing contexts

New bounded contexts require:
- Clear boundary definition
- Domain event specification
- Integration points with existing contexts
- Justification for why existing contexts don't fit

### Cross-Context Integration

Workflows can span multiple bounded contexts:
- **PromptEngineering** workflows may use **ContextDiscovery** for input analysis
- **ContextDiscovery** workflows may use **GleanIntegration** to retrieve information
- All workflows use **WorkflowOrchestration** for coordination

When integrating across contexts:
- Use domain events for communication
- Maintain clear boundaries
- Avoid tight coupling
- Use anti-corruption layers if needed
