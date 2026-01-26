# Validation Dimensions Reference

This document describes the standard validation dimensions used across workflows for quality assessment.

## Overview

Quality validation is decomposed into multiple dimensions, each with specific checks and scoring. This allows granular feedback and targeted refinement.

### Standard Dimensions:

1. **Structural** - Format, schema, required elements
2. **Completeness** - All required content present
3. **Quality** - Clarity, effectiveness, coherence
4. **Context** - Input/output relationships, dependencies

---

## 1. Structural Validation

**Purpose:** Verify that output conforms to expected format and schema.

**Weight:** Typically 35-40% of total score

**Checks:**

### Format Well-Formed
- **Description:** Output is valid in its format (XML, JSON, Markdown, etc.)
- **Points:** 10
- **Severity:** error
- **Examples:**
  - XML: Valid tags, proper nesting, escaped characters
  - JSON: Valid syntax, matching braces, proper quotes
  - Markdown: Valid headers, lists, code blocks

### Required Sections Present
- **Description:** All mandatory sections/fields are included
- **Points:** 15
- **Severity:** error
- **Examples:**
  - XML prompts: `<metadata>`, `<primary_goal>`, `<role>`, `<task>`
  - Reports: Executive summary, findings, recommendations
  - Code: Function signature, docstring, implementation

### Schema Compliance
- **Description:** Output adheres to defined schema or contract
- **Points:** 10
- **Severity:** error
- **Examples:**
  - Field types match (string, number, boolean)
  - Required fields present
  - Constraints satisfied (min/max, patterns)

### Naming Conventions
- **Description:** Identifiers follow specified naming rules
- **Points:** 5
- **Severity:** warning
- **Examples:**
  - Prompt names: `xxx-xxx-xxx` pattern
  - Variable names: camelCase or snake_case
  - File names: kebab-case

**Structural Score Calculation:**
```
structural_score = Σ(check_points if passed) - Σ(penalties)
structural_percentage = (structural_score / max_structural_points) * structural_weight
```

**Common Structural Issues:**
- Malformed XML/JSON
- Missing required tags/fields
- Incorrect nesting depth
- Invalid characters in names
- Schema violations

---

## 2. Completeness Validation

**Purpose:** Ensure all required content is substantive and comprehensive.

**Weight:** Typically 25-30% of total score

**Checks:**

### Section Content Substantive
- **Description:** Sections contain meaningful content, not placeholders
- **Points:** 15
- **Severity:** error
- **Examples:**
  - Not "TBD", "TODO", "Example", "Lorem ipsum"
  - Each section has at least 20 characters
  - Content is specific to the task, not generic

### Required Elements Count
- **Description:** Minimum number of required elements present
- **Points:** 10
- **Severity:** warning
- **Examples:**
  - At least 2 good examples
  - At least 1 bad example
  - At least 3 processing steps
  - At least 5 validation rules

### Coverage
- **Description:** All aspects of requirements addressed
- **Points:** 5
- **Severity:** info
- **Examples:**
  - All input fields have validation
  - All edge cases documented
  - All user stories covered

**Completeness Score Calculation:**
```
completeness_score = Σ(check_points if passed) - Σ(penalties)
completeness_percentage = (completeness_score / max_completeness_points) * completeness_weight
```

**Common Completeness Issues:**
- Placeholder text not replaced
- Missing examples
- Incomplete instructions
- Undefined outputs
- Generic content not customized

---

## 3. Quality Validation

**Purpose:** Assess clarity, effectiveness, and coherence of output.

**Weight:** Typically 20-30% of total score

**Checks:**

### Clarity and Specificity
- **Description:** Content is clear, unambiguous, and specific
- **Points:** 10
- **Severity:** warning
- **Examples:**
  - No vague terms ("process the data", "do the thing")
  - Concrete actions ("Extract customer_id from JSON field 'id'")
  - Specific constraints ("Maximum 500 tokens", not "reasonable length")

### Examples Effectiveness
- **Description:** Examples demonstrate full range of expected behavior
- **Points:** 10
- **Severity:** warning
- **Examples:**
  - Examples use realistic data (not "foo", "bar")
  - Cover edge cases and common scenarios
  - Bad examples explain what's wrong
  - Examples align with instructions

### Coherence
- **Description:** All sections align and support primary goal
- **Points:** 5
- **Severity:** info
- **Examples:**
  - Instructions match stated task
  - Output format matches examples
  - Constraints don't contradict requirements
  - Consistent terminology throughout

### Best Practices
- **Description:** Follows domain-specific best practices
- **Points:** 5
- **Severity:** info
- **Examples:**
  - Proper tag hierarchy in XML
  - Appropriate nesting depth (≤3 levels)
  - Security considerations addressed
  - Performance optimization noted

**Quality Score Calculation:**
```
quality_score = Σ(check_points if passed) - Σ(penalties) + bonuses
quality_percentage = (quality_score / max_quality_points) * quality_weight
```

**Common Quality Issues:**
- Vague or ambiguous language
- Generic examples not tailored to task
- Inconsistent terminology
- Sections don't align with goal
- Missing best practices

---

## 4. Context Validation (New)

**Purpose:** Verify input specifications and context requirements are correct.

**Weight:** Typically 10% of total score

**Checks:**

### Input Specifications Present
- **Description:** Required inputs are clearly specified
- **Points:** 15
- **Severity:** error (if analyze_context=true)
- **Examples:**
  - Input name, type, source defined
  - Required vs. optional marked
  - Validation rules specified

### Input Descriptions Clear
- **Description:** Each input has clear, actionable description
- **Points:** 5
- **Severity:** warning
- **Examples:**
  - "Meeting transcript as plain text" not just "transcript"
  - "ISO 8601 timestamp" not just "date"
  - "Comma-separated list of email addresses" not "emails"

### Context Sources Accessible
- **Description:** Specified context sources are valid and accessible
- **Points:** 10
- **Severity:** error
- **Examples:**
  - Glean queries use valid filters
  - Referenced documents exist
  - APIs are reachable
  - Tools are available

### Glean Integration Valid
- **Description:** Glean MCP tools and queries are correct
- **Points:** 10
- **Severity:** error
- **Examples:**
  - Tool names valid (mcp__glean__search, etc.)
  - Query syntax correct
  - Filters appropriate for data source
  - Permissions sufficient

**Context Score Calculation:**
```
context_score = Σ(check_points if passed) - Σ(penalties)
context_percentage = (context_score / max_context_points) * context_weight
```

**Common Context Issues:**
- Missing input specifications
- Invalid Glean queries
- Inaccessible context sources
- Incorrect MCP tool names
- Missing input type information

---

## Overall Quality Score

### Formula:
```
overall_score =
  (structural_percentage × structural_weight) +
  (completeness_percentage × completeness_weight) +
  (quality_percentage × quality_weight) +
  (context_percentage × context_weight) +
  bonuses - penalties

where:
  structural_weight + completeness_weight + quality_weight + context_weight = 1.0
```

### Standard Weights:
- **Structural:** 0.35-0.40
- **Completeness:** 0.25-0.30
- **Quality:** 0.20-0.30
- **Context:** 0.10

### Bonuses:
- Extra good example: +2 points each
- Extra bad example: +2 points each
- Optional sections: +1 point each
- **Max total bonus:** 10 points

### Penalties:
- Error-level issue: -20 points
- Warning-level issue: -5 points
- Info-level issue: 0 points (tracked but not penalized)

---

## Success Thresholds

### Standard Thresholds:
- **High Quality (90-100):** Production-ready, minimal issues
- **Good Quality (75-89):** Acceptable with minor refinements
- **Needs Work (60-74):** Significant issues to address
- **Poor Quality (<60):** Major problems, requires substantial rework

### Recommended Thresholds by Use Case:
- **Production prompts:** 90
- **Internal tools:** 80
- **Prototypes/experiments:** 70
- **Draft outputs:** 60

---

## Feedback Generation

### Feedback Prioritization:
1. **Errors first** - Must be fixed to pass validation
2. **Warnings second** - Should be addressed for quality
3. **Info last** - Nice-to-have improvements

### Feedback Templates:

**Error:**
```
ERROR [rule_id] section_name: Specific problem → How to fix
Example: "ERROR [required_sections] metadata: Missing <metadata> tag → Add metadata section with name and version"
```

**Warning:**
```
WARNING [rule_id] section_name: Issue description → Suggested improvement
Example: "WARNING [examples_quality] examples: Only 1 good example found → Add at least 1 more realistic example"
```

**Recommendation:**
```
Priority level. Specific improvement (Reference: example_id)
Example: "HIGH. Make instructions more specific by adding concrete field names (See: good_example_02)"
```

### Max Feedback Items:
- **Per attempt:** 10 items (prioritized by severity)
- **Errors:** All included
- **Warnings:** Top 5 by impact
- **Recommendations:** Top 3 by improvement potential

---

## Validation Best Practices

### For Workflow Designers:

1. **Set Appropriate Thresholds**
   - Not too high (causes excessive retries)
   - Not too low (poor quality outputs)
   - 90 is good for most use cases

2. **Balance Dimension Weights**
   - Structural: Higher for format-critical outputs
   - Completeness: Higher for documentation
   - Quality: Higher for user-facing content
   - Context: Higher for integration-heavy workflows

3. **Define Clear Error Conditions**
   - What absolutely must be present?
   - What format violations are unacceptable?
   - What missing elements prevent usage?

4. **Provide Actionable Feedback**
   - Specific problem descriptions
   - Clear fix instructions
   - Reference examples when possible

5. **Track Improvement Across Attempts**
   - Verify feedback is being addressed
   - Escalate if no improvement after 2 attempts
   - Log what changed between attempts

### For Agent Builders:

1. **Align Output to Validation**
   - Understand what will be validated
   - Generate output that passes checks
   - Include all required elements

2. **Use Validation Rules as Checklist**
   - Before outputting, verify:
     - Format is correct
     - All required sections present
     - Content is substantive
     - Examples are realistic

3. **Address Feedback Systematically**
   - Parse feedback into categories
   - Fix errors first, then warnings
   - Document what was changed
   - Preserve working sections

4. **Learn from Examples**
   - Study good examples
   - Understand why bad examples fail
   - Match patterns from high-quality outputs
