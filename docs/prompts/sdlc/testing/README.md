---
title: "Testing Subdomain"
version: 1.0
date: 2026-01-22
status: draft
purpose: "Documentation for Testing Subdomain"
---

# Testing Subdomain

**SDLC Phase:** Quality Assurance & Testing
**Prompts in Domain:** 2
**Primary Focus:** Quality validation, test execution, acceptance verification

---

## Domain Overview

The Testing subdomain contains prompts responsible for validating quality, reviewing test plans, and ensuring acceptance criteria are met. These prompts act as quality gates between implementation and deployment.

### Key Responsibilities

1. **Quality Gates** - Enforce test/doc/tracking workflow before progression
2. **Test Plan Review** - Validate test plan completeness and scope
3. **Test Implementation** - Guide functional test development
4. **Make Command Validation** - Verify test commands pass
5. **Documentation Currency** - Ensure docs reflect current state

---

## Prompts in This Domain

| Prompt | Short Name | Tech Spec |
|--------|------------|-----------|
| `quality_gate.xml` | `quality-gate` | [SPEC_quality-gate.md](./SPEC_quality-gate.md) |
| `test-review-implementation.xml` | `tst-rvw-imp` | [SPEC_tst-rvw-imp.md](./SPEC_tst-rvw-imp.md) |

---

## Domain Connectivity

### Upstream Dependencies

| Provider Domain | Provider Prompt | Data Provided |
|-----------------|-----------------|---------------|
| Implementation | `cycle-implement` | Completed work to validate |
| Planning | `unified-plan` | Test plan structure |
| Implementation | `rep-mak-reg` | Test make commands |

### Downstream Consumers

| Consumer Domain | Consumer Prompt | Integration Point |
|-----------------|-----------------|-------------------|
| Deployment | `demo-prep` | Only validated work demoed |
| Maintenance | `update-readme` | Documents validated features |
| Requirements | `yml-bck-mgr` | Updates story status |

### Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                       TESTING DOMAIN                            │
└─────────────────────────────────────────────────────────────────┘

  Completed Work                      Validation Result
  ┌──────────────────┐               ┌────────────────────┐
  │ Code Changes     │               │ Tests: PASS/FAIL   │
  │ Make Commands    │ ─quality-gate─▶│ Docs: Updated ✓   │
  │ Status Tracker   │               │ Status: Updated ✓  │
  └──────────────────┘               │ Ready: YES/NO      │
                                     └────────────────────┘

  Test Plan                           Reviewed Plan
  ┌──────────────────┐               ┌────────────────────┐
  │ Test Cases       │               │ Scope: Validated   │
  │ Coverage         │ ─tst-rvw-imp─▶│ Tests: Implemented │
  │ Workflows        │               │ Docs: Updated      │
  └──────────────────┘               └────────────────────┘
```

---

## Shared Concepts

### Quality Gate Checklist

```yaml
quality_gate_checklist:
  testing:
    - id: QG-T1
      check: "Run relevant make test commands"
      validation: "Output shows all tests pass"

    - id: QG-T2
      check: "Verify no unexpected warnings"
      validation: "Clean output with expected messages"

  tracking:
    - id: QG-K1
      check: "Update ticket/story status"
      validation: "Status reflects completion"

    - id: QG-K2
      check: "Link commits/PRs to story"
      validation: "Traceability established"

  documentation:
    - id: QG-D1
      check: "Update README with new commands"
      validation: "README reflects current state"

    - id: QG-D2
      check: "Document new dependencies"
      validation: "Setup instructions current"
```

### Test Plan Review Structure

```yaml
test_plan_review:
  completeness:
    - feature_coverage: "All features have test cases"
    - boundary_definition: "Scope boundaries clear"
    - acceptance_criteria: "AC mapped to tests"

  validation:
    - scope_appropriate: "Not over/under tested"
    - boundaries_defined: "Clear in/out of scope"
    - traceability: "Tests link to requirements"

  approval:
    - decision: approved | needs_revision
    - conditions: "Any conditions for approval"
```

---

## Usage Patterns

### Quality Gate Workflow

```bash
# 1. Identify completed work items
# Check backlog for in_progress stories

# 2. Run quality gate
# Prompt: "Run quality gate for story P0-F1-001"

# 3. Execute make commands and verify
make test-unit
make test-integration

# 4. Update status and documentation
# quality-gate guides updates

# 5. Proceed to next item only after gate passes
```

### Test Plan Review Workflow

```bash
# 1. Review test plan document
# Prompt: "Review and validate the test plan for Phase 1"

# 2. Validate feature scope
# tst-rvw-imp checks all features have tests

# 3. Approve or request revisions
# Gate at step 3 - no implementation without approval

# 4. Implement tests with traceability
# Reference Section 5 make commands
```

---

## Best Practices

1. **Real Output Verification** - Always run commands and check actual output
2. **Mandatory Updates** - Status/tracking updates are not optional
3. **Documentation as Deliverable** - README updates are part of completion
4. **Sequential Gates** - Complete all checks before progressing
5. **Repeatable Process** - Same checklist for every work item

---

## Related Documentation

- [SDLC Domain Index](../SDLC_PROMPT_DOMAIN_INDEX.md)
- [Implementation Domain](../implementation/README.md) (previous phase)
- [Deployment Domain](../deployment/README.md) (next phase)
