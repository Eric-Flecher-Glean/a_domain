---
title: "Technical Specification: quality-gate"
version: 1.0
date: 2026-01-22
status: draft
purpose: "Documentation for Technical Specification: quality-gate"
---

# Technical Specification: quality-gate

**Prompt Name:** Quality Gate
**Short Name:** `quality-gate`
**Version:** 1.0
**Stateful:** No
**SDLC Subdomain:** Testing

---

## 1. Purpose & Objectives

### Primary Goal

Ensure all completed work is fully tested, documented, and tracked before moving on to the next priority item.

### Key Objectives

1. **Test Verification** - Run make commands and verify actual output
2. **Status Updates** - Update all tracking systems
3. **Documentation Currency** - Ensure README reflects current state
4. **Progression Control** - Block next item until gate passes
5. **Repeatability** - Same process for every work item

---

## 2. Input/Output Schemas

### Input Sources

| Source Type | Description | Purpose |
|-------------|-------------|---------|
| Completed Work | Code changes, tests | Items to validate |
| Make Commands | Test/build targets | Validation commands |
| Status Tracker | Current work status | Tracking updates |
| README | Current documentation | Doc updates |

### Input Format

```yaml
quality_gate_input:
  work_items:
    - story_id: "P0-F1-001"
      status: in_progress
      changes:
        - "src/core/discovery.py"
        - "tests/test_discovery.py"

  make_commands:
    - name: test-unit
      expected: "All tests pass"
    - name: test-integration
      expected: "Integration suite passes"

  tracking_system:
    type: yaml_backlog
    file: "IMPLEMENTATION_BACKLOG.yaml"

  readme_path: "README.md"
```

### Output Schema (Checklist)

```markdown
## Quality Gate Checklist

### 1. Testing
- [ ] Identify make commands for completed work
- [ ] Run `make test-unit` - verify output
- [ ] Run `make test-integration` - verify output
- [ ] Confirm no unexpected warnings/errors

### 2. Tracking Updates
- [ ] Update story status (in_progress → completed)
- [ ] Link commits/PRs to story
- [ ] Log completion notes

### 3. Documentation Updates
- [ ] Update README with new commands/usage
- [ ] Document new configuration/dependencies
- [ ] Verify setup instructions current

### 4. Gate Decision
- [ ] All tests pass: ✓
- [ ] Tracking updated: ✓
- [ ] Documentation current: ✓
- **GATE STATUS:** PASS / FAIL

### 5. Next Item
- [ ] Proceed to next priority item
```

---

## 3. Dependencies

### Required Inputs

| Dependency | Type | Description |
|------------|------|-------------|
| Completed Work | Context | Work to validate |
| Make Commands | Makefile | Test targets |
| Status System | File | Tracking updates |

### Runtime Dependencies

| Dependency | Purpose |
|------------|---------|
| `cycle-implement` | Provides completed work |
| `rep-mak-reg` | Lists available commands |
| File System | Run commands, update files |

### Downstream Consumers

| Consumer | Purpose |
|----------|---------|
| `yml-bck-mgr` | Receives status updates |
| Next work item | Proceeds after gate pass |
| `demo-prep` | Only demos gated work |

---

## 4. Processing Steps

### Step 1: Identify Work Items

**Actions:**
- List work items ready for validation
- Identify corresponding make targets
- Note expected outcomes

### Step 2: Run Make Commands

**Actions:**
- Execute each relevant make command
- Observe actual console output
- Compare to expected behavior
- Document pass/fail status

**Validation Criteria:**
- All tests passing
- Builds succeeding
- No unexpected warnings
- No unresolved errors

### Step 3: Fix Issues (If Found)

**Actions:**
- If issues found, fix them
- Re-run make commands
- Iterate until output clean
- Document fixes made

### Step 4: Update Tracking

**Actions:**
- Update story/ticket status
- Log completion notes
- Link commits/PRs
- Record validation timestamp

### Step 5: Update Documentation

**Actions:**
- Review README for currency
- Add new make commands
- Document new dependencies
- Update configuration details
- Verify setup instructions

### Step 6: Gate Decision

**Criteria:**
- All tests pass: Required
- Tracking updated: Required
- Documentation current: Required

**Decision:**
- All criteria met → PASS → Proceed to next item
- Any criteria failed → FAIL → Address before proceeding

---

## 5. Usage Examples

### Example 1: Successful Gate

**Prompt:**
```
Run quality gate for story P0-F1-001 (Work Unit Discovery).
```

**Expected Flow:**
```bash
$ make test-unit
✓ 23 tests passed, 0 failed

$ make test-integration
✓ Integration suite: 5/5 passed

# Update IMPLEMENTATION_BACKLOG.yaml
# P0-F1-001: status: completed

# Update README.md
# Added: make work-unit-discovery documentation

# GATE STATUS: PASS
# Proceed to P0-F1-002
```

### Example 2: Failed Gate

**Prompt:**
```
Run quality gate for story P0-F1-002.
```

**Expected Flow:**
```bash
$ make test-unit
✓ 22 tests passed, 1 failed
  FAIL: test_baseline_comparison - assertion error

# GATE STATUS: FAIL
# Fix required before proceeding
# Do not update status to completed
# Do not proceed to next item
```

### Example 3: Documentation Gap

**Prompt:**
```
Complete quality gate - tests pass but README outdated.
```

**Expected Behavior:**
- Tests: PASS
- Tracking: Updated
- Documentation: FAIL (missing new commands)
- GATE STATUS: FAIL
- Action: Update README, then re-run gate

---

## 6. Integration Points

### Integration with cycle-implement

```yaml
# quality-gate validates cycle-implement output
workflow:
  1. cycle-implement completes work item
  2. quality-gate runs validation
  3. If PASS: status updated, proceed
  4. If FAIL: fixes required, re-implement
```

### Integration with yml-bck-mgr

```yaml
# Tracking updates flow to backlog
workflow:
  1. quality-gate validates work
  2. Updates IMPLEMENTATION_BACKLOG.yaml
  3. Changes story status to completed
  4. Adds validation timestamp
```

### Integration with update-readme

```yaml
# Documentation updates coordinated
workflow:
  1. quality-gate identifies README gaps
  2. Updates README with new information
  3. Or triggers update-readme for comprehensive update
```

---

## 7. Success Criteria

### Validation Rules

| Rule | Description |
|------|-------------|
| Real Output | Commands actually run, output verified |
| Expected Behavior | Output matches expectations |
| Clean Results | No unresolved failures/warnings |
| Status Current | Tracking reflects completion |
| Docs Updated | README reflects changes |
| Gate Sequential | All checks complete before decision |

### Quality Metrics

| Metric | Target |
|--------|--------|
| Test Coverage | All relevant tests executed |
| Pass Rate | 100% tests pass |
| Doc Currency | README matches implementation |
| Tracking Accuracy | Status reflects reality |

---

## 8. Constraints

1. **No Skip** - Cannot skip or combine steps
2. **Repeatable** - Same process for every work item
3. **Checklist Format** - Clear, followable checklist
4. **Real Verification** - Actual output, not assumed success
5. **Sequential** - Complete current before next

---

## 9. Error Handling

| Error Condition | Handling |
|-----------------|----------|
| Test failure | Document failure, block progression |
| Build error | Fix and re-run, do not proceed |
| Missing docs | Update before gate decision |
| Tracking failure | Retry, document if persistent |

---

## 10. Output Format

### Checklist Structure

```markdown
## Quality Gate: [Story ID]

### Step 1: Testing
**Commands to Run:**
- `make [command]` - [purpose]

**Results:**
- [ ] [Command]: [PASS/FAIL] - [output notes]

### Step 2: Tracking Updates
- [ ] Status updated to: [new status]
- [ ] Commits linked: [commit refs]
- [ ] Notes logged: [summary]

### Step 3: Documentation
- [ ] README updated: [changes made]
- [ ] New commands documented: [list]
- [ ] Dependencies documented: [list]

### Gate Decision
- Testing: [PASS/FAIL]
- Tracking: [PASS/FAIL]
- Documentation: [PASS/FAIL]

**OVERALL: [PASS/FAIL]**

### Next Action
[Proceed to next item / Fix and re-gate]
```

---

## Appendix: Common Make Commands for Testing

| Command | Purpose | Expected Output |
|---------|---------|-----------------|
| `make test-unit` | Unit tests | "X tests passed, 0 failed" |
| `make test-integration` | Integration tests | "Suite: X/Y passed" |
| `make test-functional` | Functional tests | "Functional: PASS" |
| `make lint` | Code linting | No errors |
| `make validate-backlog` | Backlog validation | "Validation passed" |
| `make check-artifacts` | Artifact coverage | "100% coverage" |
