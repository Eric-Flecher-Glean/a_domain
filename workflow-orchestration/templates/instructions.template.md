# Stage {{stage_number}}: {{stage_name}} Instructions

## Objective
{{objective}}

## Processing Steps

{{#each processing_steps}}
{{step_number}}. **{{step_title}}**
   {{step_description}}
   {{#if substeps}}{{#each substeps}}
   - {{this}}{{/each}}{{/if}}

{{/each}}

## Quality Criteria

### {{quality_dimension_1}}
{{quality_criteria_1}}

### {{quality_dimension_2}}
{{quality_criteria_2}}

### {{quality_dimension_3}}
{{quality_criteria_3}}

{{#if feedback_handling}}
## Handling Feedback

If this is a refinement attempt (attempt_number > 1):

1. **Review previous attempt**
   - Identify what sections failed validation
   - Understand the specific issues raised

2. **Apply feedback systematically**
   - Address each feedback item explicitly
   - Prioritize error-level feedback first
   - Then address warnings

3. **Preserve what worked**
   - Keep high-quality sections from previous attempt
   - Only modify sections that need improvement

4. **Document changes**
   - Track which feedback items were addressed
   - Note in metadata
{{/if}}

## Output Format

{{output_format_description}}

{{#if output_example}}
### Example Output:
```{{output_format_type}}
{{output_example}}
```
{{/if}}

{{#if anti_patterns}}
## Anti-Patterns to Avoid

{{#each anti_patterns}}
{{@index}}. **{{pattern_name}}** - {{pattern_description}}
{{/each}}
{{/if}}

## Reference Materials

{{#if reference_materials}}
{{#each reference_materials}}
- {{description}}: `{{path}}`
{{/each}}
{{/if}}
- Load examples from: `examples/good/` and `examples/bad/`
- Global examples: `workflow-orchestration/global/examples/`
