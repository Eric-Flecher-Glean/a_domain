---
title: "SDLC Prompt System - Domain Index"
version: 1.0
date: 2026-01-22
status: draft
purpose: "Documentation for SDLC Prompt System - Domain Index"
---

# SDLC Prompt System - Domain Index

**Version**: 1.0
**Created**: 2026-01-21
**Total Prompts**: 21 (14 existing + 7 new Artifact Intelligence)
**Total Domains**: 7 SDLC subdomains
**Total Bounded Contexts**: 8

---

## Domain Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         SDLC PROMPT SYSTEM ARCHITECTURE                          │
│                                                                                  │
│  ┌────────────────────────────────────────────────────────────────────────────┐ │
│  │                           CORE DOMAIN LAYER                                 │ │
│  │  ┌──────────────────────────┐  ┌──────────────────────────┐               │ │
│  │  │  BACKLOG STATE MGMT      │  │  EXECUTION ORCHESTRATION │               │ │
│  │  │  • yml-bck-mgr           │  │  • cycle-implement       │               │ │
│  │  │  • yml-bck-refresh       │  │  • scope-change          │               │ │
│  │  └──────────────────────────┘  └──────────────────────────┘               │ │
│  └────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                  │
│  ┌────────────────────────────────────────────────────────────────────────────┐ │
│  │                        SUPPORTING DOMAIN LAYER                              │ │
│  │  ┌──────────────────────────┐  ┌──────────────────────────┐               │ │
│  │  │  ARCHITECTURE GOVERNANCE │  │  QUALITY ASSURANCE       │               │ │
│  │  │  • unified-plan          │  │  • quality-gate          │               │ │
│  │  │  • ddd-make-align        │  │  • tst-rvw-imp           │               │ │
│  │  │  • organize              │  │  └──────────────────────┘               │ │
│  │  │  • rep-mak-reg           │                                             │ │
│  │  └──────────────────────────┘                                             │ │
│  │                                                                            │ │
│  │  ┌──────────────────────────┐                                             │ │
│  │  │  PLANNING & DOCUMENTATION│                                             │ │
│  │  │  • unified-plan          │                                             │ │
│  │  │  • organize              │                                             │ │
│  │  └──────────────────────────┘                                             │ │
│  └────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                  │
│  ┌────────────────────────────────────────────────────────────────────────────┐ │
│  │                        GENERIC SUBDOMAIN LAYER                              │ │
│  │  ┌──────────────────────────┐  ┌──────────────────────────┐               │ │
│  │  │  DOCUMENTATION MGMT      │  │  VISUALIZATION & REPORT  │               │ │
│  │  │  • update-readme         │  │  • demo-prep             │               │ │
│  │  │  • update-status         │  │  • diagram               │               │ │
│  │  └──────────────────────────┘  └──────────────────────────┘               │ │
│  └────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                  │
│  ┌────────────────────────────────────────────────────────────────────────────┐ │
│  │                    NEW: ARTIFACT INTELLIGENCE DOMAIN                        │ │
│  │  ┌──────────────────────────────────────────────────────────────────────┐ │ │
│  │  │                      ARTIFACT INTELLIGENCE                            │ │ │
│  │  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐    │ │ │
│  │  │  │ artifact-   │→│ artifact-   │→│ artifact-   │→│ question-   │    │ │ │
│  │  │  │   search    │ │  process    │ │   refine    │ │  maintain   │    │ │ │
│  │  │  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘    │ │ │
│  │  │         │                                              ↓             │ │ │
│  │  │         │         ┌─────────────┐ ┌─────────────┐      │             │ │ │
│  │  │         │         │ feedback-   │←│ story-      │←─────┘             │ │ │
│  │  │         │         │ incorporate │ │  refine     │                    │ │ │
│  │  │         │         └─────────────┘ └─────────────┘                    │ │ │
│  │  │         │               ↓                                            │ │ │
│  │  │         │         ┌─────────────┐                                    │ │ │
│  │  │         └────────→│ backlog-    │→ IMPLEMENTATION_BACKLOG.yaml       │ │ │
│  │  │                   │ prioritize  │                                    │ │ │
│  │  │                   └─────────────┘                                    │ │ │
│  │  └──────────────────────────────────────────────────────────────────────┘ │ │
│  └────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## Complete Prompt Catalog

### 1. Requirements Domain

| Prompt ID | Name | UV Make Target | Bounded Context | Status |
|-----------|------|----------------|-----------------|--------|
| yml-bck-mgr | YAML Backlog Manager | `make backlog-init` | Backlog State Mgmt | Active |
| scope-change | Scope Change Handler | `make scope-update` | Execution Orchestration | Active |

### 2. Planning Domain

| Prompt ID | Name | UV Make Target | Bounded Context | Status |
|-----------|------|----------------|-----------------|--------|
| unified-plan | Unified Planning | `make plan-unify` | Architecture Governance | Active |
| ddd-make-align | DDD Alignment | `make ddd-align` | Architecture Governance | Active |
| organize | Project Organizer | `make project-organize` | Architecture Governance | Active |

### 3. Implementation Domain

| Prompt ID | Name | UV Make Target | Bounded Context | Status |
|-----------|------|----------------|-----------------|--------|
| cycle-implement | Cycle Implementation | `make cycle-next` | Execution Orchestration | Active |
| yml-bck-refresh | Backlog Refresh | `make backlog-refresh` | Backlog State Mgmt | Active |
| rep-mak-reg | Make Registry | `make registry-update` | Architecture Governance | Active |

### 4. Testing Domain

| Prompt ID | Name | UV Make Target | Bounded Context | Status |
|-----------|------|----------------|-----------------|--------|
| quality-gate | Quality Gate | `make quality-gate` | Quality Assurance | Active |
| tst-rvw-imp | Test Review | `make test-review` | Quality Assurance | Active |

### 5. Deployment Domain

| Prompt ID | Name | UV Make Target | Bounded Context | Status |
|-----------|------|----------------|-----------------|--------|
| demo-prep | Demo Preparation | `make demo-generate` | Visualization & Reporting | Active |
| diagram | Diagram Generator | `make diagram-generate` | Visualization & Reporting | Active |

### 6. Maintenance Domain

| Prompt ID | Name | UV Make Target | Bounded Context | Status |
|-----------|------|----------------|-----------------|--------|
| update-readme | README Updater | `make readme-update` | Documentation Mgmt | Active |
| update-status | Status Updater | `make status-report` | Documentation Mgmt | Active |

### 7. Artifact Intelligence Domain (NEW)

| Prompt ID | Name | UV Make Target | Bounded Context | Status |
|-----------|------|----------------|-----------------|--------|
| artifact-search | Artifact Search | `make artifact-search` | Artifact Intelligence | **NEW** |
| artifact-process | Artifact Process | `make artifact-process` | Artifact Intelligence | **NEW** |
| artifact-refine | Artifact Refine | `make artifact-refine` | Artifact Intelligence | **NEW** |
| question-maintain | Question Maintain | `make question-maintain` | Artifact Intelligence | **NEW** |
| feedback-incorporate | Feedback Incorporate | `make feedback-incorporate` | Artifact Intelligence | **NEW** |
| story-refine | Story Refine | `make story-refine` | Artifact Intelligence | **NEW** |
| backlog-prioritize | Backlog Prioritize | `make backlog-prioritize` | Artifact Intelligence | **NEW** |

---

## Bounded Context Map

### Core Domain Layer (Strategic - High Business Value)

#### 1. Backlog State Management Context
**Strategic Importance**: Core - Single source of truth for work items

| Attribute | Value |
|-----------|-------|
| **Prompts** | yml-bck-mgr, yml-bck-refresh |
| **State File** | IMPLEMENTATION_BACKLOG.yaml |
| **Integration Pattern** | Published Language (YAML schema) |
| **Upstream** | Planning & Documentation, Artifact Intelligence |
| **Downstream** | Execution Orchestration |

#### 2. Execution Orchestration Context
**Strategic Importance**: Core - Drives actual implementation work

| Attribute | Value |
|-----------|-------|
| **Prompts** | cycle-implement, scope-change |
| **State File** | Current cycle state |
| **Integration Pattern** | Conformist (follows backlog) |
| **Upstream** | Backlog State Management |
| **Downstream** | Quality Assurance |

### Supporting Domain Layer (Differentiating Capabilities)

#### 3. Architecture Governance Context
**Strategic Importance**: Supporting - Ensures consistency

| Attribute | Value |
|-----------|-------|
| **Prompts** | unified-plan, ddd-make-align, organize, rep-mak-reg |
| **State Files** | MAKE_COMMAND_REGISTRY.yaml, DDD alignment reports |
| **Integration Pattern** | Anti-Corruption Layer |
| **Relationship** | Cross-cutting governance for all contexts |

#### 4. Quality Assurance Context
**Strategic Importance**: Supporting - Ensures delivery quality

| Attribute | Value |
|-----------|-------|
| **Prompts** | quality-gate, tst-rvw-imp |
| **Integration Pattern** | Customer-Supplier |
| **Upstream** | Execution Orchestration |
| **Downstream** | Documentation Management |

#### 5. Planning & Documentation Context
**Strategic Importance**: Supporting - Maintains project coherence

| Attribute | Value |
|-----------|-------|
| **Prompts** | unified-plan, organize |
| **Integration Pattern** | Partnership |
| **Relationship** | Bidirectional with Backlog State Management |

### Generic Subdomain Layer (Commodity Capabilities)

#### 6. Documentation Management Context
**Strategic Importance**: Generic - Standard documentation updates

| Attribute | Value |
|-----------|-------|
| **Prompts** | update-readme, update-status |
| **Integration Pattern** | Separate Ways (independent) |
| **Upstream** | Quality Assurance |
| **Downstream** | Backlog State Management (feedback loop) |

#### 7. Visualization & Reporting Context
**Strategic Importance**: Generic - Visual outputs and demos

| Attribute | Value |
|-----------|-------|
| **Prompts** | demo-prep, diagram |
| **Integration Pattern** | Separate Ways (independent) |
| **Upstream** | Quality Assurance, Documentation Management |

### NEW: Artifact Intelligence Context

#### 8. Artifact Intelligence Context
**Strategic Importance**: Core - Automated requirements discovery

| Attribute | Value |
|-----------|-------|
| **Prompts** | artifact-search, artifact-process, artifact-refine, question-maintain, feedback-incorporate, story-refine, backlog-prioritize |
| **State Files** | artifacts/*.yaml |
| **Integration Pattern** | Open Host Service (Glean MCP) |
| **External Systems** | Glean Knowledge Graph via MCP |
| **Downstream** | Backlog State Management |

---

## Workflow Patterns

### Pattern 1: Artifact-to-Backlog Pipeline

```
artifact-search → artifact-process → artifact-refine → story-refine → backlog-prioritize → yml-bck-mgr
                         ↓                    ↑
                  question-maintain → feedback-incorporate
```

**Use Case**: Transform PRDs and design docs into prioritized backlog items

### Pattern 2: Implementation Cycle

```
yml-bck-mgr → cycle-implement → quality-gate → update-status
     ↑              ↓                ↓
     └──────────────┴────────────────┘
```

**Use Case**: Execute implementation work with quality validation

### Pattern 3: Governance Loop

```
ddd-make-align → rep-mak-reg → organize → unified-plan
       ↑                                        │
       └────────────────────────────────────────┘
```

**Use Case**: Maintain architectural consistency and documentation

---

## UV Quick Reference

### Artifact Intelligence Commands

```bash
# Search for PRDs from the last month
make artifact-search ARTIFACT_TYPE=prd OWNER=me DATE_RANGE=past_month

# Process discovered artifacts
make artifact-process

# Refine with conflict detection
make artifact-refine CONFLICT_RESOLUTION=flag

# List open questions
make question-maintain ACTION=list

# Answer a question
make question-maintain ACTION=answer QUESTION_ID=Q-001 ANSWER="200ms p95"

# Create stories
make story-refine

# Prioritize and add to backlog
make backlog-prioritize ALGORITHM=wsjf DRY_RUN=true
```

### Core SDLC Commands

```bash
# Start implementation cycle
make cycle-next

# Run quality gate
make quality-gate

# Update status
make status-report

# Validate governance
make validate-governance
```

---

## Integration Points

### Glean MCP Integration

The Artifact Intelligence domain uses Glean MCP tools:

| Tool | Used By | Purpose |
|------|---------|---------|
| `mcp__glean_default__search` | artifact-search | Document discovery |
| `mcp__glean_default__read_document` | artifact-process | Content extraction |
| `mcp__glean_default__chat` | artifact-refine | AI synthesis |
| `mcp__glean_default__user_activity` | artifact-search | Activity-based discovery |

### File System Integration

| File | Purpose | Updated By |
|------|---------|------------|
| `IMPLEMENTATION_BACKLOG.yaml` | Work item tracking | yml-bck-mgr, backlog-prioritize |
| `MAKE_COMMAND_REGISTRY.yaml` | Make command catalog | rep-mak-reg |
| `artifacts/discovered_index.yaml` | Artifact catalog | artifact-search |
| `artifacts/extracted_requirements.yaml` | Requirements | artifact-process |
| `artifacts/open_questions.yaml` | Question tracking | question-maintain |
| `artifacts/draft_stories.yaml` | Story drafts | story-refine |

---

## Schema Validation

All XML prompts must validate against:
- **Schema**: `schema/aflac-prompt-schema.xsd`
- **Validation Command**: `make validate-schema`

Required metadata fields:
- `name` (kebab-case)
- `version` (semver)
- `sdlc_domain` (enum)
- `bounded_context` (enum)
- `stateful` (boolean)
- `purpose` (string)
- `created` (date)

---

## Related Documentation

- [Claude Orchestration Architecture](../architecture/CLAUDE_ORCHESTRATION_ARCHITECTURE.md)
- [XSD Schema](../../schema/aflac-prompt-schema.xsd)
- [Bounded Context Map](../architecture/BOUNDED_CONTEXT_MAP.md)
- [Make Command Registry](../../MAKE_COMMAND_REGISTRY.yaml)

---

*Document Version: 1.0 | Last Updated: 2026-01-21*
