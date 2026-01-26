# Workflow Templates

This directory contains templates for generating new workflows in the document-driven agent orchestration system.

## Available Templates

### 1. workflow-metadata.template.json
Master workflow definition template with:
- Workflow ID, version, description
- Bounded context assignment
- Stage definitions
- Orchestration patterns and loop logic
- Data passing between stages
- Global configuration overrides
- Metrics tracking

### 2. stage-config.template.json
Stage-specific configuration template with:
- Agent configuration (model, temperature, tokens)
- Execution settings (timeout, retries)
- Input/output schemas
- Validation rules
- Resource paths (instructions, examples)
- Feedback handling
- Loop handling

### 3. instructions.template.md
Agent instruction template with:
- Stage objective
- Processing steps
- Quality criteria
- Feedback handling guidance
- Output format specification
- Anti-patterns to avoid
- Reference materials

### 4. validation-rules.template.json
Validation rules template with:
- Success threshold
- Validation rules (structural, completeness, quality)
- Loop logic and feedback configuration
- Scoring weights by dimension
- Dimension-specific checks
- Bonuses and penalties
- Feedback templates

### 5. agent-spec.template.yaml
New agent specification template with:
- Agent ID and metadata
- Bounded context
- Capabilities list
- Input/output contracts
- Glean integrations
- Model configuration
- System instructions
- Retry policy
- Performance expectations

## Template Syntax

Templates use Handlebars-style syntax:

### Variables
```
{{variable_name}}
```

### Conditionals
```
{{#if condition}}
  Content if true
{{/if}}
```

### Loops
```
{{#each array}}
  {{this}} or {{property_name}}
{{/each}}
```

### Unless
```
{{#unless @last}},{{/unless}}
```

## Usage

Templates are used by the `/new-workflow` Claude Code skill to generate workflow files. The skill:

1. Collects user input through interactive questions
2. Populates template variables
3. Instantiates templates with user data
4. Validates generated files
5. Writes files to appropriate locations

## Manual Usage

To manually use templates:

1. **Copy template to target location:**
   ```bash
   cp workflow-orchestration/templates/workflow-metadata.template.json \
      workflow-orchestration/workflows/my-workflow/workflow-metadata.json
   ```

2. **Replace all `{{variables}}` with actual values:**
   - Find all `{{...}}` patterns
   - Replace with appropriate values
   - Remove conditional blocks not needed
   - Expand loops manually

3. **Validate generated file:**
   ```bash
   # For JSON
   cat workflow-metadata.json | jq .

   # For YAML
   yamllint agent-spec.yaml
   ```

## Template Variables Reference

### workflow-metadata.template.json

| Variable | Type | Description | Example |
|----------|------|-------------|---------|
| workflow_id | string | Kebab-case identifier | "customer-feedback-analysis" |
| version | string | Semantic version | "1.0.0" |
| description | string | Workflow purpose | "Analyze customer feedback..." |
| pattern | string | Orchestration pattern | "stg-val-wkf" |
| created_date | string | ISO date | "2026-01-26" |
| bounded_context | string | Domain context | "CustomerAnalytics" |
| stages | array | Stage definitions | [{stage_id: "01-analyze", ...}] |
| orchestration_pattern | string | Orchestration type | "sequential_with_loops" |
| loop_target | string | Feedback destination | "loop_to_generator" |
| max_total_attempts | number | Max retry count | 3 |
| feedback_strategy | string | Feedback mode | "cumulative" |
| primary_output | string | Main output field | "analysis_result" |
| data_mappings | array | Stage I/O mappings | [{mapping_id: "...", fields: [...]}] |
| timeout_seconds | number | Workflow timeout | 300 |
| enable_debug | boolean | Debug logging | true |
| global_success_threshold | number | Quality threshold | 90 |

### stage-config.template.json

| Variable | Type | Description | Example |
|----------|------|-------------|---------|
| stage_id | string | Stage identifier | "01-generate-prompt" |
| stage_name | string | Human-readable name | "Prompt Generation" |
| agent_id | string | Agent to use | "prompt-generator-001" |
| model | string | LLM model | "claude-sonnet-4" |
| temperature | number | Sampling temp | 0.3 |
| max_tokens | number | Response limit | 4000 |
| top_p | number | Nucleus sampling | 0.9 |
| timeout_seconds | number | Stage timeout | 120 |
| strict_mode | boolean | Strict validation | true |
| required_inputs | array | Required fields | ["user_request"] |
| input_properties | array | Input schema | [{name: "...", type: "string", ...}] |
| required_outputs | array | Required outputs | ["xml_prompt"] |
| output_properties | array | Output schema | [{name: "...", type: "string", ...}] |
| validation_enabled | boolean | Run validation | true |
| success_threshold | number | Pass threshold | 90 |

### instructions.template.md

| Variable | Type | Description | Example |
|----------|------|-------------|---------|
| stage_number | number | Stage sequence | 1 |
| stage_name | string | Stage name | "Prompt Generation" |
| objective | string | Stage goal | "Transform request to XML" |
| processing_steps | array | Step definitions | [{step_number: 1, ...}] |
| quality_dimension_1 | string | Quality aspect | "Structure" |
| quality_criteria_1 | string | Criteria details | "Tag hierarchy..." |
| feedback_handling | boolean | Include feedback section | true |
| output_format_description | string | Output description | "Complete XML prompt" |
| output_example | string | Example output | "<?xml..." |
| anti_patterns | array | Things to avoid | [{pattern_name: "...", ...}] |

### validation-rules.template.json

| Variable | Type | Description | Example |
|----------|------|-------------|---------|
| stage_id | string | Stage identifier | "02-validate-quality" |
| validation_type | string | Validation mode | "quality_assessment" |
| success_threshold | number | Pass score | 90 |
| max_attempts | number | Retry limit | 3 |
| structural_min | number | Min structural score | 32 |
| structural_max | number | Max structural score | 40 |
| completeness_min | number | Min completeness | 24 |
| completeness_max | number | Max completeness | 30 |
| quality_min | number | Min quality score | 24 |
| quality_max | number | Max quality score | 30 |
| track_feedback | boolean | Track addressed feedback | true |
| scoring_weights | array | Dimension weights | [{dimension: "structural", weight: 0.4}] |
| structural_checks | array | Structural validations | [{check_id: "...", points: 10, ...}] |

### agent-spec.template.yaml

| Variable | Type | Description | Example |
|----------|------|-------------|---------|
| agent_id | string | Agent identifier | "feedback-analyzer-001" |
| agent_name | string | Display name | "Feedback Analyzer" |
| created_date | string | Creation date | "2026-01-26" |
| description | string | Agent purpose | "Analyzes customer feedback..." |
| bounded_context | string | Domain context | "CustomerAnalytics" |
| capabilities | array | What agent can do | ["Parse feedback", ...] |
| input_contract | array | Input schema | [{name: "feedback_text", type: "string", ...}] |
| output_contract | array | Output schema | [{name: "sentiment_score", type: "number", ...}] |
| glean_integrations | array | Glean MCP tools | [{type: "mcp_server", ...}] |
| model | string | LLM model | "claude-sonnet-4" |
| temperature | number | Sampling temp | 0.3 |
| max_tokens | number | Response limit | 4000 |
| workflow_id | string | Parent workflow | "customer-feedback-analysis" |
| stage_id | string | Stage in workflow | "01-analyze-feedback" |
| system_instructions | string | Agent prompt | "You are a sentiment analyzer..." |
| max_attempts | number | Retry limit | 3 |
| validation_note | string | Validation info | "Validation by stage 2" |
| constraints | array | Agent limits | ["no_write_actions", ...] |
| expected_latency | number | Expected ms | 3000 |
| max_latency | number | Max ms | 120000 |
| tags | array | Categorization | ["sentiment-analysis", ...] |

## Best Practices

### 1. Variable Naming
- Use descriptive names
- Use snake_case for multi-word variables
- Keep consistent with existing templates

### 2. Conditionals
- Use sparingly - prefer explicit over implicit
- Document when sections are optional
- Provide default values when possible

### 3. Loops
- Keep loop bodies simple
- Use `@index`, `@first`, `@last` helpers
- Validate array data before looping

### 4. Validation
- Always validate generated JSON/YAML
- Check for missing required fields
- Verify data types match schema

### 5. Documentation
- Comment template sections
- Explain complex conditionals
- Provide example values

## Testing Templates

To test template changes:

1. **Use /new-workflow skill with test data**
2. **Verify generated files are valid**
3. **Check all variables are replaced**
4. **Ensure no template syntax remains**
5. **Validate against schemas**

## Extending Templates

To add new template features:

1. **Add variable to template**
2. **Update variable reference table**
3. **Document usage in skill**
4. **Test with /new-workflow**
5. **Update this README**

## Related Documentation

- `/new-workflow` skill: `.claude/skills/new-workflow.md`
- Workflow patterns: `.claude/knowledge/workflow-creation/workflow-patterns.md`
- Bounded contexts: `.claude/knowledge/workflow-creation/bounded-contexts.md`
- Agent catalog: `.claude/knowledge/workflow-creation/agent-catalog.md`
