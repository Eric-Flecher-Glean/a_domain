---
title: "UV Deterministic API Integration Specification"
version: 1.0
date: 2026-01-22
status: active
purpose: "Documentation for UV Deterministic API Integration Specification"
---

# UV Deterministic API Integration Specification

**Version:** 1.0
**Created:** 2026-01-21
**Status:** Active

---

## Overview

This specification defines the UV (Universal Versioned) Deterministic API integration for all 14 SDLC prompts. The UV API provides:

1. **Deterministic execution** - Same inputs produce same outputs
2. **Make-based triggers** - Unified command interface
3. **Structured I/O** - JSON/YAML schemas for inputs and outputs
4. **Exit code semantics** - Machine-readable success/failure signals
5. **Artifact logging** - Full traceability of all changes

---

## Makefile Integration

### New UV Prompt Targets

Add the following targets to the root Makefile:

```makefile
# ============================================================================
# UV DETERMINISTIC PROMPT API TARGETS
# ============================================================================

.PHONY: uv-yml-bck-mgr uv-yml-bck-refresh uv-scope-change \
        uv-cycle-implement uv-quality-gate uv-tst-rvw-imp \
        uv-unified-plan uv-organize uv-rep-mak-reg uv-ddd-make-align \
        uv-update-readme uv-update-status uv-demo-prep uv-diagram

# ─────────────────────────────────────────────────────────────────────────────
# CORE DOMAIN: Backlog State Management
# ─────────────────────────────────────────────────────────────────────────────

# yml-bck-mgr: Create/update YAML backlog from source documents
# Usage: make uv-yml-bck-mgr [SOURCE_DOCS=path] [MODE=bootstrap|incremental]
uv-yml-bck-mgr:
	@echo "🎯 Running yml-bck-mgr prompt (Backlog State Management)"
	@mkdir -p .uv
	@uv run scripts/prompts/yml_bck_mgr.py \
		--source-docs "$(SOURCE_DOCS)" \
		--mode "$(or $(MODE),incremental)" \
		--output "IMPLEMENTATION_BACKLOG.yaml" \
		--result ".uv/yml-bck-mgr-result.json"
	@echo "✅ Backlog updated: IMPLEMENTATION_BACKLOG.yaml"

# yml-bck-refresh: Synchronize backlog state with repository artifacts
# Usage: make uv-yml-bck-refresh
uv-yml-bck-refresh:
	@echo "🔄 Running yml-bck-refresh prompt (State Synchronization)"
	@mkdir -p .uv
	@uv run scripts/prompts/yml_bck_refresh.py \
		--backlog "IMPLEMENTATION_BACKLOG.yaml" \
		--result ".uv/yml-bck-refresh-result.json"
	@echo "✅ Backlog synchronized"

# scope-change: Adapt project to new scope
# Usage: make uv-scope-change SCOPE="path/to/scope.yaml"
uv-scope-change:
	@echo "📐 Running scope-change prompt (Scope Adaptation)"
	@mkdir -p .uv
	@if [ -z "$(SCOPE)" ]; then \
		echo "❌ Missing SCOPE parameter"; \
		echo "Usage: make uv-scope-change SCOPE=\"path/to/scope.yaml\""; \
		exit 1; \
	fi
	@uv run scripts/prompts/scope_change.py \
		--scope "$(SCOPE)" \
		--backlog "IMPLEMENTATION_BACKLOG.yaml" \
		--result ".uv/scope-change-result.json"
	@echo "✅ Scope adapted"

# ─────────────────────────────────────────────────────────────────────────────
# CORE DOMAIN: Execution Engine
# ─────────────────────────────────────────────────────────────────────────────

# cycle-implement: Execute next work item from backlog
# Usage: make uv-cycle-implement [STORY_ID=P0-XXX] [DRY_RUN=true]
uv-cycle-implement:
	@echo "⚡ Running cycle-implement prompt (Execution Engine)"
	@mkdir -p .uv
	@uv run scripts/prompts/cycle_implement.py \
		--backlog "IMPLEMENTATION_BACKLOG.yaml" \
		$(if $(STORY_ID),--story-id "$(STORY_ID)",) \
		$(if $(DRY_RUN),--dry-run,) \
		--result ".uv/cycle-implement-result.json"
	@echo "✅ Work item execution complete"

# ─────────────────────────────────────────────────────────────────────────────
# SUPPORTING DOMAIN: Quality Assurance
# ─────────────────────────────────────────────────────────────────────────────

# quality-gate: Validate completed work meets all gates
# Usage: make uv-quality-gate [WORK_ITEM=id] [STRICT=true|false]
uv-quality-gate:
	@echo "🚦 Running quality-gate prompt (Quality Assurance)"
	@mkdir -p .uv
	@uv run scripts/prompts/quality_gate.py \
		$(if $(WORK_ITEM),--work-item "$(WORK_ITEM)",) \
		--strict "$(or $(STRICT),true)" \
		--report ".uv/quality-gate-report.md" \
		--result ".uv/quality-gate-result.json"
	@echo "✅ Quality gate validation complete"

# tst-rvw-imp: Review and validate test plans
# Usage: make uv-tst-rvw-imp TEST_PLAN="path/to/plan.yaml"
uv-tst-rvw-imp:
	@echo "🧪 Running tst-rvw-imp prompt (Test Engineering)"
	@mkdir -p .uv
	@if [ -z "$(TEST_PLAN)" ]; then \
		echo "❌ Missing TEST_PLAN parameter"; \
		echo "Usage: make uv-tst-rvw-imp TEST_PLAN=\"path/to/plan.yaml\""; \
		exit 1; \
	fi
	@uv run scripts/prompts/tst_rvw_imp.py \
		--test-plan "$(TEST_PLAN)" \
		--result ".uv/tst-rvw-imp-result.json"
	@echo "✅ Test review complete"

# ─────────────────────────────────────────────────────────────────────────────
# SUPPORTING DOMAIN: Planning & Architecture
# ─────────────────────────────────────────────────────────────────────────────

# unified-plan: Consolidate planning artifacts
# Usage: make uv-unified-plan [PLAN_SOURCES=path] [OUTPUT=file.md]
uv-unified-plan:
	@echo "📋 Running unified-plan prompt (Planning & Architecture)"
	@mkdir -p .uv
	@uv run scripts/prompts/unified_plan.py \
		$(if $(PLAN_SOURCES),--sources "$(PLAN_SOURCES)",) \
		--output "$(or $(OUTPUT),IMPLEMENTATION_PLAN.md)" \
		--result ".uv/unified-plan-result.json"
	@echo "✅ Plan consolidated"

# organize: Maintain project organization and indexes
# Usage: make uv-organize
uv-organize:
	@echo "📁 Running organize prompt (Repository Organization)"
	@mkdir -p .uv
	@uv run scripts/prompts/organize.py \
		--result ".uv/organize-result.json"
	@echo "✅ Repository organized"

# ─────────────────────────────────────────────────────────────────────────────
# SUPPORTING DOMAIN: Build System Governance
# ─────────────────────────────────────────────────────────────────────────────

# rep-mak-reg: Update make command registry
# Usage: make uv-rep-mak-reg [DOMAIN_FILTER=domain] [FORCE_BOOTSTRAP=true]
uv-rep-mak-reg:
	@echo "📚 Running rep-mak-reg prompt (Build System Governance)"
	@mkdir -p .uv
	@uv run scripts/prompts/rep_mak_reg.py \
		$(if $(DOMAIN_FILTER),--domain "$(DOMAIN_FILTER)",) \
		$(if $(FORCE_BOOTSTRAP),--force-bootstrap,) \
		--output "MAKE_COMMAND_REGISTRY.yaml" \
		--result ".uv/rep-mak-reg-result.json"
	@echo "✅ Make registry updated"

# ddd-make-align: Validate DDD alignment of make commands
# Usage: make uv-ddd-make-align
uv-ddd-make-align:
	@echo "🎯 Running ddd-make-align prompt (DDD Governance)"
	@mkdir -p .uv
	@uv run scripts/prompts/ddd_make_align.py \
		--registry "MAKE_COMMAND_REGISTRY.yaml" \
		--result ".uv/ddd-make-align-result.json"
	@echo "✅ DDD alignment validated"

# ─────────────────────────────────────────────────────────────────────────────
# SUPPORTING DOMAIN: Documentation & Deployment
# ─────────────────────────────────────────────────────────────────────────────

# update-readme: Update root README with progress and learning story
# Usage: make uv-update-readme
uv-update-readme:
	@echo "📖 Running update-readme prompt (Documentation Maintenance)"
	@mkdir -p .uv
	@uv run scripts/prompts/update_readme.py \
		--readme "README.md" \
		--result ".uv/update-readme-result.json"
	@echo "✅ README updated"

# update-status: Generate project progress report
# Usage: make uv-update-status [OUTPUT=report.md]
uv-update-status:
	@echo "📊 Running update-status prompt (Status Reporting)"
	@mkdir -p .uv
	@uv run scripts/prompts/update_status.py \
		--output "$(or $(OUTPUT),reports/status_report.md)" \
		--result ".uv/update-status-result.json"
	@echo "✅ Status report generated"

# demo-prep: Prepare demo specifications
# Usage: make uv-demo-prep SPEC="path/to/spec.yaml"
uv-demo-prep:
	@echo "🎬 Running demo-prep prompt (Demo Preparation)"
	@mkdir -p .uv
	@if [ -z "$(SPEC)" ]; then \
		echo "❌ Missing SPEC parameter"; \
		echo "Usage: make uv-demo-prep SPEC=\"path/to/spec.yaml\""; \
		exit 1; \
	fi
	@uv run scripts/prompts/demo_prep.py \
		--spec "$(SPEC)" \
		--result ".uv/demo-prep-result.json"
	@echo "✅ Demo prepared"

# diagram: Generate ASCII documentation for target folder
# Usage: make uv-diagram TARGET="path/to/folder"
uv-diagram:
	@echo "📐 Running diagram prompt (Visualization)"
	@mkdir -p .uv
	@if [ -z "$(TARGET)" ]; then \
		echo "❌ Missing TARGET parameter"; \
		echo "Usage: make uv-diagram TARGET=\"path/to/folder\""; \
		exit 1; \
	fi
	@uv run scripts/prompts/diagram.py \
		--target "$(TARGET)" \
		--result ".uv/diagram-result.json"
	@echo "✅ Diagrams generated"

# ─────────────────────────────────────────────────────────────────────────────
# UTILITY TARGETS
# ─────────────────────────────────────────────────────────────────────────────

# List all UV prompt targets
uv-help:
	@echo "UV Deterministic API - Available Prompt Targets"
	@echo ""
	@echo "CORE DOMAIN: Backlog State Management"
	@echo "  make uv-yml-bck-mgr [SOURCE_DOCS=path] [MODE=bootstrap|incremental]"
	@echo "  make uv-yml-bck-refresh"
	@echo "  make uv-scope-change SCOPE=\"path/to/scope.yaml\""
	@echo ""
	@echo "CORE DOMAIN: Execution Engine"
	@echo "  make uv-cycle-implement [STORY_ID=P0-XXX] [DRY_RUN=true]"
	@echo ""
	@echo "SUPPORTING DOMAIN: Quality Assurance"
	@echo "  make uv-quality-gate [WORK_ITEM=id] [STRICT=true|false]"
	@echo "  make uv-tst-rvw-imp TEST_PLAN=\"path/to/plan.yaml\""
	@echo ""
	@echo "SUPPORTING DOMAIN: Planning & Architecture"
	@echo "  make uv-unified-plan [PLAN_SOURCES=path] [OUTPUT=file.md]"
	@echo "  make uv-organize"
	@echo ""
	@echo "SUPPORTING DOMAIN: Build System Governance"
	@echo "  make uv-rep-mak-reg [DOMAIN_FILTER=domain] [FORCE_BOOTSTRAP=true]"
	@echo "  make uv-ddd-make-align"
	@echo ""
	@echo "SUPPORTING DOMAIN: Documentation & Deployment"
	@echo "  make uv-update-readme"
	@echo "  make uv-update-status [OUTPUT=report.md]"
	@echo "  make uv-demo-prep SPEC=\"path/to/spec.yaml\""
	@echo "  make uv-diagram TARGET=\"path/to/folder\""

# Clean UV artifacts
uv-clean:
	@echo "🧹 Cleaning UV artifacts..."
	@rm -rf .uv/
	@echo "✅ UV artifacts cleaned"

# Verify UV determinism for a prompt
# Usage: make uv-verify-determinism PROMPT=yml-bck-mgr
uv-verify-determinism:
	@echo "🔍 Verifying determinism for $(PROMPT)..."
	@if [ -z "$(PROMPT)" ]; then \
		echo "❌ Missing PROMPT parameter"; \
		exit 1; \
	fi
	@mkdir -p .uv/verify
	@$(MAKE) uv-$(PROMPT) 2>/dev/null | tee .uv/verify/run1.log
	@cp .uv/$(PROMPT)-result.json .uv/verify/run1-result.json 2>/dev/null || true
	@$(MAKE) uv-$(PROMPT) 2>/dev/null | tee .uv/verify/run2.log
	@cp .uv/$(PROMPT)-result.json .uv/verify/run2-result.json 2>/dev/null || true
	@diff .uv/verify/run1-result.json .uv/verify/run2-result.json && \
		echo "✅ Determinism verified: outputs match" || \
		echo "⚠️ Non-deterministic: outputs differ (may be expected)"
```

---

## Parameter Reference

### All UV Prompt Parameters

| Prompt | Required Params | Optional Params | Default Values |
|--------|----------------|-----------------|----------------|
| `uv-yml-bck-mgr` | - | `SOURCE_DOCS`, `MODE` | `MODE=incremental` |
| `uv-yml-bck-refresh` | - | - | - |
| `uv-scope-change` | `SCOPE` | - | - |
| `uv-cycle-implement` | - | `STORY_ID`, `DRY_RUN` | - |
| `uv-quality-gate` | - | `WORK_ITEM`, `STRICT` | `STRICT=true` |
| `uv-tst-rvw-imp` | `TEST_PLAN` | - | - |
| `uv-unified-plan` | - | `PLAN_SOURCES`, `OUTPUT` | `OUTPUT=IMPLEMENTATION_PLAN.md` |
| `uv-organize` | - | - | - |
| `uv-rep-mak-reg` | - | `DOMAIN_FILTER`, `FORCE_BOOTSTRAP` | - |
| `uv-ddd-make-align` | - | - | - |
| `uv-update-readme` | - | - | - |
| `uv-update-status` | - | `OUTPUT` | `OUTPUT=reports/status_report.md` |
| `uv-demo-prep` | `SPEC` | - | - |
| `uv-diagram` | `TARGET` | - | - |

---

## Exit Code Semantics

### Standard Exit Codes

| Code | Category | Meaning | Action |
|------|----------|---------|--------|
| 0 | Success | All operations completed successfully | Proceed to next step |
| 1 | Partial | Some operations succeeded, others failed | Review and retry |
| 2 | Validation | Input validation failed | Fix inputs |
| 3 | Dependency | Missing dependency or upstream data | Resolve dependency |
| 4 | Permission | Access denied to required resource | Check permissions |
| 5+ | Specific | Prompt-specific error | See prompt documentation |

### Prompt-Specific Exit Codes

#### quality-gate
| Code | Gate | Meaning |
|------|------|---------|
| 0 | All | All gates passed |
| 1 | Test | Test gate failed |
| 2 | Tracking | Status tracking incomplete |
| 3 | Documentation | Documentation outdated |

#### cycle-implement
| Code | Phase | Meaning |
|------|-------|---------|
| 0 | Complete | Work item fully implemented |
| 1 | Partial | Partially complete, blockers documented |
| 2 | Blocked | Cannot proceed, external resolution needed |

---

## Output Schemas

### Result JSON Schema

All UV prompts produce a result JSON file in `.uv/`:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["prompt", "version", "timestamp", "status", "exit_code"],
  "properties": {
    "prompt": {
      "type": "string",
      "description": "Prompt short name"
    },
    "version": {
      "type": "string",
      "description": "Prompt version"
    },
    "timestamp": {
      "type": "string",
      "format": "date-time",
      "description": "Execution timestamp (ISO 8601)"
    },
    "status": {
      "type": "string",
      "enum": ["success", "partial", "failed", "blocked"]
    },
    "exit_code": {
      "type": "integer",
      "minimum": 0
    },
    "duration_ms": {
      "type": "integer",
      "description": "Execution duration in milliseconds"
    },
    "inputs": {
      "type": "object",
      "description": "Input parameters used"
    },
    "outputs": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "path": {"type": "string"},
          "type": {"type": "string"},
          "checksum": {"type": "string"}
        }
      }
    },
    "validation": {
      "type": "object",
      "properties": {
        "rules_checked": {"type": "integer"},
        "rules_passed": {"type": "integer"},
        "violations": {"type": "array"}
      }
    },
    "determinism": {
      "type": "object",
      "properties": {
        "input_hash": {"type": "string"},
        "output_hash": {"type": "string"},
        "is_deterministic": {"type": "boolean"}
      }
    }
  }
}
```

### Example Result

```json
{
  "prompt": "yml-bck-mgr",
  "version": "2.0",
  "timestamp": "2026-01-21T14:30:00Z",
  "status": "success",
  "exit_code": 0,
  "duration_ms": 1523,
  "inputs": {
    "source_docs": "docs/planning/",
    "mode": "incremental"
  },
  "outputs": [
    {
      "path": "IMPLEMENTATION_BACKLOG.yaml",
      "type": "yaml",
      "checksum": "sha256:abc123..."
    }
  ],
  "validation": {
    "rules_checked": 7,
    "rules_passed": 7,
    "violations": []
  },
  "determinism": {
    "input_hash": "sha256:def456...",
    "output_hash": "sha256:abc123...",
    "is_deterministic": true
  }
}
```

---

## Script Directory Structure

Create the following directory structure for prompt implementation scripts:

```
scripts/
└── prompts/
    ├── __init__.py
    ├── base.py                    # Base class for UV prompts
    ├── yml_bck_mgr.py             # yml-bck-mgr implementation
    ├── yml_bck_refresh.py         # yml-bck-refresh implementation
    ├── scope_change.py            # scope-change implementation
    ├── cycle_implement.py         # cycle-implement implementation
    ├── quality_gate.py            # quality-gate implementation
    ├── tst_rvw_imp.py             # tst-rvw-imp implementation
    ├── unified_plan.py            # unified-plan implementation
    ├── organize.py                # organize implementation
    ├── rep_mak_reg.py             # rep-mak-reg implementation
    ├── ddd_make_align.py          # ddd-make-align implementation
    ├── update_readme.py           # update-readme implementation
    ├── update_status.py           # update-status implementation
    ├── demo_prep.py               # demo-prep implementation
    └── diagram.py                 # diagram implementation
```

---

## Base Script Template

```python
#!/usr/bin/env -S uv run --quiet --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "pyyaml>=6.0",
#   "jsonschema>=4.17.0",
# ]
# ///
"""
UV Deterministic Prompt: {prompt_name}
Version: 2.0
Bounded Context: {context_name}
"""

import argparse
import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path

class UVPromptBase:
    """Base class for UV deterministic prompts."""

    def __init__(self, prompt_name: str, version: str, context: str):
        self.prompt_name = prompt_name
        self.version = version
        self.context = context
        self.start_time = datetime.now()
        self.outputs = []
        self.validation_results = {"rules_checked": 0, "rules_passed": 0, "violations": []}

    def run(self, args) -> int:
        """Execute the prompt. Returns exit code."""
        raise NotImplementedError("Subclasses must implement run()")

    def add_output(self, path: str, artifact_type: str):
        """Register an output artifact."""
        checksum = self._compute_checksum(path)
        self.outputs.append({
            "path": path,
            "type": artifact_type,
            "checksum": checksum
        })

    def _compute_checksum(self, path: str) -> str:
        """Compute SHA256 checksum of file."""
        if not Path(path).exists():
            return "sha256:not_found"
        with open(path, "rb") as f:
            return f"sha256:{hashlib.sha256(f.read()).hexdigest()}"

    def write_result(self, result_path: str, status: str, exit_code: int, inputs: dict):
        """Write result JSON file."""
        duration_ms = int((datetime.now() - self.start_time).total_seconds() * 1000)

        result = {
            "prompt": self.prompt_name,
            "version": self.version,
            "timestamp": datetime.now().isoformat() + "Z",
            "status": status,
            "exit_code": exit_code,
            "duration_ms": duration_ms,
            "inputs": inputs,
            "outputs": self.outputs,
            "validation": self.validation_results,
            "determinism": {
                "is_deterministic": True  # Override in subclass if needed
            }
        }

        Path(result_path).parent.mkdir(parents=True, exist_ok=True)
        with open(result_path, "w") as f:
            json.dump(result, f, indent=2)

        return result


def main():
    # Subclass implementation here
    pass


if __name__ == "__main__":
    sys.exit(main())
```

---

## Workflow Integration

### Complete Workflow Example

```bash
# 1. Initialize backlog from planning documents
make uv-yml-bck-mgr SOURCE_DOCS=docs/planning/ MODE=bootstrap

# 2. Execute work items in cycle
make uv-cycle-implement

# 3. Validate completed work
make uv-quality-gate

# 4. Update documentation
make uv-update-readme
make uv-update-status

# 5. Verify determinism
make uv-verify-determinism PROMPT=yml-bck-mgr
```

### CI/CD Integration

```yaml
# .github/workflows/uv-prompts.yml
name: UV Prompt Validation

on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        run: curl -LsSf https://astral.sh/uv/install.sh | sh

      - name: Validate Backlog
        run: make uv-yml-bck-refresh

      - name: Run Quality Gate
        run: make uv-quality-gate STRICT=true

      - name: Verify Determinism
        run: |
          make uv-verify-determinism PROMPT=yml-bck-mgr
          make uv-verify-determinism PROMPT=quality-gate
```

---

## Changelog

| Date | Version | Changes |
|------|---------|---------|
| 2026-01-21 | 1.0 | Initial API integration specification |
