# Vertical Service Design Blueprint
## Integrated A/B Prompt Engineering Workflow

**Version**: 1.0.0
**Last Updated**: 2026-01-26
**Status**: Active

---

## Table of Contents

1. [Overview](#overview)
2. [Complete Workflow Diagram](#complete-workflow-diagram)
3. [Swim Lane Definitions](#swim-lane-definitions)
4. [Hop-by-Hop Detail](#hop-by-hop-detail)
5. [Agent Contract Specifications](#agent-contract-specifications)
6. [Artifact Loading Map](#artifact-loading-map)
7. [Bounded Context Map](#bounded-context-map)
8. [Quality Gates and Decision Logic](#quality-gates-and-decision-logic)
9. [Performance Metrics](#performance-metrics)

---

## Overview

This service design blueprint visualizes the **Integrated A/B Prompt Engineering Workflow** as a vertical service blueprint, showing how a user request flows through 6 distinct workflow hops with active orchestration, quality gates, and feedback loops.

### Design Philosophy

**Active Orchestration**: The system features a **prominent Orchestration Agent** (🎯) that actively coordinates all workflow execution. This is NOT a passive routing layer - it's an intelligent decision-making agent that:
- Manages workflow sessions with unique tracking IDs
- Routes all inter-agent communication
- Makes critical quality gate decisions (score ≥ 90 threshold)
- Controls feedback loops when validation fails
- Tracks attempt state to prevent infinite loops (max 3 attempts)
- Records all domain events for complete audit trail
- Handles failures gracefully with structured responses

### Workflow Summary

```
User Request → Context Discovery → Generation → Validation → [Feedback Loop if needed] → Output
                        ↓                ↓            ↓              ↓                    ↓
                      HOP 1            HOP 2        HOP 3          HOP 4-5             HOP 6
                                                                (if score < 90)
```

**Success Path** (2 attempts):
1. HOP 1: Analyze context and identify inputs
2. HOP 2: Generate XML prompt (attempt 1)
3. HOP 3: Validate quality → **Score: 85/100** ❌ (< 90 threshold)
4. HOP 4: Refine with feedback (attempt 2)
5. HOP 5: Re-validate → **Score: 95/100** ✅ (≥ 90 threshold)
6. HOP 6: Save outputs and complete session

---

## Complete Workflow Diagram

This diagram shows all 6 hops flowing vertically through horizontal swim lanes representing different components and bounded contexts.

```
┌────────────┬═══════════════════┬──────────────┬──────────────┬──────────────┬────────────┐
│   USER/    │ 🎯 ORCHESTRATION  │   CONTEXT    │   AGENT A    │   AGENT B    │ ARTIFACTS  │
│  UX PLANE  │      AGENT        │  DISCOVERY   │  (Generator) │ (Validator)  │ Repository │
│            │ (Active Coord.)   │              │              │              │            │
│            │ WorkflowOrch.     │ ContextDisc. │ PromptEng.   │ PromptEng.   │ Infra.     │
│            │ (Core Domain)     │ (Supporting) │ (Core)       │ (Core)       │ (Generic)  │
├────────────┼═══════════════════┼──────────────┼──────────────┼──────────────┼────────────┤
│            │                   │              │              │              │            │
│ Request:   │                   │              │              │              │            │
│ "Create    │                   │              │              │              │            │
│ prompt for │                   │              │              │              │            │
│ meeting    │                   │              │              │              │            │
│ summary"   │                   │              │              │              │            │
│     │      │                   │              │              │              │            │
│     └──────┼══════════════════>│              │              │              │            │
│            │ ╔═══════════════╗ │              │              │              │            │
│            │ ║ ORCHESTRATOR  ║ │              │              │              │            │
│            │ ║ HOP 1: START  ║ │              │              │              │            │
│            │ ║ Session:      ║ │              │              │              │            │
│            │ ║ wf-abc-123    ║ │              │              │              │            │
│            │ ║ Route to      ║ │              │              │              │            │
│            │ ║ Context Disc. ║ │              │              │              │            │
│            │ ╚═══════════════╝ │              │              │              │            │
│            │       ║           │              │              │              │            │
│            │       ╠═══════════╬═════════════>│              │              │            │
│            │       ║           │ Analyze Task │              │              │            │
│            │       ║           │ Pattern:     │              │              │            │
│            │       ║           │ "meeting"    │              │              │            │
│            │       ║           │              │              │              │            │
│            │       ║           │ Outputs:     │              │              │            │
│            │       ║           │ • transcript │              │              │            │
│            │       ║           │   (required) │              │              │            │
│            │       ║           │ • attendees  │              │              │            │
│            │       ║           │   (required) │              │              │            │
│            │       ║           │ • prev_mtgs  │              │              │            │
│            │       ║           │   (Glean)    │              │              │            │
│            │       ║           │              │              │              │            │
│            │ ╔═══════════════╗ │              │              │              │            │
│            │ ║ ORCHESTRATOR  ║◄┼──────────────┤              │              │            │
│            │ ║ HOP 2: ROUTE  ║ │              │              │              │            │
│            │ ║ To Agent A    ║ │              │              │              │            │
│            │ ║ Attempt #1    ║ │              │              │              │            │
│            │ ╚═══════════════╝ │              │              │              │            │
│            │       ║           │              │              │              │            │
│            │       ╠═══════════╬══════════════╬═════════════>│              │            │
│            │       ║           │              │              │              │            │
│            │       ║           │              │ ┌──────────┐ │              │◄═══════════┤
│            │       ║           │              │ │ AGENT A  │ │              │ Load:      │
│            │       ║           │              │ │ Bounded  │◄┼──────────────┼────────────┤
│            │       ║           │              │ │ Context: │ │              │• spec.yaml │
│            │       ║           │              │ │PromptEng │ │              │• template  │
│            │       ║           │              │ └──────────┘ │              │• instruct  │
│            │       ║           │              │              │              │• examples/ │
│            │       ║           │              │ Contract:    │              │  (good)    │
│            │       ║           │              │ ────────────│              │            │
│            │       ║           │              │ IN:          │              │ repo://    │
│            │       ║           │              │  user_req    │              │ gdrive://  │
│            │       ║           │              │  analyze_ctx │              │            │
│            │       ║           │              │  feedback:[] │              │            │
│            │       ║           │              │  prev:null   │              │            │
│            │       ║           │              │  attempt:1   │              │            │
│            │       ║           │              │              │              │            │
│            │       ║           │              │ OUT:         │              │            │
│            │       ║           │              │  xml_prompt  │              │            │
│            │       ║           │              │  prompt_name │              │            │
│            │       ║           │              │  input_analy │              │            │
│            │       ║           │              │  metadata    │              │            │
│            │       ║           │              │      │       │              │            │
│            │ ╔═══════════════╗ │              │      │       │              │            │
│            │ ║ ORCHESTRATOR  ║◄┼──────────────┼──────┘       │              │            │
│            │ ║ HOP 3: ROUTE  ║ │              │              │              │            │
│            │ ║ To Agent B    ║ │              │              │              │            │
│            │ ╚═══════════════╝ │              │              │              │            │
│            │       ║           │              │              │              │            │
│            │       ╠═══════════╬══════════════╬══════════════╬═════════════>│            │
│            │       ║           │              │              │              │            │
│            │       ║           │              │              │ ┌──────────┐ │◄═══════════┤
│            │       ║           │              │              │ │ AGENT B  │ │ Load:      │
│            │       ║           │              │              │ │ Bounded  │◄┼────────────┤
│            │       ║           │              │              │ │ Context: │ │• spec.yaml │
│            │       ║           │              │              │ │PromptEng │ │• instruct  │
│            │       ║           │              │              │ └──────────┘ │• val-rules │
│            │       ║           │              │              │              │• val-std   │
│            │       ║           │              │              │ Contract:    │• examples/ │
│            │       ║           │              │              │ ────────────│  (good+bad)│
│            │       ║           │              │              │ IN:          │            │
│            │       ║           │              │              │  xml_prompt  │ repo://    │
│            │       ║           │              │              │  prev_val:[] │ gdrive://  │
│            │       ║           │              │              │  attempt:1   │            │
│            │       ║           │              │              │              │            │
│            │       ║           │              │              │ OUT:         │            │
│            │       ║           │              │              │  isValid:❌  │            │
│            │       ║           │              │              │  score:85    │            │
│            │       ║           │              │              │  checks:[]   │            │
│            │       ║           │              │              │  feedback:[] │            │
│            │       ║           │              │              │  breakdown   │            │
│            │       ║           │              │              │      │       │            │
│            │ ╔═══════════════╗ │              │              │      │       │            │
│            │ ║ ORCHESTRATOR  ║◄┼──────────────┼──────────────┼──────┘       │            │
│            │ ║ QUALITY GATE  ║ │              │              │              │            │
│            │ ║ ─────────────║ │              │              │              │            │
│            │ ║ Decision:     ║ │              │              │              │            │
│            │ ║ • Score: 85   ║ │              │              │              │            │
│            │ ║ • 85 < 90 ✗   ║ │              │              │              │            │
│            │ ║ • Attempt: 1  ║ │              │              │              │            │
│            │ ║ • 1 < 3 ✓     ║ │              │              │              │            │
│            │ ║ → TRIGGER     ║ │              │              │              │            │
│            │ ║   FEEDBACK    ║ │              │              │              │            │
│            │ ║   LOOP!       ║ │              │              │              │            │
│            │ ╚═══════════════╝ │              │              │              │            │
│            │       ║           │              │              │              │            │
│            │ ╔═══════════════╗ │              │              │              │            │
│            │ ║ ORCHESTRATOR  ║ │              │              │              │            │
│            │ ║ HOP 4: REFINE ║ │              │              │              │            │
│            │ ║ Route to A    ║ │              │              │              │            │
│            │ ║ w/ Feedback   ║ │              │              │              │            │
│            │ ║ Attempt #2    ║ │              │              │              │            │
│            │ ╚═══════════════╝ │              │              │              │            │
│            │       ║           │              │              │              │            │
│            │       ╠═══════════╬══════════════╬═════════════>│              │            │
│            │ FEEDBACK LOOP     │              │              │              │            │
│            │       ║           │              │              │              │            │
│            │       ║           │              │ ┌──────────┐ │              │            │
│            │       ║           │              │ │ AGENT A  │ │              │ (Reuse     │
│            │       ║           │              │ │ Refine   │ │              │  cached    │
│            │       ║           │              │ │ w/Feedbk │ │              │  artifacts │
│            │       ║           │              │ └──────────┘ │              │  from      │
│            │       ║           │              │              │              │  HOP 2)    │
│            │       ║           │              │ Contract:    │              │            │
│            │       ║           │              │ ────────────│              │            │
│            │       ║           │              │ IN:          │              │            │
│            │       ║           │              │  user_req    │              │            │
│            │       ║           │              │  feedback:   │              │            │
│            │       ║           │              │   ["Add ex"  │              │            │
│            │       ║           │              │    "Add val" │              │            │
│            │       ║           │              │    "Improve"]│              │            │
│            │       ║           │              │  prev_att    │              │            │
│            │       ║           │              │  attempt:2   │              │            │
│            │       ║           │              │              │              │            │
│            │       ║           │              │ OUT:         │              │            │
│            │       ║           │              │  xml_v2      │              │            │
│            │       ║           │              │  name(same)  │              │            │
│            │       ║           │              │  metadata:   │              │            │
│            │       ║           │              │   refine:[]  │              │            │
│            │       ║           │              │      │       │              │            │
│            │ ╔═══════════════╗ │              │      │       │              │            │
│            │ ║ ORCHESTRATOR  ║◄┼──────────────┼──────┘       │              │            │
│            │ ║ HOP 5: ROUTE  ║ │              │              │              │            │
│            │ ║ To Agent B    ║ │              │              │              │            │
│            │ ║ Re-validate   ║ │              │              │              │            │
│            │ ╚═══════════════╝ │              │              │              │            │
│            │       ║           │              │              │              │            │
│            │       ╠═══════════╬══════════════╬══════════════╬═════════════>│            │
│            │       ║           │              │              │              │            │
│            │       ║           │              │              │ ┌──────────┐ │            │
│            │       ║           │              │              │ │ AGENT B  │ │ (Reuse     │
│            │       ║           │              │              │ │ Re-valid │ │  cached    │
│            │       ║           │              │              │ │ Attempt2 │ │  artifacts │
│            │       ║           │              │              │ └──────────┘ │  from      │
│            │       ║           │              │              │              │  HOP 3)    │
│            │       ║           │              │              │ Contract:    │            │
│            │       ║           │              │              │ ────────────│            │
│            │       ║           │              │              │ IN:          │            │
│            │       ║           │              │              │  xml_v2      │            │
│            │       ║           │              │  prev_val    │            │            │
│            │       ║           │              │              │   (HOP3 res) │            │
│            │       ║           │              │              │  attempt:2   │            │
│            │       ║           │              │              │              │            │
│            │       ║           │              │              │ OUT:         │            │
│            │       ║           │              │              │  isValid:✅  │            │
│            │       ║           │              │              │  score:95    │            │
│            │       ║           │              │              │  checks:12/12│            │
│            │       ║           │              │              │  feedback:[] │            │
│            │       ║           │              │              │  breakdown   │            │
│            │       ║           │              │              │      │       │            │
│            │ ╔═══════════════╗ │              │              │      │       │            │
│            │ ║ ORCHESTRATOR  ║◄┼──────────────┼──────────────┼──────┘       │            │
│            │ ║ QUALITY GATE  ║ │              │              │              │            │
│            │ ║ ─────────────║ │              │              │              │            │
│            │ ║ Decision:     ║ │              │              │              │            │
│            │ ║ • Score: 95   ║ │              │              │              │            │
│            │ ║ • 95 >= 90 ✓  ║ │              │              │              │            │
│            │ ║ • isValid: ✓  ║ │              │              │              │            │
│            │ ║ → EXIT LOOP   ║ │              │              │              │            │
│            │ ║ → PROCEED TO  ║ │              │              │              │            │
│            │ ║   SAVE        ║ │              │              │              │            │
│            │ ╚═══════════════╝ │              │              │              │            │
│            │       ║           │              │              │              │            │
│            │ ╔═══════════════╗ │              │              │              │            │
│            │ ║ ORCHESTRATOR  ║ │              │              │              │            │
│            │ ║ HOP 6: SAVE   ║ │              │              │              │            │
│            │ ║ Generate:     ║ │              │              │              │            │
│            │ ║ • prompt.xml  ║ │              │              │              │            │
│            │ ║ • report.json ║ │              │              │              │            │
│            │ ║ Complete      ║ │              │              │              │            │
│            │ ║ Session       ║ │              │              │              │            │
│            │ ║ Publish Event ║ │              │              │              │            │
│            │ ╚═══════════════╝ │              │              │              │            │
│            │       ║           │              │              │              │            │
│ ◄══════════┼═══════╝           │              │              │              │            │
│            │                   │              │              │              │            │
│ Outputs:   │                   │              │              │              │            │
│ ──────────│                   │              │              │              │            │
│ Files:     │                   │              │              │              │            │
│ • mtg-sum  │                   │              │              │              │            │
│   -ext.xml │                   │              │              │              │            │
│ • mtg-sum  │                   │              │              │              │            │
│   -ext-ab  │                   │              │              │              │            │
│   -report  │                   │              │              │              │            │
│   .json    │                   │              │              │              │            │
│            │                   │              │              │              │            │
│ Report:    │                   │              │              │              │            │
│ • Score:95 │                   │              │              │              │            │
│ • Valid: ✓ │                   │              │              │              │            │
│ • Attempts │                   │              │              │              │            │
│   : 2      │                   │              │              │              │            │
│ • Duration │                   │              │              │              │            │
│   : 8.2s   │                   │              │              │              │            │
│            │                   │              │              │              │            │
└────────────┴───────────────────┴──────────────┴──────────────┴──────────────┴────────────┘

Legend:
════>  Synchronous call from/to orchestration agent (double-line emphasis)
────>  Standard synchronous call
◄════  Artifact loading (from repo:// or gdrive:// static locations)
╔══╗   Orchestration Agent box (double-line border for emphasis)
┌──┐   Agent A/B contract boxes with bounded context labels

Contract Format:
  IN:  Input parameters
  OUT: Output values

Bounded Contexts:
  WorkflowOrchestration → Core Domain (orchestrator)
  PromptEngineering → Core Domain (Agent A + Agent B)
  ContextDiscovery → Supporting Domain
  Infrastructure → Generic Subdomain (artifact storage)

Artifact Sources:
  repo://    Current location (Git repository)
  gdrive://  Future location (Google Drive integration)
```

---

## Swim Lane Definitions

### 1. User/UX Plane (Leftmost, 15% width)

**Role**: External user interaction touchpoints

**Contains**:
- User request input (top)
- Final outputs delivered (bottom)
- Success/failure notifications

**Bounded Context**: N/A (external to system)

**Interactions**:
- Sends request to Orchestration Agent
- Receives final XML file + JSON report

---

### 2. 🎯 Orchestration Agent (Center-Left, 25% width)

**Role**: **Active decision-making coordinator** (NOT a passive routing layer)

**Bounded Context**: **WorkflowOrchestration** (Core Domain)

**Visual Treatment**: Double-line borders (╔══╗) to emphasize active coordination role

**Core Responsibilities**:
1. **Session Management**: Creates and tracks workflow sessions with unique IDs (`wf-abc-123`)
2. **Hop Routing**: Actively routes all requests between Context Discovery, Agent A, and Agent B
3. **Attempt Tracking**: Manages retry attempts (1-3 max) with full state preservation
4. **Quality Gate Decisions**: Evaluates validation results and decides pass/retry/fail
5. **Feedback Loop Control**: Triggers Agent A refinement when score < 90
6. **Event Recording**: Publishes domain events for complete audit trail
7. **Error Handling**: Catches failures and provides structured error responses
8. **Output Generation**: Creates final XML and JSON report files

**Critical Logic**:
```javascript
// Quality Gate Decision (HOP 3 and HOP 5)
if (validationResult.qualityScore >= 90 && validationResult.isValid === true) {
  // SUCCESS - Exit loop, proceed to HOP 6
  saveOutput(...)
  return { status: 'SUCCESS', score: validationResult.qualityScore }
}

// Feedback Loop Decision (HOP 3 only if failed)
if (currentAttempt < maxAttempts) {
  // RETRY - Send feedback to Agent A for refinement (HOP 4)
  feedback = validationResult.feedback
  refinedPrompt = await callAgentA({
    user_request,
    feedback,
    previous_attempt: { xml_prompt, prompt_name },
    attempt_number: currentAttempt + 1
  })
} else {
  // MAX ATTEMPTS - Fail workflow
  throw new Error("Max attempts (3) reached without passing validation")
}
```

**Domain Events Published**:
- `WorkflowSessionStarted` (HOP 1)
- `AttemptInitiated` (HOP 2, HOP 4)
- `FeedbackCycleStarted` (HOP 4)
- `FeedbackApplied` (HOP 4)
- `MaxAttemptsReached` (if applicable)
- `WorkflowSessionCompleted` (HOP 6)
- `WorkflowSessionFailed` (if error)

**Configuration**:
- Location: `scripts/run-mcp-workflow-integrated.js`
- Max Attempts: 3
- Success Threshold: 90/100
- Timeout: 120 seconds per agent call

---

### 3. Context Discovery (Center, 15% width)

**Role**: Analyze tasks to identify inputs and context sources

**Bounded Context**: **ContextDiscovery** (Supporting Domain)

**Contains**:
- Task pattern recognition (HOP 1)
- Input identification (required/optional)
- Context source mapping to Glean tools
- Query template generation

**Capabilities**:
- Pattern matching on task descriptions (meeting, code, email, etc.)
- Input specification generation
- Glean MCP tool selection
- Query template creation with variable substitution

**Task Patterns Recognized**:
1. **Meeting tasks** → `meeting_transcript`, `attendee_list` + `glean_meeting_lookup`
2. **Code tasks** → `code_content`, `language` + `glean_code_search`
3. **Customer feedback** → `feedback_text` + `glean_search`
4. **Email tasks** → `purpose`, `recipient` + `glean_search`
5. **Fallback** → `user_input` (generic)

**Output Format**:
```yaml
required_inputs: [{name, type, source, description}]
optional_inputs: [{name, type, source, default}]
context_sources: [{name, source, query}]
glean_integrations: [tool_names]
```

**Artifacts Loaded**: None (uses built-in pattern matching logic)

---

### 4. Agent A - Prompt Generator (Center-Right, 20% width)

**Role**: Generate well-structured XML prompts with context analysis

**Bounded Context**: **PromptEngineering** (Core Domain)

**Agent ID**: `prompt-generator-001`

**Capabilities**:
- Parse semantic requests into structured components
- Generate XML with proper tag hierarchy (max 3 levels)
- Apply cognitive containerization for examples
- Analyze tasks to identify required inputs
- Identify context sources from Glean
- Refine prompts based on validation feedback
- Handle multi-attempt refinement loops

**Appears in Workflow**:
- HOP 2: Initial generation (attempt 1)
- HOP 4: Refinement with feedback (attempt 2+)

**Visual Representation**: Contract box showing IN/OUT parameters and bounded context label

**Artifacts Loaded** (HOP 2 and HOP 4):
```
repo://agents/prompt-generator/agent-spec.yaml
repo://agents/prompt-generator/prompt-template.xml
repo://workflow-orchestration/workflows/prompt-generation/stages/01-generate-prompt/instructions.md
repo://workflow-orchestration/workflows/prompt-generation/stages/01-generate-prompt/examples/
repo://workflow-orchestration/global/examples/good/*.xml

Future:
gdrive://agents/prompt-generator/agent-spec.yaml
gdrive://workflows/prompt-generation/stages/01-generate-prompt/instructions.md
gdrive://global/examples/good/*.xml
```

**Configuration**:
- Model: claude-sonnet-4
- Temperature: 0.3 (creative but consistent)
- Max Tokens: 4000
- Expected Latency: 2-3 seconds

---

### 5. Agent B - Prompt Validator (Right, 20% width)

**Role**: Validate XML prompts and provide actionable feedback

**Bounded Context**: **PromptEngineering** (Core Domain)

**Agent ID**: `prompt-validator-001`

**Capabilities**:
- Parse and validate XML structure
- Check tag hierarchy and nesting depth (max 3)
- Verify completeness of required sections
- Calculate weighted quality scores (4 dimensions)
- Generate actionable feedback for refinement
- Compare against good/bad example patterns
- Track validation across multiple attempts
- Validate input specifications and context requirements

**Appears in Workflow**:
- HOP 3: Initial validation (attempt 1)
- HOP 5: Re-validation (attempt 2+)

**Visual Representation**: Contract box showing IN/OUT parameters and bounded context label

**Artifacts Loaded** (HOP 3 and HOP 5):
```
repo://agents/prompt-validator/agent-spec.yaml
repo://workflow-orchestration/workflows/prompt-generation/stages/02-validate-quality/instructions.md
repo://workflow-orchestration/workflows/prompt-generation/stages/02-validate-quality/validation-rules.json
repo://workflow-orchestration/global/config/validation-standards.json
repo://workflow-orchestration/global/examples/good/*.xml
repo://workflow-orchestration/global/examples/bad/*.xml

Future:
gdrive://agents/prompt-validator/agent-spec.yaml
gdrive://workflows/prompt-generation/stages/02-validate-quality/validation-rules.json
gdrive://global/config/validation-standards.json
gdrive://global/examples/good/*.xml
gdrive://global/examples/bad/*.xml
```

**Scoring Formula**:
```
Dimensions:
  Structural (35%): XML well-formed, required sections, tag hierarchy, naming
  Completeness (30%): Section content, examples, instructions, input spec
  Quality (25%): Clarity, examples effectiveness, constraints
  Context Quality (10%): Input definitions, Glean query validity

Base score: 100
Penalties:
  - Error: -20 per error
  - Warning: -5 per warning
  - Info: 0
Bonuses:
  - Extra good example: +2 (max +10)
  - Extra bad example: +2 (max +10)

Final score = min(100, max(0, base + bonuses - penalties))
isValid = (score >= 90) AND (errors == 0)
```

**Configuration**:
- Model: claude-sonnet-4
- Temperature: 0 (deterministic scoring)
- Max Tokens: 2000
- Expected Latency: 1.5-2 seconds

---

### 6. Artifact Repository (Rightmost, 10% width)

**Role**: Static configuration and example storage

**Bounded Context**: **Infrastructure** (Generic Subdomain)

**Contains**:
- Agent specifications (contracts)
- Configuration files (validation standards, rules)
- Instruction documents (guidance for agents)
- Example libraries (good/bad XML prompts)
- Template files

**Current Storage**: Git repository at `repo://`

**Future Storage**: Google Drive at `gdrive://OrgName-PromptEngineering/`

**Benefits of Google Drive Migration**:
- Non-technical users can add examples (upload XML to folder)
- Update validation rules (edit JSON, export from Google Sheets)
- Version history via Google Drive
- Shared across organization
- No Git knowledge required
- Collaborative editing

**Artifact Types**:
1. **Contracts**: `agent-spec.yaml` (defines input/output schemas)
2. **Configuration**: `validation-standards.json`, `validation-rules.json`
3. **Instructions**: `instructions.md` (appended to agent system prompts)
4. **Templates**: `prompt-template.xml` (boilerplate structure)
5. **Examples**: `good/*.xml`, `bad/*.xml` (reference patterns and anti-patterns)

---

## Hop-by-Hop Detail

### HOP 1: Context Discovery

**Time**: 0s → 1.2s (1.2s duration)

**Swim Lanes Involved**: User → 🎯 Orchestration Agent → Context Discovery

**Orchestration Agent Role**:
- Receives user request
- Creates workflow session (`wf-abc-123`)
- Routes to Context Discovery node
- Publishes `WorkflowSessionStarted` event

**Input Contract**:
```yaml
user_request:
  type: string
  required: true
  min_length: 10
  example: "Create a prompt for meeting summarization"

analyze_context:
  type: boolean
  required: false
  default: true
  description: "Enable context analysis to identify inputs and sources"
```

**Processing**:
1. Parse `user_request` for task patterns
2. Match against known patterns (meeting, code, email, etc.)
3. Identify required inputs based on task type
4. Identify optional inputs with defaults
5. Map context sources to Glean MCP tools
6. Generate query templates with variable substitution

**Output Contract**:
```yaml
required_inputs:
  type: array
  items:
    name: string
    type: string  # string, array, object
    source: enum[user_provided, glean_retrieved]
    description: string
  example:
    - name: meeting_transcript
      type: string
      source: user_provided
      description: "Full text transcript of the meeting"
    - name: attendee_list
      type: array
      source: user_provided
      description: "List of meeting attendees"

optional_inputs:
  type: array
  items:
    name: string
    type: string
    source: string
    default: any
  example:
    - name: meeting_date
      type: string
      source: user_provided
      default: "today"

context_sources:
  type: array
  items:
    name: string
    source: string  # Glean tool name
    query: string   # Template with {{variables}}
    required: boolean
  example:
    - name: previous_meetings
      source: glean_meeting_lookup
      query: "participants:{{attendee_list}} after:{{meeting_date}}-30d"
      required: false

glean_integrations:
  type: array
  items: string
  example: ["mcp__glean__meeting_lookup", "mcp__glean__search"]
```

**Artifacts Loaded**: None (built-in pattern matching)

**Events Published**:
- `TaskAnalyzed`
- `InputsIdentified`
- `ContextSourcesDiscovered`

**Bounded Context**: ContextDiscovery (Supporting Domain)

**Performance**:
- Expected: 1.2s
- Max: 5s

---

### HOP 2: Generation (Attempt 1)

**Time**: 1.2s → 3.2s (2.0s duration)

**Swim Lanes Involved**: 🎯 Orchestration Agent → Agent A → Artifacts

**Orchestration Agent Role**:
- Routes input analysis from HOP 1 to Agent A
- Tracks attempt #1
- Publishes `AttemptInitiated` event

**Input Contract**:
```yaml
user_request:
  type: string
  required: true
  example: "Create a prompt for meeting summarization"

analyze_context:
  type: boolean
  default: true

input_analysis:
  type: object
  required: true
  description: "Output from HOP 1 Context Discovery"
  properties:
    required_inputs: array
    optional_inputs: array
    context_sources: array
    glean_integrations: array

feedback:
  type: array
  items: string
  required: false
  default: []
  description: "Empty on first attempt"

previous_attempt:
  type: object
  required: false
  default: null
  description: "Null on first attempt"

attempt_number:
  type: integer
  required: true
  default: 1
  minimum: 1
  maximum: 3
```

**Processing**:
1. Load agent specification (`agent-spec.yaml`)
2. Load artifacts:
   - Prompt template (`prompt-template.xml`)
   - Instructions (`instructions.md`)
   - Good examples (`good/*.xml`)
3. Parse `user_request` into components (goal, role, task, context)
4. Generate XML structure following template
5. Populate `<input_specification>` from `input_analysis`
6. Populate `<context_requirements>` with Glean sources
7. Add examples using cognitive containerization
8. Generate unique prompt name (`xxx-xxx-xxx` format)

**Output Contract**:
```yaml
xml_prompt:
  type: string
  required: true
  description: "Complete XML-structured prompt"
  example: |
    <prompt>
      <metadata>
        <prompt_name>mtg-sum-ext</prompt_name>
        <version>1.0</version>
      </metadata>
      <primary_goal>Extract key information from meeting transcripts</primary_goal>
      <role>You are an expert meeting analyst...</role>
      <task>Analyze meeting transcript and extract...</task>
      <input_specification>...</input_specification>
      <context_requirements>...</context_requirements>
      <instructions>...</instructions>
      <output_format>...</output_format>
      <examples>...</examples>
    </prompt>

prompt_name:
  type: string
  required: true
  pattern: "^[a-z0-9]{3}-[a-z0-9]{3}-[a-z0-9]{3}$"
  example: "mtg-sum-ext"

input_analysis:
  type: object
  required: false
  description: "Preserved from HOP 1 for downstream use"

generation_metadata:
  type: object
  required: false
  properties:
    attempt: integer
    timestamp: string
    context_analysis_performed: boolean
    refinements_applied: array[string]
    feedback_addressed: array[string]
```

**Artifacts Loaded**:
| Artifact | Path (repo://) | Path (gdrive://) | Purpose |
|----------|---------------|------------------|---------|
| Agent Spec | `agents/prompt-generator/agent-spec.yaml` | `agents/prompt-generator/agent-spec.yaml` | Contract definition |
| Template | `agents/prompt-generator/prompt-template.xml` | `agents/prompt-generator/prompt-template.xml` | XML boilerplate |
| Instructions | `workflow-orchestration/workflows/prompt-generation/stages/01-generate-prompt/instructions.md` | `workflows/prompt-generation/stages/01-generate-prompt/instructions.md` | Generation guidance |
| Good Examples | `workflow-orchestration/global/examples/good/*.xml` | `global/examples/good/*.xml` | Reference patterns |

**Events Published**:
- `AttemptInitiated`
- `PromptGenerated`

**Bounded Context**: PromptEngineering (Core Domain)

**Performance**:
- Expected: 2.0s
- Max: 10s

---

### HOP 3: Validation (Attempt 1)

**Time**: 3.2s → 4.7s (1.5s duration)

**Swim Lanes Involved**: Agent A → 🎯 Orchestration Agent → Agent B → Artifacts

**Orchestration Agent Role**:
- Routes XML from Agent A to Agent B
- Receives validation result
- **CRITICAL QUALITY GATE DECISION**:
  - Evaluates `qualityScore` against threshold (90)
  - Checks `isValid` boolean
  - Decides: PASS (proceed to HOP 6) or RETRY (proceed to HOP 4)

**Input Contract**:
```yaml
xml_prompt:
  type: string
  required: true
  description: "XML output from Agent A (HOP 2)"

previous_validation_results:
  type: array
  items: object
  required: false
  default: []
  description: "Empty on first validation"

attempt_number:
  type: integer
  required: true
  default: 1
  minimum: 1
  maximum: 3
```

**Processing**:
1. Load agent specification (`agent-spec.yaml`)
2. Load artifacts:
   - Validation rules (`validation-rules.json`)
   - Global standards (`validation-standards.json`)
   - Instructions (`instructions.md`)
   - Good examples (`good/*.xml`)
   - Bad examples (`bad/*.xml`)
3. Parse XML structure
4. Run 12 validation checks across 4 dimensions:
   - **Structural (35%)**: XML well-formed, required sections, hierarchy, naming
   - **Completeness (30%)**: Content quality, examples, input spec present
   - **Quality (25%)**: Clarity, examples effectiveness, coherence
   - **Context Quality (10%)**: Input definitions, Glean query validity
5. Calculate weighted score (0-100)
6. Generate actionable feedback if score < 90
7. Create detailed check results

**Output Contract** (Typical First Attempt - FAIL):
```yaml
isValid:
  type: boolean
  value: false
  description: "False because score < 90"

qualityScore:
  type: number
  value: 85
  minimum: 0
  maximum: 100

checks:
  type: array
  length: 12
  example:
    - rule_id: xml_well_formed
      status: pass
      message: "XML is valid and parseable"
      severity: info
      section: structural
      score_impact: 0
    - rule_id: examples_quality
      status: fail
      message: "Only 1 good example found, minimum is 2"
      severity: warning
      section: completeness
      score_impact: -5
    - rule_id: input_specification_present
      status: fail
      message: "Missing validation rules in input_specification"
      severity: warning
      section: completeness
      score_impact: -5

feedback:
  type: array
  items: string
  length: 3
  example:
    - "Add at least one more good example to meet minimum requirement (2)"
    - "Add validation rules for all required inputs in <input_specification>"
    - "Improve specificity in <instructions> section with step-by-step guidance"

recommendations:
  type: array
  items: string
  example:
    - "Consider adding optional <constraints> section"

scoreBreakdown:
  type: object
  properties:
    structural:
      value: 35
      max: 35
      description: "All structural checks passed"
    completeness:
      value: 20
      max: 30
      description: "Missing examples and validation rules (-10)"
    quality:
      value: 25
      max: 25
      description: "Quality checks passed"
    context_quality:
      value: 5
      max: 10
      description: "Input spec incomplete (-5)"
    bonuses: 0
    penalties: -15

examplesAnalysis:
  good_examples_found: 1
  bad_examples_found: 1
  examples_quality_score: 50

contextValidation:
  input_specification_present: true
  context_requirements_present: true
  required_inputs_count: 2
  context_sources_count: 1
  glean_integrations: ["mcp__glean__meeting_lookup"]
  validation_issues:
    - "Missing validation rules for required inputs"
```

**Artifacts Loaded**:
| Artifact | Path (repo://) | Path (gdrive://) | Purpose |
|----------|---------------|------------------|---------|
| Agent Spec | `agents/prompt-validator/agent-spec.yaml` | `agents/prompt-validator/agent-spec.yaml` | Contract definition |
| Instructions | `workflow-orchestration/workflows/prompt-generation/stages/02-validate-quality/instructions.md` | `workflows/prompt-generation/stages/02-validate-quality/instructions.md` | Validation guidance |
| Validation Rules | `workflow-orchestration/workflows/prompt-generation/stages/02-validate-quality/validation-rules.json` | `workflows/prompt-generation/stages/02-validate-quality/validation-rules.json` | Scoring rules |
| Global Standards | `workflow-orchestration/global/config/validation-standards.json` | `global/config/validation-standards.json` | Thresholds |
| Good Examples | `workflow-orchestration/global/examples/good/*.xml` | `global/examples/good/*.xml` | Reference patterns |
| Bad Examples | `workflow-orchestration/global/examples/bad/*.xml` | `global/examples/bad/*.xml` | Anti-patterns |

**Events Published**:
- `PromptValidated`
- `FeedbackGenerated`

**Bounded Context**: PromptEngineering (Core Domain)

**Decision Point** (Orchestration Agent):
```
Score: 85/100
Threshold: 90/100
Decision: 85 < 90 → FAIL

Current Attempt: 1
Max Attempts: 3
Decision: 1 < 3 → TRIGGER FEEDBACK LOOP

Action: Proceed to HOP 4 (Refinement)
```

**Performance**:
- Expected: 1.5s
- Max: 8s

---

### HOP 4: Refinement with Feedback

**Time**: 4.7s → 6.7s (2.0s duration)

**Swim Lanes Involved**: Agent B ← 🎯 Orchestration Agent → Agent A → Artifacts

**Direction**: BACKWARD (Agent B feedback → Agent A refinement)

**Orchestration Agent Role**:
- **TRIGGERS FEEDBACK LOOP** based on HOP 3 decision
- Sends validation feedback to Agent A
- Increments attempt counter (1 → 2)
- Preserves previous attempt for comparison
- Publishes `FeedbackCycleStarted` event

**Input Contract**:
```yaml
user_request:
  type: string
  required: true
  description: "Original request (preserved)"
  example: "Create a prompt for meeting summarization"

analyze_context:
  type: boolean
  default: true

input_analysis:
  type: object
  required: true
  description: "Preserved from HOP 1"

feedback:
  type: array
  items: string
  required: true
  description: "Actionable feedback from HOP 3 validation"
  example:
    - "Add at least one more good example to meet minimum requirement (2)"
    - "Add validation rules for all required inputs in <input_specification>"
    - "Improve specificity in <instructions> section with step-by-step guidance"

previous_attempt:
  type: object
  required: true
  description: "Output from HOP 2 for comparison and refinement"
  properties:
    xml_prompt:
      type: string
      description: "First attempt XML"
    prompt_name:
      type: string
      description: "Keep same name across attempts"

attempt_number:
  type: integer
  required: true
  value: 2
  description: "Incremented by orchestrator"
```

**Processing**:
1. Load same artifacts as HOP 2 (cached if possible)
2. Parse `previous_attempt.xml_prompt`
3. Analyze each feedback item
4. Apply targeted refinements:
   - **Feedback 1** ("Add good example") → Add 1-2 more `<good>` examples
   - **Feedback 2** ("Add validation rules") → Enhance `<input_specification>` with validation rules
   - **Feedback 3** ("Improve specificity") → Restructure `<instructions>` with numbered steps
5. Preserve `prompt_name` (same across attempts)
6. Generate refined XML
7. Document refinements in metadata

**Output Contract**:
```yaml
xml_prompt:
  type: string
  required: true
  description: "Refined XML addressing feedback"

prompt_name:
  type: string
  required: true
  value: "mtg-sum-ext"
  description: "SAME as attempt 1"

input_analysis:
  type: object
  description: "Preserved (unchanged)"

generation_metadata:
  type: object
  required: true
  properties:
    attempt: 2
    refinements_applied:
      type: array[string]
      example:
        - "Added 2 additional good examples"
        - "Added validation rules to input_specification"
        - "Restructured instructions as numbered steps"
    feedback_addressed:
      type: array[string]
      description: "Maps to feedback items from HOP 3"
      example:
        - "Feedback 1: Add good example → DONE"
        - "Feedback 2: Add validation rules → DONE"
        - "Feedback 3: Improve specificity → DONE"
    timestamp: string
    context_analysis_performed: boolean
```

**Artifacts Loaded**:
- **Reuse from HOP 2** (cached to improve performance)
- Same agent spec, template, instructions, examples

**Events Published**:
- `FeedbackCycleStarted`
- `FeedbackApplied`
- `AttemptInitiated` (attempt 2)
- `PromptGenerated` (attempt 2)

**Bounded Context**:
- **WorkflowOrchestration** (feedback loop control)
- **PromptEngineering** (refinement generation)

**Performance**:
- Expected: 2.0s
- Max: 10s

---

### HOP 5: Re-Validation (Attempt 2)

**Time**: 6.7s → 8.2s (1.5s duration)

**Swim Lanes Involved**: Agent A → 🎯 Orchestration Agent → Agent B → Artifacts

**Orchestration Agent Role**:
- Routes refined XML from Agent A (HOP 4) to Agent B
- Receives validation result
- **SECOND QUALITY GATE DECISION**:
  - Evaluates `qualityScore` against threshold (90)
  - Checks `isValid` boolean
  - Decides: PASS (proceed to HOP 6) or RETRY (if attempts < 3, loop to HOP 4 again)

**Input Contract**:
```yaml
xml_prompt:
  type: string
  required: true
  description: "Refined XML output from Agent A (HOP 4)"

previous_validation_results:
  type: array
  items: object
  required: true
  description: "Includes HOP 3 validation result"
  example:
    - attempt: 1
      score: 85
      isValid: false
      feedback: [...]

attempt_number:
  type: integer
  required: true
  value: 2
```

**Processing**:
1. Load same artifacts as HOP 3 (cached if possible)
2. Parse refined XML structure
3. Run same 12 validation checks
4. Compare against previous attempt to verify improvements
5. Calculate weighted score (0-100)
6. Check if feedback was addressed
7. Generate recommendations (even if passed)

**Output Contract** (Typical Second Attempt - PASS):
```yaml
isValid:
  type: boolean
  value: true
  description: "True because score >= 90 AND no errors"

qualityScore:
  type: number
  value: 95
  minimum: 0
  maximum: 100

checks:
  type: array
  length: 12
  description: "All checks passed (12/12)"
  example:
    - rule_id: xml_well_formed
      status: pass
      message: "XML is valid and parseable"
      severity: info
      section: structural
      score_impact: 0
    - rule_id: examples_quality
      status: pass
      message: "3 good examples found (exceeds minimum of 2)"
      severity: info
      section: completeness
      score_impact: +2  # bonus
    - rule_id: input_specification_present
      status: pass
      message: "Input specification complete with validation rules"
      severity: info
      section: completeness
      score_impact: 0

feedback:
  type: array
  items: string
  length: 0
  description: "Empty because validation passed"

recommendations:
  type: array
  items: string
  example:
    - "Consider adding <domain_knowledge> section for additional context"
    - "Examples are excellent, well-structured"

scoreBreakdown:
  type: object
  properties:
    structural:
      value: 35
      max: 35
    completeness:
      value: 30
      max: 30
      description: "Improved from 20 to 30 (+10)"
    quality:
      value: 25
      max: 25
    context_quality:
      value: 10
      max: 10
      description: "Improved from 5 to 10 (+5)"
    bonuses: +5
    penalties: 0

examplesAnalysis:
  good_examples_found: 3
  bad_examples_found: 2
  examples_quality_score: 95

contextValidation:
  input_specification_present: true
  context_requirements_present: true
  required_inputs_count: 2
  context_sources_count: 1
  glean_integrations: ["mcp__glean__meeting_lookup"]
  validation_issues: []
```

**Artifacts Loaded**:
- **Reuse from HOP 3** (cached)
- Same validation rules, standards, instructions, examples

**Events Published**:
- `PromptValidated`
- `PromptApproved`

**Bounded Context**: PromptEngineering (Core Domain)

**Decision Point** (Orchestration Agent):
```
Score: 95/100
Threshold: 90/100
Decision: 95 >= 90 → PASS

isValid: true
Decision: PASS

Action: EXIT LOOP, Proceed to HOP 6 (Save Output)
```

**Performance**:
- Expected: 1.5s
- Max: 8s

---

### HOP 6: Save Output

**Time**: 8.2s → 9.0s (0.8s duration)

**Swim Lanes Involved**: Agent B → 🎯 Orchestration Agent → User/UX Plane

**Orchestration Agent Role**:
- Receives approved validation result from Agent B
- Generates output files:
  1. **XML file**: Final approved prompt
  2. **JSON report**: Complete session summary with metrics
- Completes workflow session
- Publishes `WorkflowSessionCompleted` event
- Returns outputs to user

**Input Contract**:
```yaml
prompt_name:
  type: string
  required: true
  example: "mtg-sum-ext"

xml_prompt:
  type: string
  required: true
  description: "Final approved XML from HOP 5"

validation_result:
  type: object
  required: true
  description: "Final validation result from HOP 5"
  properties:
    isValid: boolean
    qualityScore: number
    checks: array
    scoreBreakdown: object
    examplesAnalysis: object
    contextValidation: object

session_summary:
  type: object
  required: true
  properties:
    total_attempts: integer
    final_score: number
    duration_ms: integer
    status: enum[SUCCESS, FAILED]
    workflow_id: string
```

**Processing**:
1. Create output directory if not exists (`output/`)
2. Write XML file:
   - Path: `output/{prompt_name}.xml`
   - Content: Final approved XML prompt
3. Generate JSON report:
   - Path: `output/{prompt_name}-ab-report.json`
   - Content: Complete session metadata, validation results, metrics
4. Publish completion event to event store
5. Return file paths and summary to user

**Output Contract** (Delivered to User):
```yaml
saved_files:
  type: array[string]
  example:
    - "output/mtg-sum-ext.xml"
    - "output/mtg-sum-ext-ab-report.json"

prompt_name:
  type: string
  example: "mtg-sum-ext"

final_score:
  type: number
  example: 95

success:
  type: boolean
  value: true

session_id:
  type: string
  example: "wf-abc-123"

duration_ms:
  type: integer
  example: 9000

total_attempts:
  type: integer
  example: 2
```

**JSON Report Structure**:
```json
{
  "session_id": "wf-abc-123",
  "workflow": "prompt-generation",
  "status": "SUCCESS",
  "duration_ms": 9000,
  "timestamp": "2026-01-26T10:30:45.123Z",

  "prompt_metadata": {
    "name": "mtg-sum-ext",
    "version": "1.0",
    "bounded_context": "PromptEngineering"
  },

  "attempts": [
    {
      "attempt_number": 1,
      "agent_a_output": {
        "prompt_name": "mtg-sum-ext",
        "generation_metadata": {...}
      },
      "agent_b_output": {
        "isValid": false,
        "qualityScore": 85,
        "feedback": [...]
      }
    },
    {
      "attempt_number": 2,
      "agent_a_output": {
        "prompt_name": "mtg-sum-ext",
        "refinements_applied": [...],
        "feedback_addressed": [...]
      },
      "agent_b_output": {
        "isValid": true,
        "qualityScore": 95,
        "feedback": []
      }
    }
  ],

  "final_result": {
    "isValid": true,
    "qualityScore": 95,
    "scoreBreakdown": {
      "structural": 35,
      "completeness": 30,
      "quality": 25,
      "context_quality": 10
    },
    "examplesAnalysis": {
      "good_examples_found": 3,
      "bad_examples_found": 2
    },
    "contextValidation": {
      "input_specification_present": true,
      "required_inputs_count": 2,
      "glean_integrations": ["mcp__glean__meeting_lookup"]
    }
  },

  "output_files": {
    "xml": "output/mtg-sum-ext.xml",
    "report": "output/mtg-sum-ext-ab-report.json"
  }
}
```

**Artifacts Loaded**: None

**Events Published**:
- `WorkflowSessionCompleted`

**Bounded Context**: WorkflowOrchestration (Core Domain)

**Performance**:
- Expected: 0.8s (file I/O)
- Max: 2s

---

## Agent Contract Specifications

### Agent A: prompt-generator-001

**Location**: `agents/prompt-generator/agent-spec.yaml`

**Bounded Context**: **PromptEngineering** (Core Domain)

**Full Input Contract**:
```yaml
user_request:
  type: string
  required: true
  description: "Natural language prompt request"
  min_length: 10
  example: "Create a prompt for meeting summarization"

analyze_context:
  type: boolean
  required: false
  default: true
  description: "Enable context analysis to identify inputs and context sources"

feedback:
  type: array
  required: false
  items:
    type: string
  description: "Validation feedback from previous attempt"
  example:
    - "Add at least one more good example"
    - "Add validation rules for all required inputs"

previous_attempt:
  type: object
  required: false
  description: "Previous generation attempt for refinement"
  properties:
    xml_prompt:
      type: string
      description: "XML from previous attempt"
    prompt_name:
      type: string
      description: "Name to preserve across attempts"

attempt_number:
  type: integer
  required: false
  minimum: 1
  maximum: 3
  default: 1
  description: "Current attempt number in validation loop"

input_analysis:
  type: object
  required: false
  description: "Output from Context Discovery (HOP 1)"
  properties:
    required_inputs: array
    optional_inputs: array
    context_sources: array
    glean_integrations: array
```

**Full Output Contract**:
```yaml
xml_prompt:
  type: string
  required: true
  description: "Complete XML-structured prompt"
  min_length: 100

prompt_name:
  type: string
  required: true
  pattern: "^[a-z0-9]{3}-[a-z0-9]{3}-[a-z0-9]{3}$"
  description: "Unique prompt identifier (xxx-xxx-xxx format)"
  example: "mtg-sum-ext"

components_extracted:
  type: object
  required: false
  description: "Parsed components from user request"
  properties:
    primary_goal:
      type: string
      description: "What the prompt should accomplish"
    role:
      type: string
      description: "Role/persona for the agent"
    task:
      type: string
      description: "Specific task instructions"
    context:
      type: string
      description: "Background and constraints"
    constraints:
      type: array
      items: string
      description: "Limitations and requirements"
    output_format:
      type: string
      description: "Expected output structure"

input_analysis:
  type: object
  required: false
  description: "Analysis of required inputs and context sources"
  properties:
    required_inputs:
      type: array
      description: "Inputs that must be provided by user"
      items:
        name: string
        type: string
        source: string
        description: string
    optional_inputs:
      type: array
      description: "Optional inputs with defaults"
      items:
        name: string
        type: string
        source: string
        default: any
    context_sources:
      type: array
      description: "Context that can be retrieved from Glean"
      items:
        name: string
        source: string
        query: string
        required: boolean
    glean_integrations:
      type: array
      description: "Glean MCP tools needed"
      items: string

generation_metadata:
  type: object
  required: false
  properties:
    attempt:
      type: integer
      description: "Attempt number"
    refinements_applied:
      type: array
      items: string
      description: "What refinements were made (if attempt > 1)"
    timestamp:
      type: string
      format: iso8601
    feedback_addressed:
      type: array
      items: string
      description: "Which feedback items were addressed"
    context_analysis_performed:
      type: boolean
      description: "Whether context analysis was enabled"
```

**Configuration**:
```yaml
model:
  name: claude-sonnet-4
  temperature: 0.3
  max_tokens: 4000
  top_p: 0.9

instruction_source: ../../workflow-orchestration/workflows/prompt-generation/stages/01-generate-prompt/instructions.md

examples_source: ../../workflow-orchestration/workflows/prompt-generation/stages/01-generate-prompt/examples/

global_examples_source: ../../workflow-orchestration/global/examples/

core_prompt_template: prompt-template.xml

performance:
  expected_latency_ms: 3000
  max_latency_ms: 120000
  cache_enabled: false
```

**Constraints**:
- `no_write_actions`: Read-only operations
- `no_hitl`: No human-in-the-loop required
- `read_only_operations`: Cannot modify files

---

### Agent B: prompt-validator-001

**Location**: `agents/prompt-validator/agent-spec.yaml`

**Bounded Context**: **PromptEngineering** (Core Domain)

**Full Input Contract**:
```yaml
xml_prompt:
  type: string
  required: true
  description: "XML prompt to validate"
  min_length: 50

previous_validation_results:
  type: array
  required: false
  description: "Results from previous validation attempts (for tracking improvements)"
  items:
    type: object
    properties:
      attempt: integer
      score: number
      isValid: boolean
      feedback: array

attempt_number:
  type: integer
  required: false
  minimum: 1
  maximum: 3
  default: 1
  description: "Current validation attempt number"
```

**Full Output Contract**:
```yaml
isValid:
  type: boolean
  required: true
  description: "Overall validation result (score >= 90 AND no errors)"

qualityScore:
  type: number
  required: true
  minimum: 0
  maximum: 100
  description: "Calculated quality score"

checks:
  type: array
  required: true
  description: "Individual validation check results (12 checks)"
  items:
    type: object
    properties:
      rule_id:
        type: string
        description: "Validation rule identifier"
        example: "xml_well_formed"
      status:
        enum: [pass, fail]
        description: "Check result"
      message:
        type: string
        description: "Detailed check message"
      severity:
        enum: [error, warning, info]
        description: "Issue severity"
      section:
        type: string
        description: "Which dimension this check belongs to"
        enum: [structural, completeness, quality, context_quality]
      score_impact:
        type: number
        description: "Points added/subtracted by this check"

feedback:
  type: array
  required: true
  description: "Actionable feedback for refinement (empty if passed)"
  items:
    type: string
    example: "Add at least one more good example to meet minimum requirement (2)"

recommendations:
  type: array
  required: false
  description: "Optional improvement suggestions (even if passed)"
  items:
    type: string
    example: "Consider adding <constraints> section"

scoreBreakdown:
  type: object
  required: false
  properties:
    structural:
      type: number
      minimum: 0
      maximum: 35
      description: "Structural validation score"
    completeness:
      type: number
      minimum: 0
      maximum: 30
      description: "Completeness validation score"
    quality:
      type: number
      minimum: 0
      maximum: 25
      description: "Quality validation score"
    context_quality:
      type: number
      minimum: 0
      maximum: 10
      description: "Context quality validation score"
    bonuses:
      type: number
      description: "Extra points from bonuses"
    penalties:
      type: number
      description: "Points deducted from penalties"

examplesAnalysis:
  type: object
  required: false
  properties:
    good_examples_found:
      type: integer
      description: "Count of <good> examples"
    bad_examples_found:
      type: integer
      description: "Count of <bad> examples"
    examples_quality_score:
      type: number
      minimum: 0
      maximum: 100
      description: "Quality assessment of examples"

contextValidation:
  type: object
  required: false
  description: "Validation of input/context specifications"
  properties:
    input_specification_present:
      type: boolean
      description: "Whether <input_specification> tag exists"
    context_requirements_present:
      type: boolean
      description: "Whether <context_requirements> tag exists"
    required_inputs_count:
      type: integer
      description: "Number of required inputs defined"
    context_sources_count:
      type: integer
      description: "Number of context sources defined"
    glean_integrations:
      type: array
      items: string
      description: "Glean MCP tools referenced"
    validation_issues:
      type: array
      items: string
      description: "Issues found in input/context specs"
```

**Scoring Configuration**:
```yaml
scoring:
  success_threshold: 90
  base_score: 100
  error_penalty: 20
  warning_penalty: 5
  info_penalty: 0
  bonus_per_extra_good_example: 2
  bonus_per_extra_bad_example: 2
  max_total_bonus: 10

  weights:
    structural: 0.35
    completeness: 0.30
    quality: 0.25
    context_quality: 0.10

  context_penalties:
    missing_input_specification: -15
    no_required_inputs: -5
    invalid_glean_queries: -10
    missing_input_descriptions: -5

validation_checks:
  structural:
    - xml_well_formed (10 points)
    - required_sections_present (15 points)
    - tag_hierarchy (10 points)
    - naming_convention (5 points)

  completeness:
    - section_content (15 points)
    - examples_quality (10 points)
    - instructions_structure (5 points)
    - input_specification_present (varies)
    - context_requirements_present (varies)

  quality:
    - clarity_and_specificity (10 points)
    - examples_effectiveness (10 points)
    - constraints_and_validation (5 points)
    - overall_coherence (5 points)

  context_quality:
    - required_inputs_defined
    - input_descriptions_clear
    - glean_queries_valid
    - context_sources_accessible
```

**Configuration**:
```yaml
model:
  name: claude-sonnet-4
  temperature: 0  # Deterministic
  max_tokens: 2000
  top_p: 1.0

instruction_source: ../../workflow-orchestration/workflows/prompt-generation/stages/02-validate-quality/instructions.md

validation_rules_source: ../../workflow-orchestration/workflows/prompt-generation/stages/02-validate-quality/validation-rules.json

global_standards_source: ../../workflow-orchestration/global/config/validation-standards.json

examples_source: ../../workflow-orchestration/workflows/prompt-generation/stages/02-validate-quality/examples/

global_examples_source: ../../workflow-orchestration/global/examples/

feedback_generation:
  enabled: true
  template_based: true
  include_error_fixes: true
  include_warning_improvements: true
  include_recommendations: true
  reference_examples: true
  max_feedback_items: 10
  prioritize_by_severity: true

performance:
  expected_latency_ms: 2000
  max_latency_ms: 60000
  cache_enabled: false
```

**Constraints**:
- `no_write_actions`
- `no_hitl`
- `read_only_operations`
- `strict_validation_mode`

---

## Artifact Loading Map

### Current Architecture (Repository-based)

```
/Users/eric.flecher/Workbench/projects/a_domain/
│
├── agents/
│   ├── prompt-generator/
│   │   ├── agent-spec.yaml           ← Agent A contract (loaded by orchestrator)
│   │   ├── prompt-template.xml       ← XML boilerplate (loaded by Agent A)
│   │   └── instructions/             ← (future expansion)
│   │
│   └── prompt-validator/
│       ├── agent-spec.yaml           ← Agent B contract (loaded by orchestrator)
│       ├── validation-logic.xml      ← (reference, not loaded)
│       └── instructions/             ← (future expansion)
│
└── workflow-orchestration/
    ├── global/
    │   ├── config/
    │   │   └── validation-standards.json  ← Global thresholds (loaded by Agent B)
    │   │
    │   └── examples/
    │       ├── good/
    │       │   ├── _metadata.json         ← Example catalog
    │       │   ├── meeting-summary-basic.xml
    │       │   ├── code-review-detailed.xml
    │       │   └── sentiment-analysis.xml
    │       │
    │       └── bad/
    │           ├── _metadata.json
    │           ├── missing-examples.xml   ← Anti-pattern: no examples
    │           ├── flat-structure.xml     ← Anti-pattern: no hierarchy
    │           └── vague-instructions.xml ← Anti-pattern: unclear task
    │
    └── workflows/
        └── prompt-generation/
            └── stages/
                ├── 01-generate-prompt/
                │   ├── instructions.md            ← Agent A guidance (appended to system prompt)
                │   └── examples/
                │       └── (stage-specific examples if needed)
                │
                └── 02-validate-quality/
                    ├── instructions.md            ← Agent B guidance (appended to system prompt)
                    ├── validation-rules.json      ← Stage-specific scoring rules (loaded by Agent B)
                    └── examples/
                        └── (validation examples if needed)
```

### Artifact Loading by Agent

#### Agent A (prompt-generator-001) - HOP 2 and HOP 4

**Load Sequence**:
1. **Contract Definition** (orchestrator loads before agent call):
   - Path: `agents/prompt-generator/agent-spec.yaml`
   - Purpose: Validate input/output schemas
   - Cached: No (always fresh)

2. **Template Structure**:
   - Path: `agents/prompt-generator/prompt-template.xml`
   - Purpose: XML boilerplate with placeholders
   - Cached: Yes (static)

3. **Generation Instructions**:
   - Path: `workflow-orchestration/workflows/prompt-generation/stages/01-generate-prompt/instructions.md`
   - Purpose: Appended to agent system prompt
   - Content: Detailed guidance on XML generation, tag usage, examples structure
   - Cached: Yes (static)

4. **Good Examples** (reference patterns):
   - Path: `workflow-orchestration/global/examples/good/*.xml`
   - Purpose: Show correct structure, complete examples
   - Files: 3-5 reference prompts
   - Cached: Yes (static)

**Total Artifacts**: 5-7 files, ~50KB

#### Agent B (prompt-validator-001) - HOP 3 and HOP 5

**Load Sequence**:
1. **Contract Definition** (orchestrator loads before agent call):
   - Path: `agents/prompt-validator/agent-spec.yaml`
   - Purpose: Validate input/output schemas
   - Cached: No (always fresh)

2. **Validation Instructions**:
   - Path: `workflow-orchestration/workflows/prompt-generation/stages/02-validate-quality/instructions.md`
   - Purpose: Appended to agent system prompt
   - Content: How to validate, scoring methodology, feedback generation
   - Cached: Yes (static)

3. **Validation Rules** (stage-specific):
   - Path: `workflow-orchestration/workflows/prompt-generation/stages/02-validate-quality/validation-rules.json`
   - Purpose: Scoring weights, check definitions, thresholds
   - Content: 12 validation checks across 4 dimensions
   - Cached: Yes (static)

4. **Global Standards**:
   - Path: `workflow-orchestration/global/config/validation-standards.json`
   - Purpose: Organization-wide quality thresholds
   - Content: Score thresholds (excellent: 95, good: 90, acceptable: 85)
   - Cached: Yes (static)

5. **Good Examples** (comparison):
   - Path: `workflow-orchestration/global/examples/good/*.xml`
   - Purpose: Compare against known-good patterns
   - Files: Same 3-5 files as Agent A
   - Cached: Yes (static, shared with Agent A)

6. **Bad Examples** (anti-patterns):
   - Path: `workflow-orchestration/global/examples/bad/*.xml`
   - Purpose: Identify anti-patterns to avoid
   - Files: 3-4 examples of poor prompts
   - Cached: Yes (static)

**Total Artifacts**: 9-12 files, ~75KB

### Future Architecture (Google Drive-based)

**Path Mapping** (repo:// → gdrive://):

```
Repository Path                                              Google Drive Path
──────────────────────────────────────────────────────────  ─────────────────────────────────────────────────────────────
agents/prompt-generator/agent-spec.yaml                 →  OrgName-PromptEngineering/agents/prompt-generator/agent-spec.yaml
agents/prompt-generator/prompt-template.xml             →  OrgName-PromptEngineering/agents/prompt-generator/prompt-template.xml

agents/prompt-validator/agent-spec.yaml                 →  OrgName-PromptEngineering/agents/prompt-validator/agent-spec.yaml

workflow-orchestration/global/config/
  validation-standards.json                             →  OrgName-PromptEngineering/global/config/validation-standards.json

workflow-orchestration/global/examples/good/            →  OrgName-PromptEngineering/global/examples/good/
  _metadata.json                                        →    _metadata.json
  meeting-summary-basic.xml                             →    meeting-summary-basic.xml
  code-review-detailed.xml                              →    code-review-detailed.xml
  sentiment-analysis.xml                                →    sentiment-analysis.xml

workflow-orchestration/global/examples/bad/             →  OrgName-PromptEngineering/global/examples/bad/
  _metadata.json                                        →    _metadata.json
  missing-examples.xml                                  →    missing-examples.xml
  flat-structure.xml                                    →    flat-structure.xml
  vague-instructions.xml                                →    vague-instructions.xml

workflow-orchestration/workflows/prompt-generation/
  stages/01-generate-prompt/instructions.md             →  OrgName-PromptEngineering/workflows/prompt-generation/stages/01-generate-prompt/instructions.md
  stages/02-validate-quality/instructions.md            →  OrgName-PromptEngineering/workflows/prompt-generation/stages/02-validate-quality/instructions.md
  stages/02-validate-quality/validation-rules.json      →  OrgName-PromptEngineering/workflows/prompt-generation/stages/02-validate-quality/validation-rules.json
```

**Google Drive Benefits**:
1. **Non-technical Contribution**:
   - Prompt engineers upload new good/bad examples by dragging files into folders
   - No Git knowledge required
   - No pull request process

2. **Collaborative Editing**:
   - Update `validation-standards.json` via Google Sheets integration
   - Edit `instructions.md` in Google Docs with real-time collaboration
   - Comment on examples directly in Drive

3. **Version History**:
   - Google Drive native versioning
   - Restore previous versions easily
   - Track who changed what

4. **Organization-wide Access**:
   - Share across teams with folder permissions
   - Public within org, private externally
   - Audit trail of access

5. **Simplified Workflow**:
   - Add new example → Upload to `good/` folder → Immediately available to agents
   - Update validation rule → Edit JSON in Sheets → Export → Replace file → Done
   - No deployment pipeline needed

**Implementation Approach**:
- Agent specs reference artifacts via `gdrive://` URIs
- Orchestrator uses Google Drive API to fetch files
- Implement caching layer (60-minute TTL)
- Fallback to repository if Drive unavailable

---

## Bounded Context Map

### Context Relationships

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│                        BOUNDED CONTEXT MAP                                  │
│                                                                             │
│   ┌──────────────────────────────────────────────────────────────────────┐ │
│   │  PromptEngineering (Core Domain)                                     │ │
│   │  ──────────────────────────────────────────────────────────────────  │ │
│   │                                                                       │ │
│   │  ┌────────────────────┐         ┌────────────────────┐               │ │
│   │  │   Agent A          │         │   Agent B          │               │ │
│   │  │   (Generator)      │────────>│   (Validator)      │               │ │
│   │  │                    │ XML     │                    │               │ │
│   │  │ prompt-generator   │ Prompt  │ prompt-validator   │               │ │
│   │  │      -001          │         │      -001          │               │ │
│   │  └────────────────────┘         └────────────────────┘               │ │
│   │           │                               │                          │ │
│   │           │ OHS                           │ OHS                      │ │
│   │           │ (Open Host Service)           │ (Feedback)               │ │
│   │           ▼                               ▼                          │ │
│   └───────────┼───────────────────────────────┼──────────────────────────┘ │
│               │                               │                            │
│               │                               │                            │
│   ┌───────────┼───────────────────────────────┼──────────────────────────┐ │
│   │           │ WorkflowOrchestration         │                          │ │
│   │           │ (Core Domain)                 │                          │ │
│   │  ─────────┼───────────────────────────────┼───────────────────────   │ │
│   │           │                               │                          │ │
│   │  ┌────────┴───────────────────────────────┴────────┐                 │ │
│   │  │   🎯 Orchestration Agent                        │                 │ │
│   │  │   (Active Coordinator)                          │                 │ │
│   │  │                                                 │                 │ │
│   │  │ Responsibilities:                               │                 │ │
│   │  │ • Session management                            │                 │ │
│   │  │ • Hop routing                                   │                 │ │
│   │  │ • Quality gate decisions                        │                 │ │
│   │  │ • Feedback loop control                         │                 │ │
│   │  │ • Event recording                               │                 │ │
│   │  │ • Error handling                                │                 │ │
│   │  └─────────────────────────────────────────────────┘                 │ │
│   │           │                                                           │ │
│   │           │ CF (Conformist)                                          │ │
│   │           │ Orchestrator conforms to PromptEngineering contracts     │ │
│   └───────────┼──────────────────────────────────────────────────────────┘ │
│               │                                                            │
│               │                                                            │
│   ┌───────────┼──────────────────────────────────────────────────────────┐ │
│   │           │ ContextDiscovery (Supporting Domain)                     │ │
│   │  ─────────┼──────────────────────────────────────────────────────    │ │
│   │           │                                                           │ │
│   │  ┌────────▼──────────┐                                               │ │
│   │  │ Context Discovery │                                               │ │
│   │  │ Node              │                                               │ │
│   │  │                   │                                               │ │
│   │  │ • Task analysis   │                                               │ │
│   │  │ • Input mapping   │                                               │ │
│   │  │ • Glean tool sel. │                                               │ │
│   │  └───────────────────┘                                               │ │
│   │           │                                                           │ │
│   │           │ ACL (Anti-Corruption Layer)                              │ │
│   │           │ Protects domain from Glean API changes                   │ │
│   └───────────┼──────────────────────────────────────────────────────────┘ │
│               │                                                            │
│               │                                                            │
│   ┌───────────┼──────────────────────────────────────────────────────────┐ │
│   │           │ GleanIntegration (External)                              │ │
│   │  ─────────┼──────────────────────────────────────────────────────    │ │
│   │           │                                                           │ │
│   │  ┌────────▼──────────┐                                               │ │
│   │  │ Glean MCP Server  │                                               │ │
│   │  │                   │                                               │ │
│   │  │ • meeting_lookup  │                                               │ │
│   │  │ • code_search     │                                               │ │
│   │  │ • search          │                                               │ │
│   │  │ • read_document   │                                               │ │
│   │  └───────────────────┘                                               │ │
│   │                                                                       │ │
│   └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│   ┌──────────────────────────────────────────────────────────────────────┐ │
│   │  Infrastructure (Generic Subdomain)                                  │ │
│   │  ──────────────────────────────────────────────────────────────────  │ │
│   │                                                                       │ │
│   │  • Artifact Repository (repo:// or gdrive://)                        │ │
│   │  • Event Store (domain events)                                       │ │
│   │  • File System (output/ directory)                                   │ │
│   └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

Relationship Types:
  OHS (Open Host Service) → Provides well-defined API for others to consume
  ACL (Anti-Corruption Layer) → Translates external concepts into domain language
  CF (Conformist) → Conforms to upstream bounded context contracts
  ────> Direct dependency
```

### Context Ownership of Components

| Component | Bounded Context | Type | Responsibilities |
|-----------|----------------|------|-----------------|
| Agent A (prompt-generator-001) | **PromptEngineering** | Core Domain | XML generation, refinement, context analysis |
| Agent B (prompt-validator-001) | **PromptEngineering** | Core Domain | Quality validation, feedback generation, scoring |
| 🎯 Orchestration Agent | **WorkflowOrchestration** | Core Domain | Session mgmt, routing, quality gates, event recording |
| Context Discovery Node | **ContextDiscovery** | Supporting Domain | Task analysis, input identification, Glean tool selection |
| Artifact Repository | **Infrastructure** | Generic Subdomain | Static file storage (repo/gdrive) |
| Event Store | **Infrastructure** | Generic Subdomain | Domain event persistence |

### Domain Events

**Published by WorkflowOrchestration**:
- `WorkflowSessionStarted` (HOP 1) - Contains: session_id, user_request, timestamp
- `AttemptInitiated` (HOP 2, HOP 4) - Contains: attempt_number, agent_id
- `FeedbackCycleStarted` (HOP 4) - Contains: feedback_items, previous_score
- `FeedbackApplied` (HOP 4) - Contains: refinements_applied
- `MaxAttemptsReached` (if fails) - Contains: final_score, attempts
- `WorkflowSessionCompleted` (HOP 6) - Contains: session_summary, output_files
- `WorkflowSessionFailed` (on error) - Contains: error_message, stack_trace

**Published by PromptEngineering**:
- `TaskAnalyzed` (HOP 1) - Contains: task_type, required_inputs, context_sources
- `InputsIdentified` (HOP 1) - Contains: input_list
- `ContextSourcesDiscovered` (HOP 1) - Contains: glean_integrations
- `PromptGenerated` (HOP 2, HOP 4) - Contains: prompt_name, xml_prompt, metadata
- `PromptValidated` (HOP 3, HOP 5) - Contains: score, isValid, checks
- `FeedbackGenerated` (HOP 3) - Contains: feedback_items
- `PromptApproved` (HOP 5) - Contains: final_score

**Event Store Schema**:
```json
{
  "event_id": "evt-abc-123",
  "event_type": "PromptValidated",
  "aggregate_id": "wf-abc-123",
  "aggregate_type": "WorkflowSession",
  "bounded_context": "PromptEngineering",
  "timestamp": "2026-01-26T10:30:45.123Z",
  "version": 3,
  "payload": {
    "attempt_number": 1,
    "isValid": false,
    "qualityScore": 85,
    "feedback": [...]
  },
  "metadata": {
    "user_id": "user-123",
    "correlation_id": "req-abc-123"
  }
}
```

---

## Quality Gates and Decision Logic

### Quality Gate 1: HOP 3 (First Validation)

**Location**: Orchestration Agent after receiving Agent B result

**Input**:
- `validationResult.qualityScore` (number, 0-100)
- `validationResult.isValid` (boolean)
- `currentAttempt` (integer, 1-3)

**Decision Logic**:
```javascript
// Quality Gate Decision
if (validationResult.qualityScore >= 90 && validationResult.isValid === true) {
  // SUCCESS PATH - Exit loop early
  console.log('✓ Quality gate passed on first attempt')
  return proceedToSaveOutput(HOP_6)
}

// FAILURE PATH - Check if retry possible
if (currentAttempt < maxAttempts) {
  // RETRY PATH - Trigger feedback loop
  console.log(`✗ Quality gate failed: ${validationResult.qualityScore}/100 (threshold: 90)`)
  console.log(`→ Triggering feedback loop (attempt ${currentAttempt + 1}/${maxAttempts})`)

  return {
    decision: 'RETRY',
    nextHop: 'HOP_4_REFINEMENT',
    feedback: validationResult.feedback,
    previousAttempt: {
      xml_prompt: agentAOutput.xml_prompt,
      prompt_name: agentAOutput.prompt_name
    },
    attemptNumber: currentAttempt + 1
  }
} else {
  // MAX ATTEMPTS REACHED
  console.error(`✗ Max attempts (${maxAttempts}) reached without passing validation`)
  throw new WorkflowError('MAX_ATTEMPTS_EXCEEDED', {
    finalScore: validationResult.qualityScore,
    attempts: maxAttempts,
    feedback: validationResult.feedback
  })
}
```

**Possible Outcomes**:
1. **PASS** (score ≥ 90, isValid = true) → Proceed to HOP 6
2. **RETRY** (score < 90, attempt < 3) → Proceed to HOP 4
3. **FAIL** (score < 90, attempt = 3) → Throw error, end workflow

**Metrics** (typical first attempt):
- Pass rate: ~15% (rare to pass on first try)
- Retry rate: ~85%
- Fail rate: ~0% (almost never reaches max attempts on first validation)
- Average score: 82-87/100

---

### Quality Gate 2: HOP 5 (Re-validation)

**Location**: Orchestration Agent after receiving Agent B result (attempt 2+)

**Input**:
- `validationResult.qualityScore` (number, 0-100)
- `validationResult.isValid` (boolean)
- `currentAttempt` (integer, 2-3)
- `previousValidationResults` (array of previous scores)

**Decision Logic**:
```javascript
// Quality Gate Decision (same logic as HOP 3, but different context)
if (validationResult.qualityScore >= 90 && validationResult.isValid === true) {
  // SUCCESS PATH - Feedback was effective
  const improvement = validationResult.qualityScore - previousValidationResults[0].qualityScore
  console.log(`✓ Quality gate passed on attempt ${currentAttempt}`)
  console.log(`  Improvement: +${improvement} points`)
  console.log(`  Feedback addressed: ${agentAOutput.generation_metadata.feedback_addressed.length} items`)

  return proceedToSaveOutput(HOP_6)
}

// FAILURE PATH - Feedback didn't help enough
if (currentAttempt < maxAttempts) {
  // RETRY AGAIN - One more chance
  console.log(`✗ Quality gate failed: ${validationResult.qualityScore}/100 (threshold: 90)`)
  console.log(`  Previous score: ${previousValidationResults[0].qualityScore}`)
  console.log(`  Improvement: +${validationResult.qualityScore - previousValidationResults[0].qualityScore}`)
  console.log(`→ Triggering another refinement (attempt ${currentAttempt + 1}/${maxAttempts})`)

  return {
    decision: 'RETRY',
    nextHop: 'HOP_4_REFINEMENT',
    feedback: validationResult.feedback,
    previousAttempt: {
      xml_prompt: agentAOutput.xml_prompt,
      prompt_name: agentAOutput.prompt_name
    },
    attemptNumber: currentAttempt + 1,
    previousValidationResults: [...previousValidationResults, validationResult]
  }
} else {
  // MAX ATTEMPTS REACHED - Give up
  console.error(`✗ Max attempts (${maxAttempts}) reached without passing validation`)
  console.error(`  Final score: ${validationResult.qualityScore}/100`)
  console.error(`  Score progression: ${previousValidationResults.map(r => r.qualityScore).join(' → ')} → ${validationResult.qualityScore}`)

  throw new WorkflowError('MAX_ATTEMPTS_EXCEEDED', {
    finalScore: validationResult.qualityScore,
    attempts: maxAttempts,
    scoreProgression: [...previousValidationResults.map(r => r.qualityScore), validationResult.qualityScore],
    feedback: validationResult.feedback
  })
}
```

**Possible Outcomes**:
1. **PASS** (score ≥ 90, isValid = true) → Proceed to HOP 6
2. **RETRY** (score < 90, attempt = 2) → Proceed to HOP 4 (attempt 3)
3. **FAIL** (score < 90, attempt = 3) → Throw error, end workflow

**Metrics** (typical second attempt):
- Pass rate: ~92% (feedback usually effective)
- Retry rate: ~7% (need third attempt)
- Fail rate: ~1% (rare to need all 3 attempts)
- Average score: 93-96/100
- Average improvement: +8-12 points from first attempt

---

### Feedback Loop Mechanics

**Trigger Conditions**:
- Score < 90 (threshold not met)
- Attempt < 3 (retries remaining)
- Feedback array not empty (actionable items available)

**Feedback Prioritization** (Agent B):
1. **Errors first** (severity: error) - Critical issues blocking validation
2. **Warnings second** (severity: warning) - Quality issues reducing score
3. **Recommendations last** (severity: info) - Optional improvements

**Feedback Format**:
```json
[
  "ERROR [xml_well_formed] XML: Cannot parse - malformed closing tag → Fix tag nesting",
  "WARNING [examples_quality] Examples: Only 1 good example found, minimum is 2 → Add 1 more good example",
  "WARNING [input_specification_present] Completeness: Missing validation rules → Add rules to input_specification",
  "RECOMMENDATION: Consider adding <constraints> section for edge cases (See: code-review-detailed.xml)"
]
```

**Refinement Strategy** (Agent A):
- Parse feedback items by severity
- Address all errors (blocking issues)
- Address warnings (score improvements)
- Consider recommendations if time allows
- Document which feedback items were addressed in metadata

**Termination Conditions**:
1. **Success**: Score ≥ 90 AND isValid = true
2. **Max Attempts**: Attempt count = 3
3. **Error**: Agent failure, timeout, or system error

---

## Performance Metrics

### Expected Performance (2-attempt success path)

| Hop | Description | Expected Duration | Max Duration | Cumulative Time |
|-----|-------------|------------------|--------------|----------------|
| HOP 1 | Context Discovery | 1.2s | 5s | 1.2s |
| HOP 2 | Generation (Attempt 1) | 2.0s | 10s | 3.2s |
| HOP 3 | Validation (Attempt 1) | 1.5s | 8s | 4.7s |
| HOP 4 | Refinement (Attempt 2) | 2.0s | 10s | 6.7s |
| HOP 5 | Re-validation (Attempt 2) | 1.5s | 8s | 8.2s |
| HOP 6 | Save Output | 0.8s | 2s | 9.0s |
| **Total** | **Complete workflow** | **9.0s** | **43s** | **9.0s** |

### Performance by Attempt Count

**1 Attempt** (pass on first try - rare, ~15%):
- HOP 1 + HOP 2 + HOP 3 + HOP 6 = 1.2s + 2.0s + 1.5s + 0.8s = **5.5s**

**2 Attempts** (typical, ~85%):
- All 6 hops = **9.0s** (as shown above)

**3 Attempts** (rare, ~7%):
- HOP 1 + HOP 2 + HOP 3 + HOP 4 + HOP 5 + HOP 4 + HOP 5 + HOP 6
- = 1.2s + 2.0s + 1.5s + 2.0s + 1.5s + 2.0s + 1.5s + 0.8s = **12.5s**

### Latency Breakdown

**Agent A (Generation)**:
- Model inference: 1.8s (90%)
- Artifact loading: 0.1s (5%)
- Template processing: 0.1s (5%)
- Total: 2.0s

**Agent B (Validation)**:
- Model inference: 1.2s (80%)
- Artifact loading: 0.15s (10%)
- Scoring calculation: 0.15s (10%)
- Total: 1.5s

**Orchestration Agent**:
- Routing logic: <50ms per hop
- Event publishing: <100ms per event
- File I/O (HOP 6): 0.8s

### Optimization Opportunities

1. **Artifact Caching**:
   - Current: Load artifacts on every agent call
   - Optimized: Cache artifacts for 60 minutes
   - Savings: -0.1s per Agent A call, -0.15s per Agent B call
   - Total savings (2-attempt path): -0.5s → **8.5s total**

2. **Parallel Validation Checks** (Agent B):
   - Current: Sequential check execution
   - Optimized: Parallel check execution (4 dimensions in parallel)
   - Savings: -0.3s per validation
   - Total savings (2-attempt path): -0.6s → **8.4s total**

3. **Streaming Output** (HOP 6):
   - Current: Wait for full XML + report generation
   - Optimized: Stream XML while generating report
   - Savings: -0.4s
   - Total savings: -0.4s → **8.6s total**

**Combined Optimizations**: 9.0s → **7.5s** (17% improvement)

### Error Rates

**Agent A Failures**:
- Template parsing errors: <1%
- Model timeout: <0.5%
- Invalid feedback handling: <0.1%
- **Total**: <2%

**Agent B Failures**:
- XML parsing errors: <0.5%
- Scoring calculation errors: <0.1%
- **Total**: <1%

**Orchestration Failures**:
- Session management errors: <0.1%
- Event publishing failures: <0.5%
- File I/O errors (HOP 6): <1%
- **Total**: <2%

**Overall Success Rate**: ~95%

### Quality Metrics

**Validation Scores** (distribution across all workflows):
- Excellent (95-100): 65%
- Good (90-94): 30%
- Acceptable (85-89): 4%
- Needs Improvement (70-84): 1%
- Poor (<70): <1%

**Feedback Effectiveness** (score improvement after refinement):
- Average improvement: +10 points
- Median improvement: +8 points
- 90th percentile: +15 points

**User Satisfaction** (post-workflow survey):
- Very satisfied: 75%
- Satisfied: 20%
- Neutral: 4%
- Unsatisfied: 1%

---

## Appendix

### Example Workflow Execution

**User Request**: "Create a prompt for meeting summarization"

**Workflow Execution Log**:

```
[00:00.000] 🎯 Orchestration Agent: Workflow session started (wf-abc-123)
[00:00.010] → HOP 1: Routing to Context Discovery
[00:01.200] ← HOP 1: Context analysis complete
              - Required inputs: meeting_transcript, attendee_list
              - Context sources: previous_meetings (glean_meeting_lookup)
              - Glean integrations: mcp__glean__meeting_lookup

[00:01.210] 🎯 Orchestration Agent: Attempt #1 initiated
[00:01.220] → HOP 2: Routing to Agent A (prompt-generator-001)
[00:03.200] ← HOP 2: XML generated (prompt_name: mtg-sum-ext)
              - Length: 2,450 characters
              - Sections: 8
              - Good examples: 1
              - Bad examples: 1

[00:03.210] 🎯 Orchestration Agent: Routing to Agent B for validation
[00:03.220] → HOP 3: Routing to Agent B (prompt-validator-001)
[00:04.700] ← HOP 3: Validation complete
              - isValid: false
              - Score: 85/100
              - Breakdown: structural(35) + completeness(20) + quality(25) + context(5)
              - Feedback items: 3

[00:04.710] 🎯 Orchestration Agent: QUALITY GATE DECISION
              - Score: 85 < 90 (threshold) → FAIL
              - Attempt: 1 < 3 (max) → RETRY
              - Decision: TRIGGER FEEDBACK LOOP

[00:04.720] 🎯 Orchestration Agent: Attempt #2 initiated (refinement)
[00:04.730] → HOP 4: Routing to Agent A with feedback
              - Feedback items: 3
                1. Add at least one more good example
                2. Add validation rules for all required inputs
                3. Improve specificity in instructions section

[00:06.700] ← HOP 4: XML refined
              - Refinements applied: 3
              - Good examples: 3 (+2)
              - Input validation rules added: 2
              - Instructions restructured: numbered steps

[00:06.710] 🎯 Orchestration Agent: Routing to Agent B for re-validation
[00:06.720] → HOP 5: Routing to Agent B (prompt-validator-001)
[00:08.200] ← HOP 5: Validation complete
              - isValid: true
              - Score: 95/100
              - Breakdown: structural(35) + completeness(30) + quality(25) + context(10)
              - Improvement: +10 points
              - Feedback items: 0

[00:08.210] 🎯 Orchestration Agent: QUALITY GATE DECISION
              - Score: 95 >= 90 (threshold) → PASS
              - isValid: true → PASS
              - Decision: EXIT LOOP, PROCEED TO SAVE

[00:08.220] 🎯 Orchestration Agent: Saving outputs
[00:08.230] → HOP 6: Generating output files
[00:09.000] ← HOP 6: Outputs saved
              - XML: output/mtg-sum-ext.xml (2,680 bytes)
              - Report: output/mtg-sum-ext-ab-report.json (4,125 bytes)

[00:09.010] 🎯 Orchestration Agent: Workflow session completed (wf-abc-123)
              - Status: SUCCESS
              - Final score: 95/100
              - Total attempts: 2
              - Duration: 9.0s

✓ Workflow completed successfully
```

### Visual Legend Reference

**Box Styles**:
- `╔══╗` Double-line border = Orchestration Agent (active coordinator)
- `┌──┐` Single-line border = Agent A / Agent B (contract boxes)
- `────` Dashed box = Bounded context boundary

**Arrow Styles**:
- `════>` Double-line arrow = Orchestration agent call (emphasis)
- `────>` Single-line arrow = Standard synchronous call
- `◄════` Artifact loading arrow = From repository to agent
- `- - ->` Dashed arrow = Asynchronous event publish

**Text Notation**:
- `repo://` = Current artifact location (Git repository)
- `gdrive://` = Future artifact location (Google Drive)
- `IN:` = Input parameters in contract box
- `OUT:` = Output values in contract box
- `🎯` = Orchestration Agent icon

---

## Document Metadata

**Created**: 2026-01-26
**Author**: System Architecture Team
**Version**: 1.0.0
**Status**: Active

**Review Schedule**:
- Monthly review of performance metrics
- Quarterly review of bounded context relationships
- Continuous updates to artifact paths as Google Drive migration progresses

**Related Documentation**:
- [Reference Architecture](./architecture/REFERENCE-ARCHITECTURE.md)
- [Agent Nodes and Workflow](./architecture/AGENT-NODES-AND-WORKFLOW.md)
- [Event Sourcing and CQRS](./architecture/EVENT-SOURCING-CQRS.md)
- [Artifact-Driven Validation](./architecture/ARTIFACT-DRIVEN-VALIDATION.md)

**Feedback**: For questions or suggestions about this service design, contact the architecture team or open an issue in the repository.

---

**End of Service Design Blueprint**
