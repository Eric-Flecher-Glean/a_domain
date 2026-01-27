---
title: "Technical Specification: update-readme"
version: 1.0
date: 2026-01-22
status: draft
purpose: "Documentation for Technical Specification: update-readme"
---

# Technical Specification: update-readme

**Prompt Name:** Update Root README
**Short Name:** `update-readme`
**Version:** 1.0
**Stateful:** Yes
**SDLC Subdomain:** Maintenance

---

## 1. Purpose & Objectives

### Primary Goal

Review the codebase and history to update the root README with project progress and a clear learning story from spikes into roadmap and exploration areas.

### Key Objectives

1. **Codebase Review** - Analyze entire project structure
2. **History Analysis** - Extract spike learnings from git history
3. **Learning Synthesis** - Create coherent spike narrative
4. **Roadmap Derivation** - Connect learnings to future work
5. **README Update** - Produce updated, comprehensive README

---

## 2. Input/Output Schemas

### Input Sources

| Source Type | Description | Purpose |
|-------------|-------------|---------|
| Existing README | Current root README | Base for updates |
| Git History | Commits, branches, tags | Spike analysis |
| Spike Folders | Experimental work | Learning extraction |
| Project Structure | Directory tree | Context understanding |

### Input Format

```yaml
readme_update_input:
  existing_readme: "README.md"

  git_context:
    commit_history: true
    branch_analysis: true
    tag_analysis: true

  spikes:
    - path: "spikes/spike-01/"
      status: "complete"
    - path: "spikes/spike-02/"
      status: "complete"
    - path: "spikes/spike-07/"
      status: "in_progress"

  project_structure:
    analyze_directories: true
    key_components: []
```

### Output Schema

```markdown
# [Project Name]

## Overview
[Existing overview content, preserved if current]

## Current Project Status / Progress
**Last Updated:** [Date]

### Completed Work
- [Milestone 1] ✅
- [Milestone 2] ✅

### In Progress
- [Current work]

### Key Metrics
- [Metric 1]: [Value]
- [Metric 2]: [Value]

## Spike History & Learning Story

### Theme 1: [Theme Name]

#### Spike 01: [Spike Name]
**Goal:** [What we tried to achieve]
**What We Did:** [Brief description of experiments]
**What We Learned:** [Key insights and discoveries]
**Influence on Project:** [How this shaped later decisions]

#### Spike 02: [Spike Name]
...

### Theme 2: [Theme Name]
...

## Roadmap & Potential Exploration Areas

### Confirmed Roadmap Items
These items are derived from spike learnings and validated approaches:

1. **[Feature Name]**
   - Source: Spike [N] learning about [topic]
   - Status: [Planned/In Progress]
   - Expected: [Outcome]

2. **[Feature Name]**
   ...

### Potential Exploration Areas
These represent open questions or unresolved findings:

- **[Area Name]** - [Why this is worth exploring, connection to spike]
- **[Area Name]** - [Description]

## Getting Started
[Preserved or updated setup instructions]

## Contributing
[Preserved or updated contribution guidelines]

## License
[Preserved]
```

---

## 3. Dependencies

### Required Inputs

| Dependency | Type | Description |
|------------|------|-------------|
| README.md | File | Current readme to update |
| Git Repository | Directory | History analysis |
| Spike Folders | Directories | Learning extraction |

### Runtime Dependencies

| Dependency | Purpose |
|------------|---------|
| Git CLI | History access |
| File System | Read project structure |

### Downstream Consumers

| Consumer | Purpose |
|----------|---------|
| New Contributors | Onboarding |
| Stakeholders | Project understanding |
| `yml-bck-mgr` | Informs new stories |

---

## 4. Processing Steps

### Step 1: Scan Repository

**Actions:**
- Identify key directories and components
- Note existing documentation
- Find spike/experiment folders
- Identify roadmap references

### Step 2: Explore Git History

**Actions:**
- Identify spike-related commits/branches/tags
- Read commit messages and PR descriptions
- Infer goals and outcomes from history
- Map timeline of spike work

### Step 3: Synthesize Learning Story

**Actions:**
- Extract goal, approach, learning for each spike
- Group related spikes into themes
- Connect spikes chronologically
- Note how each influenced later work

**Per-Spike Template:**
```yaml
spike:
  name: "Spike 01: Individual Work Unit Measurement"
  goal: "Validate single-user work artifact measurement"
  tried: "Manual extraction of work samples"
  learned: "51.4 min average for demo decks (32 samples)"
  influenced: "Established baseline data for comparison"
```

### Step 4: Derive Roadmap

**Actions:**
- Map spike outcomes to roadmap items
- Identify confirmed features from learnings
- List open questions as exploration areas
- Connect each item back to its spike source

**Roadmap Mapping:**
```yaml
roadmap_item:
  name: "Automated Work Unit Discovery"
  source_spike: "Spike 03"
  learning: "Manual approach too slow, automation needed"
  status: "In Progress"
```

### Step 5: Design README Updates

**Actions:**
- Decide where to insert/update sections
- Plan new sections:
  - Current Project Status
  - Spike History & Learning Story
  - Roadmap & Exploration Areas
- Preserve useful existing content

### Step 6: Edit README

**Actions:**
- Preserve overview, setup, usage
- Add/update status section
- Add/update learning story section
- Add/update roadmap section
- Ensure self-contained narrative

### Step 7: Review and Refine

**Actions:**
- Verify understandable to new contributors
- Check spike-to-roadmap connections explicit
- Validate Markdown formatting
- Ensure all sections complete

---

## 5. Usage Examples

### Example 1: Full Update

**Prompt:**
```
Update the root README with project progress and learning story from all spikes.
```

**Expected Output:**
- Current progress summary (3 of 8 spikes complete)
- Learning story for each completed spike
- Roadmap with 5 items traced to spike learnings
- 3 exploration areas from open questions

### Example 2: Milestone Update

**Prompt:**
```
Update README to reflect completion of Spike 07.
```

**Expected Behavior:**
- Adds Spike 07 to learning story
- Updates roadmap with new confirmed items
- Marks related exploration areas as addressed
- Updates progress metrics

### Example 3: Focused Update

**Prompt:**
```
Update README roadmap section based on recent learnings.
```

**Expected Behavior:**
- Reviews most recent spike outcomes
- Adds new roadmap items
- Connects to specific learnings
- Preserves existing content

---

## 6. Integration Points

### Integration with update-status

```yaml
# Status informs README updates
workflow:
  1. update-status produces progress report
  2. update-readme incorporates status summary
  3. README reflects current state
```

### Integration with yml-bck-mgr

```yaml
# Roadmap items become backlog stories
workflow:
  1. update-readme identifies roadmap items
  2. Items inform new story creation
  3. yml-bck-mgr adds stories to backlog
  4. Cycle continues
```

---

## 7. Success Criteria

### Validation Rules

| Rule | Description |
|------|-------------|
| Progress Summary | Clear current project status |
| Spike History | Concrete references to spike work |
| Learning Influence | How learnings shaped decisions |
| Roadmap Traced | Items clearly connected to spikes |
| Self-Contained | Understandable without git history |
| Contributor Friendly | Clear where to start, what to expect |

### Quality Metrics

| Metric | Target |
|--------|--------|
| Spike Coverage | All spikes documented |
| Roadmap Traceability | 100% items traced to source |
| New Contributor Test | Understandable in 5 min |

---

## 8. Constraints

1. **Preserve Critical Content** - Don't remove essential README info
2. **Both Audiences** - Readable for technical and semi-technical
3. **Markdown Only** - Valid Markdown formatting
4. **Specific Learnings** - Grounded in actual spike work
5. **Explicit Connections** - Don't imply, state connections directly

---

## 9. Error Handling

| Error Condition | Handling |
|-----------------|----------|
| No git history | Note limitation, use file timestamps |
| Incomplete spikes | Document what exists, note gaps |
| Missing README | Create from template |
| Conflicting info | Use most recent source, note conflict |

---

## 10. Output Format

### Required README Sections

1. **Overview** (preserve/update existing)
2. **Current Project Status**
   - Completed work
   - In progress work
   - Key metrics
3. **Spike History & Learning Story**
   - Grouped by theme
   - Per-spike: goal, tried, learned, influenced
4. **Roadmap & Exploration Areas**
   - Confirmed items (traced to spikes)
   - Potential exploration (from open questions)
5. **Getting Started** (preserve/update)
6. **Contributing** (preserve)

### Output Deliverables

- Full, updated README.md content as Markdown
- Optional: Short change summary preceding content
- Optional: Unified diff showing evolution

---

## Appendix: Learning Story Template

```markdown
### Spike [N]: [Name]

**Goal:** [1 sentence on what we tried to achieve]

**What We Tried:**
- [Approach 1]
- [Approach 2]

**What We Learned:**
- [Key insight 1]
- [Key insight 2]

**How It Influenced Later Work:**
- [Decision made because of this learning]
- [Feature designed based on this insight]

**Connection to Roadmap:**
- [Roadmap Item]: Derived from [specific learning]
```
