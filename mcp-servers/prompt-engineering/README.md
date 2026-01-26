# Prompt Engineering MCP Server

## Overview
This MCP (Model Context Protocol) server provides tools for generating and validating XML-structured prompts. It enables automated prompt engineering workflows through two core agents working in collaboration.

## Tools

### 1. generate_xml_prompt
Transforms natural language requests into well-structured XML prompts following Anthropic's hierarchical methodology.

**Agent**: `prompt-generator-001`

**Input**:
- `user_request` (required): Natural language description of desired prompt
- `feedback` (optional): Array of feedback items from validation
- `previous_attempt` (optional): Previous generation attempt for refinement
- `attempt_number` (optional): Current attempt number (1-3)

**Output**:
- `xml_prompt`: Complete XML-structured prompt
- `prompt_name`: Unique identifier (xxx-xxx-xxx format)
- `components_extracted`: Parsed components from request
- `generation_metadata`: Attempt info and refinements applied

**Usage Example**:
```json
{
  "user_request": "Create a prompt for meeting summarization"
}
```

### 2. validate_prompt_quality
Validates XML prompts against quality standards, checking structure, completeness, and effectiveness.

**Agent**: `prompt-validator-001`

**Input**:
- `xml_prompt` (required): XML prompt to validate
- `previous_validation_results` (optional): Previous validation history
- `attempt_number` (optional): Current validation attempt (1-3)

**Output**:
- `isValid`: Boolean (true if score ≥ 90 and no errors)
- `qualityScore`: Score 0-100
- `checks`: Array of validation check results
- `feedback`: Actionable feedback items
- `recommendations`: Improvement suggestions
- `scoreBreakdown`: Scores by category
- `examplesAnalysis`: Example count and quality

**Usage Example**:
```json
{
  "xml_prompt": "<metadata>...</metadata><primary_goal>...</primary_goal>..."
}
```

## Architecture

```
User Request
     ↓
generate_xml_prompt → XMLPrompt
     ↓
validate_prompt_quality → ValidationResult
     ↓
  [Pass/Fail?]
     ↓
Pass → Return XMLPrompt
Fail → Loop to generate_xml_prompt with feedback
```

## Configuration

### Server Config
- **Path**: `server-config.json`
- **OAuth Scopes**: AGENT, MCP, TOOLS
- **Rate Limits**: 30 req/min, 500 req/hour

### Agent Specs
- **Generator**: `../../agents/prompt-generator/agent-spec.yaml`
- **Validator**: `../../agents/prompt-validator/agent-spec.yaml`

### Resources
- **Instructions**: `../../workflow-orchestration/workflows/prompt-generation/stages/`
- **Validation Rules**: Stage-specific `validation-rules.json`
- **Examples**: `../../workflow-orchestration/global/examples/`

## Quality Standards

### Success Criteria
- Quality score ≥ 90/100
- Zero error-level validation failures
- All required sections present
- XML well-formed
- Prompt name matches `^[a-z0-9]{3}-[a-z0-9]{3}-[a-z0-9]{3}$`

### Required Sections
- `<metadata>` (name, version)
- `<primary_goal>`
- `<role>`
- `<task>`
- `<instructions>`
- `<output_format>`
- `<examples>` (minimum 2 good, 1 bad)

### Scoring
- **Structural** (40%): XML syntax, required sections, hierarchy
- **Completeness** (30%): Content quality, examples, instructions
- **Quality** (30%): Clarity, effectiveness, coherence

## Setup

### 1. Register MCP Server in Glean
```
Platform → Glean MCP servers → Create Server
  - Name: Prompt Engineering
  - Config: Upload server-config.json
  - OAuth Scopes: AGENT, MCP, TOOLS
```

### 2. Register Agents
```
Agent Builder → Create Agents
  - Agent A: prompt-generator-001
  - Agent B: prompt-validator-001
  - Link to MCP tools
```

### 3. Configure Workflow
```
Agent Builder → Workflows → Import
  - Upload: ../../workflows/prompt-generation-workflow.json
```

## Testing

### Unit Test: Generator
```json
{
  "tool": "generate_xml_prompt",
  "input": {"user_request": "Create a prompt for code review"},
  "expect": {
    "xml_prompt": "Valid XML with all sections",
    "prompt_name": "Matches xxx-xxx-xxx pattern"
  }
}
```

### Unit Test: Validator
```json
{
  "tool": "validate_prompt_quality",
  "input": {"xml_prompt": "<good example from library>"},
  "expect": {
    "isValid": true,
    "qualityScore": "≥ 90"
  }
}
```

### Integration Test
1. Generate prompt from vague request
2. Expect validation failure (score < 90)
3. Refine with feedback
4. Expect validation pass on attempt 2

## Monitoring

Tracked metrics:
- Tool call count
- Success rate
- Average execution time
- Quality score distribution

Dashboard: Glean Admin Console → MCP Servers → prompt-engineering

## Troubleshooting

### Issue: Agent not found
- **Cause**: Agent not registered or inactive
- **Fix**: Check Agent Builder, ensure agents are active

### Issue: Validation always fails
- **Cause**: Threshold too high or strict rules
- **Fix**: Adjust `success_threshold` in stage-config.json

### Issue: No feedback on failure
- **Cause**: Feedback generation disabled
- **Fix**: Set `generate_feedback_on_failure: true` in validator config

## References

- [Agent Specifications](../../agents/)
- [Workflow Configuration](../../workflow-orchestration/)
- [Global Examples](../../workflow-orchestration/global/examples/)
- [Staged Validation Pattern](../../docs/concepts/a-b-workflow.md)
