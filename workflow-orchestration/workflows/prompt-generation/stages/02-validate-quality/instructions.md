# Stage 2: Quality Validation Instructions

## Objective
Validate the generated XML prompt against quality standards and provide actionable feedback for refinement.

## Validation Checks

### 1. Structural Validation (40 points)

**XML Well-Formedness (10 points)**
- XML is parseable without errors
- All tags properly opened and closed
- No invalid characters or syntax errors
- Proper encoding and escaping

**Required Sections Present (15 points)**
- `<metadata>` with `<name>` and `<version>`
- `<primary_goal>`
- `<role>`
- `<task>`
- `<instructions>`
- `<output_format>`
- `<examples>`

**Tag Hierarchy (10 points)**
- High-priority tags (primary_goal, role, task) at outer level
- Proper nesting for contextual details
- Maximum nesting depth ≤ 3 levels
- Logical parent-child relationships

**Naming Convention (5 points)**
- Prompt name matches pattern `^[a-z0-9]{3}-[a-z0-9]{3}-[a-z0-9]{3}$`
- Name is unique and descriptive
- Uses lowercase alphanumeric with hyphens

### 2. Completeness Validation (30 points)

**Section Content (15 points)**
- All required sections have substantive content (>10 characters)
- No empty tags or whitespace-only content
- No placeholder text (TBD, TODO, Lorem ipsum, etc.)
- Metadata includes both name and version

**Examples Quality (10 points)**
- At least 2 `<good_example>` tags present
- At least 1 `<bad_example>` tag present
- Good examples include both Input and Output
- Bad examples include Issue explanation
- Examples use realistic, domain-appropriate data

**Instructions Structure (5 points)**
- Instructions are broken into clear steps
- Uses numbered format or step tags (`<step1>`, `<step2>`, etc.)
- Each step is actionable
- Steps are in logical order

### 3. Quality Validation (30 points)

**Clarity and Specificity (10 points)**
- Primary goal is unambiguous and specific
- Role defines clear expertise area (not generic "AI Assistant")
- Task is measurable and concrete
- Output format is well-defined with examples

**Examples Effectiveness (10 points)**
- Examples demonstrate the full range of expected behavior
- Good examples show realistic scenarios
- Bad examples illustrate common mistakes
- Examples are isolated in their own section (cognitive containerization)

**Constraints and Validation (5 points)**
- Constraints are explicit and measurable
- Edge cases are addressed
- Validation rules are clear (if present)
- Boundaries are well-defined

**Overall Coherence (5 points)**
- All sections align with the primary goal
- Role matches the task requirements
- Examples support the instructions
- No contradictions between sections

## Scoring Algorithm

```
base_score = 100

# Apply penalties
errors = count of error-severity failures
warnings = count of warning-severity failures

score_after_penalties = base_score - (errors × 20) - (warnings × 5)

# Apply bonuses
extra_good_examples = max(0, good_examples_count - 2)
extra_bad_examples = max(0, bad_examples_count - 1)
example_bonus = (extra_good_examples + extra_bad_examples) × 2

# Calculate final score
final_score = min(100, max(0, score_after_penalties + example_bonus))

# Determine pass/fail
isValid = (final_score >= success_threshold) AND (errors == 0)
```

## Feedback Generation

### When score < success_threshold (90):

1. **Categorize failures by severity**
   - List all error-level failures first
   - Then warning-level failures
   - Group by validation category (structural, completeness, quality)

2. **Provide specific recommendations**
   - For each failed check, explain what's wrong
   - Provide concrete examples of how to fix it
   - Reference good examples from the library
   - Suggest specific changes to specific sections

3. **Prioritize actionability**
   - Focus on highest-impact fixes first
   - Limit feedback to top 10 items (most critical)
   - Be specific, not vague ("Add context section" not "Improve quality")

4. **Reference examples**
   - Point to similar prompts in examples library
   - Show before/after comparisons when possible
   - Cite specific example files by name

### Feedback Template:

```
ERRORS (blocking issues):
- [Rule ID] [Section]: [Specific problem] → [How to fix]

WARNINGS (quality issues):
- [Rule ID] [Section]: [Specific problem] → [Suggested improvement]

RECOMMENDATIONS:
1. [Highest priority improvement]
2. [Second priority improvement]
...

REFERENCE EXAMPLES:
- See: examples/good/[filename] for [what it demonstrates]
- Avoid: examples/bad/[filename] shows [anti-pattern]
```

## Pass/Fail Criteria

### PASS (isValid: true)
- Quality score ≥ 90
- Zero error-level failures
- All required sections present
- XML is well-formed
- Prompt name matches format

### FAIL (isValid: false)
Any of:
- Quality score < 90
- One or more error-level failures
- Missing required sections
- XML parsing errors
- Invalid prompt name format

## Output Format

Return a ValidationResult object:

```json
{
  "isValid": boolean,
  "qualityScore": number,
  "checks": [
    {
      "rule_id": "xml-well-formed",
      "status": "pass" | "fail",
      "message": "Descriptive message",
      "severity": "error" | "warning" | "info",
      "section": "Which part of prompt",
      "score_impact": number
    }
  ],
  "feedback": [
    "Specific, actionable feedback item 1",
    "Specific, actionable feedback item 2"
  ],
  "recommendations": [
    "Highest priority recommendation",
    "Second priority recommendation"
  ],
  "scoreBreakdown": {
    "structural": number,
    "completeness": number,
    "quality": number,
    "bonuses": number,
    "penalties": number
  },
  "examplesAnalysis": {
    "good_examples_found": number,
    "bad_examples_found": number,
    "examples_quality_score": number
  }
}
```

## Validation Process

1. **Parse XML**
   - Attempt to parse the xml_prompt string
   - If parsing fails, immediately return error with details
   - Extract all tags and content

2. **Run Structural Checks**
   - Verify all required tags present
   - Check tag hierarchy and nesting depth
   - Validate prompt name format
   - Check for empty sections

3. **Run Completeness Checks**
   - Count good/bad examples
   - Verify example structure
   - Check for placeholder content
   - Validate instructions structure

4. **Run Quality Checks**
   - Assess clarity of primary_goal, role, task
   - Evaluate examples effectiveness
   - Check constraints and edge cases
   - Verify overall coherence

5. **Calculate Score**
   - Start with base score (100)
   - Apply penalties for failures
   - Add bonuses for extra examples
   - Cap at 100, floor at 0

6. **Generate Feedback (if needed)**
   - If score < 90, create detailed feedback
   - Prioritize by severity and impact
   - Reference specific sections
   - Suggest concrete improvements

7. **Return Result**
   - Include all check results
   - Include score breakdown
   - Include feedback and recommendations
   - Set isValid based on score and errors

## Special Cases

### Edge Case: Borderline Score (85-89)
- Provide extra detailed feedback
- Highlight which improvements would push over threshold
- Suggest quick wins

### Edge Case: Multiple Attempts
- Reference previous attempts if available
- Check if feedback from previous round was addressed
- Note improvements made since last attempt

### Edge Case: Perfect Score (100)
- Still provide recommendations for optional enhancements
- Acknowledge what was done well
- Suggest optional additions (e.g., domain_knowledge section)

## Reference Materials

- Load validation rules from: `validation-rules.json`
- Compare against examples: `examples/good/` and `examples/bad/`
- Global examples: `../../../global/examples/`
- Global standards: `../../../global/config/validation-standards.json`
