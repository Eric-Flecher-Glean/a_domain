---
title: "Technical Specification: yml-bck-mgr"
version: 1.0
date: 2026-01-22
status: draft
purpose: "Documentation for Technical Specification: yml-bck-mgr"
---

# Technical Specification: yml-bck-mgr

**Prompt Name:** YAML Backlog Manager
**Short Name:** `yml-bck-mgr`
**Version:** 1.0
**Stateful:** Yes
**SDLC Subdomain:** Requirements

---

## 1. Purpose & Objectives

### Primary Goal

Create and maintain a single-source-of-truth YAML backlog file that organizes all implementation and testing stories in priority order with mapped dependencies, and configure Claude Code to use this file for state management throughout the development lifecycle.

### Key Objectives

1. **Parse Source Documents** - Extract stories from implementation plans, design docs, and specifications
2. **Priority Classification** - Categorize stories as P0, P1, P2, P3
3. **Dependency Mapping** - Establish relationships between stories using unique IDs
4. **State Management** - Track story status throughout lifecycle
5. **Claude Code Integration** - Configure AI assistant to use backlog for session state

---

## 2. Input/Output Schemas

### Input Sources

| Source Type | Description | Example |
|-------------|-------------|---------|
| Implementation Plans | Technical plans with phases and tasks | `IMPLEMENTATION_PLAN.md` |
| Design Documents | Architecture and design specifications | `DESIGN_SPEC.md` |
| Test Plans | Test cases and validation requirements | `TEST_PLAN.md` |
| Specifications | Feature specifications | `FEATURE_SPEC.md` |

### Input Format

```yaml
# Prompt expects to parse documents containing:
- Priority indicators (P0, P1, P2, etc.)
- Section references (Section 5, Section 6)
- Task lists with dependencies
- Test case identifiers (TC1-TC35)
- Acceptance criteria
```

### Output Schema

```yaml
# IMPLEMENTATION_BACKLOG.yaml
backlog_metadata:
  last_updated: "2026-01-21T10:30:00Z"  # ISO 8601 timestamp
  version: 1                             # Integer, incremented on update
  source_documents:                      # List of parsed sources
    - "IMPLEMENTATION_PLAN.md"
    - "TEST_PLAN.md"

stories:
  - story_id: "P0-001"                   # Unique identifier
    priority: P0                          # P0|P1|P2|P3
    title: "Work Unit Discovery"          # Short title
    description: "Implement MCP-based work unit discovery"
    dependencies:                         # List of story_ids
      - "P0-000"
    status: not_started                   # not_started|in_progress|completed|blocked
    source: "IMPLEMENTATION_PLAN.md#Section5"
    test_cases:                           # Optional
      - "TC1"
      - "TC2"
    acceptance_criteria:                  # Optional
      - "AC1: Must query Glean MCP"
      - "AC2: Must return valid WorkUnit objects"
```

---

## 3. Dependencies

### Required Inputs

| Dependency | Type | Description |
|------------|------|-------------|
| Source Documents | Files | At least one document with extractable stories |
| Existing Backlog | Optional | Previous `IMPLEMENTATION_BACKLOG.yaml` for updates |

### Runtime Dependencies

| Dependency | Purpose |
|------------|---------|
| File System | Read source docs, write YAML backlog |
| YAML Parser | Parse/write valid YAML |

### Downstream Consumers

| Consumer | Purpose |
|----------|---------|
| `cycle-implement` | Reads backlog for next work item |
| `yml-bck-refresh` | Extends with artifact registry |
| `update-status` | Reads for status reporting |

---

## 4. Execution Modes

### Bootstrap Mode (First Run)

**Trigger:** No `IMPLEMENTATION_BACKLOG.yaml` exists

**Actions:**
1. Scan all source documents
2. Extract all stories with metadata
3. Classify priorities (P0-P3)
4. Map dependencies
5. Create new YAML backlog file
6. Configure Claude Code integration

### Update Mode (Subsequent Runs)

**Trigger:** `IMPLEMENTATION_BACKLOG.yaml` exists

**Actions:**
1. Parse new source documents
2. Append new stories without overwriting
3. Preserve existing status values
4. Update version number and timestamp
5. Validate dependency references

---

## 5. Usage Examples

### Example 1: Initial Backlog Creation

**Prompt:**
```
Parse the implementation plan and test plan to create a YAML backlog.
Focus on P0 features first: Work Unit Discovery, Baseline Comparison, GTM Motion.
```

**Expected Output:**
```yaml
backlog_metadata:
  last_updated: "2026-01-21T10:30:00Z"
  version: 1
  source_documents:
    - "IMPLEMENTATION_PLAN.md"
    - "TEST_PLAN.md"

stories:
  - story_id: "P0-F1-001"
    priority: P0
    title: "Work Unit Discovery"
    description: "Implement MCP-based work unit discovery from user activity"
    dependencies: []
    status: not_started
    source: "IMPLEMENTATION_PLAN.md#Section5.1"
    acceptance_criteria:
      - "AC1.1: Query Glean MCP user_activity endpoint"
      - "AC1.2: Return valid WorkUnit objects"
```

### Example 2: Update Existing Backlog

**Prompt:**
```
Update the backlog with new stories from the revised design document.
Preserve all existing story statuses.
```

**Expected Behavior:**
- Existing stories remain unchanged
- New stories appended with new IDs
- Version incremented
- Timestamp updated

---

## 6. Integration Points

### Integration with cycle-implement

```yaml
# cycle-implement reads backlog to determine next work item
session_start:
  1. Read IMPLEMENTATION_BACKLOG.yaml
  2. Find highest priority story with status=not_started
  3. Check all dependencies have status=completed
  4. Select story and begin execution
```

### Integration with yml-bck-refresh

```yaml
# yml-bck-refresh extends stories with artifact_registry
stories:
  - story_id: "P0-F1-001"
    # ... existing fields ...
    artifact_registry:           # Added by yml-bck-refresh
      implementation:
        - file_path: "src/core/discovery.py"
      tests:
        - file_path: "tests/test_discovery.py"
```

---

## 7. Success Criteria

### Validation Rules

| Rule | Description |
|------|-------------|
| Unique IDs | Every story must have unique `story_id` |
| Valid Dependencies | All dependency refs must point to valid story_ids |
| Consistent Priorities | Must use P0, P1, P2, P3 scheme |
| Source Traceability | Each story must have source reference |
| Valid YAML | Output must be parseable YAML |
| Status Enum | Status must be one of four valid values |
| Preserved State | Existing status values must not be overwritten |

### Quality Metrics

| Metric | Target |
|--------|--------|
| Story Coverage | 100% of identified tasks have stories |
| Dependency Completeness | 100% of known dependencies mapped |
| Source Traceability | 100% of stories have source reference |

---

## 8. Constraints

1. **Idempotent** - Safe to run multiple times without corruption
2. **No Implementation Trigger** - Only creates/updates backlog, does not execute work
3. **Source-Based** - All stories must come from actual documents
4. **Audit Trail** - Maintain chronological audit of updates
5. **Valid References** - Dependencies must reference existing story IDs

---

## 9. Error Handling

| Error Condition | Handling |
|-----------------|----------|
| Duplicate story_id | Reject with error, do not overwrite |
| Invalid dependency reference | Add to validation errors, flag for review |
| Missing source document | Skip extraction, log warning |
| Malformed YAML | Fail operation, preserve original |
| Missing required fields | Add placeholder with TODO marker |

---

## 10. Configuration

### Claude Code Integration

```yaml
# CLAUDE.md configuration
session_start_protocol:
  - Read IMPLEMENTATION_BACKLOG.yaml
  - Display current progress
  - Identify next available stories

session_end_protocol:
  - Update story status if work completed
  - Increment version
  - Add changelog entry
```

---

## Appendix: Complete Field Reference

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `story_id` | string | Yes | Unique identifier (e.g., "P0-F1-001") |
| `priority` | enum | Yes | P0, P1, P2, or P3 |
| `title` | string | Yes | Short descriptive title |
| `description` | string | Yes | Detailed description |
| `dependencies` | array | Yes | List of story_ids (can be empty) |
| `status` | enum | Yes | not_started, in_progress, completed, blocked |
| `source` | string | Yes | Document reference with section |
| `test_cases` | array | No | List of test case IDs |
| `acceptance_criteria` | array | No | List of AC descriptions |
| `tasks` | array | No | Breakdown of sub-tasks |
| `estimated_effort` | string | No | Time estimate |
| `assignee` | string | No | Assigned person/team |
