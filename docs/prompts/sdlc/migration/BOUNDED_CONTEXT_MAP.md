---
title: "Bounded Context Map - UV Deterministic API Integration"
version: 1.0
date: 2026-01-22
status: active
purpose: "Documentation for Bounded Context Map - UV Deterministic API Integration"
---

# Bounded Context Map - UV Deterministic API Integration

**Version:** 1.0
**Created:** 2026-01-21
**Status:** Active

---

## Overview

This document maps all 14 SDLC prompts to their bounded contexts and defines the UV API integration points for deterministic execution.

---

## Strategic Domain Layers

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              CORE DOMAIN                                         │
│  (Highest business value, competitive advantage)                                 │
│                                                                                  │
│  ┌────────────────────────────┐    ┌────────────────────────────────────────┐   │
│  │  Backlog State Management  │    │        Execution Engine                │   │
│  │                            │    │                                        │   │
│  │  • yml-bck-mgr             │    │  • cycle-implement                     │   │
│  │  • yml-bck-refresh         │    │                                        │   │
│  │  • scope-change            │    │                                        │   │
│  │                            │    │                                        │   │
│  │  Aggregate: YAML Backlog   │    │  Aggregate: Work Unit                  │   │
│  └────────────────────────────┘    └────────────────────────────────────────┘   │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────┐
│                           SUPPORTING DOMAIN                                      │
│  (Enables core domain, important but not differentiating)                        │
│                                                                                  │
│  ┌────────────────────────────┐    ┌────────────────────────────────────────┐   │
│  │    Quality Assurance       │    │      Planning & Architecture           │   │
│  │                            │    │                                        │   │
│  │  • quality-gate            │    │  • unified-plan                        │   │
│  │  • tst-rvw-imp             │    │  • organize                            │   │
│  │                            │    │                                        │   │
│  │  Aggregate: Test Results   │    │  Aggregate: Implementation Plan        │   │
│  └────────────────────────────┘    └────────────────────────────────────────┘   │
│                                                                                  │
│  ┌────────────────────────────┐    ┌────────────────────────────────────────┐   │
│  │   Build System Governance  │    │   Documentation & Deployment           │   │
│  │                            │    │                                        │   │
│  │  • rep-mak-reg             │    │  • update-readme                       │   │
│  │  • ddd-make-align          │    │  • update-status                       │   │
│  │                            │    │  • demo-prep                           │   │
│  │  Aggregate: Make Registry  │    │  • diagram                             │   │
│  └────────────────────────────┘    │                                        │   │
│                                    │  Aggregate: Documentation              │   │
│                                    └────────────────────────────────────────┘   │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## Context Relationships & Integration Patterns

### Relationship Types

| Pattern | Description | UV API Implication |
|---------|-------------|-------------------|
| **Upstream/Downstream** | One context provides data to another | Sequential make targets |
| **Shared Kernel** | Contexts share common models | Common schema definitions |
| **Anticorruption Layer** | Translation between contexts | Adapter scripts |
| **Conformist** | One context adopts another's model | Direct data passing |

---

## Context 1: Backlog State Management

**Domain Type:** Core
**Aggregate Root:** `IMPLEMENTATION_BACKLOG.yaml`
**Bounded Responsibilities:**
- Story creation and prioritization
- Dependency mapping
- Status tracking
- Artifact registration

### Prompts in Context

| Prompt | UV Make Target | Input Schema | Output Schema |
|--------|---------------|--------------|---------------|
| `yml-bck-mgr` | `make uv-yml-bck-mgr` | Source documents | Updated YAML |
| `yml-bck-refresh` | `make uv-yml-bck-refresh` | Current YAML + artifacts | Updated YAML |
| `scope-change` | `make uv-scope-change` | Scope definition + YAML | Updated YAML + plan |

### UV API Integration Points

```yaml
# Context: Backlog State Management
uv_api:
  context_id: backlog-state

  endpoints:
    - name: initialize-backlog
      make_target: uv-yml-bck-mgr
      trigger: make uv-yml-bck-mgr SOURCE_DOCS="path/to/docs"
      deterministic: true
      idempotent: true

    - name: refresh-backlog
      make_target: uv-yml-bck-refresh
      trigger: make uv-yml-bck-refresh
      deterministic: true
      idempotent: true

    - name: adapt-scope
      make_target: uv-scope-change
      trigger: make uv-scope-change SCOPE="new_scope.yaml"
      deterministic: true
      idempotent: false  # Creates new state

  shared_state:
    - path: IMPLEMENTATION_BACKLOG.yaml
      access: read-write
    - path: schema/implementation_backlog_schema.json
      access: read-only

  downstream_consumers:
    - context: execution-engine
      data: story queue, acceptance criteria
    - context: quality-assurance
      data: validation rules, test cases
```

### Context Map Visualization

```
                        ┌─────────────────────────────┐
                        │   Backlog State Management  │
                        │                             │
    SOURCE DOCS ───────▶│  yml-bck-mgr                │
                        │       │                     │
                        │       ▼                     │
    ARTIFACTS ─────────▶│  yml-bck-refresh            │──────▶ YAML Backlog
                        │       │                     │
                        │       ▼                     │
    SCOPE CHANGES ─────▶│  scope-change               │
                        │                             │
                        └─────────────────────────────┘
                                     │
                    ┌────────────────┼────────────────┐
                    ▼                ▼                ▼
            ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
            │  Execution   │  │   Quality    │  │   Planning   │
            │   Engine     │  │  Assurance   │  │              │
            └──────────────┘  └──────────────┘  └──────────────┘
```

---

## Context 2: Execution Engine

**Domain Type:** Core
**Aggregate Root:** Work Unit (ephemeral during execution)
**Bounded Responsibilities:**
- Work item selection
- Execution planning
- Implementation
- Validation against acceptance criteria

### Prompts in Context

| Prompt | UV Make Target | Input Schema | Output Schema |
|--------|---------------|--------------|---------------|
| `cycle-implement` | `make uv-cycle-implement` | YAML Backlog + context | Code changes + status |

### UV API Integration Points

```yaml
# Context: Execution Engine
uv_api:
  context_id: execution-engine

  endpoints:
    - name: execute-next-work-item
      make_target: uv-cycle-implement
      trigger: make uv-cycle-implement
      deterministic: false  # Creates new artifacts
      idempotent: false

  upstream_dependencies:
    - context: backlog-state
      data: next work item, acceptance criteria

  downstream_consumers:
    - context: quality-assurance
      data: completed work, validation results
```

### Context Map Visualization

```
    ┌─────────────────────────────┐
    │   Backlog State Management  │
    │                             │
    │   [YAML Backlog]            │
    └──────────────┬──────────────┘
                   │
                   │ Story Queue
                   ▼
    ┌─────────────────────────────┐
    │      Execution Engine       │
    │                             │
    │  cycle-implement            │───────▶ Code Changes
    │       │                     │───────▶ Status Updates
    │       ▼                     │
    │  [Work Unit]                │
    └──────────────┬──────────────┘
                   │
                   │ Completed Work
                   ▼
    ┌─────────────────────────────┐
    │     Quality Assurance       │
    └─────────────────────────────┘
```

---

## Context 3: Quality Assurance

**Domain Type:** Supporting
**Aggregate Root:** Validation Results
**Bounded Responsibilities:**
- Test execution validation
- Documentation verification
- Gate enforcement
- Test plan review

### Prompts in Context

| Prompt | UV Make Target | Input Schema | Output Schema |
|--------|---------------|--------------|---------------|
| `quality-gate` | `make uv-quality-gate` | Completed work + tests | Pass/Fail + checklist |
| `tst-rvw-imp` | `make uv-tst-rvw-imp` | Test plan | Review findings |

### UV API Integration Points

```yaml
# Context: Quality Assurance
uv_api:
  context_id: quality-assurance

  endpoints:
    - name: validate-gate
      make_target: uv-quality-gate
      trigger: make uv-quality-gate
      deterministic: true
      idempotent: true

    - name: review-tests
      make_target: uv-tst-rvw-imp
      trigger: make uv-tst-rvw-imp TEST_PLAN="path/to/plan.yaml"
      deterministic: true
      idempotent: true

  upstream_dependencies:
    - context: execution-engine
      data: completed artifacts
    - context: backlog-state
      data: acceptance criteria
```

---

## Context 4: Planning & Architecture

**Domain Type:** Supporting
**Aggregate Root:** Implementation Plan
**Bounded Responsibilities:**
- Plan consolidation
- Project organization
- Index maintenance

### Prompts in Context

| Prompt | UV Make Target | Input Schema | Output Schema |
|--------|---------------|--------------|---------------|
| `unified-plan` | `make uv-unified-plan` | Planning artifacts | Consolidated plan |
| `organize` | `make uv-organize` | Repository state | Updated indexes |

### UV API Integration Points

```yaml
# Context: Planning & Architecture
uv_api:
  context_id: planning-architecture

  endpoints:
    - name: consolidate-plan
      make_target: uv-unified-plan
      trigger: make uv-unified-plan
      deterministic: true
      idempotent: true

    - name: organize-repo
      make_target: uv-organize
      trigger: make uv-organize
      deterministic: true
      idempotent: true

  upstream_dependencies:
    - context: backlog-state
      data: story structure
```

---

## Context 5: Build System Governance

**Domain Type:** Supporting
**Aggregate Root:** `MAKE_COMMAND_REGISTRY.yaml`
**Bounded Responsibilities:**
- Make command discovery
- Registry maintenance
- DDD alignment validation

### Prompts in Context

| Prompt | UV Make Target | Input Schema | Output Schema |
|--------|---------------|--------------|---------------|
| `rep-mak-reg` | `make uv-rep-mak-reg` | Makefiles | Registry YAML |
| `ddd-make-align` | `make uv-ddd-make-align` | Registry + contexts | Alignment report |

### UV API Integration Points

```yaml
# Context: Build System Governance
uv_api:
  context_id: build-governance

  endpoints:
    - name: update-registry
      make_target: uv-rep-mak-reg
      trigger: make uv-rep-mak-reg
      deterministic: true
      idempotent: true

    - name: validate-alignment
      make_target: uv-ddd-make-align
      trigger: make uv-ddd-make-align
      deterministic: true
      idempotent: true
```

---

## Context 6: Documentation & Deployment

**Domain Type:** Supporting
**Aggregate Root:** Documentation artifacts
**Bounded Responsibilities:**
- README maintenance
- Status reporting
- Demo preparation
- Diagram generation

### Prompts in Context

| Prompt | UV Make Target | Input Schema | Output Schema |
|--------|---------------|--------------|---------------|
| `update-readme` | `make uv-update-readme` | Status + history | Updated README |
| `update-status` | `make uv-update-status` | Progress data | Status report |
| `demo-prep` | `make uv-demo-prep` | Demo requirements | Demo spec |
| `diagram` | `make uv-diagram` | Target folder | ASCII diagrams |

### UV API Integration Points

```yaml
# Context: Documentation & Deployment
uv_api:
  context_id: doc-deployment

  endpoints:
    - name: update-readme
      make_target: uv-update-readme
      trigger: make uv-update-readme
      deterministic: false  # Reads git history
      idempotent: true

    - name: generate-status
      make_target: uv-update-status
      trigger: make uv-update-status
      deterministic: true
      idempotent: true

    - name: prepare-demo
      make_target: uv-demo-prep
      trigger: make uv-demo-prep SPEC="path/to/spec.yaml"
      deterministic: true
      idempotent: true

    - name: generate-diagrams
      make_target: uv-diagram
      trigger: make uv-diagram TARGET="path/to/folder"
      deterministic: true
      idempotent: true
```

---

## Full System Context Map

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                               UV DETERMINISTIC API SYSTEM                                │
└─────────────────────────────────────────────────────────────────────────────────────────┘

                              ┌───────────────────────┐
                              │   External Triggers   │
                              │   (User / CI / Hook)  │
                              └───────────┬───────────┘
                                          │
                                    make uv-*
                                          │
                                          ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                    MAKEFILE                                              │
│                           (UV Deterministic Entry Points)                                │
└────────────┬──────────────────────────────────────────────────────────────┬─────────────┘
             │                                                              │
             ▼                                                              ▼
┌────────────────────────┐                                    ┌────────────────────────┐
│  CORE DOMAIN           │                                    │  SUPPORTING DOMAIN     │
│                        │                                    │                        │
│  ┌──────────────────┐  │                                    │  ┌──────────────────┐  │
│  │ Backlog State    │──┼────────────────────────────────────┼─▶│ Quality          │  │
│  │ • yml-bck-mgr    │  │                                    │  │ Assurance        │  │
│  │ • yml-bck-refresh│  │                                    │  │ • quality-gate   │  │
│  │ • scope-change   │  │                                    │  │ • tst-rvw-imp    │  │
│  └────────┬─────────┘  │                                    │  └──────────────────┘  │
│           │            │                                    │                        │
│           ▼            │                                    │  ┌──────────────────┐  │
│  ┌──────────────────┐  │                                    │  │ Planning &       │  │
│  │ Execution Engine │──┼────────────────────────────────────┼─▶│ Architecture     │  │
│  │ • cycle-implement│  │                                    │  │ • unified-plan   │  │
│  └──────────────────┘  │                                    │  │ • organize       │  │
│                        │                                    │  └──────────────────┘  │
└────────────────────────┘                                    │                        │
                                                              │  ┌──────────────────┐  │
                                                              │  │ Build Governance │  │
                                                              │  │ • rep-mak-reg    │  │
                                                              │  │ • ddd-make-align │  │
                                                              │  └──────────────────┘  │
                                                              │                        │
                                                              │  ┌──────────────────┐  │
                                                              │  │ Doc & Deployment │  │
                                                              │  │ • update-readme  │  │
                                                              │  │ • update-status  │  │
                                                              │  │ • demo-prep      │  │
                                                              │  │ • diagram        │  │
                                                              │  └──────────────────┘  │
                                                              │                        │
                                                              └────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                  SHARED STATE                                            │
│                                                                                          │
│  ┌───────────────────────────┐  ┌───────────────────────────┐  ┌──────────────────────┐ │
│  │ IMPLEMENTATION_BACKLOG    │  │ MAKE_COMMAND_REGISTRY     │  │ README.md            │ │
│  │ .yaml                     │  │ .yaml                     │  │ Status Reports       │ │
│  │                           │  │                           │  │ Implementation Plans │ │
│  └───────────────────────────┘  └───────────────────────────┘  └──────────────────────┘ │
│                                                                                          │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Determinism Guarantees

### Deterministic Prompts (Same Input → Same Output)

| Prompt | Determinism Level | Verification Method |
|--------|------------------|---------------------|
| `yml-bck-mgr` | **High** | Checksum of output YAML |
| `yml-bck-refresh` | **High** | Checksum of output YAML |
| `quality-gate` | **High** | Exit code + checklist hash |
| `rep-mak-reg` | **High** | Checksum of registry YAML |
| `ddd-make-align` | **High** | Alignment report hash |
| `unified-plan` | **High** | Plan document hash |
| `organize` | **High** | Index file checksums |
| `tst-rvw-imp` | **High** | Review findings hash |
| `update-status` | **High** | Status report hash |
| `demo-prep` | **High** | Demo spec hash |
| `diagram` | **High** | Diagram content hash |

### Non-Deterministic Prompts (Context-Dependent Output)

| Prompt | Variability Source | Mitigation |
|--------|-------------------|------------|
| `cycle-implement` | Creates new code | Log all outputs |
| `scope-change` | Adapts to new scope | Snapshot before/after |
| `update-readme` | Reads git history | Pin git SHA |

---

## Changelog

| Date | Version | Changes |
|------|---------|---------|
| 2026-01-21 | 1.0 | Initial bounded context map |
