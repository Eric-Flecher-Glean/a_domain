# Stage 1: Prompt Generation Instructions

## Objective
Transform a natural language request into a well-structured XML prompt following Anthropic's hierarchical methodology.

## Processing Steps

1. **Parse the user's semantic request**
   - Identify the primary goal or use case
   - Extract any specific requirements or constraints mentioned
   - Note the intended audience or context

2. **Extract core components:**
   - **Primary goal**: What the prompt should accomplish
   - **Role**: AI persona/expertise required
   - **Task**: Specific action to be performed
   - **Context**: Background information and situational details
   - **Constraints**: Boundaries and limitations
   - **Examples**: Good and bad demonstrations
   - **Output format**: Expected structure of results
   - **Validation rules**: Success criteria

3. **Generate XML structure with proper hierarchy:**
   - Outer tags = high priority (primary_goal, role, task)
   - Nested tags = contextual details
   - Maximum 2-3 levels of nesting
   - Follow cognitive containerization principles (isolate examples)

4. **Assign a unique prompt name**
   - Format: `xxx-xxx-xxx` (lowercase alphanumeric with hyphens)
   - Must match pattern: `^[a-z0-9]{3}-[a-z0-9]{3}-[a-z0-9]{3}$`
   - Examples: `mtg-sum-ext`, `sen-ana-txt`, `cod-rev-pmt`

5. **Include comprehensive examples**
   - At least 2 good examples demonstrating correct behavior
   - At least 1 bad example showing what to avoid
   - Each example should include:
     - Input
     - Output
     - Explanation (for bad examples)

6. **Ensure all required sections are present:**
   - `<metadata>` (name, version)
   - `<primary_goal>`
   - `<role>`
   - `<task>`
   - `<instructions>`
   - `<output_format>`
   - `<examples>`

7. **Optional but recommended sections:**
   - `<context>`
   - `<constraints>`
   - `<validation_rules>`
   - `<domain_knowledge>`

## Quality Criteria

### Structure
- Tag hierarchy reflects priority (see core_tag_reference)
- Maximum nesting depth of 3 levels
- Well-formed XML (proper opening/closing tags)
- Consistent indentation

### Completeness
- All required sections present
- Each section has substantive content (not placeholders)
- Examples are realistic and domain-appropriate
- Instructions are actionable and specific

### Clarity
- Primary goal is unambiguous
- Role is specific and relevant
- Task is clear and measurable
- Output format is well-defined

### Examples
- Isolated in their own section (cognitive containerization)
- Demonstrate the full range of expected behavior
- Bad examples include explanations of what's wrong
- Examples use realistic data (not "foo", "bar", "example")

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
   - Note in generation_metadata

## Output Format

Return a complete XML prompt string with proper indentation.

### Example Structure:
```xml
<metadata>
  <name>xxx-xxx-xxx</name>
  <version>1.0</version>
</metadata>

<primary_goal>
  [Clear statement of what this prompt accomplishes]
  <audience>[Who will use this]</audience>
  <tone>[Communication style]</tone>
</primary_goal>

<role>[AI persona and expertise]</role>

<task>[Specific action to perform]</task>

<context>
  [Background information and situational details]
</context>

<instructions>
  <step1>[First action]</step1>
  <step2>[Second action]</step2>
  ...
</instructions>

<output_format>
  [Detailed specification of expected output structure]
</output_format>

<constraints>
  <constraint>[Boundary or limitation]</constraint>
  ...
</constraints>

<examples>
  <good_example>
    Input: [Sample input]
    Output: [Expected output]
  </good_example>

  <good_example>
    Input: [Another sample]
    Output: [Expected output]
  </good_example>

  <bad_example>
    Output: [Incorrect output]
    Issue: [Explanation of what's wrong]
  </bad_example>
</examples>

<domain_knowledge>[Relevant expertise areas]</domain_knowledge>
```

## Anti-Patterns to Avoid

1. **Flat structure** - Everything at the same level with no hierarchy
2. **Excessive nesting** - More than 3 levels deep
3. **Placeholder content** - "TBD", "Example", "Lorem ipsum"
4. **Vague instructions** - "Do the thing", "Process the data"
5. **Missing examples** - No concrete demonstrations
6. **Generic roles** - "AI Assistant", "Helper"
7. **Undefined output** - No clear format specification

## Reference Materials

- Load examples from: `examples/good/` and `examples/bad/`
- Core tag reference: Available in validation-rules.json
- Global examples: `workflow-orchestration/global/examples/`
