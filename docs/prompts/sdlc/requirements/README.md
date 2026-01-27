---
title: "Requirements Subdomain"
version: 1.0
date: 2026-01-22
status: draft
purpose: "Documentation for Requirements Subdomain"
---

# Requirements Subdomain

**SDLC Phase:** Requirements Gathering & Management
**Prompts in Domain:** 2
**Primary Focus:** Scope definition, backlog creation, requirements change management

---

## Domain Overview

The Requirements subdomain contains prompts responsible for capturing, organizing, and managing project requirements and work items. These prompts establish the foundational state that all other SDLC phases consume.

### Key Responsibilities

1. **Backlog Creation** - Transform source documents into structured YAML backlogs
2. **Priority Assignment** - Classify work items by priority (P0-P3)
3. **Dependency Mapping** - Establish relationships between work items
4. **Scope Management** - Handle requirement changes and scope evolution
5. **State Initialization** - Set up project state for downstream phases

---

## Prompts in This Domain

| Prompt | Short Name | Tech Spec |
|--------|------------|-----------|
| `yaml-backlog-manager.xml` | `yml-bck-mgr` | [SPEC_yml-bck-mgr.md](./SPEC_yml-bck-mgr.md) |
| `scope-change.xml` | `scope-change` | [SPEC_scope-change.md](./SPEC_scope-change.md) |

---

## Domain Connectivity

### Upstream Dependencies

None - This is the entry point of the SDLC pipeline.

### Downstream Consumers

| Consumer Domain | Consumer Prompt | Integration Point |
|-----------------|-----------------|-------------------|
| Planning | `unified-plan` | Reads backlog for work breakdown |
| Implementation | `cycle-implement` | Reads backlog for next work item |
| Implementation | `yml-bck-refresh` | Extends backlog with artifact registry |
| Maintenance | `update-status` | Reads backlog for status reporting |

### Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    REQUIREMENTS DOMAIN                          │
└─────────────────────────────────────────────────────────────────┘

  Source Documents                    YAML Backlog
  ┌──────────────┐                   ┌─────────────────────┐
  │ Design Docs  │                   │ backlog_metadata:   │
  │ Test Plans   │ ──yml-bck-mgr──▶  │   version: N        │
  │ Specs        │                   │ stories:            │
  │ Requirements │                   │   - story_id: P0-*  │
  └──────────────┘                   │   - dependencies: []│
                                     └─────────────────────┘
                                              │
                                              ▼
  Scope Changes                      Updated Backlog
  ┌──────────────┐                   ┌─────────────────────┐
  │ New Reqs     │                   │ stories: (modified) │
  │ Priority Δ   │ ──scope-change──▶ │ artifacts: (updated)│
  │ Constraint Δ │                   │ plans: (aligned)    │
  └──────────────┘                   └─────────────────────┘
```

---

## Shared Concepts

### Story Structure

Both prompts work with the same story structure:

```yaml
stories:
  - story_id: "P0-001"
    priority: P0
    title: "Feature Title"
    description: "Feature description"
    dependencies: ["P0-000"]
    status: not_started | in_progress | completed | blocked
    source: "document reference"
    test_cases: ["TC1", "TC2"]
    acceptance_criteria:
      - "AC1: Criteria description"
```

### Priority Levels

| Level | Description | Typical Use |
|-------|-------------|-------------|
| P0 | Critical | Core features, blockers |
| P1 | High | Important features |
| P2 | Medium | Nice-to-have features |
| P3 | Low | Future considerations |

### Status Values

| Status | Description |
|--------|-------------|
| `not_started` | Work not yet begun |
| `in_progress` | Currently being worked on |
| `completed` | All acceptance criteria met |
| `blocked` | Cannot proceed (documented reason) |

---

## Usage Patterns

### Initial Project Setup

```bash
# 1. Run yml-bck-mgr to create initial backlog
# Prompt: "Parse the implementation plan and create YAML backlog"

# 2. Verify backlog structure
cat IMPLEMENTATION_BACKLOG.yaml | head -50
```

### Handling Scope Changes

```bash
# 1. Run scope-change when requirements evolve
# Prompt: "Adapt project to new requirement: [description]"

# 2. Verify updated artifacts
git diff IMPLEMENTATION_BACKLOG.yaml
```

---

## Best Practices

1. **Single Source of Truth** - Always update backlog through these prompts, not manually
2. **Dependency Validation** - Ensure all referenced story IDs exist
3. **Idempotent Operations** - Safe to run multiple times without corruption
4. **Source Traceability** - Every story must reference its source document

---

## Related Documentation

- [SDLC Domain Index](../SDLC_PROMPT_DOMAIN_INDEX.md)
- [Planning Domain](../planning/README.md) (next phase)
