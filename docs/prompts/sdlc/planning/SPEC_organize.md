---
title: "Technical Specification: organize"
version: 1.0
date: 2026-01-22
status: draft
purpose: "Documentation for Technical Specification: organize"
---

# Technical Specification: organize

**Prompt Name:** Project Organizer
**Short Name:** `organize`
**Version:** 1.0
**Stateful:** Yes
**SDLC Subdomain:** Planning

---

## 1. Purpose & Objectives

### Primary Goal

Maintain a clean, unified organizational and metadata system for a project directory tree, even when previous runs have been executed on subfolders. Unify and reconcile multiple index files into a consistent hierarchy.

### Key Objectives

1. **Directory Organization** - Maintain coherent folder structure aligned with bounded contexts
2. **Metadata Management** - Ensure every file has up-to-date metadata
3. **Index Hierarchy** - Synchronize global and subfolder indices
4. **Multi-Run Robustness** - Handle repeated runs at different directory levels
5. **Consistency Enforcement** - Prevent contradictions between indices

---

## 2. Input/Output Schemas

### Input Sources

| Source Type | Description | Purpose |
|-------------|-------------|---------|
| Target Path | Directory to organize | Starting point for scan |
| Existing Indices | `index.yaml`, `index.md` files | Preserve existing organization |
| File Metadata | In-file metadata blocks | Source of truth for file purpose |

### Per-File Metadata Schema

```yaml
file_metadata:
  file_name: "example.py"               # Base name
  relative_path: "src/core/example.py"  # Path from root
  local_relative_path: "core/example.py"  # Optional: from subfolder root
  bounded_context: "work_unit_synthesis"  # 1-3 words
  intent: "Extract work units"           # Brief phrase
  purpose: "Extracts work units from MCP events using temporal grouping"
  version: "1.0.0"                       # Semantic version
  last_updated: "2026-01-21T10:30:00Z"  # ISO 8601
  tags: ["mcp", "extraction"]            # Optional
  status: "active"                       # active|deprecated|experimental
  source_index: "global"                 # Which index created this
```

### Global Index Output

```yaml
# index.yaml (at target path)
metadata:
  target_path: "/workspace/repo"
  created: "2026-01-21T10:30:00Z"
  last_updated: "2026-01-21T10:30:00Z"
  total_files: 150

bounded_contexts:
  - name: "work_unit_synthesis"
    path: "src/core/"
    file_count: 12

files:
  - file_name: "work_unit_discovery.py"
    relative_path: "src/core/work_unit_discovery.py"
    bounded_context: "work_unit_synthesis"
    intent: "Discover work units from MCP data"
    purpose: "Queries Glean MCP and identifies work unit candidates"
    version: "1.0.0"
    last_updated: "2026-01-21T10:30:00Z"
```

### Global Index Markdown

```markdown
# Project Index

**Target Path:** /workspace/repo
**Last Updated:** 2026-01-21
**Total Files:** 150

## Bounded Contexts

### work_unit_synthesis (12 files)
Core domain for grouping events into work units.

| File | Intent | Status |
|------|--------|--------|
| work_unit_discovery.py | Discover work units | Active |

## Directory Structure

```
src/
├── core/           # Core domain implementations
├── models/         # Data models
└── utils/          # Utilities
```
```

---

## 3. Dependencies

### Required Inputs

| Dependency | Type | Description |
|------------|------|-------------|
| Target Path | Directory | Directory to organize |
| File System | Access | Read/write permissions |

### Runtime Dependencies

| Dependency | Purpose |
|------------|---------|
| YAML Parser | Parse/write index files |
| File Scanner | Enumerate directory contents |

### Related Prompts

| Prompt | Relationship |
|--------|--------------|
| `yml-bck-refresh` | Uses artifact registry info |
| `ddd-make-align` | Shares bounded context definitions |

---

## 4. Execution Modes

### First Run (Global)

**Trigger:** No `index.yaml` exists at target path

**Actions:**
1. Discover all files and any existing subfolder indices
2. Merge or adopt existing subfolder metadata
3. Create new global `index.yaml` and `index.md`
4. Optionally create/refresh local indices

### Follow-Up Run (Global)

**Trigger:** `index.yaml` exists at target path

**Actions:**
1. Load existing global and local indices
2. Reconcile differences with filesystem
3. Update stale or conflicting entries
4. Synchronize all indices

### Subfolder Run

**Trigger:** Target path is a subfolder with local indices

**Actions:**
1. Treat subfolder as its own root
2. Maintain local index files
3. Ensure consistency with any known global metadata

---

## 5. Processing Steps

### Step 1: Detect Run Mode

```yaml
detection:
  if: index.yaml not at target_path
  then: first_run_global
  else if: index.yaml exists
  then: follow_up_global
  if: target_path is subfolder
  then: subfolder_run
```

### Step 2: Inventory & Parse

- Enumerate all files and directories
- Parse each discovered `index.yaml`
- Extract in-file metadata where present

### Step 3: Build Unified Metadata Map

**Priority Order (highest to lowest):**
1. Filesystem existence (ultimate authority)
2. In-file metadata
3. Closest-scoped index (local/subfolder)
4. Global index

### Step 4: Adjust Structure & Contexts

- Infer bounded contexts from folder structure
- Respect existing stable subfolder boundaries
- Update paths if files moved

### Step 5: Update In-File Metadata

- Write/update metadata sections
- Use idiomatic format (YAML frontmatter for .md, comments for .py)

### Step 6: Write Global Index

- Serialize all metadata to `index.yaml`
- Generate `index.md` with structure overview

### Step 7: Write Local Indices

- Update subfolder `index.yaml` files
- Ensure no contradictions with global

### Step 8: Validation

- Every file on disk in global index
- All required fields present
- Hierarchical consistency maintained

---

## 6. Usage Examples

### Example 1: Initial Organization

**Prompt:**
```
Organize the project at /workspace/repo and create comprehensive indices.
```

**Expected Output:**
- Created `/workspace/repo/index.yaml` with 150 files
- Created `/workspace/repo/index.md` with structure overview
- Identified 8 bounded contexts from folder structure

### Example 2: Subfolder Organization

**Prompt:**
```
Organize just the spikes/spike-07 folder.
```

**Expected Behavior:**
- Creates local `index.yaml` and `index.md` in spike-07
- Paths relative to spike-07 root
- Consistent with any global organization

### Example 3: Reconciliation

**Prompt:**
```
The project has been reorganized. Update all indices to reflect changes.
```

**Expected Behavior:**
- Detects file moves
- Updates relative_path in all indices
- Preserves metadata, updates version/timestamp
- Reports changes made

---

## 7. Integration Points

### Integration with yml-bck-refresh

```yaml
# organize uses artifact registry for context
workflow:
  1. yml-bck-refresh registers artifacts with story mappings
  2. organize reads artifact_registry for bounded_context hints
  3. organize uses story context to classify files
```

### Integration with ddd-make-align

```yaml
# Shared bounded context definitions
workflow:
  1. Both use same 8 bounded contexts
  2. organize aligns files to contexts
  3. ddd-make-align aligns commands to contexts
  4. Cross-reference for consistency
```

---

## 8. Success Criteria

### Validation Rules

| Rule | Description |
|------|-------------|
| File Coverage | Every file on disk in global index |
| Field Completeness | Required fields for all entries |
| Hierarchy Consistency | Local indices subset of global |
| Path Resolution | Local paths resolve to global paths |
| Multi-Run Robustness | No duplicates or conflicts on rerun |

### Quality Metrics

| Metric | Target |
|--------|--------|
| File Coverage | 100% |
| Metadata Completeness | 100% required fields |
| Context Assignment | 100% have bounded_context |
| Consistency Score | 0 contradictions |

---

## 9. Constraints

1. **No File Drops** - Never drop or duplicate files in global index
2. **Preserve Boundaries** - Respect stable subfolder contexts
3. **Concise Metadata** - bounded_context 1-3 words, intent brief phrase
4. **Valid YAML** - All index files parseable
5. **Valid Markdown** - All .md files properly formatted
6. **Minimal Nesting** - Avoid unnecessary depth

---

## 10. Error Handling

| Error Condition | Handling |
|-----------------|----------|
| Conflicting metadata | Use priority rules, log resolution |
| Missing files | Remove from index, log warning |
| New files | Add with inferred metadata |
| Invalid in-file metadata | Override from index, flag for fix |
| Circular references | Detect and break, report error |

---

## Appendix: In-File Metadata Formats

### Python Files

```python
# /// metadata
# file_name: example.py
# bounded_context: work_unit_synthesis
# intent: Extract work units
# version: 1.0.0
# last_updated: 2026-01-21T10:30:00Z
# ///
```

### Markdown Files

```markdown
---
file_name: README.md
bounded_context: documentation
intent: Project overview
version: 1.0.0
last_updated: 2026-01-21T10:30:00Z
---
```

### YAML Files

```yaml
# metadata:
#   file_name: config.yaml
#   bounded_context: configuration
#   intent: Application settings
#   version: 1.0.0
#   last_updated: 2026-01-21T10:30:00Z
```
