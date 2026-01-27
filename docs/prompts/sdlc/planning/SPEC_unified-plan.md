---
title: "Technical Specification: unified-plan"
version: 1.0
date: 2026-01-22
status: draft
purpose: "Documentation for Technical Specification: unified-plan"
---

# Technical Specification: unified-plan

**Prompt Name:** Unified Technical Implementation Plan Refiner
**Short Name:** `unified-plan`
**Version:** 1.0
**Stateful:** No
**SDLC Subdomain:** Planning

---

## 1. Purpose & Objectives

### Primary Goal

Review all existing project planning, consolidate and update it into a single, organized implementation plan, ensure a detailed technical implementation plan is validated, and remove any outdated scope.

### Key Objectives

1. **Artifact Inventory** - Catalog all existing planning materials
2. **Inconsistency Resolution** - Identify and resolve overlapping/conflicting items
3. **Plan Consolidation** - Merge into single coherent implementation plan
4. **Technical Detail** - Ensure tasks are execution-ready with sequencing
5. **Scope Cleanup** - Archive outdated scope with rationale

---

## 2. Input/Output Schemas

### Input Sources

| Source Type | Description | Examples |
|-------------|-------------|----------|
| Project Plans | High-level roadmaps | `ROADMAP.md` |
| Design Documents | Architecture/design specs | `DESIGN_SPEC.md` |
| Task Lists | Existing task breakdowns | `TASKS.md`, `TRACKER.md` |
| Scoping Documents | Scope definitions | `SCOPE.md` |
| Timelines | Schedule information | `TIMELINE.md` |

### Input Format

```yaml
planning_artifacts:
  - path: "doc/ROADMAP.md"
    type: roadmap
    status: current | outdated
  - path: "doc/DESIGN.md"
    type: design
    status: current
```

### Output Schema

```markdown
# Consolidated Implementation Plan

## 1. Executive Summary
[1-3 paragraphs on project state, goals, approach]

## 2. Current Scope & Objectives
### Objectives
- [Objective 1]
- [Objective 2]

### Success Criteria
- [Criterion 1]
- [Criterion 2]

## 3. Consolidated Technical Implementation Plan

### Phase 1: [Phase Name]
**Milestone:** [Milestone description]
**Target:** [Target outcome]

#### Workstream 1.1: [Workstream Name]
| Task ID | Description | Dependencies | Sequencing | Effort |
|---------|-------------|--------------|------------|--------|
| T1.1.1  | Task desc   | None         | First      | 2h     |
| T1.1.2  | Task desc   | T1.1.1       | Sequential | 4h     |

### Phase 2: [Phase Name]
[...]

## 4. Assumptions, Dependencies, and Risks

### Assumptions
- [Assumption 1]

### Dependencies
- [Dependency 1]

### Risks
| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Risk1| High   | Medium      | Mitigation |

## 5. Archived / Out-of-Scope Items
| Item | Original Source | Rationale for Archive |
|------|-----------------|----------------------|
| Old feature | ROADMAP v1 | Superseded by new approach |

## 6. Change Summary
### What Was Consolidated
- [List]

### What Was Updated
- [List]

### What Was Removed
- [List]
```

---

## 3. Dependencies

### Required Inputs

| Dependency | Type | Description |
|------------|------|-------------|
| Planning Artifacts | Files | At least one planning document |
| Current Scope Definition | Context | Understanding of current project goals |

### Runtime Dependencies

| Dependency | Purpose |
|------------|---------|
| File System | Read planning documents |
| Document Parser | Extract structured content |

### Downstream Consumers

| Consumer | Purpose |
|----------|---------|
| `cycle-implement` | Uses detailed tasks for execution |
| `tst-rvw-imp` | Uses plan structure for test planning |
| `yml-bck-mgr` | Incorporates plan into backlog |

---

## 4. Processing Steps

### Step 1: Inventory & Review

**Actions:**
- Enumerate all planning artifacts
- Classify by type (charter, scope, design, timeline, tasks)
- Note current vs historical content

### Step 2: Identify Overlaps & Inconsistencies

**Actions:**
- Map content across documents
- Flag contradicting information
- Note outdated elements

### Step 3: Define Plan Structure

**Actions:**
- Establish section hierarchy
- Map objectives to phases
- Organize workstreams logically

### Step 4: Consolidate Content

**Actions:**
- Merge relevant content
- Rewrite for consistency
- Maintain clear language

### Step 5: Create Technical Detail

**Actions:**
- Break work into phases → milestones → tasks
- Define sequencing and dependencies
- Add effort estimates where possible

### Step 6: Validate Plan

**Actions:**
- Check completeness against objectives
- Verify feasibility
- Document assumptions and risks

### Step 7: Archive Outdated Scope

**Actions:**
- Move legacy items to archive section
- Provide rationale for each
- Maintain traceability

### Step 8: Produce Change Summary

**Actions:**
- Document what was consolidated
- List updates made
- Note removals

---

## 5. Usage Examples

### Example 1: Initial Consolidation

**Prompt:**
```
Review all planning artifacts in the docs/ folder and create a consolidated
implementation plan. The project has evolved and some scope is outdated.
```

**Expected Output:**
- Executive summary of current project state
- Consolidated phases with detailed tasks
- Archived scope section with rationale
- Clear change summary

### Example 2: Plan Refresh

**Prompt:**
```
Update the implementation plan to reflect completed Phase 1 work.
Move completed items to history and refine Phase 2 tasks.
```

**Expected Behavior:**
- Completed work documented as achievements
- Phase 2 tasks refined with learnings
- Updated timeline and dependencies

---

## 6. Integration Points

### Integration with yml-bck-mgr

```yaml
# Consolidated plan informs backlog structure
workflow:
  1. unified-plan creates structured implementation plan
  2. yml-bck-mgr extracts stories from plan phases
  3. Tasks become stories with dependencies
```

### Integration with cycle-implement

```yaml
# Execution uses plan tasks directly
workflow:
  1. unified-plan defines T1.1.1, T1.1.2, etc.
  2. cycle-implement selects next unblocked task
  3. Implements against defined acceptance criteria
```

---

## 7. Success Criteria

### Validation Rules

| Rule | Description |
|------|-------------|
| Single Document | Output is one coherent plan |
| Task Coverage | Every objective has corresponding tasks |
| Technical Detail | Tasks have sequencing and dependencies |
| No Outdated Scope | Legacy items archived, not in main plan |
| Risks Documented | Assumptions and risks explicit |
| Change Summary | Clear record of modifications |

### Quality Metrics

| Metric | Target |
|--------|--------|
| Objective Coverage | 100% of objectives have implementation tasks |
| Consistency | No conflicting dates, responsibilities, or scope |
| Actionability | Tasks specific enough for execution |
| Traceability | Every change documented in summary |

---

## 8. Constraints

1. **Current Scope Only** - Main plan reflects current agreed scope
2. **Execution Detail** - Tasks must be specific enough for daily work
3. **Internal Consistency** - No conflicting information within plan
4. **Implementation Language** - Avoid vague statements, use specific actions
5. **Explicit Archive** - Outdated scope in labeled archive section

---

## 9. Error Handling

| Error Condition | Handling |
|-----------------|----------|
| Missing planning docs | Document gap, proceed with available |
| Conflicting requirements | Flag conflict, propose resolution |
| Unclear scope boundaries | List ambiguities, request clarification |
| Missing dependencies | Note missing info, mark as assumption |

---

## 10. Output Format

### Required Sections

1. **Executive Summary** (1-3 paragraphs)
2. **Current Scope & Objectives**
3. **Consolidated Technical Implementation Plan**
   - Phases and milestones
   - Workstreams/modules
   - Detailed tasks with sequencing and dependencies
4. **Assumptions, Dependencies, and Risks**
5. **Archived / Out-of-Scope Items** (with brief rationale)
6. **Change Summary** (consolidated, updated, removed)

---

## Appendix: Task Specification Template

```yaml
task:
  id: "T1.1.1"
  phase: "Phase 1"
  workstream: "Core Implementation"
  title: "Implement MCP query handler"
  description: "Create handler for Glean MCP user_activity queries"
  dependencies:
    - "T1.0.1"  # Environment setup
  inputs:
    - "MCP API specification"
    - "Authentication credentials"
  outputs:
    - "src/core/mcp_handler.py"
    - "tests/test_mcp_handler.py"
  acceptance_criteria:
    - "Handler successfully queries user_activity endpoint"
    - "Results parsed into WorkUnit objects"
  effort: "4 hours"
  sequencing: "After T1.0.1, before T1.1.2"
```
