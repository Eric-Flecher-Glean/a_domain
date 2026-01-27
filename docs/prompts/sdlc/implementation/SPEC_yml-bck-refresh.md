---
title: "Technical Specification: yml-bck-refresh"
version: 1.0
date: 2026-01-22
status: draft
purpose: "Documentation for Technical Specification: yml-bck-refresh"
---

# Technical Specification: yml-bck-refresh

**Prompt Name:** YAML Backlog Refresh
**Short Name:** `yml-bck-refresh`
**Version:** 1.0
**Stateful:** Yes
**SDLC Subdomain:** Implementation

---

## 1. Purpose & Objectives

### Primary Goal

Maintain YAML backlog as the deterministic single source of truth for SDLC state management, ensuring all project artifacts are discovered, classified, registered with metadata tags, and mapped to their corresponding stories.

### Key Objectives

1. **Artifact Discovery** - Scan project for all source, test, and doc files
2. **Classification** - Categorize artifacts by type and purpose
3. **Registration** - Add artifacts to story artifact_registry
4. **Staleness Detection** - Identify old or abandoned artifacts
5. **State Synchronization** - Keep backlog current with filesystem

---

## 2. Input/Output Schemas

### Input Sources

| Source Type | Description | Purpose |
|-------------|-------------|---------|
| Project Directory | All project files | Artifact discovery |
| YAML Backlog | Existing backlog state | State baseline |
| File Metadata | Timestamps, sizes | Staleness detection |

### Artifact Registry Schema

```yaml
# Added to each story in IMPLEMENTATION_BACKLOG.yaml
artifact_registry:
  implementation:
    - file_path: "src/core/work_unit_discovery.py"
      file_type: source_code
      confidence: HIGH | MEDIUM | LOW
      registered_date: "2026-01-21T10:30:00Z"
      staleness_status: CURRENT | STALE
      staleness_note: "Optional explanation"

  tests:
    - file_path: "tests/test_discovery.py"
      file_type: test_code
      confidence: HIGH
      registered_date: "2026-01-21T10:30:00Z"

  documentation:
    - file_path: "docs/DISCOVERY_GUIDE.md"
      file_type: documentation
      confidence: MEDIUM
      registered_date: "2026-01-21T10:30:00Z"

  results:
    - file_path: "results/discovery_results_20260121.json"
      file_type: test_results
      confidence: HIGH
      registered_date: "2026-01-21T10:30:00Z"
```

### Output Report Schema

```markdown
## YAML Backlog State Management Report

**Execution Mode:** initial_run | repeated_run
**Timestamp:** 2026-01-21T10:30:00Z
**YAML Version:** 12 → 13

### Artifacts Processed
- Source Code: 45 files
- Tests: 23 files
- Documentation: 18 files
- Results: 5 files
- **Total:** 91 files

### Stories Updated
- Status Changes: 2 (1 not_started→in_progress, 1 in_progress→completed)
- Artifact Registrations: 15 stories
- Staleness Marks: 3 artifacts

### Manual Review Queue
- LOW Confidence Mappings: 2 artifacts
- STALE Artifacts: 3 files

### Validation Results
- ✓ No orphaned artifacts
- ✓ Dependency consistency maintained
- ✓ All new artifacts registered

### Next Recommended Story
**Story ID:** P0-F1-003
**Title:** GTM Motion Classification
**Why:** Dependencies met, highest priority available
```

---

## 3. Dependencies

### Required Inputs

| Dependency | Type | Description |
|------------|------|-------------|
| YAML Backlog | File | `IMPLEMENTATION_BACKLOG.yaml` |
| Project Directory | Directory | File system to scan |

### Runtime Dependencies

| Dependency | Purpose |
|------------|---------|
| `yml-bck-mgr` | Base backlog structure |
| File System | Scan and read files |
| YAML Parser | Update backlog |

### Downstream Consumers

| Consumer | Purpose |
|----------|---------|
| `organize` | Uses artifact info for organization |
| `cycle-implement` | Sees registered artifacts |
| `update-status` | Reports artifact coverage |

---

## 4. Execution Modes

### Initial Run Mode

**Trigger:** `artifact_registry` fields missing or <50% populated

**Actions:**
1. Recursively scan project directory
2. Classify each discovered artifact
3. Match artifacts to stories by content analysis
4. Populate artifact_registry fields
5. Mark unmapped artifacts for manual review
6. Detect and mark staleness

### Repeated Run Mode

**Trigger:** `artifact_registry` ≥50% populated

**Actions:**
1. Gather current state from filesystem and YAML
2. Detect new artifacts (created after last update)
3. Detect modified artifacts (changed since last update)
4. Detect deleted artifacts (in YAML but missing)
5. Build and execute maintenance plan
6. Validate and update YAML

---

## 5. Processing Steps

### Step 1: Determine Mode

```yaml
mode_detection:
  read: IMPLEMENTATION_BACKLOG.yaml
  check: artifact_registry population
  if: <50% populated
  then: initial_run
  else: repeated_run
```

### Step 2: Initial Run Workflow

**Scan Artifacts:**
- Recursively scan project
- Exclude: node_modules, .git, __pycache__, venv
- Classify: source, test, documentation, results, config

**Classify Artifacts:**
1. Read file content
2. Analyze purpose (implementation, test, doc, config)
3. Extract metadata (path, type, dates, size)
4. Match to story by:
   - File path patterns
   - Content keywords (class names, test IDs)
   - Documentation references (story IDs)
5. Assign confidence: HIGH, MEDIUM, LOW

**Register Artifacts:**
- Add artifact_registry to each story
- Include: file_path, file_type, confidence, registered_date
- LOW confidence → manual_review_queue

**Detect Staleness:**
- Compare last_modified vs story completion
- If >30 days old with no updates → STALE
- Add staleness_note explaining status

### Step 3: Repeated Run Workflow

**Gather Context:**
- Read YAML backlog state
- Scan filesystem for changes since last_updated
- Identify: new, modified, deleted artifacts

**Build Maintenance Plan:**
```yaml
maintenance_plan:
  priority: critical → high → medium → low
  actions:
    - type: NEW_ARTIFACTS
      items: [unregistered files]
    - type: MODIFIED_ARTIFACTS
      items: [changed files]
    - type: DELETED_ARTIFACTS
      items: [missing files]
    - type: STALE_CANDIDATES
      items: [>60 days no modification]
    - type: STATUS_UPDATES
      items: [complete artifact sets, status ≠ completed]
```

**Execute Plan:**
1. NEW_ARTIFACTS: Classify and register
2. MODIFIED_ARTIFACTS: Re-validate mapping
3. DELETED_ARTIFACTS: Remove from registry, log warning
4. STALE_CANDIDATES: Mark STALE or add note
5. STATUS_UPDATES: Update if all AC validated

### Step 4: Update YAML

- Increment version number
- Update last_updated timestamp
- Add changelog entry
- Preserve structure and formatting

### Step 5: Generate Report

- Execution mode used
- Artifacts processed by type
- Stories updated
- Manual review items
- Validation results
- Next recommended story

---

## 6. Usage Examples

### Example 1: Initial Population

**Prompt:**
```
Scan the project and populate artifact registries for all stories.
```

**Expected Output:**
- 91 artifacts discovered
- 85 mapped with HIGH confidence
- 4 mapped with MEDIUM confidence
- 2 added to manual review queue
- YAML version incremented

### Example 2: Maintenance Run

**Prompt:**
```
Refresh the backlog to register new artifacts created this week.
```

**Expected Behavior:**
- Detects 5 new files since last update
- Classifies and registers each
- Updates affected story artifact_registry
- Logs changes in changelog

### Example 3: Staleness Review

**Prompt:**
```
Check for stale artifacts and flag for cleanup.
```

**Expected Behavior:**
- Scans all registered artifacts
- Identifies files >60 days without modification
- Marks as STALE with staleness_note
- Lists in manual review queue

---

## 7. Integration Points

### Integration with yml-bck-mgr

```yaml
# yml-bck-refresh extends yml-bck-mgr backlog
workflow:
  1. yml-bck-mgr creates story structure
  2. yml-bck-refresh adds artifact_registry to stories
  3. Both update same YAML file
  4. Both increment version
```

### Integration with cycle-implement

```yaml
# Artifacts produced by cycle-implement registered by refresh
workflow:
  1. cycle-implement produces src/core/feature.py
  2. yml-bck-refresh scans, finds new file
  3. Matches to story P0-F1-001 by path pattern
  4. Registers in P0-F1-001.artifact_registry.implementation
```

---

## 8. Success Criteria

### Validation Rules

| Rule | Description |
|------|-------------|
| Registration Complete | Every source/test/doc file in artifact_registry |
| No Orphans | No artifact_registry entries for missing files |
| Dependency Consistent | Completed stories have completed dependencies |
| AC Validation | Status=completed only with validated AC |
| Staleness Threshold | >60 days → marked STALE |
| Confidence Validation | LOW → manual_review_queue |
| Version Increment | Version increases on every update |

### Quality Metrics

| Metric | Target |
|--------|--------|
| Registration Coverage | 100% of project files |
| HIGH Confidence Rate | ≥80% of mappings |
| Orphan Count | 0 |
| Staleness Detection | 100% of old files flagged |

---

## 9. Constraints

1. **No Unregistered Artifacts** - Every project file must be registered
2. **No Placeholders** - Only register real discovered files
3. **Status Preservation** - Don't modify dependencies, priorities, source fields
4. **No Auto-Delete** - STALE artifacts flagged, never deleted
5. **Validation Required** - Status→completed only with validated AC
6. **YAML Preservation** - Maintain structure, formatting, comments
7. **Relative Paths** - All file_path relative to project root

---

## 10. Error Handling

| Error Condition | Handling |
|-----------------|----------|
| File not found | Remove from registry, log warning |
| Ambiguous mapping | LOW confidence, add to manual_review |
| YAML parse error | Abort, preserve original |
| Permission denied | Skip file, log warning |
| Circular reference | Detect and report |

---

## Appendix: Confidence Scoring

### Scoring Criteria

| Match Type | Confidence | Example |
|------------|------------|---------|
| Exact path match | HIGH | `spikes/spike-03/src/core/discovery.py` → P0-F1-001 |
| Pattern match | MEDIUM | File contains "work_unit" → work_unit stories |
| Content keyword | MEDIUM | Class `WorkUnitDiscovery` → P0-F1-001 |
| Ambiguous | LOW | No clear story match |

### Staleness Thresholds

| Age | Status | Action |
|-----|--------|--------|
| <30 days | CURRENT | No action |
| 30-60 days | CURRENT | Review recommended |
| >60 days | STALE | Mark STALE, add to review queue |
