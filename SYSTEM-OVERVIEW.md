# Integrated A/B Prompt Engineering System

**A production-ready system for creating high-quality XML prompts with automated validation and refinement**

---

## What It Does

The system **generates and validates XML-structured prompts** using a two-agent collaboration pattern with intelligent feedback loops. Think of it as having two AI specialists working together:

- **Agent A (Generator)**: Creates XML prompts from natural language descriptions
- **Agent B (Validator)**: Checks quality and provides specific improvement feedback

The agents iterate until the prompt meets quality standards (score ≥ 90/100), with a maximum of 3 attempts.

---

## How It Works

### Step-by-Step Process

```
┌──────────────────────────────────────────────────────────────────┐
│  1. USER INPUT                                                   │
│  "Create a prompt for meeting summarization"                     │
└──────────────┬───────────────────────────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────────────────────────┐
│  2. CONTEXT DISCOVERY                                            │
│  • Identifies required inputs (meeting transcript, attendees)    │
│  • Finds relevant context sources (previous meetings)           │
│  • Maps Glean MCP tools (glean_meeting_lookup)                  │
└──────────────┬───────────────────────────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────────────────────────┐
│  3. AGENT A - GENERATE XML (Attempt 1)                           │
│  • Analyzes task requirements                                    │
│  • Generates structured XML prompt                               │
│  • Includes: inputs, context, instructions, examples            │
└──────────────┬───────────────────────────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────────────────────────┐
│  4. AGENT B - VALIDATE QUALITY                                   │
│  Checks 4 dimensions:                                            │
│  • Structural (35%): XML format, required sections              │
│  • Completeness (30%): Content quality, examples                │
│  • Quality (25%): Clarity, effectiveness                        │
│  • Context (10%): Input specs, Glean queries                    │
│                                                                  │
│  Score: 85/100 ❌ (Threshold: 90)                                │
└──────────────┬───────────────────────────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────────────────────────┐
│  5. FEEDBACK LOOP (if score < 90)                                │
│  Agent B tells Agent A exactly what to fix:                      │
│  • "Add at least one more good example"                          │
│  • "Add validation rules for all required inputs"                │
│  • "Improve specificity in instructions"                         │
└──────────────┬───────────────────────────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────────────────────────┐
│  6. AGENT A - REFINE XML (Attempt 2)                             │
│  • Addresses all feedback items                                  │
│  • Adds 2nd good example ✓                                       │
│  • Adds detailed validation rules ✓                              │
│  • Enhances instruction specificity ✓                            │
└──────────────┬───────────────────────────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────────────────────────┐
│  7. AGENT B - RE-VALIDATE                                        │
│  Score: 95/100 ✅ (Above threshold!)                             │
└──────────────┬───────────────────────────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────────────────────────┐
│  8. OUTPUT FILES                                                 │
│  • prompt.xml - Final validated XML prompt                       │
│  • report.json - Validation results and metrics                 │
│                                                                  │
│  Summary: Score 95/100, 2 attempts, 9.0 seconds                 │
└──────────────────────────────────────────────────────────────────┘
```

---

## Usage

### Quick Start

```bash
# Generate a prompt (recommended command)
make xml-prompt-ab TASK="Create a prompt for meeting summarization"

# Output files created:
# - output/ab-prompt.xml           (The XML prompt)
# - output/ab-prompt-ab-report.json (Validation details)
```

### Real Examples

```bash
# Meeting summarization
make xml-prompt-ab TASK="Create a prompt for meeting summarization"
# Result: 100/100, 1 attempt, 2 required inputs, 1 context source

# Code review
make xml-prompt-ab TASK="Create a prompt for code review"
# Result: 100/100, 1 attempt, 2 required inputs, 2 context sources

# Customer feedback analysis
make xml-prompt-ab TASK="Create a prompt for customer feedback analysis"
# Result: 100/100, 1 attempt, 1 required input, 2 context sources
```

---

## How Quality Is Ensured

### Artifact-Driven Validation

All validation rules are stored in **external files** (not hardcoded), making them easy to update:

```
📁 Repository/Google Drive
├── Global Standards (organization-wide)
│   ├── validation-standards.json    (quality thresholds: 90/100)
│   ├── required-tags.json           (metadata, primary_goal, role, task...)
│   └── examples/                    (reference library)
│
└── Workflow Rules (specific to this workflow)
    ├── validation-rules.json        (detailed scoring: 10 pts for XML, 15 pts for sections...)
    ├── instructions.md              (how validation works)
    └── examples/
        ├── good/                    (what good looks like)
        │   └── example-001-meeting-summary.xml
        └── bad/                     (what to avoid)
            └── example-001-flat-structure.xml
```

**Key Benefit**: Non-technical users can add new examples or update rules by simply adding files to Google Drive (no code changes needed).

---

## Architecture Highlights

### Domain-Driven Design (DDD)

**4 Bounded Contexts:**
- **PromptEngineering**: XML generation and validation (Agents A & B)
- **ContextDiscovery**: Input and context source identification
- **GleanIntegration**: Glean MCP tool integration
- **WorkflowOrchestration**: Agent coordination and feedback loops

**4 Core Aggregates:**
- `PromptSpecification` - Manages XML content and metadata
- `ValidationResult` - Tracks quality scores and checks
- `WorkflowSession` - Manages attempt history
- `InputAnalysis` - Identifies required inputs and context

### Event Sourcing

Every action is recorded as an event for complete audit trail:
- `WorkflowSessionStarted` → `TaskAnalyzed` → `PromptGenerated` → `PromptValidated` → `PromptApproved` → `WorkflowSessionCompleted`

### Node-Based Workflow

Agents are **generalized nodes** with tool interfaces:
- **6 hops** in a typical 2-attempt scenario
- **Feedback loop** at hop 4 (Agent B → Agent A)
- **Complete traceability** with correlation IDs

---

## Key Features

### ✅ Quality Assurance
- **90/100 threshold** ensures high-quality outputs
- **Automated validation** across 4 dimensions
- **Specific feedback** tells generators exactly what to fix

### ✅ Context Intelligence
- **Automatic input detection** (what user must provide)
- **Context source mapping** (what to retrieve from Glean)
- **Glean tool selection** (which MCP tools to use)

### ✅ Iterative Refinement
- **Up to 3 attempts** to reach quality threshold
- **Feedback-driven improvement** each iteration
- **XML evolution tracking** shows exactly what changed

### ✅ Flexibility
- **Declarative rules** in JSON/YAML files
- **Example library** for reference patterns
- **Google Drive integration** for easy updates

### ✅ Observability
- **Complete audit trail** via event sourcing
- **Validation reports** with score breakdowns
- **Attempt history** for improvement analysis

---

## Technical Architecture

### Technology Stack
- **TypeScript/Node.js** for workflow orchestration
- **YAML/JSON** for configuration and rules
- **XML** for prompt structure
- **Glean MCP** for agent integration
- **Event Store** for audit trail (future: PostgreSQL)

### Design Patterns
- **Domain-Driven Design (DDD)** for clear boundaries
- **Event Sourcing** for complete history
- **CQRS** for read/write optimization (planned)
- **Anti-Corruption Layer** for external integrations
- **Repository Pattern** for data access

---

## File Outputs

### Generated XML Prompt (`prompt.xml`)
```xml
<metadata>
  <name>m3t-4ng-s1m</name>
  <version>1.0.0</version>
  <description>Create a prompt for meeting summarization</description>
</metadata>

<primary_goal>
  Summarize meeting transcripts into actionable insights with key decisions,
  action items, and discussion points.
</primary_goal>

<input_specification>
  <input>
    <name>meeting_transcript</name>
    <type>string</type>
    <required>true</required>
    <source>user_provided</source>
  </input>
  <input>
    <name>attendee_list</name>
    <type>array</type>
    <required>true</required>
  </input>
</input_specification>

<context_requirements>
  <context>
    <name>previous_meetings</name>
    <source>glean_meeting_lookup</source>
    <query>participants:{{attendee_list}} after:{{meeting_date}}-30d</query>
  </context>
</context_requirements>

<!-- ... instructions, examples, output_format ... -->
```

### Validation Report (`report.json`)
```json
{
  "session_id": "abc-123-xyz",
  "final_score": 95,
  "attempts": 2,
  "duration_ms": 9000,
  "status": "SUCCESS",
  "scoreBreakdown": {
    "structural": 35,
    "completeness": 30,
    "quality": 25,
    "context_quality": 10
  },
  "validation_summary": {
    "total_checks": 12,
    "passed": 12,
    "failed": 0,
    "warnings": 0
  },
  "input_analysis": {
    "required_inputs": 2,
    "optional_inputs": 1,
    "context_sources": 1,
    "glean_integrations": ["mcp__glean__meeting_lookup"]
  }
}
```

---

## Benefits

### For Users
✅ **High-quality prompts** automatically generated and validated
✅ **Context-aware** - knows what inputs and context are needed
✅ **Fast iteration** - feedback loop ensures quality
✅ **Complete transparency** - see exactly what was checked and why

### For Teams
✅ **Shareable standards** - organization-wide quality thresholds
✅ **Easy customization** - update rules without code changes
✅ **Example library** - learn from best practices
✅ **Audit trail** - complete history of all changes

### For Organizations
✅ **Consistent quality** - all prompts meet minimum standards
✅ **Scalable** - add new workflows easily
✅ **Maintainable** - clear domain boundaries
✅ **Evolvable** - event sourcing enables future features

---

## Documentation

Comprehensive architecture documentation available:

- **[QUICK-START.md](./QUICK-START.md)** - Get started in 5 minutes
- **[USAGE.md](./USAGE.md)** - Detailed usage examples
- **[docs/OBSERVATION-AND-TESTING.md](./docs/OBSERVATION-AND-TESTING.md)** - Testing and observability guide
- **[docs/architecture/](./docs/architecture/)** - Complete architecture documentation
  - Reference Architecture (system design)
  - Aggregate Design (DDD patterns)
  - Event Sourcing & CQRS
  - Agent Nodes and Workflow
  - Artifact-Driven Validation

---

## Status

**Version**: 1.0.0
**Status**: ✅ Production Ready
**Last Updated**: 2026-01-26

**What's Implemented**:
- ✅ Two-agent A/B workflow with feedback loops
- ✅ Context discovery and input analysis
- ✅ Artifact-driven validation system
- ✅ Complete DDD domain model
- ✅ Event sourcing architecture
- ✅ Makefile CLI interface

**What's Next**:
- [ ] PostgreSQL event store (persistent history)
- [ ] CQRS with optimized read models
- [ ] REST API for workflow execution
- [ ] Web UI dashboard
- [ ] Google Drive artifact storage integration

---

**Built with industry best practices for enterprise AI systems.**
