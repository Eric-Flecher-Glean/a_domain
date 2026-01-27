---
title: "Refactored XML Prompts - UV Deterministic API Integration"
version: 1.0
date: 2026-01-22
status: active
purpose: "Documentation for Refactored XML Prompts - UV Deterministic API Integration"
---

# Refactored XML Prompts - UV Deterministic API Integration

**Version:** 1.0
**Created:** 2026-01-21
**Status:** Active

---

## Overview

This document provides the refactored XML prompt specifications with UV deterministic API annotations. Each prompt is enhanced with:

1. **UV API metadata** - Make target, parameters, determinism guarantees
2. **Input/Output schemas** - Structured data contracts
3. **Bounded context annotations** - DDD integration points
4. **Determinism guarantees** - Idempotency and reproducibility rules

---

## XML Schema Extensions

### New Metadata Fields

```xml
<!-- Standard metadata -->
<metadata>
  <name>prompt-short-name</name>
  <version>1.0</version>
  <stateful>true|false</stateful>
  <purpose>One-line description</purpose>
  <created>2026-01-21</created>

  <!-- UV API Extensions -->
  <uv_api>
    <make_target>uv-prompt-name</make_target>
    <bounded_context>context-id</bounded_context>
    <deterministic>true|false</deterministic>
    <idempotent>true|false</idempotent>
  </uv_api>
</metadata>

<!-- Input/Output Schema -->
<io_schema>
  <input>
    <param name="param1" type="string" required="true">Description</param>
    <param name="param2" type="file" required="false">Description</param>
  </input>
  <output>
    <artifact type="yaml" path="output.yaml">Description</artifact>
    <artifact type="markdown" path="report.md">Description</artifact>
  </output>
</io_schema>
```

---

## Refactored Prompt Specifications

### 1. yml-bck-mgr (YAML Backlog Manager)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<prompt xmlns:uv="http://uv.deterministic.api/1.0">

<metadata>
  <name>yml-bck-mgr</name>
  <version>2.0</version>
  <stateful>true</stateful>
  <purpose>Create and maintain single-source-of-truth YAML backlog file</purpose>
  <created>2026-01-16</created>
  <migrated>2026-01-21</migrated>

  <!-- UV API Extensions -->
  <uv:api>
    <uv:make_target>uv-yml-bck-mgr</uv:make_target>
    <uv:bounded_context>backlog-state</uv:bounded_context>
    <uv:deterministic>true</uv:deterministic>
    <uv:idempotent>true</uv:idempotent>
    <uv:aggregate_root>IMPLEMENTATION_BACKLOG.yaml</uv:aggregate_root>
  </uv:api>
</metadata>

<io_schema>
  <input>
    <param name="SOURCE_DOCS" type="path" required="false">
      Path to source documents for story extraction
    </param>
    <param name="BACKLOG_PATH" type="file" required="false" default="IMPLEMENTATION_BACKLOG.yaml">
      Path to backlog file
    </param>
    <param name="MODE" type="enum" values="bootstrap,incremental" default="incremental">
      Execution mode: bootstrap (fresh) or incremental (update)
    </param>
  </input>
  <output>
    <artifact type="yaml" path="IMPLEMENTATION_BACKLOG.yaml">
      Updated backlog with stories, priorities, dependencies
    </artifact>
    <artifact type="json" path=".uv/yml-bck-mgr-result.json">
      Execution result with checksums and validation status
    </artifact>
  </output>
</io_schema>

<uv:determinism_contract>
  <uv:guarantee>Same SOURCE_DOCS + same BACKLOG_PATH = same output YAML structure</uv:guarantee>
  <uv:verification>SHA256 checksum of output YAML excluding timestamps</uv:verification>
  <uv:idempotency>Running twice produces same result (incremental updates preserve state)</uv:idempotency>
</uv:determinism_contract>

<role>YAML Backlog State Manager and Claude Code Integration Specialist</role>

<primary_goal>
  Create and maintain a single-source-of-truth YAML backlog file that organizes all
  implementation and testing stories in priority order with mapped dependencies.
  <audience>Development teams using Claude Code for implementation</audience>
  <tone>Systematic and procedural</tone>
</primary_goal>

<context>
  This is a primer and manual update prompt designed to be run multiple times on the
  same system. It sets up the foundational state management infrastructure but does
  NOT trigger actual implementation work.

  <uv:context_binding>
    This prompt operates within the Backlog State Management bounded context.
    It produces the aggregate root (IMPLEMENTATION_BACKLOG.yaml) consumed by:
    - cycle-implement (Execution Engine context)
    - quality-gate (Quality Assurance context)
    - scope-change (Scope Adaptation context)
  </uv:context_binding>
</context>

<instructions>
  <steps>
    <step1>
      Scan and parse all available source documents to extract individual stories and tasks.
      <uv:input_binding param="SOURCE_DOCS"/>
    </step1>

    <step2>
      Identify and extract priority levels (P0, P1, P2, etc.) and categorize each story.
    </step2>

    <step3>
      Map dependencies between stories by identifying references and prerequisites.
    </step3>

    <step4>
      Generate or update the YAML backlog file with priority-ordered stories.
      <uv:output_binding artifact="IMPLEMENTATION_BACKLOG.yaml"/>
    </step4>

    <step5>
      Validate output against JSON schema.
      <uv:validation schema="schema/implementation_backlog_schema.json"/>
    </step5>

    <step6>
      Preserve existing state when updating (idempotent merge).
      <uv:idempotency_rule>Never overwrite existing completed status</uv:idempotency_rule>
    </step6>
  </steps>
</instructions>

<constraints>
  <constraint>This prompt must be idempotent - safe to run multiple times</constraint>
  <constraint>Do NOT trigger implementation work; only create/update backlog structure</constraint>
  <constraint>All stories must have unique IDs for dependency mapping</constraint>
  <constraint uv:enforced="true">Dependencies must reference valid story IDs</constraint>
</constraints>

<validation_rules>
  <rule uv:exit_code="0">Every story must have a unique story_id</rule>
  <rule uv:exit_code="1">All dependency references must point to valid story_ids</rule>
  <rule uv:exit_code="2">YAML must be valid and pass schema validation</rule>
</validation_rules>

</prompt>
```

---

### 2. cycle-implement (Cycle Implementation)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<prompt xmlns:uv="http://uv.deterministic.api/1.0">

<metadata>
  <name>cycle-implement</name>
  <version>2.0</version>
  <stateful>true</stateful>
  <purpose>Execute work items against acceptance criteria</purpose>
  <created>2026-01-16</created>
  <migrated>2026-01-21</migrated>

  <uv:api>
    <uv:make_target>uv-cycle-implement</uv:make_target>
    <uv:bounded_context>execution-engine</uv:bounded_context>
    <uv:deterministic>false</uv:deterministic>
    <uv:idempotent>false</uv:idempotent>
    <uv:aggregate_root>WorkUnit</uv:aggregate_root>
  </uv:api>
</metadata>

<io_schema>
  <input>
    <param name="BACKLOG" type="file" required="true" default="IMPLEMENTATION_BACKLOG.yaml">
      Path to backlog file
    </param>
    <param name="STORY_ID" type="string" required="false">
      Specific story to execute (optional, defaults to next P0)
    </param>
    <param name="DRY_RUN" type="boolean" default="false">
      Plan only, do not execute
    </param>
  </input>
  <output>
    <artifact type="code" path="varies">
      Implementation artifacts (code, tests, docs)
    </artifact>
    <artifact type="yaml" path="IMPLEMENTATION_BACKLOG.yaml">
      Updated backlog with status changes
    </artifact>
    <artifact type="json" path=".uv/cycle-implement-result.json">
      Execution log with validation results
    </artifact>
  </output>
</io_schema>

<uv:determinism_contract>
  <uv:guarantee>Non-deterministic: creates new artifacts</uv:guarantee>
  <uv:verification>Log all created files with checksums</uv:verification>
  <uv:reproducibility>Capture full execution log for replay</uv:reproducibility>
</uv:determinism_contract>

<role>
  Autonomous, detail-oriented execution agent that:
  - Interprets plans and backlogs
  - Decomposes work into actionable steps
  - Produces concrete outputs (code, docs, tests)
  - Verifies work against acceptance criteria
</role>

<primary_goal>
  Identify the next unit of work from the existing plan, create a concrete execution
  plan based on the available context, and implement that plan until the acceptance
  criteria are satisfied or a clear blocker is reached.
</primary_goal>

<context>
  <uv:upstream_dependency context="backlog-state">
    Reads story queue and acceptance criteria from IMPLEMENTATION_BACKLOG.yaml
  </uv:upstream_dependency>

  <uv:downstream_consumer context="quality-assurance">
    Produces completed work for validation by quality-gate
  </uv:downstream_consumer>
</context>

<instructions>
  <steps>
    <step1 uv:phase="selection">
      Analyze the provided plan/backlog and current statuses.
      <uv:input_binding param="BACKLOG"/>
    </step1>

    <step2 uv:phase="selection">
      Select the next unit of work: highest-priority item not done and not blocked.
      <uv:selection_criteria>
        P0 > P1 > P2 > P3; not_started > in_progress; no blocking dependencies
      </uv:selection_criteria>
    </step2>

    <step3 uv:phase="planning">
      Extract or infer acceptance criteria for the selected unit.
    </step3>

    <step4 uv:phase="planning">
      Build an execution plan with numbered sub-steps mapped to criteria.
    </step4>

    <step5 uv:phase="execution">
      Implement the plan, producing concrete artifacts.
      <uv:artifact_logging>true</uv:artifact_logging>
    </step5>

    <step6 uv:phase="validation">
      Validate implementation against acceptance criteria.
      <uv:validation_output artifact=".uv/cycle-implement-result.json"/>
    </step6>

    <step7 uv:phase="completion">
      Summarize outcome and update backlog status.
      <uv:output_binding artifact="IMPLEMENTATION_BACKLOG.yaml"/>
    </step7>
  </steps>
</instructions>

<validation_rules>
  <rule uv:exit_code="0">Work item meets all acceptance criteria</rule>
  <rule uv:exit_code="1">Work item partially complete (blockers documented)</rule>
  <rule uv:exit_code="2">Work item blocked (no progress possible)</rule>
</validation_rules>

</prompt>
```

---

### 3. quality-gate (Quality Gate)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<prompt xmlns:uv="http://uv.deterministic.api/1.0">

<metadata>
  <name>quality-gate</name>
  <version>2.0</version>
  <stateful>false</stateful>
  <purpose>Ensure completed work is tested, documented, and tracked before progression</purpose>
  <created>2026-01-16</created>
  <migrated>2026-01-21</migrated>

  <uv:api>
    <uv:make_target>uv-quality-gate</uv:make_target>
    <uv:bounded_context>quality-assurance</uv:bounded_context>
    <uv:deterministic>true</uv:deterministic>
    <uv:idempotent>true</uv:idempotent>
  </uv:api>
</metadata>

<io_schema>
  <input>
    <param name="WORK_ITEM" type="string" required="false">
      Specific work item to validate (optional)
    </param>
    <param name="STRICT" type="boolean" default="true">
      Fail on any gate violation
    </param>
  </input>
  <output>
    <artifact type="markdown" path=".uv/quality-gate-report.md">
      Gate validation checklist
    </artifact>
    <artifact type="json" path=".uv/quality-gate-result.json">
      Machine-readable validation result
    </artifact>
  </output>
</io_schema>

<uv:determinism_contract>
  <uv:guarantee>Same repository state = same validation result</uv:guarantee>
  <uv:verification>Hash of all checked files determines output</uv:verification>
  <uv:idempotency>Read-only validation, no state changes</uv:idempotency>
</uv:determinism_contract>

<role>
  Detail-oriented software engineer ensuring high-quality delivery and accurate project hygiene.
</role>

<primary_goal>
  Ensure all completed work is fully tested, documented, and tracked before moving
  on to the next priority item.
</primary_goal>

<context>
  <uv:upstream_dependency context="execution-engine">
    Receives completed work items from cycle-implement
  </uv:upstream_dependency>

  <uv:gate_enforcement>
    Blocks progression until all validation criteria pass
  </uv:gate_enforcement>
</context>

<instructions>
  <steps>
    <step1 uv:gate="test">
      Identify which work items are ready to be tested.
      Run relevant make commands and verify output.
      <uv:validation>make test-all must exit 0</uv:validation>
    </step1>

    <step2 uv:gate="test">
      If issues found, document and fail gate.
      <uv:on_failure exit_code="1">Document test failures</uv:on_failure>
    </step2>

    <step3 uv:gate="tracking">
      Update all relevant status and tracking systems.
      <uv:validation>Backlog status must be updated</uv:validation>
    </step3>

    <step4 uv:gate="documentation">
      Review and update README and related documentation.
      <uv:validation>README reflects current state</uv:validation>
    </step4>

    <step5 uv:gate="approval">
      All gates passed - approve progression to next item.
      <uv:on_success exit_code="0">All gates passed</uv:on_success>
    </step5>
  </steps>
</instructions>

<validation_rules>
  <rule uv:gate="test" uv:exit_code="1">All make commands pass with no failures</rule>
  <rule uv:gate="tracking" uv:exit_code="2">Status tracking is current</rule>
  <rule uv:gate="documentation" uv:exit_code="3">README is up to date</rule>
</validation_rules>

<uv:exit_codes>
  <code value="0">All gates passed</code>
  <code value="1">Test gate failed</code>
  <code value="2">Tracking gate failed</code>
  <code value="3">Documentation gate failed</code>
</uv:exit_codes>

</prompt>
```

---

### 4. rep-mak-reg (Make Registry)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<prompt xmlns:uv="http://uv.deterministic.api/1.0">

<metadata>
  <name>rep-mak-reg</name>
  <version>2.0</version>
  <stateful>true</stateful>
  <purpose>Create and maintain make command registry</purpose>
  <created>2026-01-16</created>
  <migrated>2026-01-21</migrated>

  <uv:api>
    <uv:make_target>uv-rep-mak-reg</uv:make_target>
    <uv:bounded_context>build-governance</uv:bounded_context>
    <uv:deterministic>true</uv:deterministic>
    <uv:idempotent>true</uv:idempotent>
    <uv:aggregate_root>MAKE_COMMAND_REGISTRY.yaml</uv:aggregate_root>
  </uv:api>
</metadata>

<io_schema>
  <input>
    <param name="DOMAIN_FILTER" type="string" required="false">
      Limit scan to specific domain(s)
    </param>
    <param name="REGISTRY_PATH" type="file" default="MAKE_COMMAND_REGISTRY.yaml">
      Custom path for output registry
    </param>
    <param name="FORCE_BOOTSTRAP" type="boolean" default="false">
      Force complete re-scan even if registry exists
    </param>
  </input>
  <output>
    <artifact type="yaml" path="MAKE_COMMAND_REGISTRY.yaml">
      Updated registry with all make commands
    </artifact>
    <artifact type="json" path=".uv/rep-mak-reg-result.json">
      Execution result with discovery statistics
    </artifact>
  </output>
</io_schema>

<uv:determinism_contract>
  <uv:guarantee>Same Makefiles = same registry content (excluding timestamps)</uv:guarantee>
  <uv:verification>SHA256 of all Makefiles determines expected registry</uv:verification>
  <uv:idempotency>Incremental mode: never deletes, only adds or enhances</uv:idempotency>
  <uv:boyscout_rule>Each execution leaves registry more complete</uv:boyscout_rule>
</uv:determinism_contract>

<role>Repository organization specialist and build system analyst</role>

<primary_goal>
  Create and maintain a comprehensive YAML registry of all make commands across the
  repository, organized by domain, with full traceability to implementation backlog items.
</primary_goal>

<context>
  <uv:boyscout_rule>
    This prompt follows the boyscout rule: leave the repository more organized than
    you found it. Each execution should improve the registry.
  </uv:boyscout_rule>

  <uv:traceability>
    Links make commands to IMPLEMENTATION_BACKLOG.yaml stories
  </uv:traceability>
</context>

<instructions>
  <steps>
    <step1 uv:phase="detection">
      Check if MAKE_COMMAND_REGISTRY.yaml exists.
      <uv:mode_selection>
        exists=false → bootstrap mode
        exists=true AND FORCE_BOOTSTRAP=false → incremental mode
        FORCE_BOOTSTRAP=true → bootstrap mode
      </uv:mode_selection>
    </step1>

    <step2 uv:phase="scan">
      Recursively scan repository for all Makefiles.
      Extract all make targets, descriptions, dependencies.
    </step2>

    <step3 uv:phase="classification">
      Classify each make command into functional domains.
      <uv:domains>build, test, deploy, database, documentation, utilities, ci-cd</uv:domains>
    </step3>

    <step4 uv:phase="linking">
      Parse IMPLEMENTATION_BACKLOG.yaml and create traceability links.
      <uv:upstream_binding context="backlog-state"/>
    </step4>

    <step5 uv:phase="generation">
      Create or update MAKE_COMMAND_REGISTRY.yaml.
      <uv:output_binding artifact="MAKE_COMMAND_REGISTRY.yaml"/>
    </step5>

    <step6 uv:phase="documentation">
      Add changelog entry documenting improvements.
      <uv:changelog_required>true</uv:changelog_required>
    </step6>
  </steps>
</instructions>

<constraints>
  <constraint uv:enforced="true">Never delete information from existing registry</constraint>
  <constraint>Maintain alphabetical ordering within each domain</constraint>
  <constraint>Preserve all previous changelog entries</constraint>
</constraints>

</prompt>
```

---

### 5. unified-plan (Unified Plan)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<prompt xmlns:uv="http://uv.deterministic.api/1.0">

<metadata>
  <name>unified-plan</name>
  <version>2.0</version>
  <stateful>false</stateful>
  <purpose>Consolidate and validate technical implementation plans</purpose>
  <created>2026-01-16</created>
  <migrated>2026-01-21</migrated>

  <uv:api>
    <uv:make_target>uv-unified-plan</uv:make_target>
    <uv:bounded_context>planning-architecture</uv:bounded_context>
    <uv:deterministic>true</uv:deterministic>
    <uv:idempotent>true</uv:idempotent>
  </uv:api>
</metadata>

<io_schema>
  <input>
    <param name="PLAN_SOURCES" type="path" required="false">
      Directory containing planning artifacts
    </param>
    <param name="OUTPUT" type="file" default="IMPLEMENTATION_PLAN.md">
      Output consolidated plan file
    </param>
  </input>
  <output>
    <artifact type="markdown" path="IMPLEMENTATION_PLAN.md">
      Consolidated implementation plan
    </artifact>
    <artifact type="json" path=".uv/unified-plan-result.json">
      Consolidation summary and validation results
    </artifact>
  </output>
</io_schema>

<uv:determinism_contract>
  <uv:guarantee>Same source artifacts = same consolidated plan</uv:guarantee>
  <uv:verification>Hash of input files determines expected output</uv:verification>
</uv:determinism_contract>

<role>
  Senior technical project manager and solutions architect responsible for
  bringing a project from planning into execution.
</role>

<primary_goal>
  Review all existing project planning, consolidate into a single, organized
  implementation plan, validate for completeness, and remove outdated scope.
</primary_goal>

</prompt>
```

---

### 6-14. Remaining Prompts (Summary Table)

| Prompt | UV Target | Context | Deterministic | Key Changes |
|--------|----------|---------|---------------|-------------|
| `scope-change` | `uv-scope-change` | backlog-state | false | Added scope binding |
| `ddd-make-align` | `uv-ddd-make-align` | build-governance | true | Added DDD context validation |
| `organize` | `uv-organize` | planning-architecture | true | Added index management |
| `tst-rvw-imp` | `uv-tst-rvw-imp` | quality-assurance | true | Added test plan binding |
| `demo-prep` | `uv-demo-prep` | doc-deployment | true | Added demo spec output |
| `diagram` | `uv-diagram` | doc-deployment | true | Added folder target binding |
| `update-readme` | `uv-update-readme` | doc-deployment | false | Added git history binding |
| `update-status` | `uv-update-status` | doc-deployment | true | Added status report output |
| `yml-bck-refresh` | `uv-yml-bck-refresh` | backlog-state | true | Added artifact sync |

---

## Common UV API Patterns

### 1. Make Target Convention

All UV-integrated prompts use the naming convention:

```bash
make uv-{prompt-short-name} [PARAM=value]...
```

Examples:
```bash
make uv-yml-bck-mgr SOURCE_DOCS=docs/
make uv-cycle-implement STORY_ID=P0-INFRA-001
make uv-quality-gate STRICT=true
make uv-diagram TARGET=spikes/spike-07/
```

### 2. Output Directory

All UV execution artifacts are stored in `.uv/` directory:

```
.uv/
├── yml-bck-mgr-result.json
├── cycle-implement-result.json
├── quality-gate-result.json
├── quality-gate-report.md
└── ...
```

### 3. Exit Code Standard

| Code | Meaning | Action |
|------|---------|--------|
| 0 | Success | Proceed |
| 1 | Partial failure | Review and retry |
| 2 | Validation failure | Fix inputs |
| 3+ | Specific error | See prompt docs |

### 4. Determinism Verification

```bash
# Run prompt twice, compare outputs
make uv-{prompt} > /tmp/run1.out
make uv-{prompt} > /tmp/run2.out
diff /tmp/run1.out /tmp/run2.out  # Should be empty for deterministic prompts
```

---

## Changelog

| Date | Version | Changes |
|------|---------|---------|
| 2026-01-21 | 1.0 | Initial refactored prompt specifications |
