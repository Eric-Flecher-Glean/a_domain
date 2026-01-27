---
title: "AFL XML Migration Specification"
version: 1.0
date: 2026-01-22
status: active
purpose: "Documentation for AFL XML Migration Specification"
---

# AFL XML Migration Specification

**Version:** 1.0
**Created:** 2026-01-21
**Status:** Active
**Purpose:** Migrate SDLC XML prompts to Aflac system with UV deterministic API triggers

---

## Overview

This document provides the complete migration specification for transitioning 14 SDLC XML prompts to a standardized Aflac (Agent-Friendly Layered Automation Context) system with UV (Unified Versioned) deterministic API integration.

### Migration Goals

1. **Standardize XML Schema** - Ensure all prompts follow consistent metadata and structure
2. **UV API Integration** - Add deterministic `make` command triggers for automation
3. **Bounded Context Mapping** - Align prompts with DDD bounded contexts
4. **Idempotency Guarantees** - Ensure all stateful operations are safely repeatable
5. **Traceability** - Link prompts to IMPLEMENTATION_BACKLOG.yaml stories

---

## 1. Migration Inventory

### Complete Prompt Inventory (14 Prompts)

| # | Prompt File | Short Name | SDLC Domain | Stateful | Current Version | Migration Status | UV Target |
|---|------------|------------|-------------|----------|-----------------|------------------|-----------|
| 1 | `yaml-backlog-manager.xml` | `yml-bck-mgr` | Requirements | Yes | 1.0 | Ready | `make backlog-init` |
| 2 | `scope-change.xml` | `scope-change` | Requirements | Yes | 1.0 | Ready | `make scope-update` |
| 3 | `unified-technical-implementation-plan-refiner.xml` | `unified-plan` | Planning | No | 1.0 | Ready | `make plan-unify` |
| 4 | `ddd-make-alignment.xml` | `ddd-make-align` | Planning | Yes | 1.0 | Ready | `make ddd-align` |
| 5 | `organize.xml` | `organize` | Planning | Yes | 1.0 | Ready | `make project-organize` |
| 6 | `cycle-implement.xml` | `cycle-implement` | Implementation | Yes | 1.0 | Ready | `make cycle-next` |
| 7 | `core-yaml-backlog-refresh.xml` | `yml-bck-refresh` | Implementation | Yes | 1.0 | Ready | `make backlog-refresh` |
| 8 | `repeatable-make-registry.xml` | `rep-mak-reg` | Implementation | Yes | 1.0 | Ready | `make registry-update` |
| 9 | `quality_gate.xml` | `quality-gate` | Testing | No | 1.0 | Ready | `make quality-gate` |
| 10 | `test-review-implementation.xml` | `tst-rvw-imp` | Testing | No | 1.0 | Ready | `make test-review` |
| 11 | `demo-prep.xml` | `demo-prep` | Deployment | No | 1.0 | Ready | `make demo-generate` |
| 12 | `diagram.xml` | `diagram` | Deployment | No | 1.0 | Ready | `make diagram-generate` |
| 13 | `update_root_readme.xml` | `update-readme` | Maintenance | Yes | 1.0 | Ready | `make readme-update` |
| 14 | `update_status.xml` | `update-status` | Maintenance | No | 1.0 | Ready | `make status-report` |

### Metadata Compliance Status

| Prompt | Has Metadata | Has Version | Has Stateful | Has Purpose | Has Created | Compliance |
|--------|--------------|-------------|--------------|-------------|-------------|------------|
| yml-bck-mgr | ✅ | ✅ | ✅ | ✅ | ✅ | 100% |
| scope-change | ✅ | ✅ | ✅ | ❌ | ❌ | 60% |
| unified-plan | ✅ | ✅ | ✅ | ❌ | ❌ | 60% |
| ddd-make-align | ✅ | ✅ | ✅ | ❌ | ❌ | 60% |
| organize | ✅ | ✅ | ✅ | ❌ | ❌ | 60% |
| cycle-implement | ✅ | ✅ | ✅ | ✅ | ✅ | 100% |
| yml-bck-refresh | ✅ | ✅ | ✅ | ❌ | ❌ | 60% |
| rep-mak-reg | ✅ | ✅ | ✅ | ❌ | ❌ | 60% |
| quality-gate | ✅ | ✅ | ✅ | ✅ | ✅ | 100% |
| tst-rvw-imp | ✅ | ✅ | ✅ | ❌ | ❌ | 60% |
| demo-prep | ✅ | ✅ | ✅ | ✅ | ✅ | 100% |
| diagram | ✅ | ✅ | ✅ | ❌ | ❌ | 60% |
| update-readme | ✅ | ✅ | ✅ | ❌ | ❌ | 60% |
| update-status | ✅ | ✅ | ✅ | ❌ | ❌ | 60% |

**Average Compliance: 68%** (10/14 prompts need metadata completion)

---

## 2. Bounded Context Map

### Context Boundaries

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        SDLC PROMPT BOUNDED CONTEXT MAP                           │
└─────────────────────────────────────────────────────────────────────────────────┘

  ╔═══════════════════════════════════════════════════════════════════════════════╗
  ║                         CORE DOMAIN LAYER                                      ║
  ║                    (Differentiating Capabilities)                              ║
  ╚═══════════════════════════════════════════════════════════════════════════════╝

  ┌──────────────────────────────┐    ┌──────────────────────────────┐
  │  BACKLOG STATE MANAGEMENT    │    │  EXECUTION ORCHESTRATION     │
  │                              │    │                              │
  │  Prompts:                    │    │  Prompts:                    │
  │  • yml-bck-mgr              │◀──▶│  • cycle-implement           │
  │  • yml-bck-refresh          │    │                              │
  │  • scope-change             │    │  UV Targets:                 │
  │                              │    │  • make cycle-next           │
  │  UV Targets:                 │    │                              │
  │  • make backlog-init         │    │  Entities:                   │
  │  • make backlog-refresh      │    │  • WorkItem                  │
  │  • make scope-update         │    │  • ExecutionPlan             │
  │                              │    │  • AcceptanceCriteria        │
  │  Entities:                   │    │                              │
  │  • Story                     │    │  Strategic Layer: CORE       │
  │  • Artifact                  │    └──────────────────────────────┘
  │  • Dependency                │              │
  │                              │              │
  │  Strategic Layer: CORE       │              │
  └──────────────────────────────┘              │
              │                                  │
              ▼                                  ▼
  ╔═══════════════════════════════════════════════════════════════════════════════╗
  ║                       SUPPORTING DOMAIN LAYER                                  ║
  ║                    (Enables Core But Not Differentiating)                      ║
  ╚═══════════════════════════════════════════════════════════════════════════════╝

  ┌──────────────────────────────┐    ┌──────────────────────────────┐
  │  ARCHITECTURE GOVERNANCE     │    │  QUALITY ASSURANCE           │
  │                              │    │                              │
  │  Prompts:                    │    │  Prompts:                    │
  │  • ddd-make-align           │    │  • quality-gate              │
  │  • rep-mak-reg              │    │  • tst-rvw-imp               │
  │  • organize                 │    │                              │
  │  • unified-plan             │    │  UV Targets:                 │
  │                              │    │  • make quality-gate         │
  │  UV Targets:                 │    │  • make test-review          │
  │  • make ddd-align            │    │                              │
  │  • make registry-update      │    │  Entities:                   │
  │  • make project-organize     │    │  • TestPlan                  │
  │  • make plan-unify           │    │  • ValidationRule            │
  │                              │    │  • QualityMetric             │
  │  Entities:                   │    │                              │
  │  • BoundedContext            │    │  Strategic Layer: SUPPORTING │
  │  • MakeCommand               │    └──────────────────────────────┘
  │  • ImplementationPlan        │              │
  │                              │              │
  │  Strategic Layer: SUPPORTING │              │
  └──────────────────────────────┘              │
              │                                  │
              ▼                                  ▼
  ╔═══════════════════════════════════════════════════════════════════════════════╗
  ║                        GENERIC SUBDOMAIN LAYER                                 ║
  ║                    (Common Utilities, No Domain Specificity)                   ║
  ╚═══════════════════════════════════════════════════════════════════════════════╝

  ┌──────────────────────────────┐    ┌──────────────────────────────┐
  │  DOCUMENTATION MANAGEMENT    │    │  VISUALIZATION & REPORTING   │
  │                              │    │                              │
  │  Prompts:                    │    │  Prompts:                    │
  │  • update-readme            │    │  • demo-prep                 │
  │  • update-status            │    │  • diagram                   │
  │                              │    │                              │
  │  UV Targets:                 │    │  UV Targets:                 │
  │  • make readme-update        │    │  • make demo-generate        │
  │  • make status-report        │    │  • make diagram-generate     │
  │                              │    │                              │
  │  Entities:                   │    │  Entities:                   │
  │  • README                    │    │  • Demo                      │
  │  • StatusReport              │    │  • Diagram                   │
  │  • LearningStory             │    │  • ValueNarrative            │
  │                              │    │                              │
  │  Strategic Layer: GENERIC    │    │  Strategic Layer: GENERIC    │
  └──────────────────────────────┘    └──────────────────────────────┘
```

### Context Dependencies Matrix

| Producer Context | Consumer Context | Integration Pattern | Data Flow |
|-----------------|------------------|---------------------|-----------|
| Backlog State | Execution Orchestration | Published Language | Story → WorkItem |
| Backlog State | Quality Assurance | Shared Kernel | Story.status → TestPlan |
| Execution Orchestration | Quality Assurance | Upstream/Downstream | WorkOutput → Validation |
| Quality Assurance | Documentation | Conformist | QualityReport → README |
| Architecture Governance | Backlog State | Partner | MakeCommand → Story.tasks |
| Visualization | Documentation | Open Host | Demo → README.demos |

### Strategic Domain Distribution

| Strategic Layer | Context Count | Prompt Count | Expected Coverage |
|----------------|---------------|--------------|-------------------|
| CORE | 2 | 4 | 30% |
| SUPPORTING | 2 | 6 | 40% |
| GENERIC | 2 | 4 | 30% |
| **TOTAL** | **6** | **14** | **100%** |

---

## 3. Refactored XML Prompts with UV Annotations

### Standard AFL XML Schema

All prompts must conform to this enhanced schema with UV integration:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<prompt xmlns="urn:aflac:prompt:v1">
  <metadata>
    <name>kebab-case-name</name>
    <version>1.0</version>
    <stateful>true|false</stateful>
    <purpose>One-line description</purpose>
    <created>YYYY-MM-DD</created>
    <sdlc_domain>requirements|planning|implementation|testing|deployment|maintenance</sdlc_domain>
    <bounded_context>context-name</bounded_context>
    <strategic_layer>CORE|SUPPORTING|GENERIC</strategic_layer>
  </metadata>

  <uv_integration>
    <primary_trigger>make target-name</primary_trigger>
    <parameters>
      <param name="param_name" type="string|boolean|path" required="true|false">
        <description>Parameter description</description>
        <default>default_value</default>
      </param>
    </parameters>
    <idempotency>
      <guarantee>true|false</guarantee>
      <state_artifact>path/to/state.yaml</state_artifact>
      <version_field>metadata.version</version_field>
    </idempotency>
    <determinism>
      <exit_codes>
        <code value="0">Success</code>
        <code value="1">Validation failure</code>
        <code value="2">State conflict</code>
      </exit_codes>
      <output_format>yaml|json|markdown</output_format>
    </determinism>
  </uv_integration>

  <role>...</role>
  <primary_goal>...</primary_goal>
  <context>...</context>
  <instructions>...</instructions>
  <constraints>...</constraints>
  <steps>...</steps>
  <validation_rules>...</validation_rules>
  <output_format>...</output_format>
  <reasoning>...</reasoning>
</prompt>
```

### Refactored Prompt Examples

#### 3.1 yml-bck-mgr (Backlog State Management Context)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<prompt xmlns="urn:aflac:prompt:v1">
  <metadata>
    <name>yml-bck-mgr</name>
    <version>1.1</version>
    <stateful>true</stateful>
    <purpose>Create and maintain single-source-of-truth YAML backlog file</purpose>
    <created>2026-01-16</created>
    <sdlc_domain>requirements</sdlc_domain>
    <bounded_context>backlog-state-management</bounded_context>
    <strategic_layer>CORE</strategic_layer>
  </metadata>

  <uv_integration>
    <primary_trigger>make backlog-init</primary_trigger>
    <parameters>
      <param name="SOURCES" type="path" required="false">
        <description>Comma-separated list of source document paths to parse</description>
        <default>./docs/</default>
      </param>
      <param name="OUTPUT" type="path" required="false">
        <description>Output path for IMPLEMENTATION_BACKLOG.yaml</description>
        <default>./IMPLEMENTATION_BACKLOG.yaml</default>
      </param>
      <param name="RESET" type="boolean" required="false">
        <description>Force complete re-initialization (destroys existing state)</description>
        <default>false</default>
      </param>
    </parameters>
    <idempotency>
      <guarantee>true</guarantee>
      <state_artifact>IMPLEMENTATION_BACKLOG.yaml</state_artifact>
      <version_field>backlog_metadata.version</version_field>
    </idempotency>
    <determinism>
      <exit_codes>
        <code value="0">Backlog created/updated successfully</code>
        <code value="1">Source document parsing failed</code>
        <code value="2">YAML validation failed</code>
        <code value="3">Dependency cycle detected</code>
      </exit_codes>
      <output_format>yaml</output_format>
    </determinism>
  </uv_integration>

  <!-- ... existing prompt content ... -->
</prompt>
```

#### 3.2 cycle-implement (Execution Orchestration Context)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<prompt xmlns="urn:aflac:prompt:v1">
  <metadata>
    <name>cycle-implement</name>
    <version>1.1</version>
    <stateful>true</stateful>
    <purpose>Execute next work item against acceptance criteria</purpose>
    <created>2026-01-16</created>
    <sdlc_domain>implementation</sdlc_domain>
    <bounded_context>execution-orchestration</bounded_context>
    <strategic_layer>CORE</strategic_layer>
  </metadata>

  <uv_integration>
    <primary_trigger>make cycle-next</primary_trigger>
    <parameters>
      <param name="STORY_ID" type="string" required="false">
        <description>Specific story ID to work on (overrides priority selection)</description>
        <default></default>
      </param>
      <param name="DRY_RUN" type="boolean" required="false">
        <description>Show what would be executed without making changes</description>
        <default>false</default>
      </param>
      <param name="VALIDATE_ONLY" type="boolean" required="false">
        <description>Only validate acceptance criteria without implementing</description>
        <default>false</default>
      </param>
    </parameters>
    <idempotency>
      <guarantee>true</guarantee>
      <state_artifact>IMPLEMENTATION_BACKLOG.yaml</state_artifact>
      <version_field>stories[].status</version_field>
    </idempotency>
    <determinism>
      <exit_codes>
        <code value="0">Work item completed, all criteria met</code>
        <code value="1">Work item blocked, documented blockers</code>
        <code value="2">Work item partial, some criteria unmet</code>
        <code value="3">No eligible work items found</code>
      </exit_codes>
      <output_format>markdown</output_format>
    </determinism>
  </uv_integration>

  <!-- ... existing prompt content ... -->
</prompt>
```

#### 3.3 quality-gate (Quality Assurance Context)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<prompt xmlns="urn:aflac:prompt:v1">
  <metadata>
    <name>quality-gate</name>
    <version>1.1</version>
    <stateful>false</stateful>
    <purpose>Enforce test/doc/tracking workflow before progression</purpose>
    <created>2026-01-16</created>
    <sdlc_domain>testing</sdlc_domain>
    <bounded_context>quality-assurance</bounded_context>
    <strategic_layer>SUPPORTING</strategic_layer>
  </metadata>

  <uv_integration>
    <primary_trigger>make quality-gate</primary_trigger>
    <parameters>
      <param name="STORY_ID" type="string" required="true">
        <description>Story ID to validate for quality gate passage</description>
      </param>
      <param name="SKIP_TESTS" type="boolean" required="false">
        <description>Skip test execution (check other gates only)</description>
        <default>false</default>
      </param>
      <param name="STRICT" type="boolean" required="false">
        <description>Fail on any warnings, not just errors</description>
        <default>false</default>
      </param>
    </parameters>
    <idempotency>
      <guarantee>true</guarantee>
      <state_artifact>none</state_artifact>
      <version_field>n/a</version_field>
    </idempotency>
    <determinism>
      <exit_codes>
        <code value="0">All quality gates passed</code>
        <code value="1">Tests failed</code>
        <code value="2">Documentation incomplete</code>
        <code value="3">Tracking not updated</code>
        <code value="4">Multiple gates failed</code>
      </exit_codes>
      <output_format>markdown</output_format>
    </determinism>
  </uv_integration>

  <!-- ... existing prompt content ... -->
</prompt>
```

---

## 4. API Integration Spec

### UV Make Command Syntax

All UV triggers follow this syntax pattern:

```bash
make <target> [PARAM1=value1] [PARAM2=value2] ...
```

### Complete UV Target Registry

| UV Target | Prompt | Parameters | Exit Codes | Output |
|-----------|--------|------------|------------|--------|
| `make backlog-init` | yml-bck-mgr | SOURCES, OUTPUT, RESET | 0,1,2,3 | YAML |
| `make backlog-refresh` | yml-bck-refresh | STORIES, ARTIFACTS | 0,1,2 | YAML |
| `make scope-update` | scope-change | SCOPE_DOC, VALIDATE | 0,1,2 | YAML |
| `make plan-unify` | unified-plan | PLANS, OUTPUT | 0,1 | Markdown |
| `make ddd-align` | ddd-make-align | REGISTRY, CONTEXTS | 0,1,2 | YAML |
| `make project-organize` | organize | PATH, INDEX | 0,1 | YAML+MD |
| `make cycle-next` | cycle-implement | STORY_ID, DRY_RUN, VALIDATE_ONLY | 0,1,2,3 | Markdown |
| `make registry-update` | rep-mak-reg | FORCE_BOOTSTRAP | 0,1 | YAML |
| `make quality-gate` | quality-gate | STORY_ID, SKIP_TESTS, STRICT | 0,1,2,3,4 | Markdown |
| `make test-review` | tst-rvw-imp | PLAN, VERBOSE | 0,1 | Markdown |
| `make demo-generate` | demo-prep | OUTPUT_DIR | 0,1 | Markdown |
| `make diagram-generate` | diagram | TARGET_PATH, FORMAT | 0,1 | ASCII/MD |
| `make readme-update` | update-readme | SCOPE | 0,1,2 | Markdown |
| `make status-report` | update-status | PERIOD, FORMAT | 0,1 | Markdown |

### Deterministic Execution Guarantees

1. **Same Input → Same Output**: Given identical input parameters and state, UV targets produce identical outputs
2. **Idempotency**: Stateful prompts can be run multiple times safely; subsequent runs with unchanged input produce no-op
3. **Atomic State Updates**: YAML state files are updated atomically with version increments
4. **Exit Code Consistency**: Each exit code maps to a specific, documented failure mode

### Makefile Integration Template

```makefile
# ============================================================================
# UV PROMPT INTEGRATION TARGETS
# ============================================================================

.PHONY: backlog-init backlog-refresh scope-update plan-unify ddd-align \
        project-organize cycle-next registry-update quality-gate test-review \
        demo-generate diagram-generate readme-update status-report

# --- REQUIREMENTS DOMAIN ---

backlog-init:  ## Initialize YAML backlog from source documents
	@echo "🎯 Executing yml-bck-mgr prompt..."
	@uv run scripts/prompt_runner.py yml-bck-mgr \
		--sources "$(SOURCES)" \
		--output "$(OUTPUT)" \
		$(if $(RESET),--reset,)

backlog-refresh:  ## Refresh backlog state and artifact registration
	@echo "🔄 Executing yml-bck-refresh prompt..."
	@uv run scripts/prompt_runner.py yml-bck-refresh \
		$(if $(STORIES),--stories "$(STORIES)",) \
		$(if $(ARTIFACTS),--artifacts "$(ARTIFACTS)",)

scope-update:  ## Update project scope from scope document
	@echo "📋 Executing scope-change prompt..."
	@uv run scripts/prompt_runner.py scope-change \
		--scope-doc "$(SCOPE_DOC)" \
		$(if $(VALIDATE),--validate,)

# --- PLANNING DOMAIN ---

plan-unify:  ## Consolidate implementation plans
	@echo "📊 Executing unified-plan prompt..."
	@uv run scripts/prompt_runner.py unified-plan \
		--plans "$(PLANS)" \
		--output "$(OUTPUT)"

ddd-align:  ## Align make commands with DDD bounded contexts
	@echo "🏗️ Executing ddd-make-align prompt..."
	@uv run scripts/prompt_runner.py ddd-make-align \
		$(if $(REGISTRY),--registry "$(REGISTRY)",) \
		$(if $(CONTEXTS),--contexts "$(CONTEXTS)",)

project-organize:  ## Organize project directory and metadata
	@echo "📁 Executing organize prompt..."
	@uv run scripts/prompt_runner.py organize \
		--path "$(PATH)" \
		$(if $(INDEX),--index "$(INDEX)",)

# --- IMPLEMENTATION DOMAIN ---

cycle-next:  ## Execute next work item from backlog
	@echo "⚡ Executing cycle-implement prompt..."
	@uv run scripts/prompt_runner.py cycle-implement \
		$(if $(STORY_ID),--story-id "$(STORY_ID)",) \
		$(if $(DRY_RUN),--dry-run,) \
		$(if $(VALIDATE_ONLY),--validate-only,)

registry-update:  ## Update make command registry
	@echo "📝 Executing rep-mak-reg prompt..."
	@uv run scripts/prompt_runner.py rep-mak-reg \
		$(if $(FORCE_BOOTSTRAP),--force-bootstrap,)

# --- TESTING DOMAIN ---

quality-gate:  ## Validate story through quality gates
	@echo "✅ Executing quality-gate prompt..."
	@uv run scripts/prompt_runner.py quality-gate \
		--story-id "$(STORY_ID)" \
		$(if $(SKIP_TESTS),--skip-tests,) \
		$(if $(STRICT),--strict,)

test-review:  ## Review and validate test implementation
	@echo "🧪 Executing tst-rvw-imp prompt..."
	@uv run scripts/prompt_runner.py tst-rvw-imp \
		--plan "$(PLAN)" \
		$(if $(VERBOSE),--verbose,)

# --- DEPLOYMENT DOMAIN ---

demo-generate:  ## Generate value-based demo documentation
	@echo "🎬 Executing demo-prep prompt..."
	@uv run scripts/prompt_runner.py demo-prep \
		--output-dir "$(OUTPUT_DIR)"

diagram-generate:  ## Generate ASCII architecture diagrams
	@echo "📐 Executing diagram prompt..."
	@uv run scripts/prompt_runner.py diagram \
		--target-path "$(TARGET_PATH)" \
		$(if $(FORMAT),--format "$(FORMAT)",)

# --- MAINTENANCE DOMAIN ---

readme-update:  ## Update root README with progress
	@echo "📖 Executing update-readme prompt..."
	@uv run scripts/prompt_runner.py update-readme \
		$(if $(SCOPE),--scope "$(SCOPE)",)

status-report:  ## Generate project status report
	@echo "📊 Executing update-status prompt..."
	@uv run scripts/prompt_runner.py update-status \
		--period "$(PERIOD)" \
		$(if $(FORMAT),--format "$(FORMAT)",)
```

### UV Parameter Reference

| Parameter | Type | Description | Used By |
|-----------|------|-------------|---------|
| `SOURCES` | path | Source document paths | backlog-init |
| `OUTPUT` | path | Output file path | backlog-init, plan-unify |
| `RESET` | boolean | Force re-initialization | backlog-init |
| `STORIES` | string | Comma-separated story IDs | backlog-refresh |
| `ARTIFACTS` | path | Artifact paths to register | backlog-refresh |
| `SCOPE_DOC` | path | Scope change document | scope-update |
| `VALIDATE` | boolean | Validate only mode | scope-update |
| `PLANS` | path | Implementation plan paths | plan-unify |
| `REGISTRY` | path | Make command registry path | ddd-align |
| `CONTEXTS` | path | Bounded context definitions | ddd-align |
| `PATH` | path | Target directory path | project-organize |
| `INDEX` | boolean | Generate index files | project-organize |
| `STORY_ID` | string | Specific story to process | cycle-next, quality-gate |
| `DRY_RUN` | boolean | Show without executing | cycle-next |
| `VALIDATE_ONLY` | boolean | Validate only | cycle-next |
| `FORCE_BOOTSTRAP` | boolean | Force complete re-scan | registry-update |
| `SKIP_TESTS` | boolean | Skip test execution | quality-gate |
| `STRICT` | boolean | Strict validation mode | quality-gate |
| `PLAN` | path | Test plan path | test-review |
| `VERBOSE` | boolean | Verbose output | test-review |
| `OUTPUT_DIR` | path | Demo output directory | demo-generate |
| `TARGET_PATH` | path | Diagram target folder | diagram-generate |
| `FORMAT` | string | Output format | diagram-generate, status-report |
| `SCOPE` | string | Update scope | readme-update |
| `PERIOD` | string | Reporting period | status-report |

---

## 5. Migration Summary

### Key Changes

| Area | Before | After |
|------|--------|-------|
| **Metadata Schema** | Partial (3-5 fields) | Complete (8+ fields with UV) |
| **SDLC Classification** | Implicit | Explicit domain assignment |
| **Bounded Contexts** | None | 6 contexts mapped |
| **UV Integration** | None | 14 make targets |
| **Idempotency** | Documented | Enforced with versioning |
| **Exit Codes** | Ad-hoc | Standardized per prompt |
| **State Management** | Manual | Automated with artifact tracking |

### Migration Statistics

| Metric | Value |
|--------|-------|
| Total Prompts | 14 |
| Bounded Contexts | 6 |
| UV Make Targets | 14 |
| Strategic Layers | 3 |
| Unique Parameters | 24 |
| Exit Codes Defined | 47 |
| Metadata Fields Added | ~56 (4 per prompt) |

### Next Steps

1. **Phase 1: Metadata Completion** (Immediate)
   - Add missing `purpose` and `created` fields to 10 prompts
   - Add `sdlc_domain` and `bounded_context` to all prompts
   - Run `make lint-prompts --fix` for auto-completion

2. **Phase 2: UV Integration** (Week 1)
   - Create `scripts/prompt_runner.py` for UV execution
   - Add Makefile targets from template above
   - Test determinism with sample inputs

3. **Phase 3: Validation** (Week 2)
   - Run `make validate-prompts` for compliance check
   - Execute each UV target with test parameters
   - Document any edge cases or limitations

4. **Phase 4: Documentation** (Week 3)
   - Update SDLC_PROMPT_DOMAIN_INDEX.md with UV targets
   - Create per-prompt usage examples
   - Add UV integration to CLAUDE.md governance section

### Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| State corruption during migration | HIGH | Version backup before changes |
| Exit code conflicts | MEDIUM | Standardize codes per domain |
| Parameter naming collisions | LOW | Prefix with domain (e.g., BACKLOG_OUTPUT) |
| Backward compatibility breaks | MEDIUM | Support legacy invocation temporarily |

---

## Appendix: Bounded Context Glossary

| Context | Description | Key Entities |
|---------|-------------|--------------|
| Backlog State Management | Maintains IMPLEMENTATION_BACKLOG.yaml as single source of truth | Story, Artifact, Dependency |
| Execution Orchestration | Executes work items against acceptance criteria | WorkItem, ExecutionPlan, AcceptanceCriteria |
| Architecture Governance | Manages DDD alignment and make command registry | BoundedContext, MakeCommand, ImplementationPlan |
| Quality Assurance | Enforces testing and validation workflows | TestPlan, ValidationRule, QualityMetric |
| Documentation Management | Updates README and status reports | README, StatusReport, LearningStory |
| Visualization & Reporting | Generates demos and diagrams | Demo, Diagram, ValueNarrative |

---

**Document Created:** 2026-01-21
**Status:** Active Migration Spec
**Maintainer:** SDLC Prompt System
