# Prompt Generator Agent (Agent A)

## Overview
**Agent ID**: `prompt-generator-001`
**Role**: Transform natural language requests into well-structured XML prompts
**Pattern**: Executor in staged validation workflow

## Capabilities
- Parse semantic requests into structured components (goal, role, task, etc.)
- Generate XML with proper tag hierarchy following Anthropic methodology
- Apply cognitive containerization for examples
- Refine prompts based on validation feedback
- Generate unique prompt names (xxx-xxx-xxx format)
- Handle multi-attempt refinement loops (up to 3 attempts)

## Input Contract

### Required
- **user_request** (string): Natural language description of desired prompt
  - Minimum 10 characters
  - Examples: "Create a prompt for meeting summarization", "Generate a code review prompt"

### Optional
- **feedback** (array<string>): Validation feedback from previous attempt
  - Provided by prompt-validator-001 when validation fails
  - Each item describes a specific issue to fix

- **previous_attempt** (object): Previous generation attempt for refinement
  - Contains: xml_prompt, prompt_name
  - Used to preserve working sections during refinement

- **attempt_number** (integer): Current attempt number (1-3)
  - Default: 1
  - Incremented by workflow orchestration on retry

## Output Contract

### Required
- **xml_prompt** (string): Complete XML-structured prompt
  - Must be well-formed XML
  - Must include all required sections
  - Must pass structural validation

- **prompt_name** (string): Unique prompt identifier
  - Pattern: `^[a-z0-9]{3}-[a-z0-9]{3}-[a-z0-9]{3}$`
  - Example: `mtg-sum-ext`, `cod-rev-chk`

### Optional
- **components_extracted** (object): Parsed components from user request
  - primary_goal, role, task, context, constraints, output_format

- **generation_metadata** (object): Attempt information
  - attempt, refinements_applied, timestamp, feedback_addressed

## Processing Logic

### Attempt 1 (Initial Generation)
1. Parse user_request for components
2. Generate XML structure with proper hierarchy
3. Create realistic examples (2+ good, 1+ bad)
4. Assign unique name (xxx-xxx-xxx)
5. Return complete prompt

### Attempt 2+ (Refinement)
1. Review feedback from previous validation
2. Identify specific sections that failed
3. Preserve sections that passed
4. Apply targeted fixes to failed sections
5. Track which feedback items were addressed
6. Return refined prompt

## Required XML Sections

All prompts must include:
- `<metadata>` with `<name>` and `<version>`
- `<primary_goal>`
- `<role>`
- `<task>`
- `<instructions>`
- `<output_format>`
- `<examples>` with minimum 2 `<good_example>` and 1 `<bad_example>`

Optional but recommended:
- `<context>`
- `<constraints>`
- `<validation_rules>`
- `<domain_knowledge>`

## Quality Standards

Generated prompts must achieve:
- Quality score ≥ 90/100 (validated by Agent B)
- Zero error-level failures
- Well-formed XML structure
- Substantive content (no placeholders)
- Valid naming convention

## Configuration

### Model
- **Name**: claude-sonnet-4
- **Temperature**: 0.3 (balanced creativity/consistency)
- **Max Tokens**: 4000
- **Top-p**: 0.9

### Resources
- **Instructions**: `../../workflow-orchestration/.../01-generate-prompt/instructions.md`
- **Examples**: `../../workflow-orchestration/.../01-generate-prompt/examples/`
- **Global Examples**: `../../workflow-orchestration/global/examples/`
- **Core Prompt**: `prompt-template.xml`

## Usage

### Via MCP Server
```json
{
  "tool": "generate_xml_prompt",
  "input": {
    "user_request": "Create a prompt for sentiment analysis",
    "attempt_number": 1
  }
}
```

### Via Glean Workflow
Invoked automatically by `prompt-generation-workflow` at Stage 1.

## Integration

### Glean Agent Builder
1. Navigate to Agent Builder
2. Create new agent with ID: `prompt-generator-001`
3. Upload agent-spec.yaml
4. Link to MCP tool: `generate_xml_prompt`
5. Configure settings from agent-spec.yaml
6. Activate agent

### MCP Server Binding
- Server: `prompt-engineering`
- Tool: `generate_xml_prompt`
- Method: Direct invocation

## Testing

### Unit Test: Basic Generation
```
Input: "Create a prompt for code review"
Expected:
  - Valid XML with all required sections
  - Prompt name matches xxx-xxx-xxx
  - At least 2 good examples, 1 bad example
```

### Unit Test: Refinement
```
Input:
  user_request: "Create a prompt for data analysis"
  feedback: ["Add more specific constraints", "Include edge case examples"]
  attempt_number: 2
Expected:
  - Constraints section enhanced
  - Edge case examples added
  - generation_metadata.feedback_addressed contains both items
```

## Collaboration Pattern

This agent is **Agent A** in a staged validation workflow:

```
User Request
     ↓
[Agent A] Generate → XMLPrompt
     ↓
[Agent B] Validate → ValidationResult
     ↓
  Fail? → Loop to [Agent A] with feedback
  Pass? → Output final prompt
```

Maximum 3 attempts before escalation.

## Troubleshooting

### Issue: Validation always fails
- **Check**: Are you addressing all error-level feedback items?
- **Fix**: Review feedback array, ensure each item is fixed in xml_prompt

### Issue: Name doesn't match pattern
- **Check**: Is name in format xxx-xxx-xxx?
- **Fix**: Use lowercase alphanumeric only, exactly 3-3-3 with hyphens

### Issue: Examples are placeholders
- **Check**: Do examples use "foo", "bar", "example data"?
- **Fix**: Use realistic, domain-appropriate examples

## References
- [Agent Specification](agent-spec.yaml)
- [Core Prompt Template](prompt-template.xml)
- [Stage 1 Instructions](../../workflow-orchestration/workflows/prompt-generation/stages/01-generate-prompt/instructions.md)
- [Validation Rules](../../workflow-orchestration/workflows/prompt-generation/stages/01-generate-prompt/validation-rules.json)
