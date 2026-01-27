---
title: "Technical Specification: diagram"
version: 1.0
date: 2026-01-22
status: draft
purpose: "Documentation for Technical Specification: diagram"
---

# Technical Specification: diagram

**Prompt Name:** Diagram Generator
**Short Name:** `diagram`
**Version:** 1.0
**Stateful:** No
**SDLC Subdomain:** Deployment

---

## 1. Purpose & Objectives

### Primary Goal

Analyze and document the structure and behavior of a targeted folder containing code and design assets, producing ASCII-based documentation artifacts.

### Key Objectives

1. **Structure Analysis** - Scan and classify folder contents
2. **Architecture Inference** - Identify components and relationships
3. **Data Modeling** - Extract entities and relationships
4. **Process Mapping** - Derive workflows and control flows
5. **ASCII Visualization** - Represent all diagrams in ASCII only

---

## 2. Input/Output Schemas

### Input Sources

| Source Type | Description | Purpose |
|-------------|-------------|---------|
| Target Folder | Directory path | Scope of analysis |
| Source Code | .py, .js, etc. | Component discovery |
| Config Files | .yaml, .json, etc. | Configuration mapping |
| Documentation | .md, .txt | Context and design intent |
| Build Files | Makefile, etc. | Build relationships |

### Input Format

```yaml
diagram_input:
  target_path: "spikes/spike-07-action-item-driven-work-units/"
  include_patterns:
    - "*.py"
    - "*.yaml"
    - "*.md"
  exclude_patterns:
    - "__pycache__"
    - ".git"
```

### Output Schema

```markdown
# Folder Documentation: [folder_name]

## 1. Overview
**Summary:** [System description]
**Technology Hints:** [Frameworks, languages detected]

## 2. Folder & File Summary
| Directory/File | Description |
|----------------|-------------|
| src/core/ | Core business logic |
| src/models/ | Data model definitions |
| tests/ | Test suite |

## 3. ASCII Architecture Diagram(s)

```
┌─────────────────────────────────────────────────────────────┐
│                    SYSTEM ARCHITECTURE                       │
└─────────────────────────────────────────────────────────────┘

  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
  │   Extractor  │────▶│   Assembler  │────▶│   Reporter   │
  │              │     │              │     │              │
  │  MCP Queries │     │  Grouping    │     │  Output Gen  │
  └──────────────┘     └──────────────┘     └──────────────┘
         │                    │                    │
         ▼                    ▼                    ▼
  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
  │  MCP Client  │     │   WorkUnit   │     │   JSON/MD    │
  │   (Glean)    │     │    Model     │     │   Output     │
  └──────────────┘     └──────────────┘     └──────────────┘
```

**Explanation:** [Description of architecture]

## 4. Data Models & ASCII Data Diagrams

### Main Entities
- **WorkUnit** - Represents a unit of knowledge work
- **ActionItem** - An extracted action item from meetings

### Entity Relationship Diagram

```
  ┌─────────────────┐         ┌─────────────────┐
  │    WorkUnit     │         │   ActionItem    │
  ├─────────────────┤         ├─────────────────┤
  │ id: str         │         │ id: str         │
  │ title: str      │    1:N  │ description: str│
  │ duration: int   │◀────────│ work_unit_id: FK│
  │ documents: []   │         │ status: str     │
  └─────────────────┘         └─────────────────┘
```

## 5. Processes, Maps, and Flows

### Core Workflow: Work Unit Discovery

```
  ┌─────────┐
  │  START  │
  └────┬────┘
       │
       ▼
  ┌─────────────────┐
  │ Query MCP       │
  │ user_activity   │
  └────────┬────────┘
           │
           ▼
  ┌─────────────────┐
  │ Parse Events    │
  │ to Documents    │
  └────────┬────────┘
           │
           ▼
  ┌─────────────────┐     ┌─────────────────┐
  │ Group by        │     │ Too few events? │
  │ temporal rules  │────▶│ (decision)      │
  └────────┬────────┘     └────────┬────────┘
           │                       │ Yes
           │ No                    ▼
           │              ┌─────────────────┐
           │              │ Request more    │
           │              │ date range      │
           │              └─────────────────┘
           ▼
  ┌─────────────────┐
  │ Create WorkUnit │
  │ objects         │
  └────────┬────────┘
           │
           ▼
  ┌─────────┐
  │   END   │
  └─────────┘
```

## 6. File-to-Concept Mapping

| Concept | Primary File(s) |
|---------|-----------------|
| MCP Query Handler | src/core/extractor.py |
| Work Unit Model | src/models/work_unit.py |
| Temporal Grouping | src/core/assembler.py |
| JSON Output | src/core/reporter.py |

## 7. Onboarding & Maintenance Notes

### Recommended Reading Order
1. Start with `README.md` for context
2. Read `src/models/` to understand data structures
3. Study `src/core/extractor.py` for entry point
4. Review `tests/` for usage examples

### Notable Design Patterns
- **Dataclass Models** - All entities use Python dataclasses
- **Pipeline Pattern** - Extract → Assemble → Report

### Areas Requiring Caution
- MCP rate limiting not yet implemented
- Error handling minimal in prototype
```

---

## 3. Dependencies

### Required Inputs

| Dependency | Type | Description |
|------------|------|-------------|
| Target Folder | Directory | Scope for analysis |
| File Access | Permission | Read access to files |

### Runtime Dependencies

| Dependency | Purpose |
|------------|---------|
| File System | Scan and read files |
| Code Parser | Understand structure |

### Downstream Consumers

| Consumer | Purpose |
|----------|---------|
| New Contributors | Onboarding documentation |
| `demo-prep` | Architecture reference |
| `update-readme` | Documentation source |

---

## 4. Processing Steps

### Step 1: Scan and Summarize Folder

**Actions:**
- List main directories and important files
- Describe role of each major area
- Note technologies/frameworks detected

**Output:**
- Directory tree summary
- File type classification
- Technology stack identification

### Step 2: Infer Architecture

**Actions:**
- Identify main components, services, modules
- Describe how they interact
- Map calls, dependencies, data flows

**Output:**
- ASCII architecture diagram
- Component descriptions
- Relationship explanations

### Step 3: Extract Data Models

**Actions:**
- Identify key entities, schemas, models
- Describe important fields
- Map relationships (1:1, 1:N, N:M)

**Output:**
- Entity list with descriptions
- ASCII ER-style diagrams
- Relationship documentation

### Step 4: Map Processes and Flows

**Actions:**
- Identify primary processes/workflows
- Map business or system processes
- Create sequence/flowcharts

**Output:**
- Process descriptions
- ASCII flowcharts
- Decision point documentation

### Step 5: Connect Artifacts to Files

**Actions:**
- Reference key files for each concept
- Note configuration points
- Document integration points

**Output:**
- File-to-concept mapping table
- Entry point identification
- Configuration reference

### Step 6: Provide Onboarding Guide

**Actions:**
- Recommend reading order
- Highlight risks and complexities
- Note non-obvious design decisions

**Output:**
- Reading order recommendation
- Design pattern notes
- Caution areas

---

## 5. Usage Examples

### Example 1: Spike Documentation

**Prompt:**
```
Generate ASCII documentation for spikes/spike-07-action-item-driven-work-units/
```

**Expected Output:**
- Overview of spike purpose
- 5 main directories documented
- Architecture diagram showing pipeline
- Data model for ActionItem and WorkUnit
- Workflow flowchart for extraction
- Recommended reading order

### Example 2: Module Documentation

**Prompt:**
```
Document the src/core/ module with architecture diagrams.
```

**Expected Output:**
- Summary of core module purpose
- Component diagram (4 main files)
- Data flow through core components
- File-to-concept mapping

### Example 3: Onboarding Doc

**Prompt:**
```
Create onboarding documentation for new contributors to this folder.
```

**Expected Output:**
- High-level overview
- Reading order (1-2-3-4)
- Key concepts explained
- "Where to start" guidance

---

## 6. Integration Points

### Integration with demo-prep

```yaml
# Diagrams inform demo documentation
workflow:
  1. diagram generates architecture visualization
  2. demo-prep references architecture
  3. Demos include system understanding
```

### Integration with update-readme

```yaml
# README may embed diagrams
workflow:
  1. diagram generates ASCII diagrams
  2. update-readme incorporates diagrams
  3. README shows system architecture
```

---

## 7. Success Criteria

### Validation Rules

| Rule | Description |
|------|-------------|
| Architecture Diagram | At least one clear ASCII diagram |
| Data Model | Primary entities identified and diagrammed |
| Process Flow | At least one ASCII flow for critical path |
| ASCII Only | All diagrams in plain ASCII characters |
| File References | Concepts map to concrete files |
| Understandable | New engineer can understand system |

### Quality Metrics

| Metric | Target |
|--------|--------|
| Diagram Count | ≥3 (architecture, data, flow) |
| File Coverage | Main files documented |
| Concept Coverage | Key concepts explained |
| Readability | Understandable without source |

---

## 8. Constraints

1. **ASCII Only** - No images or rich graphics
2. **Evidence-Based** - Only infer from folder contents
3. **Organized Sections** - Clearly labeled structure
4. **Concise but Complete** - Enough for onboarding
5. **Monospace Friendly** - Renders correctly in terminals

---

## 9. Error Handling

| Error Condition | Handling |
|-----------------|----------|
| Empty folder | Note as empty, no diagrams |
| Binary files | Skip, note in summary |
| Complex structure | Simplify, note limitations |
| Uncertain inference | State assumption explicitly |

---

## 10. Output Format

### Required Sections

1. **Overview** (1-2 paragraphs)
   - System summary
   - Technology hints

2. **Folder & File Summary**
   - Table of directories/files
   - Brief descriptions

3. **ASCII Architecture Diagram(s)**
   - Box-and-arrow diagrams
   - Component labels
   - Textual explanation

4. **Data Models & ASCII Data Diagrams**
   - Entity list
   - ER-style diagrams
   - Relationship descriptions

5. **Processes, Maps, and Flows**
   - Workflow descriptions
   - Flowcharts/sequence diagrams

6. **File-to-Concept Mapping**
   - Table: concept → file(s)

7. **Onboarding & Maintenance Notes**
   - Reading order
   - Design patterns
   - Caution areas

---

## Appendix: ASCII Diagram Elements

### Box Characters

```
┌──────┐  ╔══════╗  +------+
│      │  ║      ║  |      |
└──────┘  ╚══════╝  +------+
```

### Arrow Characters

```
────▶  ◀────  │  ▼  ▲  ←  →
```

### Flow Elements

```
Decision Diamond:
    ◇
   / \
  /   \
 /     \

Process Box:
┌─────────────┐
│  Process    │
└─────────────┘

Start/End:
(  START  )
```
