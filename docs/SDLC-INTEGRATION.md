# SDLC Framework Integration Guide

Complete guide to the SDLC framework integration in the a_domain project.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Installation](#installation)
- [Command Reference](#command-reference)
- [Claude Skills](#claude-skills)
- [Workflows](#workflows)
- [Troubleshooting](#troubleshooting)

## Overview

The a_domain project now includes the SDLC (Software Development Lifecycle) governance framework, providing development lifecycle management alongside the existing prompt engineering workflow.

### What Changed

**Added**:
- SDLC framework as Git submodule at `.sdlc/`
- Python 3.13 virtual environment at `.sdlc/.venv/`
- SDLC make targets integrated into main Makefile
- SDLC Claude skills accessible via `/sdlc-*` commands
- Comprehensive development lifecycle tools

**Unchanged**:
- All 17 existing make targets (xml-prompt, explorer, etc.)
- All 3 custom Claude skills (generate-examples, new-workflow, ux-review-timeline)
- Node.js project structure and dependencies
- Observability and reporting features

## Architecture

### Dual-System Design

The project operates two independent but complementary systems:

```
a_domain/
├── Node.js Project (Prompt Engineering)
│   ├── scripts/              # JavaScript workflow scripts
│   ├── observability/        # OpenTelemetry traces, reports
│   ├── output/               # Generated prompts
│   └── Makefile.local        # Project-specific make targets
│
└── SDLC Framework (Governance)
    ├── .sdlc/                # Git submodule
    │   ├── .venv/            # Python 3.13 environment
    │   ├── .sdlc/            # Framework code
    │   └── Makefile          # SDLC make targets
    ├── .sdlc-integration.mk  # Integration layer
    └── Makefile              # Unified entry point
```

### Makefile Integration

The main `Makefile` acts as an integration hub:

1. Includes `.sdlc-integration.mk` (SDLC targets)
2. Includes `Makefile.local` (project targets)
3. Provides unified `make help` command

**Priority**: Project targets override SDLC targets with the same name.

### Skills Organization

Claude skills are organized by namespace:

```
.claude/skills/
├── project/              # a_domain-specific skills
│   ├── generate-examples/
│   ├── new-workflow/
│   └── ux-review-timeline/
└── sdlc/                 # Symlink → .sdlc/.sdlc/skills/
    ├── plan.md
    ├── implement.md
    ├── test.md
    └── ... (10+ SDLC skills)
```

Skills are invoked with namespace prefix:
- `/project-generate-examples`
- `/sdlc-plan`

## Installation

### For Existing Clone

If you already have this repository cloned:

```bash
# Initialize SDLC submodule
git submodule update --init --recursive

# Verify installation
make help
```

### For New Clone

```bash
# Clone with submodules
git clone --recurse-submodules <repo-url>
cd a_domain

# Verify
make help
```

### Manual Verification

```bash
# Check Python environment
.sdlc/.venv/bin/python --version
# Should show: Python 3.13.9

# Check SDLC package
.sdlc/.venv/bin/python -c "import sdlc_framework; print('✓')"

# Check submodule
git submodule status
# Should show: <commit> .sdlc (heads/main)

# Check skills
ls .claude/skills/project/
ls .claude/skills/sdlc/
```

## Command Reference

### a_domain Project Commands

All existing commands work unchanged:

```bash
# Prompt Generation
make xml-prompt TASK="your task"
make xml-prompt-enhanced TASK="your task"
make xml-prompt-ab TASK="your task"  # Recommended

# Validation
make validate-prompt FILE="output/prompt.xml"

# Testing
make test-workflow
make test-context-analysis
make test-ab-workflow

# Reporting
make view-latest-report
make generate-report
make explorer
make explorer-install

# UX Review
make ux-review

# Cleanup
make clean
```

### SDLC Framework Commands

New governance and lifecycle commands:

```bash
# Session Management
make session-start    # Start development session
make session-end      # End session with recap

# Status & Planning
make status           # Show backlog and health
make backlog-next     # Next tasks from backlog

# Testing & Quality
make test-all         # Run SDLC test suite
make validate-governance  # Check compliance

# Artifacts
make check-artifacts     # Find unregistered artifacts
make register-artifacts  # Register new artifacts
make coverage-report     # Artifact coverage stats

# Skills Generation
make sdlc-generate-skills  # Generate Claude skills
make sdlc-verify-skills    # Verify skill structure
```

### Unified Help

```bash
make help
# Shows both a_domain and SDLC commands
```

## Claude Skills

### Project Skills

Use these for prompt engineering workflows:

#### `/project-generate-examples`
Generate example prompts and test cases.

**When to use**: Creating workflow examples

#### `/project-new-workflow`
Create new workflow orchestration pattern.

**When to use**: Adding new agent workflows

#### `/project-ux-review-timeline`
Comprehensive UX review of timeline reports.

**When to use**: Reviewing report UX, creating user stories

### SDLC Skills

Use these for development lifecycle:

#### `/sdlc-plan`
Query backlog, analyze dependencies, suggest next work.

**When to use**: Starting new feature, planning sprint

#### `/sdlc-implement`
Execute story tasks, update backlog, track progress.

**When to use**: Working on backlog item

#### `/sdlc-test`
Execute test suite, parse results, report pass/fail.

**When to use**: Running tests, validating changes

#### `/sdlc-quality`
Run governance + tests, block on failures.

**When to use**: Pre-commit checks, quality gates

#### `/sdlc-status`
Display backlog summary, governance health, test status.

**When to use**: Checking project health

#### `/sdlc-session`
Session start context, session end validation + recap.

**When to use**: Beginning/ending work sessions

#### `/sdlc-artifact`
Search and process artifacts via Glean MCP.

**When to use**: Finding work artifacts, documents

#### `/sdlc-new-feature-chat`
Interactive TDD story creation wizard.

**When to use**: Creating new features with TDD

## Workflows

### Combined Workflow Example

Using both systems together:

```bash
# 1. Start SDLC session
make session-start

# 2. Check what to work on
make status
/sdlc-plan

# 3. Generate prompt using a_domain
make xml-prompt-ab TASK="Create sentiment analysis prompt"

# 4. Review generated prompt
make view-latest-report

# 5. Run tests (both systems)
make test-workflow          # a_domain tests
make test-all              # SDLC tests

# 6. Quality check
/sdlc-quality

# 7. Register artifacts
make register-artifacts

# 8. End session
make session-end
```

### Prompt Engineering Workflow

Using just a_domain (unchanged):

```bash
# Generate validated prompt
make xml-prompt-ab TASK="Summarize customer feedback"

# Review timeline report
make explorer

# Iterate with context analysis
make test-context-analysis
```

### Governance Workflow

Using just SDLC:

```bash
# Check compliance
make validate-governance

# Run tests
make test-all

# Track artifacts
make coverage-report
```

## Troubleshooting

### Submodule Not Initialized

**Symptom**: `.sdlc/` directory is empty or missing files

**Solution**:
```bash
git submodule update --init --recursive
```

### Python Environment Missing

**Symptom**: `make sdlc-*` commands fail with "No such file"

**Solution**:
```bash
# Check if venv exists
ls .sdlc/.venv/

# If missing, recreate
cd .sdlc
uv venv
uv pip install -e .
cd ..
```

### Make Targets Not Found

**Symptom**: `make status` says "No rule to make target"

**Solution**:
```bash
# Check integration file exists
ls .sdlc-integration.mk

# Check Makefile includes
grep "include" Makefile
```

### Skills Not Discoverable

**Symptom**: `/sdlc-plan` not recognized by Claude Code

**Solution**:
```bash
# Check symlink
ls -l .claude/skills/sdlc

# Should point to: ../../.sdlc/.sdlc/skills/

# Recreate if broken
rm .claude/skills/sdlc
ln -s ../../.sdlc/.sdlc/skills .claude/skills/sdlc
```

### Conflicts Between Systems

**Symptom**: Command behaves unexpectedly

**Check which target is running**:
```bash
make -n <command>
```

**Priority order**:
1. Makefile.local (highest - project commands)
2. .sdlc-integration.mk (SDLC commands)
3. Built-in make rules

If a project command conflicts with SDLC, the project version wins.

### Git Submodule Out of Sync

**Symptom**: SDLC features missing or outdated

**Solution**:
```bash
# Update submodule to latest
cd .sdlc
git pull origin main
cd ..
git add .sdlc
git commit -m "Update SDLC framework"
```

### Cleanup and Reinstall

If something is broken, complete cleanup:

```bash
# Remove SDLC submodule
git submodule deinit -f .sdlc
rm -rf .git/modules/.sdlc
git rm -f .sdlc
rm -f .gitmodules

# Restore backup (if needed)
cat .sdlc-init-backup.txt
# Follow instructions in docs/ROLLBACK.md
```

## Getting Help

- **SDLC Framework Docs**: `.sdlc/README.md`
- **Quick Reference**: `.sdlc/QUICK-REFERENCE.md`
- **Rollback Guide**: `docs/ROLLBACK.md`
- **GitHub Issues**: https://github.com/Eric-Flecher-Glean/sdlc/issues

## Related Documentation

- [ROLLBACK.md](ROLLBACK.md) - Complete removal instructions
- [../README.md](../README.md) - Project overview with SDLC section
- [../.sdlc/README.md](../.sdlc/README.md) - SDLC framework documentation
- [../.claude/skills/README.md](../.claude/skills/README.md) - Skills organization
