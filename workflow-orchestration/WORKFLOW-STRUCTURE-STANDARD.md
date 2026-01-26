# Workflow Structure Standard

**Version**: 1.0.0
**Last Updated**: 2026-01-26
**Status**: Official Standard

## Overview

This document defines the canonical structure for all workflows in the workflow-orchestration system. All workflows MUST follow this structure to ensure consistency, maintainability, and compatibility with orchestration tools.

**Reference Implementation**: `workflow-orchestration/workflows/prompt-generation/`

## Directory Structure

```
workflow-orchestration/workflows/{workflow-id}/
├── workflow-metadata.json          # REQUIRED - Master workflow definition
├── README.md                       # REQUIRED - Workflow documentation
├── config/
│   └── workflow-settings.json      # REQUIRED - Execution overrides
├── examples/                       # OPTIONAL - Global examples
│   ├── good/                       # Good examples (populate when available)
│   └── bad/                        # Bad examples (populate when available)
└── stages/
    └── {NN-stage-name}/            # REQUIRED - Numbered stages (01, 02, ...)
        ├── stage-config.json       # REQUIRED - Agent config + schemas
        ├── instructions.md         # REQUIRED - Processing instructions
        ├── validation-rules.json   # REQUIRED - Validation checks
        └── examples/               # OPTIONAL - Stage-specific examples
            ├── good/
            └── bad/
```

## Required Files

### 1. workflow-metadata.json (Root Level)

**Purpose**: Master workflow definition containing orchestration logic, stage sequencing, and global configuration.

**Required Fields**:
```json
{
  "workflow_id": "string",           // Kebab-case identifier
  "version": "string",               // Semantic version (e.g., "1.0.0")
  "name": "string",                  // Human-readable name
  "description": "string",           // What the workflow does
  "pattern": "string",               // Pattern type (e.g., "stg-val-wkf")
  "created": "ISO8601",              // Creation timestamp
  "updated": "ISO8601",              // Last update timestamp
  "status": "string",                // active | deprecated | testing
  "stages": [                        // Array of stage definitions
    {
      "stage_id": "string",          // Matches directory name
      "agent": "string",             // Agent identifier
      "config_path": "string",       // Relative path to stage-config.json
      "requirements": {}             // Stage-specific requirements
    }
  ],
  "orchestration": {                 // How stages are sequenced
    "pattern": "string",             // sequential | parallel | conditional
    "loop_logic": {},                // If applicable
    "max_total_attempts": number     // Global retry limit
  },
  "data_passing": {                  // Input/output mappings between stages
    "stage_to_stage": {}
  },
  "global_config_overrides": {},     // Workflow-wide settings
  "metrics": {                       // What to track
    "enabled": boolean,
    "track": []
  },
  "compensation": {                  // Rollback configuration
    "enabled": boolean
  }
}
```

**Validation Rules**:
- `workflow_id` must be kebab-case and match directory name
- `version` must follow semantic versioning (MAJOR.MINOR.PATCH)
- `status` must be one of: `active`, `deprecated`, `testing`
- All `stages[].config_path` must point to existing files
- `stages` array must not be empty

### 2. README.md (Root Level)

**Purpose**: Human-readable documentation of the workflow's purpose, stages, configuration, and usage.

**Required Sections**:

```markdown
# {Workflow Name}

## Overview
[Brief description of workflow purpose and pattern]

## Workflow Stages
[Description of each stage, agent involved, inputs/outputs]

## Execution Flow
[ASCII diagram or description of how stages connect]

## Configuration Files
[List of all configuration files and their purposes]

## Success Criteria
[What defines successful completion]

## Usage
[Example inputs and expected outputs]

## Metrics
[What metrics are tracked]

## Notes
[Migration notes, deployment considerations, etc.]
```

### 3. config/workflow-settings.json

**Purpose**: Workflow-specific execution settings and overrides.

**Required Fields**:
```json
{
  "execution_overrides": {           // Per-stage model/execution settings
    "stage_id": {
      "model": "string",
      "temperature": number,
      "max_tokens": number,
      "top_p": number
    }
  },
  "validation_overrides": {          // Validation behavior customization
    "quality_score_weights": {},
    "require_zero_errors": boolean,
    "generate_feedback": boolean
  },
  "retry_behavior": {                // How retries are handled
    "feedback_mode": "string",       // incremental | full | none
    "preserve_previous_attempts": boolean
  },
  "output_configuration": {          // What to include in outputs
    "include_best_attempt_on_failure": boolean,
    "include_validation_details": boolean,
    "include_metrics": boolean
  }
}
```

### 4. stages/{NN-stage-name}/stage-config.json

**Purpose**: Agent configuration, input/output schemas, and stage-specific validation settings.

**Required Fields**:
```json
{
  "stage_id": "string",              // Must match directory name
  "agent": "string",                 // Agent identifier (e.g., "prompt-generator-001")
  "version": "string",               // Stage version
  "description": "string",           // What this stage does
  "model_config": {                  // LLM configuration
    "model": "string",
    "temperature": number,
    "max_tokens": number,
    "top_p": number
  },
  "input_schema": {                  // Expected inputs
    "required": [],
    "optional": []
  },
  "output_schema": {                 // Expected outputs
    "required": [],
    "optional": []
  },
  "validation": {                    // Validation behavior
    "enabled": boolean,
    "fail_on_errors": boolean,
    "rules_path": "string"           // Path to validation-rules.json
  },
  "resources": {                     // Available resources
    "instructions_path": "string",
    "validation_rules_path": "string",
    "examples_path": "string"
  }
}
```

**Validation Rules**:
- `stage_id` must match the directory name (e.g., "01-generate-prompt")
- `agent` must reference a valid agent in the system
- All paths in `resources` must exist
- `input_schema.required` must list at least one field
- `output_schema.required` must list at least one field

### 5. stages/{NN-stage-name}/instructions.md

**Purpose**: Detailed processing instructions for the agent executing this stage.

**Required Sections**:

```markdown
# {Stage Name} - Instructions

## Objective
[Clear statement of what this stage accomplishes]

## Processing Steps
[Numbered steps describing how to process inputs]

## Quality Criteria
[What defines a good output from this stage]

## Handling Feedback (if applicable)
[How to process feedback from downstream stages]

## Output Format
[Expected structure and format of outputs]

## Anti-Patterns
[Common mistakes to avoid]

## Reference Materials
[Links to examples, validation rules, etc.]
```

### 6. stages/{NN-stage-name}/validation-rules.json

**Purpose**: Structural and semantic validation checks for stage outputs.

**Required Fields**:
```json
{
  "rules": [
    {
      "rule_id": "string",           // Unique identifier
      "description": "string",       // What this rule checks
      "severity": "string",          // error | warning | info
      "check": {},                   // Validation logic specification
      "message": "string",           // Error message template
      "fix": "string"                // How to fix if violated
    }
  ],
  "scoring": {                       // How to calculate quality score
    "base_score": number,
    "error_penalty": number,
    "warning_penalty": number
  }
}
```

**Validation Rules**:
- Must include at least one rule with `severity: "error"`
- Each `rule_id` must be unique
- `scoring.base_score` typically starts at 100
- Penalties should be negative numbers or subtracted from base score

## Optional Directories

### examples/ (Root and Stage Level)

**Purpose**: Provide concrete examples of good and bad inputs/outputs.

**Structure**:
```
examples/
├── good/                            # Examples of correct outputs
│   ├── example-01-{description}.md
│   ├── example-02-{description}.md
│   └── ...
└── bad/                             # Examples of incorrect outputs
    ├── example-01-{description}.md
    ├── example-02-{description}.md
    └── ...
```

**Example File Format**:
```markdown
# {Good|Bad} Example: {Description}

## Context
[What user requested or scenario]

## Input
[Input data provided]

## Output
[Generated output]

## Why This Is {Good|Bad}
- [Reason 1]
- [Reason 2]
- [...]

## Lessons
[What to learn from this example]
```

**Best Practices**:
- Include 2-3 good examples showing different scenarios
- Include 2-3 bad examples showing common mistakes
- Add `.gitkeep` files to preserve empty directories in version control
- Use descriptive filenames: `example-01-meeting-summary.md`

## Naming Conventions

### Workflow IDs
- **Format**: `kebab-case`
- **Examples**: `prompt-generation`, `data-enrichment`, `multi-stage-validation`
- **Rules**: lowercase, hyphens only, no spaces or special characters

### Stage Names
- **Format**: `{NN-stage-name}`
- **Examples**: `01-generate-prompt`, `02-validate-quality`, `03-enrich-data`
- **Rules**:
  - Two-digit prefix (01, 02, 03, ...)
  - Kebab-case after prefix
  - Descriptive verb-noun structure

### Agent Identifiers
- **Format**: `{role}-{version}`
- **Examples**: `prompt-generator-001`, `prompt-validator-001`, `data-enricher-002`
- **Rules**: kebab-case role, three-digit version suffix

### File Names
- **Configuration**: Exact names required (see Required Files)
- **Examples**: Descriptive with prefix (e.g., `example-01-meeting-summary.md`)
- **Documentation**: Use kebab-case for multi-word files

## Validation Checklist

Use this checklist when creating or reviewing a workflow:

### Structure
- [ ] Workflow directory matches `workflow_id` in metadata
- [ ] All required files present
- [ ] All stages numbered sequentially (01, 02, ...)
- [ ] `config/` directory exists
- [ ] `stages/` directory exists

### Configuration Files
- [ ] `workflow-metadata.json` is valid JSON
- [ ] `workflow-metadata.json` includes all required fields
- [ ] `config/workflow-settings.json` exists and is valid
- [ ] Each stage has `stage-config.json`
- [ ] Each `stage-config.json` includes all required fields

### Documentation
- [ ] Root `README.md` exists and follows required structure
- [ ] Each stage has `instructions.md`
- [ ] Instructions include all required sections
- [ ] Instructions are specific and actionable

### Validation
- [ ] Each stage has `validation-rules.json`
- [ ] Validation rules include at least one error-level rule
- [ ] Scoring configuration is present
- [ ] All severity levels are valid (error/warning/info)

### Paths and References
- [ ] All `config_path` references in metadata point to existing files
- [ ] All `resources` paths in stage configs exist
- [ ] Stage IDs in metadata match directory names
- [ ] Agent identifiers reference valid agents

### Examples (Optional)
- [ ] If examples exist, they follow the standard format
- [ ] Good/bad examples are clearly separated
- [ ] Example files have descriptive names
- [ ] Empty example directories have `.gitkeep` files

### Version Control
- [ ] All configuration files tracked in git
- [ ] `.gitkeep` files in empty directories
- [ ] No sensitive data in configuration
- [ ] Version numbers follow semantic versioning

## Automated Validation

A validation script is provided to check workflow structure:

```bash
./scripts/validate-workflow-structure.sh workflow-orchestration/workflows/{workflow-id}
```

This script verifies:
- All required files exist
- Directory structure is correct
- Stage numbering is sequential
- Configuration files are valid JSON

## Migration from Non-Standard Structure

If you have an existing workflow that doesn't follow this structure:

1. **Create new structure**: Set up directories according to this standard
2. **Migrate metadata**: Move workflow configuration to `workflow-metadata.json`
3. **Organize stages**: Rename stage directories with numbered prefixes
4. **Extract settings**: Move execution overrides to `config/workflow-settings.json`
5. **Update paths**: Fix all relative path references
6. **Add documentation**: Create README.md and instructions.md files
7. **Validate**: Run validation script to confirm structure
8. **Test**: Execute workflow to ensure functionality preserved

## Reference Implementation

The **`prompt-generation` workflow** serves as the canonical reference:

```
workflow-orchestration/workflows/prompt-generation/
```

When in doubt, refer to this implementation for:
- Complete file structure
- Field naming conventions
- Documentation style
- Configuration organization

## Version History

| Version | Date       | Changes                          |
|---------|------------|----------------------------------|
| 1.0.0   | 2026-01-26 | Initial standard documentation   |

## Questions or Issues

For questions about this standard:
1. Review the reference implementation (`prompt-generation`)
2. Check existing workflows for examples
3. Consult the team for clarification
4. Propose updates via pull request if standard needs revision
