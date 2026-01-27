---
title: "Technical Specification: scope-change"
version: 1.0
date: 2026-01-22
status: draft
purpose: "Documentation for Technical Specification: scope-change"
---

# Technical Specification: scope-change

**Prompt Name:** Scope Change Handler
**Short Name:** `scope-change`
**Version:** 1.0
**Stateful:** Yes
**SDLC Subdomain:** Requirements

---

## 1. Purpose & Objectives

### Primary Goal

Adapt the project to a new scope and then autonomously execute the highest-priority feasible work item until its acceptance criteria are satisfied or a clear blocker is reached.

### Key Objectives

1. **Scope Analysis** - Understand changes in requirements, priorities, or constraints
2. **Impact Assessment** - Identify affected artifacts (designs, code, plans, trackers)
3. **Artifact Updates** - Modify existing artifacts to reflect new scope
4. **Execution Continuation** - After adaptation, execute next priority work item
5. **Validation** - Verify work against acceptance criteria

---

## 2. Input/Output Schemas

### Input Sources

| Source Type | Description | Required |
|-------------|-------------|----------|
| Scope Change Description | New requirements or constraint changes | Yes |
| Existing Plans | Current backlog, roadmaps, design docs | Yes |
| Code/Implementation | Current codebase state | Context |
| Status Tracking | Current work item statuses | Yes |

### Input Format

```yaml
scope_change_input:
  description: "New requirement description"
  type: requirement_addition | priority_change | constraint_change
  affected_areas:
    - "area1"
    - "area2"

existing_context:
  backlog: "IMPLEMENTATION_BACKLOG.yaml"
  design_docs: ["DESIGN.md", "ARCHITECTURE.md"]
  status_tracker: "TRACKER.md"
```

### Output Schema

```yaml
scope_change_output:
  analysis:
    scope_change_summary: "Brief description of change"
    artifacts_reviewed:
      - path: "artifact_path"
        type: "design|code|plan|tracker"
    modifications:
      - artifact: "path"
        changes: "description of modifications"
    new_documents:
      - path: "new_doc_path"
        reason: "why creation was necessary"

  execution:
    selected_work_item:
      name: "Work item name"
      description: "Goal description"
      rationale: "Why selected"

    acceptance_criteria:
      - criterion: "AC1"
        type: explicit | inferred
        reasoning: "if inferred"

    execution_plan:
      - step: 1
        description: "Step description"
        supports_criteria: ["AC1", "AC2"]

    implementation:
      - step: 1
        artifacts_produced:
          - type: "code|config|doc|test"
            content: "..."

    validation:
      - criterion: "AC1"
        status: met | partially_met | unmet
        justification: "..."

    summary:
      status: complete | partially_complete | blocked
      risks: []
      open_questions: []
      next_steps: []
```

---

## 3. Dependencies

### Required Inputs

| Dependency | Type | Description |
|------------|------|-------------|
| YAML Backlog | File | `IMPLEMENTATION_BACKLOG.yaml` |
| Planning Artifacts | Files | Design docs, implementation plans |
| Status Tracker | File | Current work status |
| Scope Change Request | Input | Description of new scope |

### Runtime Dependencies

| Dependency | Purpose |
|------------|---------|
| `yml-bck-mgr` | Backlog structure and state |
| File System | Read/write artifacts |
| Version Control | Track changes |

### Downstream Consumers

| Consumer | Purpose |
|----------|---------|
| `cycle-implement` | Continues execution with updated scope |
| `quality-gate` | Validates scope-adjusted work |
| `update-status` | Reports on scope changes |

---

## 4. Execution Phases

### Phase 1: Scope Change Analysis

**Purpose:** Understand and document the scope change

**Steps:**
1. Parse scope change description
2. Identify type of change (requirement, priority, constraint)
3. Map affected artifacts
4. Document impact assessment

### Phase 2: Artifact Updates

**Purpose:** Modify existing artifacts to reflect new scope

**Steps:**
1. Review all relevant documents
2. Update plans and specifications
3. Modify status trackers
4. Create new documents only when necessary
5. Prefer updating over creating

### Phase 3: Execution

**Purpose:** Execute highest-priority work item

**Steps:**
1. Analyze updated backlog
2. Select next work item (highest priority, unblocked)
3. Extract acceptance criteria
4. Build execution plan
5. Implement with concrete artifacts
6. Validate against criteria

---

## 5. Usage Examples

### Example 1: New Requirement Addition

**Prompt:**
```
Adapt the project to include a new requirement:
"Add support for meeting transcript extraction from Glean MCP"
```

**Expected Output:**

```yaml
scope_change_output:
  analysis:
    scope_change_summary: "Add meeting transcript extraction capability"
    artifacts_reviewed:
      - path: "IMPLEMENTATION_BACKLOG.yaml"
        type: plan
      - path: "docs/ARCHITECTURE.md"
        type: design
    modifications:
      - artifact: "IMPLEMENTATION_BACKLOG.yaml"
        changes: "Added story P1-F5-001 for transcript extraction"
      - artifact: "docs/ARCHITECTURE.md"
        changes: "Updated Activity Ingestion context to include meetings"
    new_documents: []
```

### Example 2: Priority Change

**Prompt:**
```
Reprioritize the project: GTM Classification is now P0, move above Baseline Comparison.
```

**Expected Behavior:**
- Update story priorities in backlog
- Reorder stories by new priority
- Adjust dependency chains if needed
- Document change in changelog

### Example 3: Constraint Change

**Prompt:**
```
New constraint: All MCP queries must include rate limiting.
Adapt the project accordingly.
```

**Expected Behavior:**
- Add rate limiting requirement to affected stories
- Update acceptance criteria
- Potentially add new infrastructure story
- Update technical specs

---

## 6. Integration Points

### Integration with yml-bck-mgr

```yaml
# scope-change modifies backlog created by yml-bck-mgr
workflow:
  1. yml-bck-mgr creates initial backlog
  2. Scope change received
  3. scope-change reads and modifies backlog
  4. Updates version and changelog
  5. Validates against yml-bck-mgr schema
```

### Integration with cycle-implement

```yaml
# After scope adaptation, execution continues with cycle-implement logic
execution_phase:
  1. Read updated backlog
  2. Apply cycle-implement selection logic
  3. Execute work item
  4. Update status on completion
```

---

## 7. Success Criteria

### Validation Rules

| Rule | Description |
|------|-------------|
| Artifact Preservation | Prefer updating over creating new documents |
| Priority Respect | Follow defined priority order unless explicitly changed |
| Context Authority | Use provided context as source of truth |
| No Fabrication | Do not invent requirements or data |
| Blocker Documentation | Document blockers with required follow-ups |
| Acceptance Validation | Every criterion has explicit status |

### Quality Metrics

| Metric | Target |
|--------|--------|
| Artifact Review Coverage | 100% of affected artifacts reviewed |
| Scope Alignment | All updates aligned to scope change |
| Criteria Coverage | 100% of AC items validated |
| Traceability | All changes traceable to scope change request |

---

## 8. Constraints

1. **Context Authority** - Provided context is source of truth
2. **No Silent Invention** - Missing info must be called out explicitly
3. **Priority Preservation** - Don't change priorities unless allowed
4. **Update Preference** - Prefer updating existing artifacts
5. **Completion Gate** - Don't switch items until current is done or blocked
6. **Transparent Reasoning** - Keep outputs human-followable

---

## 9. Error Handling

| Error Condition | Handling |
|-----------------|----------|
| Ambiguous scope change | Request clarification, list options |
| Conflicting requirements | Document conflict, flag for decision |
| Missing artifacts | Note missing info, proceed with available |
| Blocked execution | Document blocker, specify required info |
| Invalid dependencies | Flag broken chain, suggest resolution |

---

## 10. Output Format

### Section Structure

1. **Scope Change Analysis and Artifact Updates**
   - Scope change summary
   - Artifacts reviewed (with types)
   - Modifications made
   - New documents created (with rationale)

2. **Selected Next Unit of Work**
   - Name and goal
   - Selection rationale

3. **Acceptance Criteria**
   - Explicit vs inferred labeling
   - Reasoning for inferred items

4. **Execution Plan**
   - Numbered sub-steps
   - Criteria mapping per step

5. **Implementation**
   - Grouped by sub-step
   - Concrete artifacts (code, config, docs, tests)
   - Deviation notes

6. **Validation Against Acceptance Criteria**
   - Status per criterion (met/partial/unmet)
   - Justifications
   - Assumptions

7. **Summary and Next Steps**
   - Overall status
   - Risks and uncertainties
   - Open questions
   - Follow-up actions

---

## Appendix: Scope Change Types

| Type | Description | Typical Artifacts Affected |
|------|-------------|---------------------------|
| `requirement_addition` | New feature or capability | Backlog, design docs, test plans |
| `requirement_modification` | Change to existing requirement | Backlog, specs, implementation |
| `requirement_removal` | Feature descoped | Backlog, archive docs |
| `priority_change` | Reprioritization of work | Backlog ordering |
| `constraint_addition` | New technical/business constraint | Architecture, implementation |
| `constraint_removal` | Constraint lifted | Implementation, tests |
| `dependency_change` | External dependency changed | Integration points, tests |
