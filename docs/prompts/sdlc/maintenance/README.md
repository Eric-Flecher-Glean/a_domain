---
title: "Maintenance Subdomain"
version: 1.0
date: 2026-01-22
status: draft
purpose: "Documentation for Maintenance Subdomain"
---

# Maintenance Subdomain

**SDLC Phase:** Operations & Maintenance
**Prompts in Domain:** 2
**Primary Focus:** Documentation updates, status tracking, project health

---

## Domain Overview

The Maintenance subdomain contains prompts responsible for updating documentation, tracking status, and maintaining project health. These prompts close the SDLC loop by feeding back into requirements.

### Key Responsibilities

1. **README Updates** - Keep root README current with progress
2. **Status Reporting** - Produce comprehensive progress reports
3. **Learning Capture** - Document spike learnings and outcomes
4. **Roadmap Evolution** - Connect learnings to future work
5. **Stakeholder Communication** - Synthesize work for audiences

---

## Prompts in This Domain

| Prompt | Short Name | Tech Spec |
|--------|------------|-----------|
| `update_root_readme.xml` | `update-readme` | [SPEC_update-readme.md](./SPEC_update-readme.md) |
| `update_status.xml` | `update-status` | [SPEC_update-status.md](./SPEC_update-status.md) |

---

## Domain Connectivity

### Upstream Dependencies

| Provider Domain | Provider Prompt | Data Provided |
|-----------------|-----------------|---------------|
| Requirements | `yml-bck-mgr` | Backlog state |
| Deployment | `demo-prep` | Demo documentation |
| Testing | `quality-gate` | Validation results |
| Implementation | All | Completed artifacts |

### Downstream Consumers

| Consumer Domain | Consumer Prompt | Integration Point |
|-----------------|-----------------|-------------------|
| Requirements | `yml-bck-mgr` | Informs new stories |
| Requirements | `scope-change` | Triggers scope updates |
| External | Stakeholders | Status communications |

### Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                     MAINTENANCE DOMAIN                          │
└─────────────────────────────────────────────────────────────────┘

  Project History                     Updated README
  ┌──────────────────┐               ┌────────────────────┐
  │ Git History      │               │ Progress Summary   │
  │ Spikes           │ ─update-readme─▶│ Learning Story    │
  │ Current README   │               │ Roadmap            │
  └──────────────────┘               └────────────────────┘

  Status Inputs                       Progress Report
  ┌──────────────────┐               ┌────────────────────┐
  │ Reported Progress│               │ Executive Summary  │
  │ Planned Work     │ ─update-status─▶│ Completed Work    │
  │ Risks/Blockers   │               │ Next Steps         │
  └──────────────────┘               └────────────────────┘

                    FEEDBACK LOOP
                         │
                         ▼
              ┌──────────────────┐
              │  REQUIREMENTS    │
              │  (New Stories)   │
              └──────────────────┘
```

---

## Shared Concepts

### README Structure

```markdown
# Project Name

## Current Project Status
- [Progress summary]
- [Key metrics]

## Spike History & Learning Story
### Spike 1: [Name]
- **Goal:** [What we tried]
- **Learning:** [What we discovered]
- **Influence:** [How it shaped decisions]

### Spike 2: [Name]
...

## Roadmap & Exploration Areas
### Confirmed Roadmap
1. [Feature derived from learnings]

### Potential Exploration
- [Open question from spikes]
```

### Status Report Structure

```markdown
# Project Progress Report

## Executive Summary
- [2-5 bullets on overall status]

## Completed Work
- [By workstream/milestone]

## Current Status & In-Progress
- [Active work items]
- [On track / At risk / Blocked status]

## Planned Work
- [Upcoming tasks/phases]

## Risks, Blockers, Dependencies
- [Known issues with mitigation]

## Detailed Next Steps
- [Specific, actionable items]

## Open Questions
- [Items needing clarification]
```

---

## Usage Patterns

### README Update Workflow

```bash
# 1. Analyze git history and spike outcomes
# Prompt: "Update README with project progress and learning story"

# 2. Synthesize spike learnings into narrative
# Connect each spike to decisions/roadmap

# 3. Update root README with:
#    - Current status
#    - Learning story
#    - Roadmap items
```

### Status Report Workflow

```bash
# 1. Gather all status inputs
#    - Backlog state
#    - Recent completions
#    - Upcoming work

# 2. Generate comprehensive report
# Prompt: "Produce project progress report with next steps"

# 3. Report includes:
#    - Executive summary
#    - Detailed completed/planned work
#    - Actionable next steps
```

---

## Feedback Loop Integration

The Maintenance subdomain completes the SDLC cycle:

```
Requirements → Planning → Implementation → Testing → Deployment
     ↑                                                    │
     │                                                    │
     └────────────── Maintenance ◀────────────────────────┘

1. update-status identifies gaps and open questions
2. update-readme captures learnings and roadmap items
3. Learnings feed back into yml-bck-mgr as new stories
4. Open questions trigger scope-change for clarification
```

---

## Best Practices

1. **Regular Updates** - Update README after each significant milestone
2. **Specific Learnings** - Ground spike stories in concrete work
3. **Traceable Roadmap** - Connect roadmap items to spike outcomes
4. **Actionable Next Steps** - Make follow-ups specific and assignable
5. **Stakeholder Clarity** - Write for both technical and non-technical readers

---

## Related Documentation

- [SDLC Domain Index](../SDLC_PROMPT_DOMAIN_INDEX.md)
- [Deployment Domain](../deployment/README.md) (previous phase)
- [Requirements Domain](../requirements/README.md) (feedback loop)
