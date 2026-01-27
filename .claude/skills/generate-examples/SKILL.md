---
name: generate-examples
description: Analyzes workflow configurations and generates realistic, domain-appropriate good and bad examples for each stage. Creates comprehensive examples demonstrating proper usage and common pitfalls.
---

# /generate-examples - Workflow Example Generator

## Description

Intelligent skill that analyzes workflow configurations and generates realistic, domain-appropriate examples for each stage. Reads workflow metadata, stage configurations, instructions, and validation rules to create comprehensive good and bad examples that demonstrate proper usage and common pitfalls.

**Category**: Workflow Development
**Complexity**: Moderate
**Prerequisites**: Existing workflow with configuration files

## Usage

```
/generate-examples
```

Run from within a workflow directory, or:

```
/generate-examples path/to/workflow
```

Specify a workflow path explicitly.

---

## What This Skill Does

The `/generate-examples` skill provides these key capabilities:

1. **Configuration Analysis**: Reads workflow-metadata.json, stage-config.json, instructions.md, and validation-rules.json to understand workflow purpose and requirements
2. **Domain Intelligence**: Identifies the workflow's domain (e.g., prompt engineering, data analysis, customer feedback) and generates contextually appropriate examples
3. **Good Example Generation**: Creates 2-3 realistic examples per stage showing correct inputs, expected outputs, and proper formatting
4. **Bad Example Generation**: Creates 2-3 anti-pattern examples per stage demonstrating common mistakes with explanations of what's wrong
5. **End-to-End Examples**: Generates workflow-level examples showing complete multi-stage execution flows
6. **Automatic Documentation**: Creates structured example files with clear explanations, use cases, and learning objectives

---

## When to Use This Skill

Use `/generate-examples` when:

1. **After Creating New Workflow**: You've used `/new-workflow` and need to populate the examples/ directories
2. **Improving Documentation**: Existing workflow lacks clear usage examples or demonstrations
3. **Training New Users**: Team members need concrete examples to understand workflow capabilities
4. **Quality Assurance**: Want to establish baseline examples for testing and validation
5. **Before Agent Registration**: Need examples to include in Glean Agent Builder registration

---

## Example Session

### Basic Usage (Current Directory)

```
User: /generate-examples

Claude: Analyzing workflow in current directory...

Found workflow: prompt-generation
Pattern: stg-val-wkf (Staged Validation Workflow)
Stages: 2 (01-generate-prompt, 02-validate-quality)
Domain: PromptEngineering

Reading configuration files:
✓ workflow-metadata.json
✓ stages/01-generate-prompt/stage-config.json
✓ stages/01-generate-prompt/instructions.md
✓ stages/01-generate-prompt/validation-rules.json
✓ stages/02-validate-quality/stage-config.json
✓ stages/02-validate-quality/instructions.md
✓ stages/02-validate-quality/validation-rules.json

Generating examples for PromptEngineering domain...

Domain identified: XML prompt generation and validation
Example themes selected:
- Meeting summarization prompts
- Code review prompts
- Sentiment analysis prompts
- Data extraction prompts

Creating stage-level examples:
✓ Stage 1 - Good Example: Meeting summarization request
✓ Stage 1 - Good Example: Code review automation
✓ Stage 1 - Bad Example: Vague prompt with missing sections
✓ Stage 1 - Bad Example: Excessive nesting anti-pattern
✓ Stage 2 - Good Example: Well-validated prompt feedback
✓ Stage 2 - Good Example: Comprehensive quality assessment
✓ Stage 2 - Bad Example: Incomplete validation report
✓ Stage 2 - Bad Example: Missing quality scores

Creating end-to-end workflow examples:
✓ E2E Example: Complete prompt generation with validation loop
✓ E2E Example: Failed validation with refinement cycle
✓ E2E Example: Multi-attempt convergence to quality

Files created:
📁 stages/01-generate-prompt/examples/
  📄 good/meeting-summary-prompt.md
  📄 good/code-review-prompt.md
  📄 bad/vague-incomplete-prompt.md
  📄 bad/excessive-nesting-prompt.md

📁 stages/02-validate-quality/examples/
  📄 good/thorough-validation-report.md
  📄 good/actionable-feedback.md
  📄 bad/incomplete-validation.md
  📄 bad/missing-quality-scores.md

📁 examples/
  📄 end-to-end-success.md
  📄 end-to-end-refinement-loop.md
  📄 end-to-end-convergence.md

Summary:
- 11 example files created
- 6 good examples
- 4 bad examples
- 3 end-to-end scenarios

Next steps:
1. Review generated examples for accuracy
2. Customize examples for your specific use cases
3. Add more domain-specific scenarios if needed
4. Reference examples in agent registration
```

### Usage with Specific Workflow Path

```
User: /generate-examples workflow-orchestration/workflows/customer-feedback-analysis

Claude: Analyzing workflow at: workflow-orchestration/workflows/customer-feedback-analysis

Found workflow: customer-feedback-analysis
Pattern: sequential
Stages: 3 (sentiment-analysis, category-classification, report-generation)
Domain: CustomerAnalytics

Reading configuration files...
✓ All configuration files loaded

Generating examples for CustomerAnalytics domain...

Domain identified: Customer feedback analysis and reporting
Example themes selected:
- Product feedback from support tickets
- Feature request categorization
- NPS survey responses
- Bug report sentiment

[Creates examples specific to customer analytics domain...]

Files created: 15 example files across 3 stages + workflow-level examples
```

---

## How It Works

The skill follows this 6-step process:

### Step 1: Workflow Discovery
- Detects workflow directory (current directory or specified path)
- Reads workflow-metadata.json to understand pattern and stages
- Validates workflow structure completeness

### Step 2: Configuration Analysis
- Reads each stage's stage-config.json for input/output schemas
- Analyzes instructions.md to understand processing logic
- Examines validation-rules.json to identify quality criteria
- Extracts domain context and bounded context information

### Step 3: Domain Identification
- Analyzes workflow description and purpose
- Identifies domain (PromptEngineering, CustomerAnalytics, DataProcessing, etc.)
- Selects appropriate example themes based on domain
- Determines realistic data scenarios

### Step 4: Good Example Generation
For each stage:
- Creates 2-3 examples demonstrating correct usage
- Follows input schema exactly
- Shows expected output format
- Includes metadata and explanations
- Uses realistic, domain-appropriate data
- Demonstrates edge cases and variations

### Step 5: Bad Example Generation
For each stage:
- Creates 2-3 examples showing common mistakes
- Violates specific validation rules
- Demonstrates anti-patterns from instructions
- Includes clear explanations of what's wrong
- References relevant validation rule IDs
- Shows how to fix the issue

### Step 6: End-to-End Example Generation
- Creates 1-3 workflow-level examples
- Shows complete execution flow across all stages
- Demonstrates feedback loops (if stg-val-wkf pattern)
- Includes success, failure, and refinement scenarios
- Documents expected behavior and outcomes

---

## Example File Format

Each generated example follows this standard template:

```markdown
# [Example Title]

## Type
[Good Example | Bad Example]

## Use Case
[Brief description of what this example demonstrates]

## Input

\`\`\`json
{
  "user_request": "Create a prompt for summarizing weekly team meetings...",
  "context": {
    "domain": "meeting_management",
    "audience": "engineering_teams"
  }
}
\`\`\`

## Expected Output

\`\`\`json
{
  "xml_prompt": "<metadata>...</metadata>...",
  "prompt_name": "mtg-sum-wkl",
  "components_extracted": {...},
  "generation_metadata": {...}
}
\`\`\`

## Why This Works (Good Example)
- ✓ Clear, specific user request
- ✓ Appropriate domain context
- ✓ Well-structured XML output
- ✓ Follows naming conventions
- ✓ Complete metadata included

## What's Wrong (Bad Example)
- ✗ Violates validation rule: `name-format`
- ✗ Missing required section: `examples`
- ✗ Contains placeholder content: "TBD"
- ✗ Excessive nesting depth (4 levels)

## How to Fix (Bad Example)
1. Change prompt name from "meeting_summary" to "mtg-sum-xxx"
2. Add at least 2 good examples and 1 bad example
3. Replace "TBD" with actual content
4. Flatten structure to max 3 levels

## Validation Rule References
- `name-format` (validation-rules.json, line 45-52)
- `required-sections` (validation-rules.json, line 17-32)
- `no-placeholder-content` (validation-rules.json, line 93-108)
- `nesting-depth` (validation-rules.json, line 68-75)

## Related Examples
- See also: `good/code-review-prompt.md` for another good example
- Compare with: `bad/excessive-nesting-prompt.md` for similar anti-pattern
```

---

## Generated Examples

### Stage-Level Examples

**Good Examples** (`stages/{stage-id}/examples/good/`):
- Demonstrate correct input format matching input_schema
- Show expected output following output_schema
- Use realistic, domain-appropriate data
- Highlight best practices from instructions.md
- Pass all validation rules with high scores
- Include metadata showing validation success

**Bad Examples** (`stages/{stage-id}/examples/bad/`):
- Violate specific validation rules from validation-rules.json
- Demonstrate common anti-patterns mentioned in instructions
- Show incomplete or malformed data
- Include clear explanations of what's wrong
- Reference specific rule IDs and severity levels
- Provide step-by-step fix instructions

### Workflow-Level Examples

**End-to-End Scenarios** (`examples/`):
- **Success Path**: Complete workflow execution with all stages passing
- **Refinement Loop**: Validation failure triggering feedback and regeneration
- **Convergence**: Multi-attempt process improving quality scores
- **Edge Cases**: Unusual inputs or boundary conditions
- **Error Handling**: How workflow handles failures and escalation

---

## Configuration Analysis

The skill reads and analyzes these configuration files:

### workflow-metadata.json
- **Extracts**: Workflow ID, pattern, stages, orchestration logic
- **Uses for**: Understanding stage sequence, feedback loops, success thresholds
- **Informs**: End-to-end example structure, multi-stage dependencies

### stage-config.json
- **Extracts**: Input schema, output schema, agent configuration
- **Uses for**: Generating valid input/output examples, understanding data types
- **Informs**: Example structure, required fields, optional parameters

### instructions.md
- **Extracts**: Processing steps, quality criteria, anti-patterns
- **Uses for**: Understanding what makes a good vs bad example
- **Informs**: Good example best practices, bad example violations

### validation-rules.json
- **Extracts**: Validation rules, severity levels, error messages
- **Uses for**: Creating bad examples that violate specific rules
- **Informs**: Bad example explanations, fix instructions, rule references

---

## Best Practices

### 1. Domain-Appropriate Data
Generate examples using realistic data for the workflow's domain:
- **PromptEngineering**: Use cases like meeting summaries, code reviews, data extraction
- **CustomerAnalytics**: Support tickets, NPS surveys, feature requests
- **DataProcessing**: CSV files, API responses, database records
- **WorkflowOrchestration**: Multi-agent coordination, task decomposition

### 2. Cover Edge Cases
Include examples demonstrating:
- Minimum required fields (bare minimum valid input)
- Maximum complexity (all optional fields populated)
- Boundary conditions (empty arrays, null values, max lengths)
- Special characters (Unicode, XML entities, escaped quotes)

### 3. Reference Validation Rules
Bad examples should:
- Explicitly reference violated rule IDs
- Quote error messages from validation-rules.json
- Link to specific line numbers in configuration files
- Show both the error and the fix

### 4. Progressive Complexity
Order examples from simple to complex:
- Start with basic, straightforward cases
- Progress to more nuanced scenarios
- End with complex, multi-faceted examples
- Build on concepts from earlier examples

### 5. Explain the "Why"
Every example should include:
- **Context**: Why this scenario matters
- **Learning objective**: What the example teaches
- **Key takeaways**: Bullet points of important lessons
- **Related concepts**: Links to other examples or documentation

### 6. Use Real-World Scenarios
Avoid generic placeholders:
- ❌ "Process the data", "Example input", "Sample output"
- ✓ "Summarize Q4 engineering standup notes", "Extract action items from customer call transcript"

---

## Integration with /new-workflow

The `/generate-examples` skill complements `/new-workflow`:

### Workflow Creation Flow
1. **Create Workflow**: Use `/new-workflow` to design and generate workflow files
2. **Generate Examples**: Use `/generate-examples` to populate example directories
3. **Customize**: Review and refine generated examples for your use case
4. **Test**: Use examples as test cases for workflow validation
5. **Register**: Include examples in Glean Agent Builder registration

### File Structure Alignment
`/new-workflow` creates this structure:
```
workflow-orchestration/workflows/{workflow-id}/
├── stages/
│   └── {stage-id}/
│       ├── examples/          # Empty directories
│       │   ├── good/          # ← /generate-examples populates
│       │   └── bad/           # ← /generate-examples populates
│       └── [config files]
└── examples/                  # ← /generate-examples creates E2E examples
```

### Consistency Guarantees
`/generate-examples` ensures:
- Examples match input/output schemas from stage-config.json
- Examples follow patterns described in instructions.md
- Bad examples violate rules from validation-rules.json
- All examples use the standard format from templates

---

## Workflow Support

The skill works with all workflow patterns:

### stg-val-wkf (Staged Validation Workflow)
- Generates examples showing validation feedback loops
- Creates refinement cycle scenarios
- Demonstrates convergence to quality thresholds
- Shows max attempts and escalation behavior

### sequential
- Creates linear stage progression examples
- Shows data passing between stages
- Demonstrates cumulative processing

### parallel
- Generates concurrent stage execution examples
- Shows independent processing paths
- Demonstrates result aggregation

### custom
- Analyzes custom orchestration logic
- Generates examples matching specific patterns
- Adapts to unique workflow requirements

---

## Validation

Before creating example files, the skill validates:

### Configuration Completeness
- ✓ All required config files exist (workflow-metadata.json, stage-config.json, etc.)
- ✓ Schemas are well-formed and parseable JSON
- ✓ Instructions files contain substantive content
- ✓ Validation rules define specific criteria

### Schema Compliance
- ✓ Generated inputs match stage input_schema
- ✓ Generated outputs match stage output_schema
- ✓ Required fields are always included
- ✓ Data types are correct (string, integer, array, object)

### Example Quality
- ✓ Good examples pass all validation rules
- ✓ Bad examples violate specific, identifiable rules
- ✓ All examples include complete documentation
- ✓ Examples use realistic, domain-appropriate data

### Directory Structure
- ✓ Creates examples/good/ and examples/bad/ directories
- ✓ Follows naming conventions (lowercase, hyphens, descriptive)
- ✓ Organizes files logically by theme or use case

---

## Customization

### Controlling Example Count
By default, generates 2-3 examples per category. Customize with:
```
/generate-examples --good-count 4 --bad-count 2
```

### Specifying Example Themes
Override automatic domain detection:
```
/generate-examples --themes "security,compliance,audit"
```

### Targeting Specific Stages
Generate examples for one stage only:
```
/generate-examples --stage 01-generate-prompt
```

### Using Custom Templates
Provide your own example template:
```
/generate-examples --template path/to/custom-template.md
```

### Skipping End-to-End Examples
Generate stage-level examples only:
```
/generate-examples --no-e2e
```

---

## Troubleshooting

### Issue: "Cannot find workflow-metadata.json"
**Cause**: Not running from a valid workflow directory
**Fix**:
- Run from within a workflow directory, or
- Specify path: `/generate-examples path/to/workflow`

### Issue: "Input schema not found in stage-config.json"
**Cause**: Stage configuration is incomplete or malformed
**Fix**:
- Verify stage-config.json has `input_schema` and `output_schema` fields
- Check JSON is well-formed (no trailing commas, proper quotes)
- Regenerate with `/new-workflow` if needed

### Issue: "Cannot determine domain from workflow description"
**Cause**: Workflow description is too vague or missing
**Fix**:
- Add detailed description to workflow-metadata.json
- Or specify themes manually: `/generate-examples --themes "your,domains"`

### Issue: "Generated examples are too generic"
**Cause**: Insufficient context in configuration files
**Fix**:
- Enhance instructions.md with specific use cases
- Add domain context to workflow-metadata.json
- Customize generated examples manually after creation

### Issue: "Bad examples don't clearly show what's wrong"
**Cause**: Validation rules lack detailed error messages
**Fix**:
- Review validation-rules.json and add descriptive error_message fields
- Ensure rule_id and description fields are clear
- Regenerate examples after improving validation rules

### Issue: "Examples directory already exists, won't overwrite"
**Cause**: Protection against overwriting existing examples
**Fix**:
- Review existing examples to see if they should be kept
- Rename existing examples/ to examples.backup/
- Or use: `/generate-examples --force` to overwrite (with confirmation)

---

## Related Skills

- **/new-workflow**: Create new workflows (run this first, then generate examples)
- **/validate-workflow**: Validate workflow configuration and examples
- **/test-workflow**: Run workflow with example inputs as test cases

## Related Documentation

- **Workflow Structure Standard**: `docs/WORKFLOW-STRUCTURE-STANDARD.md`
- **Example Format Guidelines**: `workflow-orchestration/templates/example-template.md`
- **Validation Rules Reference**: `docs/architecture/ARTIFACT-DRIVEN-VALIDATION.md`
- **Domain Catalog**: `.claude/knowledge/workflow-creation/bounded-contexts.md`
- **Agent Catalog**: `.claude/knowledge/workflow-creation/agent-catalog.md`

---

## Technical Implementation Notes

### Example Generation Algorithm
1. Parse all configuration files into structured data
2. Extract domain keywords from descriptions and instructions
3. Match domain to example theme catalog
4. Generate realistic data using domain-specific templates
5. Validate generated examples against schemas
6. Format examples using standard markdown template
7. Write files with proper directory structure

### Domain Detection
Uses keyword matching and semantic analysis:
- **PromptEngineering**: Keywords like "prompt", "XML", "Claude", "generation"
- **CustomerAnalytics**: Keywords like "feedback", "sentiment", "NPS", "support"
- **DataProcessing**: Keywords like "transform", "ETL", "parse", "aggregate"
- **WorkflowOrchestration**: Keywords like "agent", "stage", "coordinate", "orchestrate"

### Quality Assurance
- All generated examples are validated before writing
- Good examples must score ≥ success_threshold
- Bad examples must score < success_threshold
- JSON/XML outputs are validated for well-formedness
- File names follow conventions (lowercase, hyphens, .md extension)

### Performance Considerations
- Caches parsed configuration files
- Generates examples in parallel where possible
- Streams file writes for large example sets
- Provides progress feedback for workflows with many stages

---

## Version History

- **1.0.0** (2026-01-26): Initial release with core example generation
- Support for all workflow patterns (stg-val-wkf, sequential, parallel, custom)
- Domain-aware example generation
- Good/bad example creation with validation
- End-to-end workflow examples
