---
title: "Planning Subdomain"
version: 1.0
date: 2026-01-22
status: draft
purpose: "Documentation for Planning Subdomain"
---

# Planning Subdomain

**SDLC Phase:** Design & Planning
**Prompts in Domain:** 3
**Primary Focus:** Architecture design, work breakdown, project structure

---

## Domain Overview

The Planning subdomain contains prompts responsible for designing implementation approaches, organizing project structure, and establishing architectural alignment. These prompts transform requirements into actionable implementation plans.

### Key Responsibilities

1. **Plan Consolidation** - Unify disparate planning artifacts into coherent implementation plans
2. **Architecture Alignment** - Map operational tooling to DDD bounded contexts
3. **Project Organization** - Maintain clean directory structure with metadata
4. **Work Decomposition** - Break high-level requirements into executable tasks
5. **Scope Validation** - Remove outdated scope and ensure plan currency

---

## Prompts in This Domain

| Prompt | Short Name | Tech Spec |
|--------|------------|-----------|
| `unified-technical-implementation-plan-refiner.xml` | `unified-plan` | [SPEC_unified-plan.md](./SPEC_unified-plan.md) |
| `ddd-make-alignment.xml` | `ddd-make-align` | [SPEC_ddd-make-align.md](./SPEC_ddd-make-align.md) |
| `organize.xml` | `organize` | [SPEC_organize.md](./SPEC_organize.md) |

---

## Domain Connectivity

### Upstream Dependencies

| Provider Domain | Provider Prompt | Data Provided |
|-----------------|-----------------|---------------|
| Requirements | `yml-bck-mgr` | Story structure and priorities |
| Requirements | `scope-change` | Updated scope definitions |

### Downstream Consumers

| Consumer Domain | Consumer Prompt | Integration Point |
|-----------------|-----------------|-------------------|
| Implementation | `cycle-implement` | Uses execution plan |
| Testing | `tst-rvw-imp` | Uses test plan structure |
| Deployment | `demo-prep` | Uses project structure |

### Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                      PLANNING DOMAIN                            │
└─────────────────────────────────────────────────────────────────┘

  YAML Backlog                        Consolidated Plan
  ┌──────────────┐                   ┌─────────────────────┐
  │ Stories      │                   │ Executive Summary   │
  │ Priorities   │ ──unified-plan──▶ │ Phases/Milestones   │
  │ Dependencies │                   │ Detailed Tasks      │
  └──────────────┘                   │ Risks & Assumptions │
                                     └─────────────────────┘

  Make Commands                       DDD-Aligned Registry
  ┌──────────────┐                   ┌─────────────────────┐
  │ Makefile     │                   │ Bounded Contexts    │
  │ Targets      │ ─ddd-make-align─▶ │ Strategic Layers    │
  │ Descriptions │                   │ Domain Entities     │
  └──────────────┘                   │ Intent Documentation│
                                     └─────────────────────┘

  Directory Tree                      Organized Structure
  ┌──────────────┐                   ┌─────────────────────┐
  │ Files        │                   │ index.yaml          │
  │ Folders      │ ────organize────▶ │ index.md            │
  │ Metadata     │                   │ Per-file Metadata   │
  └──────────────┘                   └─────────────────────┘
```

---

## Shared Concepts

### Plan Structure

All planning prompts work toward consistent plan organization:

```yaml
plan_structure:
  executive_summary: "1-3 paragraphs"

  current_scope:
    objectives: []
    success_criteria: []

  implementation_phases:
    - phase_id: "P1"
      name: "Phase Name"
      milestones: []
      workstreams: []
      tasks:
        - task_id: "T1.1"
          description: ""
          dependencies: []
          sequencing: ""

  assumptions: []
  dependencies: []
  risks: []

  archived_scope:
    - item: ""
      rationale: ""
```

### DDD Bounded Contexts

| Context | Layer | Description |
|---------|-------|-------------|
| `activity_ingestion` | CORE | Event normalization from MCP |
| `work_unit_synthesis` | CORE | Event grouping into work units |
| `work_classification` | CORE | Work unit categorization |
| `knowledge_labor_metrics` | CORE | Metric aggregation |
| `validation_experimentation` | SUPPORTING | Model validation |
| `reporting_analytics` | SUPPORTING | Reports and dashboards |
| `feedback_labeling` | SUPPORTING | User corrections |
| `identity_permissions` | GENERIC | External user/team refs |

### Strategic Layers

| Layer | Purpose | Expected Coverage |
|-------|---------|-------------------|
| CORE | Differentiating capabilities | 60-70% |
| SUPPORTING | Enables core domain | 25-35% |
| GENERIC | Common utilities | 5-10% |

---

## Usage Patterns

### Plan Consolidation

```bash
# Run unified-plan to consolidate planning artifacts
# Prompt: "Review all planning documents and create consolidated implementation plan"

# Output: Structured plan with phases, tasks, and archived scope
```

### DDD Alignment

```bash
# Run ddd-make-align to add architectural context to make commands
# Prompt: "Map all make commands to DDD bounded contexts"

# Verify alignment
cat MAKE_COMMAND_REGISTRY.yaml | grep bounded_context
```

### Project Organization

```bash
# Run organize to maintain directory structure
# Prompt: "Organize the project directory and update metadata"

# Verify organization
cat index.yaml
```

---

## Best Practices

1. **Single Consolidated Plan** - Maintain one authoritative implementation plan
2. **Architectural Traceability** - Every command maps to exactly one bounded context
3. **Metadata Consistency** - File metadata synchronized across sources
4. **Scope Clarity** - Outdated scope explicitly archived, not deleted
5. **Incremental Updates** - Never overwrite, always enhance

---

## Related Documentation

- [SDLC Domain Index](../SDLC_PROMPT_DOMAIN_INDEX.md)
- [Requirements Domain](../requirements/README.md) (previous phase)
- [Implementation Domain](../implementation/README.md) (next phase)
