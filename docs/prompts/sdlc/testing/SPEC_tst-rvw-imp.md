---
title: "Technical Specification: tst-rvw-imp"
version: 1.0
date: 2026-01-22
status: draft
purpose: "Documentation for Technical Specification: tst-rvw-imp"
---

# Technical Specification: tst-rvw-imp

**Prompt Name:** Test Review & Implementation
**Short Name:** `tst-rvw-imp`
**Version:** 1.0
**Stateful:** No
**SDLC Subdomain:** Testing

---

## 1. Purpose & Objectives

### Primary Goal

Review and validate the test plan document, approve it for implementation, and use it to guide functional test development while maintaining documentation quality.

### Key Objectives

1. **Plan Review** - Thoroughly review test plan for completeness
2. **Scope Validation** - Ensure features correctly scoped with clear boundaries
3. **Approval Gate** - Approve plan before implementation begins
4. **Guided Implementation** - Use approved plan for test development
5. **Documentation Maintenance** - Update existing docs, avoid sprawl

---

## 2. Input/Output Schemas

### Input Sources

| Source Type | Description | Purpose |
|-------------|-------------|---------|
| Test Plan | Test plan document | Review target |
| Section 5 | Production workflow docs | Implementation reference |
| Existing Docs | Current documentation | Update targets |

### Input Format

```yaml
test_plan_input:
  document_path: "TEST_PLAN.md"

  sections:
    - section: 1
      title: "Overview"
      content: "..."

    - section: 5
      title: "Production Workflows"
      make_commands:
        - test-unit
        - test-integration
        - test-functional

    - section: 6
      title: "Expected Outcomes"
      validation_criteria: [...]

    - section: 7
      title: "Test Data Setup"
      procedures: [...]
```

### Output Schema

```markdown
## Test Plan Review Report

### Step 1: Review
**Status:** Complete
**Findings:**
- Feature coverage: 100%
- Boundary definitions: Clear
- AC mapping: Complete

**Issues Identified:**
- Minor: TC-15 missing edge case

### Step 2: Validation
**Status:** Complete
**Scope Assessment:**
- All features correctly scoped
- Boundaries well-defined
- Coverage appropriate (not over/under tested)

### Step 3: Approval Decision
**Decision:** APPROVED
**Conditions:** Address TC-15 edge case before final implementation

### Step 4: Implementation Guidance
**Traceability Matrix:**
| Test Case | Feature | AC Reference |
|-----------|---------|--------------|
| TC-01 | Work Unit Discovery | AC1.1 |

**Section 5 Commands:**
- `make test-unit` - Unit test execution
- `make test-integration` - Integration validation

### Step 5: Documentation Updates
**Files Updated:**
- TEST_PLAN.md - Added TC-15 edge case
- No new documents created
```

---

## 3. Dependencies

### Required Inputs

| Dependency | Type | Description |
|------------|------|-------------|
| Test Plan | Document | Plan to review |
| Section 5 | Reference | Production workflows |
| Requirements | Context | Feature requirements |

### Runtime Dependencies

| Dependency | Purpose |
|------------|---------|
| `unified-plan` | Provides plan structure |
| Existing docs | Update targets |

### Downstream Consumers

| Consumer | Purpose |
|----------|---------|
| Test implementation | Follows approved plan |
| `quality-gate` | Uses implemented tests |

---

## 4. Processing Steps

### Step 1: Review Test Plan

**Actions:**
- Read test plan document thoroughly
- Check for completeness
- Verify clarity of test cases
- Assess alignment with requirements

**Review Criteria:**
- All features have test cases
- Test cases are specific and measurable
- Expected outcomes documented
- Test data requirements clear

### Step 2: Validate Feature Scope

**Actions:**
- Verify all features correctly scoped
- Check coverage appropriateness
- Confirm boundaries well-defined

**Validation Criteria:**
- Not over-tested (unnecessary duplication)
- Not under-tested (missing coverage)
- Clear in-scope vs out-of-scope

### Step 3: Approval Gate

**Actions:**
- Make approval decision based on review
- Document decision with rationale
- Note any conditions

**Approval Criteria:**
- Plan complete and clear
- Scope appropriate
- Boundaries defined
- Requirements traced

**Decision Options:**
- APPROVED - Proceed to implementation
- APPROVED_WITH_CONDITIONS - Minor fixes needed
- NEEDS_REVISION - Major issues found

**CRITICAL:** Do NOT proceed to implementation without approval

### Step 4: Guide Implementation

**Actions:**
- Use approved plan for test development
- Maintain traceability between plan and tests
- Reference Section 5 make commands
- Follow production workflow patterns

**Traceability Requirements:**
- Every test case traces to feature/AC
- Every feature has corresponding tests
- Implementation follows plan structure

### Step 5: Reference Section 5 Commands

**Actions:**
- Use documented make commands
- Follow production workflow patterns
- Ensure test execution matches plan

**Common Commands:**
- `make test-unit` - Unit test suite
- `make test-integration` - Integration tests
- `make test-functional` - Functional tests

### Step 6: Update Documentation

**Actions:**
- Update existing docs if stale/incorrect
- Avoid creating new documents
- Consolidate information

**Documentation Rules:**
- Prefer updating over creating
- Minimize document sprawl
- Keep information consolidated

---

## 5. Usage Examples

### Example 1: Full Review Cycle

**Prompt:**
```
Review and validate the test plan for Phase 1 features.
```

**Expected Flow:**
1. Review test plan document
2. Identify: 35 test cases, 8 features
3. Validate: All features scoped, boundaries clear
4. Approve: APPROVED
5. Guide: Create traceability matrix
6. Reference: Section 5 make commands
7. Update: No doc changes needed

### Example 2: Approval with Conditions

**Prompt:**
```
Review test plan - approve for implementation if ready.
```

**Expected Behavior:**
- Review finds minor gap in TC-15
- Approval: APPROVED_WITH_CONDITIONS
- Condition: "Add edge case to TC-15 before final"
- Implementation may proceed with condition noted

### Example 3: Revision Required

**Prompt:**
```
Review test plan for the new GTM classification feature.
```

**Expected Behavior:**
- Review finds major gaps
- Missing: 3 features have no test cases
- Unclear: Boundary between M3 and M4 motions
- Approval: NEEDS_REVISION
- Block: No implementation until revised

---

## 6. Integration Points

### Integration with unified-plan

```yaml
# Test plan structure from unified-plan
workflow:
  1. unified-plan creates implementation plan
  2. Test plan derived from plan structure
  3. tst-rvw-imp reviews test plan
  4. Ensures alignment with implementation
```

### Integration with quality-gate

```yaml
# Implemented tests used by quality-gate
workflow:
  1. tst-rvw-imp approves test plan
  2. Tests implemented following plan
  3. quality-gate runs implemented tests
  4. Uses Section 5 make commands
```

---

## 7. Success Criteria

### Validation Rules

| Rule | Description |
|------|-------------|
| Feature Coverage | All features have test cases |
| Clear Boundaries | Scope limits well-defined |
| Traceability | Tests link to requirements |
| Section 5 Reference | Production commands used |
| Doc Updates | Existing docs updated, not created |
| Approval Gate | No implementation without approval |

### Quality Metrics

| Metric | Target |
|--------|--------|
| Feature Coverage | 100% |
| AC Traceability | 100% of ACs have tests |
| Boundary Clarity | All boundaries documented |
| Doc Consolidation | No unnecessary new docs |

---

## 8. Constraints

1. **No New Docs** - Update existing when possible
2. **Minimize Sprawl** - Consolidate information
3. **Section 5 Required** - Must reference production commands
4. **Approval Gate** - Step 3 blocks without validation
5. **Traceability** - Tests must trace to plan

---

## 9. Error Handling

| Error Condition | Handling |
|-----------------|----------|
| Missing features | Flag for revision, list gaps |
| Unclear boundaries | Request clarification |
| No Section 5 | Document gap, request addition |
| Stale documentation | Update rather than create new |

---

## 10. Output Format

### Per-Step Output

```markdown
## Test Plan Review: [Plan Name]

### Step 1: Review
**Status:** Complete | In Progress | Blocked
**Findings:**
- [Key findings from review]

**Issues:**
- [Any issues identified]

### Step 2: Validation
**Scope Assessment:**
- Feature X: [appropriate/over/under] tested
- Boundaries: [clear/unclear]

### Step 3: Approval
**Decision:** APPROVED | APPROVED_WITH_CONDITIONS | NEEDS_REVISION
**Rationale:** [Why this decision]
**Conditions:** [If applicable]

### Step 4: Implementation Guidance
**Traceability Matrix:**
[Table mapping tests to features/ACs]

### Step 5: Section 5 References
**Commands Used:**
- [Command]: [Purpose]

### Step 6: Documentation Updates
**Updates Made:**
- [File]: [Changes]

**New Documents:** None (or justification if created)
```

---

## Appendix: Review Checklist

```markdown
## Test Plan Review Checklist

### Completeness
- [ ] All features have test cases
- [ ] All ACs have corresponding tests
- [ ] Test data requirements documented
- [ ] Expected outcomes specified
- [ ] Error scenarios included

### Scope
- [ ] Coverage appropriate (not excessive)
- [ ] Boundaries clearly defined
- [ ] In-scope items listed
- [ ] Out-of-scope items listed
- [ ] No overlap with other test plans

### Traceability
- [ ] Tests link to requirements
- [ ] Features link to user stories
- [ ] ACs link to validation criteria

### Production Readiness
- [ ] Section 5 commands referenced
- [ ] Make targets documented
- [ ] Execution order specified
- [ ] Dependencies noted

### Documentation
- [ ] Existing docs reviewed
- [ ] Updates made where needed
- [ ] No unnecessary new docs
- [ ] Information consolidated
```
