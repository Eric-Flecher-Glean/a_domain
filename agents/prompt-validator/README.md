# Prompt Validator Agent (Agent B)

## Overview
**Agent ID**: `prompt-validator-001`
**Role**: Validate XML prompts against quality standards
**Pattern**: Validator in staged validation workflow

## Capabilities
- Parse and validate XML structure
- Check tag hierarchy and nesting depth
- Verify completeness of required sections
- Calculate quality scores (0-100) across multiple dimensions
- Generate actionable feedback for failed validations
- Compare against good/bad example patterns
- Track validation results across multiple attempts

## Input Contract

### Required
- **xml_prompt** (string): XML prompt to validate
  - Minimum 50 characters
  - Should be complete XML structure

### Optional
- **previous_validation_results** (array): Results from previous attempts
  - Used to track improvement across iterations
  - Helps identify if feedback was addressed

- **attempt_number** (integer): Current validation attempt (1-3)
  - Default: 1
  - Used to adjust feedback strategy

## Output Contract

### Required
- **isValid** (boolean): Overall validation result
  - `true` if score ≥ 90 AND error_count == 0
  - `false` otherwise

- **qualityScore** (number): Calculated quality score (0-100)
  - Based on structural, completeness, and quality checks
  - Includes penalties for failures and bonuses for extras

- **checks** (array): Individual validation check results
  - Each check includes: rule_id, status, message, severity, section, score_impact

- **feedback** (array<string>): Actionable feedback items
  - Only populated if score < 90
  - Prioritized by severity (errors first, then warnings)
  - Limited to 10 most critical items

### Optional
- **recommendations** (array<string>): Improvement suggestions
- **scoreBreakdown** (object): Scores by category (structural, completeness, quality, bonuses, penalties)
- **examplesAnalysis** (object): Example count and quality assessment

## Validation Dimensions

### 1. Structural Validation (40% of score)
- **XML Well-Formed** (10 pts): Can be parsed without errors
- **Required Sections** (15 pts): All 7 required tags present
- **Tag Hierarchy** (10 pts): Proper nesting, priority-based structure
- **Naming Convention** (5 pts): Prompt name matches `xxx-xxx-xxx`

### 2. Completeness Validation (30% of score)
- **Section Content** (15 pts): Substantive content, no placeholders
- **Examples Quality** (10 pts): ≥2 good examples, ≥1 bad example
- **Instructions Structure** (5 pts): Numbered steps or clear format

### 3. Quality Validation (30% of score)
- **Clarity and Specificity** (10 pts): Unambiguous goal, specific role
- **Examples Effectiveness** (10 pts): Realistic, domain-appropriate
- **Constraints** (5 pts): Explicit boundaries, edge cases
- **Overall Coherence** (5 pts): Sections align with primary goal

## Scoring Algorithm

```
base_score = 100

# Count failures by severity
errors = count of error-severity failures
warnings = count of warning-severity failures

# Apply penalties
score_after_penalties = base_score - (errors × 20) - (warnings × 5)

# Count extra examples
extra_good_examples = max(0, good_examples_count - 2)
extra_bad_examples = max(0, bad_examples_count - 1)

# Apply bonuses
example_bonus = (extra_good_examples + extra_bad_examples) × 2
total_bonus = min(10, example_bonus + optional_sections_bonus)

# Calculate final score
final_score = min(100, max(0, score_after_penalties + total_bonus))

# Determine validity
isValid = (final_score >= 90) AND (errors == 0)
```

## Feedback Generation

### When to Generate Feedback
- **Always** if `score < 90`
- **Optionally** if `score >= 90` (provide recommendations for enhancements)

### Feedback Format
```
ERROR [rule-id] Section: Problem → Fix
WARNING [rule-id] Section: Issue → Suggestion
RECOMMENDATION: Improvement (See: example-reference)
```

### Feedback Prioritization
1. Error-level failures (blocks validation)
2. Warning-level failures (reduces quality)
3. Info-level suggestions (optional improvements)

### Feedback Quality Standards
- **Specific**: Reference exact sections and issues
- **Actionable**: Provide concrete steps to fix
- **Referenced**: Point to good/bad examples
- **Limited**: Max 10 items (most critical first)

## Configuration

### Model
- **Name**: claude-sonnet-4
- **Temperature**: 0 (deterministic validation)
- **Max Tokens**: 2000
- **Top-p**: 1.0

### Resources
- **Instructions**: `../../workflow-orchestration/.../02-validate-quality/instructions.md`
- **Validation Rules**: `../../workflow-orchestration/.../02-validate-quality/validation-rules.json`
- **Examples**: `../../workflow-orchestration/.../02-validate-quality/examples/`
- **Global Standards**: `../../workflow-orchestration/global/config/validation-standards.json`

## Usage

### Via MCP Server
```json
{
  "tool": "validate_prompt_quality",
  "input": {
    "xml_prompt": "<metadata>...</metadata>...",
    "attempt_number": 1
  }
}
```

### Via Glean Workflow
Invoked automatically by `prompt-generation-workflow` at Stage 2.

## Integration

### Glean Agent Builder
1. Navigate to Agent Builder
2. Create new agent with ID: `prompt-validator-001`
3. Upload agent-spec.yaml
4. Link to MCP tool: `validate_prompt_quality`
5. Configure settings from agent-spec.yaml (temperature: 0)
6. Activate agent

### MCP Server Binding
- Server: `prompt-engineering`
- Tool: `validate_prompt_quality`
- Method: Direct invocation

## Testing

### Unit Test: High-Quality Prompt
```
Input: Good example from library (example-001-meeting-summary.xml)
Expected:
  - isValid: true
  - qualityScore: ≥ 90
  - checks: All pass
  - feedback: []
```

### Unit Test: Low-Quality Prompt
```
Input: Bad example from library (example-001-flat-structure.xml)
Expected:
  - isValid: false
  - qualityScore: < 50
  - checks: Multiple failures
  - feedback: Specific, actionable items
```

### Unit Test: Borderline Prompt
```
Input: Prompt with score 85-89
Expected:
  - isValid: false
  - qualityScore: 85-89
  - feedback: Highlights which improvements push over threshold
```

## Collaboration Pattern

This agent is **Agent B** in a staged validation workflow:

```
XMLPrompt (from Agent A)
     ↓
[Agent B] Validate → ValidationResult
     ↓
  isValid == true? → Output final prompt
  isValid == false? → Return feedback to Agent A
```

Maximum 3 validation attempts before escalation.

## Success Criteria

A prompt passes validation when:
- Quality score ≥ 90
- Zero error-level failures
- All required sections present and complete
- XML is well-formed
- Prompt name matches pattern

## Troubleshooting

### Issue: Score always < 90 despite fixes
- **Check**: Are all error-level items fixed?
- **Debug**: Review scoreBreakdown to see which category is low
- **Fix**: Address highest-impact failures first

### Issue: Feedback not actionable
- **Check**: Is feedback specific to sections?
- **Debug**: Review feedback template configuration
- **Fix**: Ensure feedback includes section names and concrete fixes

### Issue: Validation inconsistent
- **Check**: Is temperature set to 0?
- **Debug**: Review agent configuration
- **Fix**: Set temperature: 0 for deterministic results

## References
- [Agent Specification](agent-spec.yaml)
- [Validation Logic Template](validation-logic.xml)
- [Stage 2 Instructions](../../workflow-orchestration/workflows/prompt-generation/stages/02-validate-quality/instructions.md)
- [Validation Rules](../../workflow-orchestration/workflows/prompt-generation/stages/02-validate-quality/validation-rules.json)
- [Global Standards](../../workflow-orchestration/global/config/validation-standards.json)
