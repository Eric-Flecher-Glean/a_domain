# Workflow Development Guide

**Version**: 1.0.0
**Last Updated**: 2026-01-26
**Audience**: Workflow Developers and Contributors

---

## Overview

This guide explains the complete workflow for creating, documenting, and deploying new workflows in the document-driven agent orchestration system.

## Quick Start: Creating a New Workflow

### The Two-Skill Workflow

Creating a production-ready workflow involves two complementary skills:

1. **`/new-workflow`** - Creates structure and configuration
2. **`/generate-examples`** - Populates examples and documentation

```bash
# Step 1: Create workflow structure
/new-workflow

# Step 2: Generate examples
/generate-examples

# Step 3: Validate structure
./scripts/validate-workflow-structure.sh workflow-orchestration/workflows/{workflow-id}

# Step 4: Test workflow
# [Run actual workflow execution tests]

# Step 5: Register agents
# [Register with Glean Agent Builder]
```

---

## Phase 1: Workflow Design with `/new-workflow`

### What `/new-workflow` Creates

The `/new-workflow` skill creates the complete directory structure and configuration files:

```
workflow-orchestration/workflows/{workflow-id}/
├── workflow-metadata.json          # Master workflow definition
├── README.md                       # Workflow documentation
├── config/
│   └── workflow-settings.json      # Execution overrides
├── examples/                       # Empty (populated by /generate-examples)
│   ├── good/.gitkeep
│   └── bad/.gitkeep
└── stages/
    └── {NN-stage-name}/
        ├── stage-config.json       # Agent config + schemas
        ├── instructions.md         # Processing instructions
        ├── validation-rules.json   # Validation checks
        └── examples/               # Empty (populated by /generate-examples)
            ├── good/.gitkeep
            └── bad/.gitkeep
```

### Interactive Questions

`/new-workflow` guides you through:

1. **Workflow Purpose**: What problem does this solve?
2. **Bounded Context**: Which domain? (PromptEngineering, WorkflowOrchestration, etc.)
3. **Agent Selection**: Reuse existing agents or create new ones?
4. **Pattern Selection**: Sequential, parallel, stg-val-wkf, or custom?
5. **Stage Configuration**: Number of stages, inputs/outputs, validation
6. **Data Mapping**: How data flows between stages
7. **Review & Validation**: Check design before generation

### Output

✅ Complete workflow directory structure
✅ All required configuration files
✅ Proper naming conventions
✅ Valid JSON/YAML syntax
✅ Empty example directories (with .gitkeep files)
✅ README with usage instructions

---

## Phase 2: Example Generation with `/generate-examples`

### What `/generate-examples` Creates

The `/generate-examples` skill analyzes your workflow configuration and generates realistic examples:

```
workflow-orchestration/workflows/{workflow-id}/
├── examples/
│   ├── end-to-end-success.md           # Complete workflow execution
│   ├── end-to-end-refinement-loop.md   # Validation feedback loop
│   └── end-to-end-convergence.md       # Multi-attempt improvement
└── stages/
    └── {stage-id}/
        └── examples/
            ├── good/
            │   ├── example-01-{theme}.md       # Correct usage example
            │   └── example-02-{theme}.md       # Another good example
            └── bad/
                ├── example-01-{antipattern}.md # Common mistake
                └── example-02-{antipattern}.md # Another mistake
```

### What It Analyzes

`/generate-examples` reads:

- **workflow-metadata.json** - Workflow pattern, stages, orchestration
- **stage-config.json** - Input/output schemas, agent configuration
- **instructions.md** - Processing steps, quality criteria, anti-patterns
- **validation-rules.json** - Validation rules, severity levels, error messages

### Domain Intelligence

The skill identifies your workflow's domain and generates contextually appropriate examples:

| Domain | Example Themes |
|--------|----------------|
| **PromptEngineering** | Meeting summaries, code reviews, data extraction prompts |
| **CustomerAnalytics** | Support tickets, NPS surveys, feature requests, bug reports |
| **DataProcessing** | CSV transformations, API responses, database records |
| **WorkflowOrchestration** | Multi-agent coordination, task decomposition |

### Output

✅ 2-3 good examples per stage showing correct usage
✅ 2-3 bad examples per stage showing common mistakes
✅ 1-3 end-to-end workflow examples
✅ Clear explanations of what makes each example good/bad
✅ References to validation rules
✅ How-to-fix instructions for bad examples

---

## Phase 3: Validation with `validate-workflow-structure.sh`

### Automated Structure Validation

Run the validation script to ensure your workflow follows the standard:

```bash
./scripts/validate-workflow-structure.sh workflow-orchestration/workflows/{workflow-id}
```

### What Gets Validated

The script checks:

- ✅ All required files exist (workflow-metadata.json, README.md, etc.)
- ✅ All required directories exist (config/, stages/, examples/)
- ✅ Stage naming follows convention (NN-stage-name)
- ✅ JSON files are valid and parseable
- ✅ Required fields present in workflow-metadata.json
- ✅ Version follows semantic versioning
- ✅ Status field has valid value (active/deprecated/testing)

### Expected Output

```
╔════════════════════════════════════════════════════════════╗
║  Workflow Structure Validation                             ║
╚════════════════════════════════════════════════════════════╝

Validating: workflow-orchestration/workflows/{workflow-id}

━━━ Root Level Files ━━━
✅ Found: workflow-metadata.json
✅ Found: README.md

━━━ Config Directory ━━━
✅ Found directory: config
✅ Found: config/workflow-settings.json

━━━ Stages Directory ━━━
✅ Found directory: stages

━━━ Stage: 01-{stage-name} ━━━
✅ Found: stages/01-{stage-name}/stage-config.json
✅ Found: stages/01-{stage-name}/instructions.md
✅ Found: stages/01-{stage-name}/validation-rules.json

╔════════════════════════════════════════════════════════════╗
║  Validation Summary                                        ║
╚════════════════════════════════════════════════════════════╝

✅ Workflow structure is valid!
   No errors or warnings found.
```

---

## Phase 4: Customization and Refinement

### Customizing Generated Files

After running `/new-workflow` and `/generate-examples`, customize:

1. **Instructions** (`stages/{stage-id}/instructions.md`):
   - Add domain-specific processing steps
   - Refine quality criteria
   - Add more anti-patterns
   - Include troubleshooting tips

2. **Validation Rules** (`stages/{stage-id}/validation-rules.json`):
   - Adjust scoring weights
   - Add custom validation checks
   - Refine error messages
   - Update fix instructions

3. **Examples**:
   - Review generated examples for accuracy
   - Add more domain-specific scenarios
   - Enhance explanations
   - Include edge cases specific to your use case

4. **Workflow Settings** (`config/workflow-settings.json`):
   - Tune model parameters (temperature, max_tokens)
   - Adjust success thresholds
   - Configure retry behavior
   - Set timeout values

---

## Phase 5: Testing

### Using Examples as Test Cases

Generated examples serve as test cases:

```bash
# Test with good examples (should pass)
cat stages/01-generate-prompt/examples/good/meeting-summary-prompt.md | \
  # [Extract input JSON] | \
  # [Run workflow] | \
  # [Verify output matches expected]

# Test with bad examples (should fail validation)
cat stages/01-generate-prompt/examples/bad/vague-incomplete-prompt.md | \
  # [Extract input JSON] | \
  # [Run workflow] | \
  # [Verify validation catches the error]
```

### End-to-End Testing

Use workflow-level examples to test complete execution:

```bash
# Test success path
cat examples/end-to-end-success.md | \
  # [Extract inputs] | \
  # [Run full workflow] | \
  # [Verify all stages pass]

# Test refinement loop
cat examples/end-to-end-refinement-loop.md | \
  # [Extract inputs] | \
  # [Run workflow] | \
  # [Verify feedback loop triggers]
```

---

## Phase 6: Agent Registration

### Preparing for Glean Agent Builder

When registering agents with Glean Agent Builder, include:

1. **Agent Specification** (`agents/{agent-id}/agent-spec.yaml`)
2. **Example Inputs/Outputs** (from `stages/{stage-id}/examples/good/`)
3. **Validation Criteria** (from `stages/{stage-id}/validation-rules.json`)
4. **Instructions** (from `stages/{stage-id}/instructions.md`)

### Registration Checklist

- [ ] Agent spec YAML is complete and valid
- [ ] At least 2 good examples documented
- [ ] Validation thresholds defined
- [ ] Input/output schemas specified
- [ ] Model configuration set
- [ ] Bounded context identified
- [ ] Glean integration configured (if applicable)

---

## Reference Implementation: `prompt-generation`

The **`prompt-generation` workflow** serves as the canonical reference for all workflows:

```
workflow-orchestration/workflows/prompt-generation/
```

### What Makes It Exemplary

1. **Complete Structure**: All required files present
2. **Comprehensive Documentation**: Detailed README and instructions
3. **Rich Configuration**: Full schemas, validation rules, orchestration logic
4. **Clear Data Flow**: Explicit mappings between stage inputs/outputs
5. **Quality Validation**: Multi-dimensional scoring with clear thresholds
6. **Proper Naming**: Numbered stages (01-, 02-), descriptive names
7. **Examples Ready**: Directories structured with .gitkeep files

### Use It As Your Template

When in doubt:
- Copy the structure from `prompt-generation`
- Adapt the configurations to your domain
- Follow the same naming patterns
- Use similar documentation style

---

## Workflow Patterns

### stg-val-wkf (Staged Validation Workflow)

**Best For**: Quality-critical outputs requiring validation and refinement

**Characteristics**:
- Generator stage produces output
- Validator stage assesses quality
- Feedback loop on validation failure
- Max attempts with escalation

**Example**: `prompt-generation` workflow

**When to Use**:
- Output quality is critical
- Iterative refinement improves results
- Validation criteria are well-defined
- Feedback can guide improvements

### sequential

**Best For**: Linear transformations with clear stage dependencies

**Characteristics**:
- Stages execute in order (1 → 2 → 3)
- Each stage depends on previous output
- No loops or parallel execution
- Simple data pipeline

**When to Use**:
- Clear sequential processing steps
- Each stage transforms previous output
- No validation loops needed
- Straightforward data flow

### parallel

**Best For**: Independent tasks that can run concurrently

**Characteristics**:
- Multiple stages execute simultaneously
- No dependencies between parallel stages
- Results aggregated at the end
- Faster overall execution

**When to Use**:
- Independent processing tasks
- No shared state between stages
- Time-sensitive workloads
- Embarrassingly parallel problems

### custom

**Best For**: Complex business logic not fitting standard patterns

**Characteristics**:
- Conditional routing
- Dynamic stage selection
- Complex orchestration logic
- Custom success criteria

**When to Use**:
- Standard patterns don't fit
- Complex decision trees
- Human-in-the-loop requirements
- Advanced coordination needs

---

## Best Practices

### 1. Start Simple

- Begin with the simplest pattern that works
- Use `sequential` unless you need validation loops or parallelism
- Add complexity only when justified

### 2. Reuse Agents When Possible

- Check the agent catalog before creating new agents
- Existing agents are tested and validated
- Reuse reduces maintenance burden

### 3. Write Clear Instructions

- Assume the agent has no domain knowledge
- Provide step-by-step processing guidance
- Include quality criteria and anti-patterns
- Use examples to clarify expectations

### 4. Define Specific Validation Rules

- Avoid vague criteria like "good quality"
- Define measurable checks (e.g., "contains at least 2 examples")
- Specify severity levels (error, warning, info)
- Provide actionable error messages

### 5. Generate Realistic Examples

- Use domain-appropriate data
- Include edge cases and boundary conditions
- Show both success and failure scenarios
- Explain what makes each example good/bad

### 6. Test Early and Often

- Validate structure before testing functionality
- Use examples as automated test cases
- Test feedback loops and retry behavior
- Verify metrics collection works

---

## Troubleshooting

### Common Issues

#### "Workflow validation fails with missing fields"

**Cause**: Workflow metadata doesn't include all required fields

**Fix**:
```bash
# Check what's missing
./scripts/validate-workflow-structure.sh workflow-orchestration/workflows/{workflow-id}

# Common missing fields:
# - name (add to workflow-metadata.json)
# - updated (add current date)
# - status (set to "active", "testing", or "deprecated")
```

#### "Examples don't match my workflow's domain"

**Cause**: `/generate-examples` couldn't detect domain from description

**Fix**:
1. Enhance workflow description in workflow-metadata.json
2. Add domain context to stage instructions
3. Manually specify themes: `/generate-examples --themes "your,domains"`
4. Customize generated examples after creation

#### "Agent can't find required resources"

**Cause**: Resource paths in stage-config.json are incorrect

**Fix**:
```json
{
  "resources": {
    "instructions_path": "instructions.md",           // Relative to stage dir
    "validation_rules_path": "validation-rules.json", // Relative to stage dir
    "examples_path": "examples/",                     // Relative to stage dir
    "global_examples_path": "../../examples/"         // Relative path to workflow examples
  }
}
```

#### "Validation script reports JSON errors"

**Cause**: Trailing commas or malformed JSON in config files

**Fix**:
```bash
# Validate JSON syntax
python3 -m json.tool workflow-orchestration/workflows/{workflow-id}/workflow-metadata.json

# Common issues:
# - Trailing commas in JSON (not allowed)
# - Missing quotes around strings
# - Unclosed braces or brackets
```

---

## Additional Resources

### Documentation

- **Workflow Structure Standard**: `workflow-orchestration/WORKFLOW-STRUCTURE-STANDARD.md`
- **Template Documentation**: `workflow-orchestration/templates/README.md`
- **Bounded Contexts Guide**: `.claude/knowledge/workflow-creation/bounded-contexts.md`
- **Workflow Patterns Guide**: `.claude/knowledge/workflow-creation/workflow-patterns.md`
- **Validation Dimensions**: `.claude/knowledge/workflow-creation/validation-dimensions.md`
- **Agent Catalog**: `.claude/knowledge/workflow-creation/agent-catalog.md`

### Tools

- **`/new-workflow`**: Create new workflow structure
- **`/generate-examples`**: Populate examples directories
- **`validate-workflow-structure.sh`**: Automated structure validation

### Reference Implementations

- **`workflow-orchestration/workflows/prompt-generation/`**: Canonical workflow example
- **`agents/prompt-generator/`**: Example agent implementation
- **`agents/prompt-validator/`**: Example validator agent

---

## Quick Reference Card

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  Workflow Development Quick Reference                    ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

1. CREATE WORKFLOW
   /new-workflow
   → Answer interactive questions
   → Review and confirm
   → Files generated ✅

2. GENERATE EXAMPLES
   /generate-examples
   → Analyzes configuration
   → Creates good/bad examples
   → Generates E2E scenarios ✅

3. VALIDATE STRUCTURE
   ./scripts/validate-workflow-structure.sh \
     workflow-orchestration/workflows/{workflow-id}
   → Checks all required files
   → Validates JSON syntax
   → Verifies naming conventions ✅

4. CUSTOMIZE
   → Edit instructions.md
   → Tune validation-rules.json
   → Refine examples
   → Adjust workflow-settings.json

5. TEST
   → Use examples as test cases
   → Test validation loops
   → Verify metrics collection

6. REGISTER AGENTS
   → Upload agent-spec.yaml to Glean
   → Include examples
   → Configure integrations

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  File Structure                                           ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

workflow-orchestration/workflows/{workflow-id}/
├── workflow-metadata.json       # /new-workflow creates
├── README.md                    # /new-workflow creates
├── config/
│   └── workflow-settings.json   # /new-workflow creates
├── examples/                    # /generate-examples populates
│   ├── good/
│   └── bad/
└── stages/
    └── {NN-stage-name}/
        ├── stage-config.json    # /new-workflow creates
        ├── instructions.md      # /new-workflow creates
        ├── validation-rules.json # /new-workflow creates
        └── examples/            # /generate-examples populates
            ├── good/
            └── bad/

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  Workflow Patterns                                        ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

stg-val-wkf   Quality-critical with validation loops
sequential    Linear transformations
parallel      Independent concurrent tasks
custom        Complex business logic
```

---

**Version**: 1.0.0
**Last Updated**: 2026-01-26
**Maintained By**: Workflow Orchestration Team
