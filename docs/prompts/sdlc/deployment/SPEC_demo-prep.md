---
title: "Technical Specification: demo-prep"
version: 1.0
date: 2026-01-22
status: draft
purpose: "Documentation for Technical Specification: demo-prep"
---

# Technical Specification: demo-prep

**Prompt Name:** Demo Preparation
**Short Name:** `demo-prep`
**Version:** 1.0
**Stateful:** No
**SDLC Subdomain:** Deployment

---

## 1. Purpose & Objectives

### Primary Goal

Create a value-based demo experience from the existing project work.

### Key Objectives

1. **Project Analysis** - Understand purpose, goals, and progress
2. **Artifact Discovery** - Identify demo-able production and spike work
3. **Value Narratives** - Design demos that tell compelling value stories
4. **Demo Structure** - Create organized demo folder with documentation
5. **Run Instructions** - Provide exact commands with expected outputs

---

## 2. Input/Output Schemas

### Input Sources

| Source Type | Description | Purpose |
|-------------|-------------|---------|
| README | Project overview | Understand purpose |
| Architecture Docs | Design documentation | Understand structure |
| Spikes | Experimental work | Demo-able artifacts |
| Makefiles | Executable commands | Demo execution |
| Production Code | Working features | Demo targets |

### Input Format

```yaml
project_context:
  readme: "README.md"
  architecture_docs:
    - "docs/ARCHITECTURE.md"
    - "docs/DESIGN.md"

  spikes:
    - path: "spikes/spike-07/"
      makefile: "Makefile"
      status: "60% complete"

  production_code:
    - path: "src/core/"
      features: ["discovery", "classification"]

  make_registry: "MAKE_COMMAND_REGISTRY.yaml"
```

### Output Schema

```markdown
# Demo Package Documentation

## Section 1: Project Overview
**Purpose:** [Project purpose]
**Primary Goals:** [List of goals]
**Progress Summary:** [Current state vs goals]

## Section 2: Existing Demo-able Artifacts
### Production Features
- [Feature 1] - [Status] - [Demo potential]

### Make Targets
- `make target-1` - [What it demonstrates]

### Spike Scripts
- `spikes/spike-07/demo.py` - [Capability shown]

## Section 3: Demo Folder Structure
```
docs/demo/
├── README.md                 # Demo index
├── 01-work-unit-discovery/
│   ├── README.md            # Demo details
│   ├── run.sh               # Execution script
│   └── expected_output.json # Verification
├── 02-baseline-comparison/
│   └── ...
└── narrative.md             # End-to-end story
```

## Section 4: Demo Specifications

### Demo 1: Work Unit Discovery
**Name:** Automated Work Unit Discovery
**Value Story:**
> Problem: Manual tracking wastes 10+ hours/week
> Solution: Automated MCP discovery
> Value: 80% time reduction in activity logging

**Underlying Artifacts:**
- `spikes/spike-07/src/core/extractor.py`
- `make spike07-extract-live`

**Prerequisites:**
- Glean MCP access
- Environment configured

**Run Instructions:**
```bash
cd spikes/spike-07
make extract-live
```

**Expected Output:**
```
Extracted 15 work units from 2026-01-14 to 2026-01-21
Categories: 8 meetings, 4 documents, 3 presentations
JSON saved to: results/work_units_20260121.json
```

**Verification:**
- [ ] JSON file exists in results/
- [ ] Work units properly categorized
- [ ] No error messages

## Section 5: End-to-End Narrative
[How demos combine to tell the full project story]
```

---

## 3. Dependencies

### Required Inputs

| Dependency | Type | Description |
|------------|------|-------------|
| Project Codebase | Directory | Code to analyze |
| README | File | Project overview |
| Makefiles | Files | Executable commands |

### Runtime Dependencies

| Dependency | Purpose |
|------------|---------|
| `rep-mak-reg` | List of make commands |
| `quality-gate` | Validated features |
| File System | Read project structure |

### Downstream Consumers

| Consumer | Purpose |
|----------|---------|
| Stakeholders | Demo presentations |
| `update-readme` | Links to demos |
| Sales/Marketing | Customer demos |

---

## 4. Processing Steps

### Step 1: Analyze Project

**Actions:**
- Read main README
- Review architecture docs
- Skim key services/modules
- Identify entry points and APIs
- Review existing spikes/experiments

**Outputs:**
- Purpose understanding
- Target users identified
- Key goals listed
- Current progress assessment

### Step 2: Extract Demo-able Artifacts

**Actions:**
- Identify production features exercisable end-to-end
- List make targets that demonstrate capabilities
- Find spike scripts illustrating specific behaviors

**Artifact Categories:**
| Category | Examples |
|----------|----------|
| Production Code | Complete features, APIs |
| Make Targets | test-*, demo-*, report-* |
| Spike Scripts | Numbered experiments |
| Data Outputs | Generated reports, JSON |

### Step 3: Design Value-Based Demos

**Actions:**
- Group artifacts into coherent demo stories
- Prioritize by value and impressiveness
- Create 2-5 concrete demos
- Define clear value stories for each

**Value Story Template:**
```
Problem: [What pain point does this solve?]
Solution: [How does the demo address it?]
Value: [Quantified benefit or outcome]
```

### Step 4: Define Demo Folder Structure

**Actions:**
- Propose `docs/demo/` directory tree
- Create numbered demo folders
- Include README for each demo
- Add supporting files (scripts, expected outputs)

**Standard Structure:**
```
docs/demo/
├── README.md              # Index of all demos
├── 01-demo-name/
│   ├── README.md          # Purpose, value, instructions
│   ├── run.sh             # Optional: execution script
│   └── expected_output/   # Reference outputs
├── 02-demo-name/
│   └── ...
└── narrative.md           # Combined story
```

### Step 5: Specify Each Demo

**For Each Demo:**
- Name and short description
- Value story (problem → solution → value)
- Underlying artifacts (code, scripts, make targets)
- Prerequisites (setup, credentials, data)
- Step-by-step run instructions
- Expected outputs (exact or representative)
- Verification checklist

### Step 6: Build End-to-End Narrative

**Actions:**
- Chain demos into overall story
- Create "Day in the Life" or "Problem-to-Solution" flow
- Show how demos build on each other
- Connect to project goals

---

## 5. Usage Examples

### Example 1: Full Demo Package

**Prompt:**
```
Review the project and design a complete demo package.
```

**Expected Output:**
- Project overview (purpose, goals, progress)
- 4 identified demos from existing work
- Complete folder structure proposal
- Full specifications for each demo
- Narrative connecting all demos

### Example 2: Single Feature Demo

**Prompt:**
```
Create a demo for the work unit discovery feature.
```

**Expected Output:**
- Value story for discovery
- Make commands to run
- Expected output examples
- Verification steps
- Integration with other demos

### Example 3: Spike-Based Demos

**Prompt:**
```
Design demos using the spike-07 experimental work.
```

**Expected Output:**
- Inventory of spike-07 capabilities
- 2-3 demos from spike work
- Clear note that these are experimental
- Paths to production features

---

## 6. Integration Points

### Integration with rep-mak-reg

```yaml
# Demo uses cataloged make commands
workflow:
  1. rep-mak-reg catalogs all commands
  2. demo-prep reads MAKE_COMMAND_REGISTRY.yaml
  3. Identifies demo-relevant commands
  4. Includes in demo specifications
```

### Integration with quality-gate

```yaml
# Only validated work becomes demos
workflow:
  1. quality-gate validates features
  2. Validated features eligible for demo
  3. demo-prep creates demo specifications
  4. Demo runs verified to work
```

---

## 7. Success Criteria

### Validation Rules

| Rule | Description |
|------|-------------|
| Project Summary | Clear purpose, goals, progress |
| Demo Structure | Explicit folder paths and filenames |
| Value Stories | Each demo tied to user/business value |
| Artifact Mapping | Demos map to specific code/scripts |
| Run Instructions | Exact commands with expected results |
| Runnable | Unfamiliar person can execute demos |

### Quality Metrics

| Metric | Target |
|--------|--------|
| Demo Count | 2-5 demos |
| Value Story Coverage | 100% demos have value stories |
| Runnable Demos | 100% have exact commands |
| Documentation Completeness | All sections filled |

---

## 8. Constraints

1. **Existing Work Only** - Use current code and spikes
2. **End-to-End Runnable** - All demos must be executable
3. **Existing Make Targets** - Prefer existing commands
4. **Simple Structure** - Discoverable by new readers
5. **No New Tooling** - Use what exists

---

## 9. Error Handling

| Error Condition | Handling |
|-----------------|----------|
| No demo-able work | Document gaps, suggest priorities |
| Missing make targets | Note missing, suggest creation |
| Broken commands | Flag for fixing before demo |
| Incomplete features | Note as "preview" or "experimental" |

---

## 10. Output Format

### Required Sections

1. **Project Overview**
   - Purpose
   - Primary goals
   - Progress toward each goal

2. **Existing Demo-able Artifacts**
   - Production features
   - Make targets
   - Spike scripts

3. **Demo Folder Structure**
   - Directory tree in code block
   - File descriptions

4. **Demo Specifications** (per demo)
   - Name and description
   - Value story
   - Underlying artifacts
   - Prerequisites
   - Run instructions (commands)
   - Expected output
   - Verification

5. **End-to-End Narrative**
   - How demos combine
   - Overall story
   - Connection to project goals

---

## Appendix: Value Story Examples

### Knowledge Work Measurement

```
Problem: Organizations can't measure knowledge work productivity
Solution: Automated work unit discovery from enterprise tools
Value: First-ever visibility into knowledge labor cycles
```

### Time Savings

```
Problem: Manual activity logging takes 10+ hours/week
Solution: Automatic extraction from Glean MCP data
Value: 80% reduction in logging overhead
```

### Decision Quality

```
Problem: Gut-feel estimates for project planning
Solution: Baseline data from validated work samples
Value: Data-driven project estimates within 15% accuracy
```
