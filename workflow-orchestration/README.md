# Workflow Orchestration System

## Overview
This directory contains the complete configuration system for Glean agent workflow orchestration. It implements a **document-driven configuration** approach where workflows, agents, and validation rules are defined in structured files that can be loaded dynamically.

## Architecture

```
workflow-orchestration/
├── global/                    # Global configs (all workflows)
│   ├── config/
│   │   ├── global-settings.json          # System-wide settings
│   │   └── validation-standards.json     # Quality thresholds
│   └── examples/
│       ├── good/                          # High-quality examples
│       └── bad/                           # Anti-patterns
│
└── workflows/                 # Individual workflow definitions
    └── prompt-generation/
        ├── workflow-metadata.json         # Workflow config
        ├── config/
        │   └── workflow-settings.json     # Workflow overrides
        ├── stages/
        │   ├── 01-generate-prompt/
        │   │   ├── instructions.md        # Agent instructions
        │   │   ├── validation-rules.json  # Validation logic
        │   │   ├── stage-config.json      # Stage settings
        │   │   └── examples/              # Stage examples
        │   └── 02-validate-quality/
        │       └── [same structure]
        └── README.md
```

## Key Concepts

### 1. Document-Driven Configuration
All workflow logic, validation rules, and agent instructions are stored in structured files (JSON, YAML, Markdown). This enables:
- **Version control**: Track changes to workflows over time
- **Non-technical updates**: Product managers can edit configs without code changes
- **Dynamic loading**: Agents load latest configs at runtime
- **Migration flexibility**: Easy to move from local files to GDrive

### 2. Hierarchical Settings
Settings cascade from global to workflow to stage:
```
Global Settings (apply to all)
    ↓ Override
Workflow Settings (apply to this workflow)
    ↓ Override
Stage Settings (apply to this stage)
```

### 3. Staged Validation Pattern
Workflows are organized into sequential stages with validation gates:
```
Stage 1 (Execute) → Validation Gate 1 → Stage 2 (Validate)
    ↓ Fail                                    ↓ Fail
    Loop back with feedback ←─────────────────┘
```

### 4. Example-Driven Learning
Each stage includes good and bad examples that agents reference:
- **Good examples**: Demonstrate best practices
- **Bad examples**: Illustrate anti-patterns and common mistakes
- **Metadata**: Explains why examples are good/bad

## Global Configuration

### global-settings.json
System-wide defaults for all workflows:
- Execution settings (max_attempts: 3, timeout: 300s)
- Validation thresholds (default: 85)
- State management (saga enabled, backup on step)
- Performance (caching, async loading)

### validation-standards.json
Quality standards and scoring rules:
- Quality thresholds (excellent: 95, good: 90, acceptable: 85)
- Scoring penalties (error: -20, warning: -5)
- Validation severity levels
- Feedback requirements

## Workflow Configuration

### workflow-metadata.json
Defines the workflow structure:
- **stages**: Ordered list of stages with agent assignments
- **orchestration**: Pattern (sequential, parallel, conditional)
- **data_passing**: How data flows between stages
- **compensation**: Saga pattern for rollback (if needed)
- **metrics**: What to track

### workflow-settings.json
Workflow-specific overrides:
- Execution timeouts
- Validation thresholds
- Agent model settings (temperature, tokens)
- Retry behavior

## Stage Configuration

Each stage has:

### instructions.md
Human-readable instructions for the agent:
- Objective: What this stage accomplishes
- Processing steps: How to execute the task
- Quality criteria: What defines success
- Output format: Structure of results

### validation-rules.json
Machine-readable validation logic:
- **rules**: List of checks with severity levels
- **scoring**: How to calculate quality scores
- **loop_logic**: What to do on failure

### stage-config.json
Stage-specific settings:
- Agent configuration (model, temperature)
- Input/output schemas
- Resource paths (instructions, examples)
- Timeout and retry policies

### examples/
Good and bad examples specific to this stage:
- `good/`: Examples that pass validation
- `bad/`: Examples that fail with explanations
- `_metadata.json`: Describes each example

## Example Library

### Global Examples
Located in `global/examples/`, these are referenced by all workflows:
- **well-structured-prompts/**: High-quality XML prompts
- **anti-patterns/**: Common mistakes to avoid

### Stage-Specific Examples
Located in each stage's `examples/` folder:
- Demonstrate the specific task of that stage
- Show edge cases relevant to that stage
- Include metadata explaining what makes them good/bad

## Data Flow

### Input
User provides input → Workflow receives it → Stage 1 executes

### Between Stages
Stage 1 output → mapped to → Stage 2 input via `data_passing` config

### Feedback Loop
Stage 2 validation fails → feedback → mapped to → Stage 1 input for retry

### Output
Final stage succeeds → workflow output includes results + metadata

## State Management (Saga Pattern)

Each workflow execution maintains state:
```
state/workflow-executions/{workflow-id}_{timestamp}.json
{
  "workflow_id": "prompt-generation",
  "execution_id": "exec-12345",
  "current_step": "validate-prompt-attempt-2",
  "completed_steps": ["generate-1", "validate-1", "generate-2"],
  "step_outputs": {...},
  "compensation_stack": []
}
```

Benefits:
- **Recovery**: Resume from failure point
- **Debugging**: Inspect state at any step
- **Audit**: Track full execution history

## Migration to GDrive

This system is designed to be path-agnostic:

### Current (Local)
```
workflow-orchestration/ (local folder)
```

### Future (GDrive)
```
https://drive.google.com/.../workflow-orchestration/
```

### Migration Steps
1. Copy entire `workflow-orchestration/` folder to GDrive
2. Update `workflow-metadata.json`:
   ```json
   "config_source": "https://drive.google.com/.../workflow-orchestration"
   ```
3. Agents load configs from GDrive URL
4. No code changes required

## Usage

### For Agent Developers
1. Create new workflow folder: `workflows/my-workflow/`
2. Copy structure from `prompt-generation/`
3. Update `workflow-metadata.json` with stages and agents
4. Write stage instructions and validation rules
5. Add examples to libraries
6. Register workflow in Glean

### For Product Managers
1. Navigate to workflow config folder
2. Edit `instructions.md` files (natural language)
3. Adjust validation rules in `validation-rules.json`
4. Update examples in `examples/` folders
5. Changes take effect immediately (agents load latest)

### For Data Scientists
1. Review `validation-rules.json` for scoring logic
2. Analyze metrics from `state/` folder
3. Adjust thresholds in `global-settings.json`
4. Add/remove validation checks
5. Update example metadata

## Best Practices

### Configuration Files
- Use clear, descriptive names
- Include version numbers
- Add comments for complex logic
- Validate JSON syntax before committing

### Instructions
- Write for the agent, not humans (be explicit)
- Include examples in instructions
- Number steps sequentially
- Define success criteria clearly

### Examples
- Use realistic, domain-appropriate data
- Include edge cases
- Explain why examples are good/bad
- Keep examples focused and concise

### Validation Rules
- Start with lenient thresholds, tighten over time
- Distinguish between errors (blocking) and warnings (quality)
- Provide actionable error messages
- Reference specific sections in feedback

## Monitoring

### Metrics to Track
- Workflow success rate (first attempt vs. total)
- Average execution time
- Quality score distribution
- Feedback effectiveness (improvement per attempt)
- Agent latency by stage

### Debugging
1. Check state file: `state/workflow-executions/latest.json`
2. Review step outputs in state
3. Inspect validation feedback
4. Compare against examples library
5. Adjust configs as needed

## References
- [Staged Validation Pattern](../docs/concepts/a-b-workflow.md)
- [Prompt Generation Workflow](workflows/prompt-generation/README.md)
- [Global Settings](global/config/global-settings.json)
- [Validation Standards](global/config/validation-standards.json)
