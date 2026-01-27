---
title: "Technical Specification: rep-mak-reg"
version: 1.0
date: 2026-01-22
status: draft
purpose: "Documentation for Technical Specification: rep-mak-reg"
---

# Technical Specification: rep-mak-reg

**Prompt Name:** Repeatable Make Registry
**Short Name:** `rep-mak-reg`
**Version:** 1.0
**Stateful:** Yes
**SDLC Subdomain:** Implementation

---

## 1. Purpose & Objectives

### Primary Goal

Create and maintain a comprehensive YAML registry of all make commands across the repository, organized by domain, with full traceability to implementation backlog items.

### Key Objectives

1. **Command Discovery** - Scan all Makefiles for targets
2. **Domain Classification** - Organize commands by functional domain
3. **Backlog Traceability** - Link commands to backlog stories
4. **Incremental Improvement** - Follow boyscout rule on each run
5. **Registry Maintenance** - Keep registry accurate and complete

---

## 2. Input/Output Schemas

### Input Sources

| Source Type | Description | Location |
|-------------|-------------|----------|
| Makefiles | All make targets | `**/Makefile` |
| Implementation Backlog | Story references | `IMPLEMENTATION_BACKLOG.yaml` |
| Existing Registry | Previous state | `MAKE_COMMAND_REGISTRY.yaml` |

### Output Schema

```yaml
# MAKE_COMMAND_REGISTRY.yaml
metadata:
  last_updated: "2026-01-21T10:30:00Z"
  execution_mode: bootstrap | incremental
  total_commands: 142
  domains_identified: 11

domains:
  testing:
    description: "Test execution and validation commands"
    commands:
      - name: test-unit
        target: test-unit
        file: Makefile
        description: "Run unit tests"
        dependencies: []
        backlog_refs:
          - "P1-TEST-001"
        usage: "make test-unit"

  spike_development:
    description: "Spike-specific development commands"
    commands:
      - name: spike07-extract-live
        target: extract-live
        file: spikes/spike-07-.../Makefile
        description: "Extract work units from live MCP"
        dependencies: [demo-data]
        backlog_refs:
          - "P0-F1-001"
        usage: "make spike07-extract-live"

changelog:
  - timestamp: "2026-01-21T10:30:00Z"
    mode: bootstrap
    improvements:
      - "Initial registry creation with 142 commands"
      - "11 functional domains identified"
      - "25 backlog references established"

untracked_commands:
  - name: clean
    reason: "Utility command, no backlog story"
  - name: help
    reason: "Documentation command"
```

---

## 3. Dependencies

### Required Inputs

| Dependency | Type | Description |
|------------|------|-------------|
| Makefiles | Files | At least one Makefile |
| Backlog | Optional | For traceability links |

### Runtime Dependencies

| Dependency | Purpose |
|------------|---------|
| File System | Scan for Makefiles |
| YAML Parser | Read/write registry |

### Downstream Consumers

| Consumer | Purpose |
|----------|---------|
| `ddd-make-align` | Extends with DDD metadata |
| `demo-prep` | Uses commands for demos |
| `quality-gate` | Uses test commands |

---

## 4. Execution Modes

### Bootstrap Mode

**Trigger:** `MAKE_COMMAND_REGISTRY.yaml` does not exist

**Actions:**
1. Recursively scan repository for all Makefiles
2. Extract all make targets with descriptions
3. Classify commands into functional domains
4. Link to backlog items where possible
5. Create new registry file
6. Document in changelog

### Incremental Mode

**Trigger:** Registry exists

**Actions:**
1. Load existing registry
2. Scan for new/changed Makefiles
3. Identify new commands
4. Apply at least one improvement
5. Update registry
6. Document changes in changelog

---

## 5. Processing Steps

### Step 1: Detect Mode

```yaml
mode_detection:
  if: MAKE_COMMAND_REGISTRY.yaml not exists
  then: bootstrap
  else if: force_bootstrap argument
  then: bootstrap
  else: incremental
```

### Step 2: Scan Repository

**Actions:**
- Find all `**/Makefile` files
- Parse each Makefile for targets
- Extract:
  - Target name
  - Description (from comments)
  - Dependencies
  - File location

**Makefile Parsing:**
```makefile
# Description comment for target
target-name: dependency1 dependency2
	command
```

### Step 3: Domain Classification

**Functional Domains:**
| Domain | Pattern Examples |
|--------|------------------|
| testing | `test-*`, `verify-*` |
| build | `build-*`, `compile-*` |
| deployment | `deploy-*`, `release-*` |
| documentation | `docs-*`, `doc-*` |
| utilities | `clean`, `help`, `lint` |
| ci_cd | `ci-*`, `pipeline-*` |
| spike_development | `spike*-*` |
| database | `db-*`, `migrate-*` |
| demo | `demo-*` |
| governance | `validate-*`, `check-*` |
| session | `session-*`, `backlog-*` |

**Classification Logic:**
1. Match target name against patterns
2. Consider file path context
3. Use description keywords
4. Default to utilities if no match

### Step 4: Backlog Linking

**Actions:**
- Parse IMPLEMENTATION_BACKLOG.yaml
- Match commands to stories by:
  - Name patterns (e.g., `spike07-*` → P0-F1-001)
  - Description keywords
  - File path context
- Add backlog_refs to matching commands
- Mark unlinked as "untracked"

### Step 5: Generate Registry

**Registry Structure:**
```yaml
metadata:
  last_updated: timestamp
  execution_mode: mode
  total_commands: count
  domains_identified: count

domains:
  domain_name:
    description: "domain purpose"
    commands: [...]

changelog:
  - timestamp: ...
    improvements: [...]

untracked_commands: [...]
```

### Step 6: Document Improvements

**Changelog Entry:**
- Timestamp
- Execution mode
- List of improvements made

**Improvement Types:**
- New commands discovered
- Better domain categorization
- Enhanced documentation
- New backlog links
- Fixed inconsistencies

---

## 6. Usage Examples

### Example 1: Bootstrap

**Prompt:**
```
Create a make command registry for the repository.
```

**Expected Output:**
```yaml
metadata:
  execution_mode: bootstrap
  total_commands: 142
  domains_identified: 11

changelog:
  - timestamp: "2026-01-21T10:30:00Z"
    mode: bootstrap
    improvements:
      - "Initial registry with 142 commands"
      - "11 domains: testing, build, spike_development, ..."
```

### Example 2: Incremental Update

**Prompt:**
```
Update the make command registry with any new commands.
```

**Expected Behavior:**
- Scans for Makefiles changed since last_updated
- Finds 3 new commands in spike-08/Makefile
- Adds to spike_development domain
- Links to new backlog story P2-SPIKE-008
- Updates changelog

### Example 3: Domain Filter

**Prompt:**
```
Update registry for just the testing domain commands.
```

**Expected Behavior:**
- Focuses on `test-*` targets
- Updates descriptions if changed
- Adds new test commands
- Preserves other domains unchanged

---

## 7. Integration Points

### Integration with ddd-make-align

```yaml
# rep-mak-reg provides base, ddd-make-align extends
workflow:
  1. rep-mak-reg creates MAKE_COMMAND_REGISTRY.yaml
  2. ddd-make-align adds ddd_metadata section
  3. Both preserve each other's fields
  4. Registry has functional + architectural organization
```

### Integration with yml-bck-mgr

```yaml
# Backlog provides story references for traceability
workflow:
  1. yml-bck-mgr creates IMPLEMENTATION_BACKLOG.yaml
  2. rep-mak-reg reads stories
  3. Links commands to relevant stories
  4. Creates bidirectional traceability
```

---

## 8. Success Criteria

### Validation Rules

| Rule | Description |
|------|-------------|
| All Categorized | Every command in at least one domain |
| Complete Metadata | name, target, file, description required |
| Valid References | backlog_refs verified against backlog |
| Changelog Present | Every execution adds changelog entry |
| Valid YAML | Registry must parse successfully |
| Meaningful Domains | Domain descriptions are informative |

### Quality Metrics

| Metric | Target |
|--------|--------|
| Command Coverage | 100% of make targets |
| Backlog Linkage | ≥80% linked to stories |
| Domain Coverage | All commands categorized |
| Description Quality | ≥90% have descriptions |

---

## 9. Constraints

1. **Never Delete** - Only add or enhance, never remove info
2. **Alphabetical Order** - Commands sorted within domains
3. **Preserve Changelog** - All previous entries kept
4. **Valid YAML** - Properly formatted output
5. **Boyscout Rule** - Each run leaves registry better

---

## 10. Error Handling

| Error Condition | Handling |
|-----------------|----------|
| Malformed Makefile | Skip, log warning |
| Invalid backlog ref | Remove from refs, log |
| Duplicate command | Merge entries, note in changelog |
| Missing description | Use "undocumented" placeholder |
| Parse error | Abort, preserve original |

---

## Appendix: Domain Definitions

| Domain | Purpose | Example Commands |
|--------|---------|------------------|
| testing | Test execution | test-unit, test-integration |
| build | Build/compile | build, compile, package |
| deployment | Release/deploy | deploy, release, publish |
| documentation | Docs generation | docs, doc-api, doc-site |
| utilities | General utils | clean, help, lint, format |
| ci_cd | CI/CD pipeline | ci-build, pipeline-run |
| spike_development | Spike work | spike07-extract, spike05-demo |
| database | DB operations | db-migrate, db-seed |
| demo | Demonstrations | demo-run, demo-prep |
| governance | Validation | validate-backlog, check-artifacts |
| session | Session management | session-start, session-end |
