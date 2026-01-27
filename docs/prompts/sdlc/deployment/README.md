---
title: "Deployment Subdomain"
version: 1.0
date: 2026-01-22
status: draft
purpose: "Documentation for Deployment Subdomain"
---

# Deployment Subdomain

**SDLC Phase:** Release & Deployment
**Prompts in Domain:** 2
**Primary Focus:** Demo preparation, visualization, release readiness

---

## Domain Overview

The Deployment subdomain contains prompts responsible for preparing demonstrations and release-ready artifacts. These prompts transform validated work into presentable deliverables.

### Key Responsibilities

1. **Demo Design** - Create value-based demo experiences
2. **Visualization** - Generate ASCII architecture and flow diagrams
3. **Artifact Organization** - Structure demo folder with documentation
4. **Narrative Building** - Connect demos into coherent stories
5. **Run Instructions** - Provide exact commands and expected outputs

---

## Prompts in This Domain

| Prompt | Short Name | Tech Spec |
|--------|------------|-----------|
| `demo-prep.xml` | `demo-prep` | [SPEC_demo-prep.md](./SPEC_demo-prep.md) |
| `diagram.xml` | `diagram` | [SPEC_diagram.md](./SPEC_diagram.md) |

---

## Domain Connectivity

### Upstream Dependencies

| Provider Domain | Provider Prompt | Data Provided |
|-----------------|-----------------|---------------|
| Testing | `quality-gate` | Validated work |
| Implementation | `rep-mak-reg` | Make commands for demos |
| Planning | `organize` | Project structure |

### Downstream Consumers

| Consumer Domain | Consumer Prompt | Integration Point |
|-----------------|-----------------|-------------------|
| Maintenance | `update-readme` | Demo documentation |
| Maintenance | `update-status` | Demo readiness status |
| External | Stakeholders | Demo presentations |

### Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                     DEPLOYMENT DOMAIN                           │
└─────────────────────────────────────────────────────────────────┘

  Project State                       Demo Package
  ┌──────────────────┐               ┌────────────────────┐
  │ Validated Code   │               │ docs/demo/         │
  │ Make Commands    │ ──demo-prep──▶│   demo-1/          │
  │ Spike Work       │               │   demo-2/          │
  └──────────────────┘               │ Run instructions   │
                                     └────────────────────┘

  Codebase                            ASCII Documentation
  ┌──────────────────┐               ┌────────────────────┐
  │ Source Files     │               │ Architecture       │
  │ Configurations   │ ───diagram───▶│ Data Models        │
  │ Documentation    │               │ Process Flows      │
  └──────────────────┘               └────────────────────┘
```

---

## Shared Concepts

### Demo Structure

```yaml
demo_specification:
  name: "Work Unit Discovery Demo"
  description: "Demonstrates MCP-based work unit discovery"

  value_story: |
    Problem: Manual tracking of knowledge work is time-consuming
    Solution: Automated discovery from Glean MCP data
    Value: 50+ hours saved per quarter

  underlying_artifacts:
    - path: "spikes/spike-07/src/core/extractor.py"
      type: production_code
    - target: "make spike07-extract-live"
      type: make_command

  run_instructions:
    prerequisites:
      - "Glean MCP access configured"
      - "Environment variables set"
    steps:
      - command: "make spike07-extract-live"
        expected_output: "Extracted 15 work units"
    verification:
      - "JSON output in results/"
      - "Work units properly classified"
```

### ASCII Diagram Types

| Type | Purpose | Example |
|------|---------|---------|
| Architecture | Component relationships | `[API] --> [Service] --> [DB]` |
| Data Model | Entity relationships | Entity-Relationship diagrams |
| Process Flow | Workflow sequences | Flowcharts with decision points |
| Sequence | Interaction over time | Call sequences between components |

---

## Usage Patterns

### Demo Preparation

```bash
# 1. Analyze project for demo-able artifacts
# Prompt: "Review the project and design value-based demos"

# 2. Create demo folder structure
# Output: docs/demo/ with organized demos

# 3. Each demo has:
#    - Purpose and value story
#    - Make commands to run
#    - Expected outputs
#    - Verification steps
```

### Architecture Visualization

```bash
# 1. Analyze target folder/codebase
# Prompt: "Generate ASCII documentation for spikes/spike-07/"

# 2. Output includes:
#    - Architecture diagram
#    - Data model diagram
#    - Process flow diagram
#    - File-to-concept mapping
```

---

## Best Practices

1. **Value-Based** - Every demo tells a value story
2. **Runnable** - All demos have exact commands
3. **ASCII Only** - No external image dependencies
4. **Existing Artifacts** - Use current work, don't create new code
5. **Discoverable** - Clear folder structure for new readers

---

## Related Documentation

- [SDLC Domain Index](../SDLC_PROMPT_DOMAIN_INDEX.md)
- [Testing Domain](../testing/README.md) (previous phase)
- [Maintenance Domain](../maintenance/README.md) (next phase)
