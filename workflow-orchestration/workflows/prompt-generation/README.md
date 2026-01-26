# Prompt Generation Workflow

## Overview
This workflow implements a 2-agent staged validation pattern for generating high-quality XML-structured prompts. It demonstrates the `stg-val-wkf` (Stage Validation Workflow) pattern with loop-back refinement.

## Workflow Stages

### Stage 1: Prompt Generation
**Agent**: `prompt-generator-001`
**Input**: Natural language prompt request
**Output**: XML-structured prompt

The generator agent transforms user requests into well-formed XML prompts following Anthropic's hierarchical methodology.

### Stage 2: Quality Validation
**Agent**: `prompt-validator-001`
**Input**: Generated XML prompt
**Output**: Validation result with quality score and feedback

The validator agent checks structure, completeness, and quality against defined standards. If validation fails (score < 90), feedback is returned to the generator for refinement.

## Execution Flow

```
User Request
    ↓
┌──────────────────────┐
│ Generate Prompt (A1) │
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│ Validate Quality (A1)│
└──────────┬───────────┘
           ↓
      [Pass/Fail?]
           ↓
    Pass → Output
           ↓
    Fail → Generate Prompt (A2) with feedback
           ↓
           Validate Quality (A2)
           ↓
      [Pass/Fail?]
           ↓
    Pass → Output
           ↓
    Fail → Generate Prompt (A3) with feedback
           ↓
           Validate Quality (A3)
           ↓
      [Pass/Fail?]
           ↓
    Pass → Output
           ↓
    Fail → Escalate with best attempt
```

## Configuration Files

- **workflow-metadata.json**: Workflow definition and stage sequence
- **config/workflow-settings.json**: Workflow-specific overrides
- **stages/01-generate-prompt/**: Stage 1 configuration
  - instructions.md
  - validation-rules.json
  - stage-config.json
  - examples/
- **stages/02-validate-quality/**: Stage 2 configuration
  - instructions.md
  - validation-rules.json
  - stage-config.json
  - examples/

## Success Criteria

- **Quality Score**: ≥ 90/100
- **Max Attempts**: 3
- **Timeout**: 300 seconds

## Usage

### Via Glean Workflow
```json
{
  "workflow_id": "prompt-generation",
  "input": {
    "user_request": "Create a prompt for meeting summarization"
  }
}
```

### Expected Output
```json
{
  "final_prompt": "<metadata>...</metadata><primary_goal>...</primary_goal>...",
  "quality_score": 92,
  "attempts_required": 1,
  "validation_details": {...}
}
```

## Metrics Tracked

- Execution time (end-to-end)
- Attempt count per workflow
- Quality scores by attempt
- Success rate (first attempt vs. total)
- Feedback effectiveness

## Migration Notes

This workflow is designed to be path-agnostic and can be migrated to GDrive by:
1. Copying the entire `workflow-orchestration/workflows/prompt-generation/` folder to GDrive
2. Updating `workflow-metadata.json` with GDrive URL
3. No code changes required

## References

- [Staged Validation Workflow Pattern](../../docs/concepts/a-b-workflow.md)
- [Global Configuration](../../global/config/)
- [Agent Specifications](../../../agents/)
