# Quick Start Guide

**📖 For a complete system overview, see [SYSTEM-OVERVIEW.md](./SYSTEM-OVERVIEW.md)**
**📊 For executive summary with ROI, see [docs/EXECUTIVE-SUMMARY.md](./docs/EXECUTIVE-SUMMARY.md)**

---

## TL;DR - What to Use

```bash
# ✅ RECOMMENDED: Integrated A/B agents with context analysis
make xml-prompt-ab TASK="Create a prompt for meeting summarization"
```

## Available Commands

| Command | Uses A/B Agents? | Context Analysis? | Use When |
|---------|-----------------|-------------------|----------|
| `make xml-prompt` | ✅ Yes | ❌ No | Basic prompts without context |
| `make xml-prompt-enhanced` | ❌ No | ✅ Yes | Testing context analysis only |
| **`make xml-prompt-ab`** | **✅ Yes** | **✅ Yes** | **Production use (RECOMMENDED)** |

## What You Get

### Integrated A/B Workflow Output

```bash
make xml-prompt-ab TASK="Create a prompt for meeting summarization"
```

**Generates**:
- `output/ab-prompt.xml` - Complete XML prompt
- `output/ab-prompt-ab-report.json` - Full report

**XML includes**:
```xml
<input_specification>
  <input>
    <name>meeting_transcript</name>
    <type>string</type>
    <required>true</required>
    <description>Full text transcript of the meeting</description>
    <source>user_provided</source>
  </input>
  ...
</input_specification>

<context_requirements>
  <context>
    <name>previous_meetings</name>
    <source>glean_meeting_lookup</source>
    <query>participants:{{attendee_list}} after:{{meeting_date}}-30d</query>
  </context>
</context_requirements>
```

**Report includes**:
```json
{
  "workflow_type": "integrated_ab_with_context",
  "attempts": 1,
  "final_score": 100,
  "input_analysis": {
    "required_inputs": [...],
    "context_sources": [...],
    "glean_integrations": ["mcp__glean__meeting_lookup"]
  },
  "validation_history": [...]
}
```

## How It Works

```
Your Task
    ↓
Agent A: Analyzes task → identifies inputs/context → generates XML
    ↓
Agent B: Validates structure + completeness + quality + context
    ↓
Score ≥ 90? → Success!
Score < 90? → Feedback to Agent A → Refine → Retry (up to 3x)
```

## Examples

### Meeting Summarization
```bash
make xml-prompt-ab TASK="Create a prompt for meeting summarization"
```
**Identifies**:
- Inputs: `meeting_transcript`, `attendee_list`, `meeting_date`
- Context: Previous meetings via `glean_meeting_lookup`
- Score: 100/100 ✅

### Code Review
```bash
make xml-prompt-ab TASK="Generate a prompt for code review"
```
**Identifies**:
- Inputs: `code_content`, `language`
- Context: Coding standards via `glean_search`, similar code via `glean_code_search`
- Score: 100/100 ✅

### Customer Feedback
```bash
make xml-prompt-ab TASK="Analyze customer sentiment"
```
**Identifies**:
- Inputs: `feedback_text`, `product_name`
- Context: Product info via `glean_search`, sentiment guidelines via `glean_document`
- Score: 100/100 ✅

## Test Suites

```bash
# Test all three workflows
make test-ab-workflow

# Test context analysis only
make test-context-analysis

# Test basic workflow
make test-workflow
```

## View Results

```bash
# View generated XML
cat output/ab-prompt.xml

# View full report
cat output/ab-prompt-ab-report.json | jq

# View just input analysis
cat output/ab-prompt-ab-report.json | jq '.input_analysis'
```

## Documentation

- **Quick Start**: `/QUICK-START.md` (this file)
- **Complete Summary**: `/docs/INTEGRATED-AB-WORKFLOW-SUMMARY.md`
- **Context Management**: `/docs/context-management.md`
- **Integration Guide**: `/docs/integrating-context-with-ab-agents.md`
- **Usage Examples**: `/USAGE.md`
- **Agent Specs**: `/agents/*/agent-spec.yaml`

## Key Differences

### Basic Workflow (`make xml-prompt`)
- Uses A/B agents ✅
- No context analysis ❌
- No input identification ❌
- Good for: Simple prompts

### Enhanced Workflow (`make xml-prompt-enhanced`)
- No A/B agents ❌
- Context analysis ✅
- Input identification ✅
- Good for: Testing context logic

### Integrated A/B Workflow (`make xml-prompt-ab`) ⭐
- Uses A/B agents ✅
- Context analysis ✅
- Input identification ✅
- Iterative refinement ✅
- **Good for: Production use**

## SDLC Framework Commands

This project now includes SDLC governance framework for development lifecycle management.

### Quick SDLC Commands

```bash
# Check development status
make status

# Start a work session
make session-start

# Run SDLC tests
make test-all

# End work session
make session-end
```

### SDLC Claude Skills

```bash
/sdlc-plan          # Plan next work
/sdlc-status        # Show project status
/sdlc-test          # Run tests
/sdlc-quality       # Quality gates
```

See [docs/SDLC-INTEGRATION.md](docs/SDLC-INTEGRATION.md) for complete SDLC documentation.

## Clean Up

```bash
make clean  # Remove all generated files
```
