---
title: "AFL-XML-MIG Migration Inventory"
version: 1.0
date: 2026-01-22
status: draft
purpose: "Documentation for AFL-XML-MIG Migration Inventory"
---

# AFL-XML-MIG Migration Inventory

**Version:** 1.0
**Migration Date:** 2026-01-21
**Status:** In Progress

---

## Overview

This document provides a complete inventory of all 14 XML prompts being migrated to the UV Deterministic API system. Each prompt is analyzed for its current state, target bounded context, and migration requirements.

---

## Migration Inventory Table

| # | Prompt File | Short Name | Current State | Target Bounded Context | Stateful | UV API Ready | Migration Priority |
|---|-------------|------------|---------------|------------------------|----------|--------------|-------------------|
| 1 | `yaml-backlog-manager.xml` | `yml-bck-mgr` | ✅ Compliant | Backlog State Management | Yes | Partial | P0 |
| 2 | `scope-change.xml` | `scope-change` | ✅ Compliant | Scope Adaptation | Yes | No | P1 |
| 3 | `unified-technical-implementation-plan-refiner.xml` | `unified-plan` | ✅ Compliant | Planning & Architecture | No | No | P1 |
| 4 | `ddd-make-alignment.xml` | `ddd-make-align` | ✅ Compliant | Build System Governance | Yes | No | P2 |
| 5 | `organize.xml` | `organize` | ✅ Compliant | Repository Organization | Yes | No | P2 |
| 6 | `cycle-implement.xml` | `cycle-implement` | ✅ Compliant | Execution Engine | Yes | Partial | P0 |
| 7 | `core-yaml-backlog-refresh.xml` | `yml-bck-refresh` | ✅ Compliant | Backlog State Management | Yes | Partial | P0 |
| 8 | `repeatable-make-registry.xml` | `rep-mak-reg` | ✅ Compliant | Build System Governance | Yes | Partial | P1 |
| 9 | `quality_gate.xml` | `quality-gate` | ✅ Compliant | Quality Assurance | No | Yes | P0 |
| 10 | `test-review-implementation.xml` | `tst-rvw-imp` | ✅ Compliant | Test Engineering | No | No | P1 |
| 11 | `demo-prep.xml` | `demo-prep` | ✅ Compliant | Deployment & Demo | No | No | P2 |
| 12 | `diagram.xml` | `diagram` | ✅ Compliant | Documentation & Visualization | No | No | P2 |
| 13 | `update_root_readme.xml` | `update-readme` | ✅ Compliant | Documentation Maintenance | Yes | No | P1 |
| 14 | `update_status.xml` | `update-status` | ✅ Compliant | Status Reporting | No | No | P1 |

---

## Current State Assessment

### Metadata Compliance Status

All 14 prompts have been validated against the metadata schema:

```yaml
required_metadata:
  - name: kebab-case short identifier
  - version: semver format (1.0, 1.1, 2.0)
  - stateful: boolean
  - purpose: one-line description
  - created: ISO date
```

**Compliance Summary:**
- ✅ **14/14** prompts have `<metadata>` blocks
- ✅ **14/14** prompts have `<name>` field
- ✅ **14/14** prompts have `<version>` field
- ✅ **14/14** prompts have `<stateful>` field
- ⚠️ **12/14** prompts have `<purpose>` field (2 truncated)
- ⚠️ **10/14** prompts have `<created>` field

---

## Bounded Context Classification

### Context 1: Backlog State Management
**Aggregate Root:** IMPLEMENTATION_BACKLOG.yaml

| Prompt | Role in Context | State Modifications |
|--------|-----------------|---------------------|
| `yml-bck-mgr` | Primary creator/updater | Creates/updates backlog structure |
| `yml-bck-refresh` | State synchronizer | Maintains artifact registry |
| `scope-change` | Scope adapter | Modifies backlog for new scope |

### Context 2: Execution Engine
**Aggregate Root:** Work Unit (ephemeral)

| Prompt | Role in Context | State Modifications |
|--------|-----------------|---------------------|
| `cycle-implement` | Primary executor | Modifies code, updates status |
| `quality-gate` | Validation enforcer | Reads state, enforces gates |

### Context 3: Build System Governance
**Aggregate Root:** MAKE_COMMAND_REGISTRY.yaml

| Prompt | Role in Context | State Modifications |
|--------|-----------------|---------------------|
| `rep-mak-reg` | Registry maintainer | Creates/updates registry |
| `ddd-make-align` | DDD alignment validator | Extends registry metadata |

### Context 4: Planning & Architecture
**Aggregate Root:** Implementation Plan (document)

| Prompt | Role in Context | State Modifications |
|--------|-----------------|---------------------|
| `unified-plan` | Plan consolidator | Produces consolidated plan |
| `organize` | Structure organizer | Maintains index files |

### Context 5: Quality Assurance
**Aggregate Root:** Test Plan / Validation Results

| Prompt | Role in Context | State Modifications |
|--------|-----------------|---------------------|
| `quality-gate` | Gate enforcer | Read-only validation |
| `tst-rvw-imp` | Test reviewer | Produces review findings |

### Context 6: Documentation & Deployment
**Aggregate Root:** README.md / Status Reports

| Prompt | Role in Context | State Modifications |
|--------|-----------------|---------------------|
| `update-readme` | README maintainer | Updates README.md |
| `update-status` | Status reporter | Produces status reports |
| `demo-prep` | Demo coordinator | Produces demo specs |
| `diagram` | Visualizer | Produces ASCII diagrams |

---

## UV API Integration Assessment

### Currently UV-Integrated Prompts

These prompts already have corresponding `make` targets using `uv run`:

| Prompt | Make Target(s) | UV Command |
|--------|---------------|------------|
| `quality-gate` | `validate-backlog` | `uv run scripts/validate_backlog.py` |
| `quality-gate` | `validate-governance` | `uv run scripts/validate_governance.py` |
| `rep-mak-reg` | (pending) | Needs implementation |
| `yml-bck-refresh` | `register-artifacts` | `uv run scripts/register_artifacts.py` |

### Prompts Requiring UV Integration

| Prompt | Required Make Target | Implementation Script |
|--------|---------------------|----------------------|
| `yml-bck-mgr` | `make prompt-yml-bck-mgr` | `scripts/prompts/yml_bck_mgr.py` |
| `scope-change` | `make prompt-scope-change` | `scripts/prompts/scope_change.py` |
| `unified-plan` | `make prompt-unified-plan` | `scripts/prompts/unified_plan.py` |
| `cycle-implement` | `make prompt-cycle-implement` | `scripts/prompts/cycle_implement.py` |
| `tst-rvw-imp` | `make prompt-tst-rvw-imp` | `scripts/prompts/tst_rvw_imp.py` |
| `demo-prep` | `make prompt-demo-prep` | `scripts/prompts/demo_prep.py` |
| `diagram` | `make prompt-diagram` | `scripts/prompts/diagram.py` |
| `update-readme` | `make prompt-update-readme` | `scripts/prompts/update_readme.py` |
| `update-status` | `make prompt-update-status` | `scripts/prompts/update_status.py` |
| `organize` | `make prompt-organize` | `scripts/prompts/organize.py` |
| `ddd-make-align` | `make prompt-ddd-make-align` | `scripts/prompts/ddd_make_align.py` |

---

## Migration Priority Rationale

### P0 - Critical Path (Core Workflow)
These prompts form the core execution loop and must be migrated first:

1. **`yml-bck-mgr`** - Foundation of state management
2. **`cycle-implement`** - Primary execution engine
3. **`yml-bck-refresh`** - State synchronization
4. **`quality-gate`** - Already integrated, needs enhancement

### P1 - High Value (Supporting Workflow)
These prompts support the core workflow and add significant value:

5. **`scope-change`** - Enables adaptive development
6. **`unified-plan`** - Planning consolidation
7. **`rep-mak-reg`** - Build system documentation
8. **`tst-rvw-imp`** - Test engineering
9. **`update-readme`** - Documentation currency
10. **`update-status`** - Stakeholder communication

### P2 - Enhancement (Extended Capability)
These prompts provide extended capabilities:

11. **`ddd-make-align`** - Advanced governance
12. **`organize`** - Repository hygiene
13. **`demo-prep`** - Demo preparation
14. **`diagram`** - Visualization

---

## Migration Blockers and Dependencies

### Technical Dependencies

```
yml-bck-mgr ────┬──▶ cycle-implement ──▶ quality-gate
                │
                ├──▶ yml-bck-refresh
                │
                └──▶ scope-change ──▶ unified-plan
```

### Blockers Identified

| Blocker | Affected Prompts | Mitigation |
|---------|------------------|------------|
| No script infrastructure | All pending | Create `scripts/prompts/` directory |
| No input validation | All | Add JSONSchema validation |
| No output standardization | All | Define standard output format |

---

## Next Steps

1. Create `scripts/prompts/` directory structure
2. Implement P0 prompts with UV deterministic triggers
3. Define standard input/output schemas
4. Integrate with existing `make` targets
5. Update Makefile with prompt execution targets

---

## Changelog

| Date | Version | Changes |
|------|---------|---------|
| 2026-01-21 | 1.0 | Initial migration inventory |
