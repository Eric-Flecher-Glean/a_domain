---
title: "Implementation Subdomain"
version: 1.0
date: 2026-01-22
status: draft
purpose: "Documentation for Implementation Subdomain"
---

# Implementation Subdomain

**SDLC Phase:** Development & Implementation
**Prompts in Domain:** 3
**Primary Focus:** Code execution, artifact production, state tracking

---

## Domain Overview

The Implementation subdomain contains prompts responsible for executing planned work items and producing concrete deliverables. These prompts transform plans into working code, tests, and documentation.

### Key Responsibilities

1. **Work Execution** - Execute planned tasks against acceptance criteria
2. **Artifact Production** - Generate code, tests, documentation
3. **State Tracking** - Maintain backlog state and artifact registration
4. **Registry Maintenance** - Track make commands and build tools
5. **Validation** - Verify work against acceptance criteria

---

## Prompts in This Domain

| Prompt | Short Name | Tech Spec |
|--------|------------|-----------|
| `cycle-implement.xml` | `cycle-implement` | [SPEC_cycle-implement.md](./SPEC_cycle-implement.md) |
| `core-yaml-backlog-refresh.xml` | `yml-bck-refresh` | [SPEC_yml-bck-refresh.md](./SPEC_yml-bck-refresh.md) |
| `repeatable-make-registry.xml` | `rep-mak-reg` | [SPEC_rep-mak-reg.md](./SPEC_rep-mak-reg.md) |

---

## Domain Connectivity

### Upstream Dependencies

| Provider Domain | Provider Prompt | Data Provided |
|-----------------|-----------------|---------------|
| Requirements | `yml-bck-mgr` | Story backlog and priorities |
| Planning | `unified-plan` | Execution plan and tasks |
| Planning | `ddd-make-align` | Context-aligned commands |

### Downstream Consumers

| Consumer Domain | Consumer Prompt | Integration Point |
|-----------------|-----------------|-------------------|
| Testing | `quality-gate` | Validates completed work |
| Testing | `tst-rvw-imp` | Uses implementation artifacts |
| Deployment | `demo-prep` | Uses make commands |
| Maintenance | `update-status` | Reports on completion |

### Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    IMPLEMENTATION DOMAIN                        │
└─────────────────────────────────────────────────────────────────┘

  YAML Backlog + Plan                 Implemented Work
  ┌──────────────────┐               ┌────────────────────┐
  │ Next Work Item   │               │ Code Files         │
  │ Acceptance Crit. │ ─cycle-impl─▶ │ Test Files         │
  │ Execution Plan   │               │ Documentation      │
  └──────────────────┘               │ Status Updates     │
                                     └────────────────────┘

  File System State                   Registered Artifacts
  ┌──────────────────┐               ┌────────────────────┐
  │ Source Files     │               │ artifact_registry  │
  │ Test Files       │ ─yml-bck-ref─▶│   implementation[] │
  │ Documentation    │               │   tests[]          │
  └──────────────────┘               │   documentation[]  │
                                     └────────────────────┘

  Makefiles                           Command Registry
  ┌──────────────────┐               ┌────────────────────┐
  │ make targets     │               │ domains:           │
  │ descriptions     │ ─rep-mak-reg─▶│   commands:        │
  │ dependencies     │               │     backlog_refs   │
  └──────────────────┘               └────────────────────┘
```

---

## Shared Concepts

### Execution Plan Structure

```yaml
execution_plan:
  - step: 1
    description: "Implement core handler"
    supports_criteria: ["AC1.1", "AC1.2"]
    deliverables:
      - type: code
        path: "src/core/handler.py"
      - type: test
        path: "tests/test_handler.py"
```

### Artifact Registration Structure

```yaml
artifact_registry:
  implementation:
    - file_path: "src/core/handler.py"
      file_type: source_code
      confidence: HIGH
      registered_date: "2026-01-21T10:30:00Z"
      staleness_status: CURRENT
  tests:
    - file_path: "tests/test_handler.py"
      file_type: test_code
      confidence: HIGH
  documentation:
    - file_path: "docs/HANDLER_GUIDE.md"
      file_type: documentation
```

### Make Command Structure

```yaml
domains:
  testing:
    commands:
      - name: test-unit
        target: test-unit
        file: Makefile
        description: "Run unit tests"
        dependencies: []
        backlog_refs: ["P1-TEST-001"]
        usage: "make test-unit"
```

---

## Usage Patterns

### Work Item Execution

```bash
# cycle-implement selects and executes next work item
# Prompt: "Execute the next priority work item from the backlog"

# Produces:
# - Code implementing the feature
# - Tests validating the code
# - Status update in backlog
```

### Artifact Registration

```bash
# yml-bck-refresh scans and registers new artifacts
# Prompt: "Scan the project and register all artifacts"

# Updates IMPLEMENTATION_BACKLOG.yaml with artifact_registry
```

### Registry Maintenance

```bash
# rep-mak-reg updates command registry
# Prompt: "Update the make command registry with new commands"

# Produces updated MAKE_COMMAND_REGISTRY.yaml
```

---

## Best Practices

1. **Acceptance-Driven** - Every step maps to acceptance criteria
2. **Concrete Artifacts** - Produce copy-pasteable code, not descriptions
3. **State Synchronization** - Update backlog after each task completion
4. **Traceability** - Link artifacts to stories via registry
5. **Incremental Progress** - Mark tasks complete individually, not in batches

---

## Related Documentation

- [SDLC Domain Index](../SDLC_PROMPT_DOMAIN_INDEX.md)
- [Planning Domain](../planning/README.md) (previous phase)
- [Testing Domain](../testing/README.md) (next phase)
