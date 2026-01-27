---
title: "Technical Specification: cycle-implement"
version: 1.0
date: 2026-01-22
status: draft
purpose: "Documentation for Technical Specification: cycle-implement"
---

# Technical Specification: cycle-implement

**Prompt Name:** Cycle Implementation
**Short Name:** `cycle-implement`
**Version:** 1.0
**Stateful:** Yes
**SDLC Subdomain:** Implementation

---

## 1. Purpose & Objectives

### Primary Goal

Identify the next unit of work from the existing plan, create a concrete execution plan based on the available context, and implement that plan until the acceptance criteria are satisfied or a clear blocker is reached.

### Key Objectives

1. **Work Selection** - Identify highest-priority unblocked work item
2. **Criteria Extraction** - Extract explicit and inferred acceptance criteria
3. **Plan Building** - Create detailed execution sub-steps
4. **Implementation** - Produce concrete, copy-pasteable artifacts
5. **Validation** - Verify each criterion as met/partial/unmet

---

## 2. Input/Output Schemas

### Input Sources

| Source Type | Description | Required |
|-------------|-------------|----------|
| Backlog/Plan | Work items with priorities | Yes |
| Status Indicators | Current completion state | Yes |
| Supporting Context | Code, docs, design notes | Context |
| Acceptance Criteria | Explicit or implicit | Yes |

### Input Format

```yaml
backlog_input:
  plan_source: "IMPLEMENTATION_BACKLOG.yaml"

  stories:
    - story_id: "P0-F1-001"
      priority: P0
      title: "Work Unit Discovery"
      status: not_started
      dependencies: []
      acceptance_criteria:
        - "AC1.1: Query Glean MCP user_activity"
        - "AC1.2: Return valid WorkUnit objects"
      tasks:
        - "Implement MCP query handler"
        - "Create WorkUnit parser"

context:
  code_snippets: []
  documentation: []
  design_notes: []
  constraints: []
```

### Output Schema

```markdown
## 1. Selected Next Unit of Work

**Name:** Work Unit Discovery
**Goal:** Implement MCP-based work unit discovery
**Rationale:** Highest priority (P0), no dependencies, not blocked

## 2. Acceptance Criteria

| ID | Criterion | Type |
|----|-----------|------|
| AC1.1 | Query Glean MCP user_activity endpoint | Explicit |
| AC1.2 | Return valid WorkUnit objects | Explicit |
| AC1.3 | Handle empty result sets gracefully | Inferred |

## 3. Execution Plan

| Step | Description | Supports |
|------|-------------|----------|
| 1 | Create MCP query handler | AC1.1 |
| 2 | Implement response parser | AC1.2 |
| 3 | Add error handling | AC1.3 |

## 4. Implementation

### Step 1: Create MCP query handler

```python
# src/core/mcp_handler.py
def query_user_activity(start_date: str, end_date: str) -> dict:
    """Query Glean MCP user_activity endpoint."""
    ...
```

## 5. Validation Against Acceptance Criteria

| Criterion | Status | Justification |
|-----------|--------|---------------|
| AC1.1 | Met | Handler queries user_activity correctly |
| AC1.2 | Met | Parser returns WorkUnit objects |
| AC1.3 | Met | Empty sets return empty list |

## 6. Summary and Next Steps

**Status:** Complete
**Risks:** None identified
**Follow-ups:** Integration testing with live MCP
```

---

## 3. Dependencies

### Required Inputs

| Dependency | Type | Description |
|------------|------|-------------|
| YAML Backlog | File | `IMPLEMENTATION_BACKLOG.yaml` |
| Context Documents | Optional | Supporting code, docs, designs |

### Runtime Dependencies

| Dependency | Purpose |
|------------|---------|
| `yml-bck-mgr` | Backlog structure |
| File System | Read context, write artifacts |
| Version Control | Track changes |

### Downstream Consumers

| Consumer | Purpose |
|----------|---------|
| `quality-gate` | Validates completed work |
| `yml-bck-refresh` | Registers produced artifacts |
| `update-status` | Reports progress |

---

## 4. Processing Steps

### Step 1: Analyze Backlog

**Actions:**
- Read entire plan/backlog
- Enumerate work items with priorities
- Note current statuses

### Step 2: Select Next Work Item

**Selection Criteria:**
1. Highest priority (P0 > P1 > P2 > P3)
2. Not yet completed (status ≠ completed)
3. Not blocked (all dependencies met)

**If All Blocked:**
- Select next unblockable, high-value item
- Document and justify alternative selection

### Step 3: Extract Acceptance Criteria

**Actions:**
- List explicit criteria from plan/spec
- Infer additional criteria from context
- Label each as explicit or inferred
- Explain reasoning for inferred items

### Step 4: Build Execution Plan

**Actions:**
- Create numbered sub-steps
- Map each step to acceptance criteria
- Ensure every criterion has supporting step(s)
- Order steps by dependency

### Step 5: Implement

**Deliverables per step:**
- Code files (copy-pasteable)
- Configuration changes
- Documentation updates
- Test cases

**During implementation:**
- Adjust plan as constraints emerge
- Keep criteria mapping explicit
- Note missing information (don't guess)

### Step 6: Validate

**For each criterion:**
- Status: met | partially_met | unmet
- Brief justification
- Assumptions made

**If criterion unmet:**
- Don't fabricate details
- Specify additional info required

### Step 7: Summarize

**Report:**
- Overall status (complete/partial/blocked)
- Open questions
- Required follow-ups

---

## 5. Usage Examples

### Example 1: Standard Execution

**Prompt:**
```
Execute the next priority work item from the backlog.
```

**Expected Flow:**
1. Reads IMPLEMENTATION_BACKLOG.yaml
2. Selects P0-F1-001 (highest priority, unblocked)
3. Extracts 5 acceptance criteria
4. Creates 8 execution steps
5. Implements each step with code
6. Validates all criteria as met
7. Summarizes as complete

### Example 2: Blocked Item Handling

**Prompt:**
```
Execute next work item. Note: P0-F1-002 depends on external API not yet available.
```

**Expected Behavior:**
- Skips P0-F1-002 (blocked)
- Selects P0-F1-003 (next unblocked)
- Documents why P0-F1-002 was skipped
- Proceeds with P0-F1-003 execution

### Example 3: Partial Completion

**Prompt:**
```
Continue implementation. Context is limited - API spec unavailable.
```

**Expected Behavior:**
- Implements available portions
- Marks missing items as "partially_met"
- Documents: "Requires API specification to complete AC1.3"
- Status: partially_complete

---

## 6. Integration Points

### Integration with yml-bck-mgr

```yaml
# cycle-implement consumes backlog from yml-bck-mgr
workflow:
  1. yml-bck-mgr creates/updates backlog
  2. cycle-implement reads backlog
  3. Selects next work item
  4. Updates status on completion
```

### Integration with yml-bck-refresh

```yaml
# Produced artifacts registered by yml-bck-refresh
workflow:
  1. cycle-implement produces code, tests, docs
  2. yml-bck-refresh scans for new artifacts
  3. Registers in artifact_registry
  4. Links to completed story
```

### Integration with quality-gate

```yaml
# Completed work validated by quality-gate
workflow:
  1. cycle-implement completes work item
  2. quality-gate runs validation tests
  3. Confirms make targets pass
  4. Approves progression
```

---

## 7. Success Criteria

### Validation Rules

| Rule | Description |
|------|-------------|
| Single Selection | One clear work item selected |
| Rationale Provided | Selection tied to plan priorities |
| Criteria Listed | All explicit/inferred labeled |
| Plan Mapped | Every step links to criteria |
| Artifacts Concrete | Copy-pasteable code, not descriptions |
| Status Explicit | Every criterion has met/partial/unmet |
| Blockers Documented | Missing context clearly stated |

### Quality Metrics

| Metric | Target |
|--------|--------|
| Criteria Coverage | 100% criteria have supporting steps |
| Artifact Completeness | All feasible steps produce output |
| Validation Rate | 100% criteria have explicit status |

---

## 8. Constraints

1. **Context Authority** - Provided context is source of truth
2. **Priority Respect** - Don't change priorities unless allowed
3. **Completion Gate** - Don't switch items until done or blocked
4. **No Guessing** - Missing info called out, not invented
5. **Human Actionable** - All outputs understandable by collaborators

---

## 9. Error Handling

| Error Condition | Handling |
|-----------------|----------|
| All items blocked | Select most unblockable, document justification |
| Missing context | Note gap, proceed with available, flag in validation |
| Conflicting requirements | Document conflict, propose resolution |
| Criterion cannot be met | Mark unmet, specify required info |

---

## 10. Output Format

### Required Sections

1. **Selected Next Unit of Work**
   - Name, short description, selection rationale

2. **Acceptance Criteria**
   - Bullet list with explicit/inferred labels

3. **Execution Plan**
   - Numbered sub-steps with criteria annotations

4. **Implementation**
   - Grouped by sub-step
   - Concrete, copy-pasteable artifacts
   - Code blocks, config snippets, docs

5. **Validation Against Acceptance Criteria**
   - Table: criterion | status | justification

6. **Summary and Next Steps**
   - Completion status
   - Risks/uncertainties
   - Follow-up questions/actions

---

## Appendix: Work Item Status Transitions

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ not_started │────▶│ in_progress │────▶│  completed  │
└─────────────┘     └─────────────┘     └─────────────┘
                           │
                           ▼
                    ┌─────────────┐
                    │   blocked   │
                    └─────────────┘
```

| Transition | Trigger |
|------------|---------|
| not_started → in_progress | cycle-implement selects item |
| in_progress → completed | All criteria validated as met |
| in_progress → blocked | Blocker identified, documented |
| blocked → in_progress | Blocker resolved |
