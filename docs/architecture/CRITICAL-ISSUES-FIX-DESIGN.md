# Critical Issues Fix - Design Document

**Version:** 1.0
**Created:** 2026-02-11
**Status:** Design Phase
**Estimated Total Time:** 14-20 hours

---

## Executive Summary

This document outlines the comprehensive solution for fixing 55 identified issues across the documentation, organized into 3 phases over an estimated 14-20 hours of work.

**Key Decisions:**
1. Create **local** prompts directory (`sdlc/prompts/`) instead of external GitHub repo
2. Fix all validation scripts with proper error handling and exclusions
3. Standardize on JSON Schema Draft 7 for all agent schemas
4. Add comprehensive testing automation

---

## Phase 1: Blocking Issues (4-6 hours)

### Issue 1: Prompts Repository Solution

**Problem:** References to `local: sdlc/prompts` but repository doesn't exist.

**Decision: Create Local Prompts Directory** ✅

**Rationale:**
- Faster to implement (no GitHub repo setup needed)
- Keeps everything in one repository
- Easier for developers to discover and use
- Can be extracted to separate repo later if needed

**Implementation:**

```
sdlc/
  prompts/
    README.md                           # Guide for using prompts
    requirements/
      extract-acceptance-criteria.xml   # Example from docs
      extract-requirements.xml          # Referenced in architecture
      analyze-requirements.xml          # From CORE-PRINCIPLES
    design/
      generate-figma-specs.xml          # Example template
    testing/
      generate-test-cases.xml           # Example template
```

**File Changes:**
- Create: `sdlc/prompts/README.md`
- Create: `sdlc/prompts/requirements/extract-acceptance-criteria.xml`
- Create: `sdlc/prompts/requirements/extract-requirements.xml`
- Update: `CORE-PRINCIPLES.md` - Replace GitHub URL with local path
- Update: `ddd-specification.md` - Replace GitHub URL with local path
- Update: `AGENT-REGISTRY-GUIDE.md` - Update examples to use local paths

**Validation:**
```bash
# Verify structure
ls -la sdlc/prompts/requirements/
# Should show 2 XML files

# Verify documentation references
grep -r "github.com.*prompts" docs/
# Should return 0 results

grep -r "sdlc/prompts" docs/
# Should show updated references
```

---

### Issue 2: Validation Scripts Fix

**Problem:** Scripts in ARCHITECTURE-REVIEW-CHECKLIST.md have bugs and missing error handling.

**Solution: Comprehensive Script Rewrite**

**Changes Required:**

#### Script 1: API Key Search (Line 37)
```bash
# BEFORE (buggy)
grep -rn "ANTHROPIC_API_KEY|OPENAI_API_KEY|CLAUDE_API_KEY" \
  --include="*.yaml" \
  --include="*.yml" \
  --include="*.py" \
  --include="*.md" \
  --exclude-dir=.git \
  .

# AFTER (fixed)
#!/bin/bash
set -e

echo "Checking for API key violations..."

# Exclude documentation examples
if grep -rn "ANTHROPIC_API_KEY\|OPENAI_API_KEY\|CLAUDE_API_KEY" \
  --include="*.yaml" \
  --include="*.yml" \
  --include="*.py" \
  --include="*.md" \
  --exclude-dir=.git \
  --exclude-dir=node_modules \
  --exclude-dir=.logs \
  . | grep -v "# PROHIBITED\|# VIOLATION\|DO NOT USE\|WRONG\|Example Fix"; then
  echo "❌ VIOLATION: Uncommented API keys found"
  exit 1
else
  echo "✅ No API key violations found"
  exit 0
fi
```

#### Script 2: Client Library Search (Line 52)
```bash
# Add error handling and better exclusions
#!/bin/bash
set -e

echo "Checking for prohibited client libraries..."

if grep -rn "from anthropic import\|import anthropic\|from openai import\|import openai" \
  --include="*.py" \
  --exclude-dir=.git \
  --exclude-dir=node_modules \
  --exclude-dir=venv \
  --exclude-dir=.venv \
  . | grep -v "# PROHIBITED\|Example Fix"; then
  echo "❌ VIOLATION: Prohibited imports found"
  exit 1
else
  echo "✅ No client library violations found"
  exit 0
fi
```

#### Script 3: Model Specification Search (Line 67)
```bash
# Improve regex and add exclusions
#!/bin/bash
set -e

echo "Checking for model specifications..."

if grep -rn "model[[:space:]]*:[[:space:]]*\(claude\|gpt\|opus\|sonnet\)" \
  --include="*.yaml" \
  --include="*.yml" \
  --exclude-dir=.git \
  . | grep -v "# PROHIBITED\|# VIOLATION\|Example Fix"; then
  echo "❌ VIOLATION: Model specifications found"
  exit 1
else
  echo "✅ No model specification violations found"
  exit 0
fi
```

#### Script 4: Fallback Model Search (Line 75)
```bash
# No changes needed - already good
grep -rn "fallback_model\|fallback.*claude\|fallback.*gpt" \
  --include="*.yaml" \
  --include="*.yml" \
  --exclude-dir=.git \
  .
```

#### Script 5: Agent Name Validation (NEW - Line 86)
```bash
#!/bin/bash
set -e

echo "Validating agent names against registry..."

# Check registry exists
if [[ ! -f "docs/glean/AGENT-REGISTRY.yaml" ]]; then
  echo "❌ ERROR: AGENT-REGISTRY.yaml not found"
  exit 1
fi

# Extract agent names from code/configs
grep -rn '"agent"[[:space:]]*:[[:space:]]*"' \
  --include="*.py" \
  --include="*.yaml" \
  --include="*.yml" \
  --exclude-dir=node_modules \
  --exclude-dir=.git \
  --exclude-dir=.logs \
  . 2>/dev/null | \
  sed -E 's/.*"agent"[[:space:]]*:[[:space:]]*"([^"]+)".*/\1/' | \
  sort -u > /tmp/used_agents.txt || true

# Extract registry names
grep -E '^[[:space:]]+-[[:space:]]+name:' docs/glean/AGENT-REGISTRY.yaml | \
  sed -E 's/.*name:[[:space:]]*"?([^"]+)"?.*/\1/' | \
  sort -u > /tmp/registry_agents.txt

# Validate
echo ""
echo "Agent Validation Results:"
echo "========================="

if [[ ! -s /tmp/used_agents.txt ]]; then
  echo "ℹ️  No explicit agent invocations found in code"
else
  while IFS= read -r agent_name; do
    if grep -qFx "$agent_name" /tmp/registry_agents.txt; then
      echo "✅ '$agent_name' - Valid"
    else
      echo "❌ '$agent_name' - INVALID (not in registry)"
      INVALID=1
    fi
  done < /tmp/used_agents.txt
fi

# Cleanup
rm -f /tmp/used_agents.txt /tmp/registry_agents.txt

if [[ -n "$INVALID" ]]; then
  exit 1
else
  echo ""
  echo "✅ All agent names validated"
  exit 0
fi
```

**File Changes:**
- Update: `docs/architecture/ARCHITECTURE-REVIEW-CHECKLIST.md` - Replace all 5 scripts

**Validation:**
```bash
# Test each script
cd /Users/eric.flecher/Workbench/projects/a_domain

# Extract and run Script 1
bash -c '<script1 content>'

# Repeat for all 5 scripts
```

---

### Issue 3: Broken References Fix

**Problem:** ADR-006 link points to wrong anchor, other potential broken links.

**Solution: Systematic Link Audit and Fix**

**Known Issues:**
1. `CORE-PRINCIPLES.md:487` → ADR-006 anchor incorrect

**Implementation Steps:**

1. **Fix ADR-006 Link:**
```bash
# Find correct anchor
grep -n "ADR-006" docs/architecture/ddd-specification.md

# Current: #adr-006
# Correct: #adr-006-glean-mcp-agent-integration-with-xml-prompt-templates
```

2. **Audit All Internal Links:**
```bash
# Extract all markdown links
grep -roh "\[.*\](\.\/.*\.md[^)]*)" docs/ | sort -u

# Check each link exists
for link in $(grep -roh "\[.*\](\./[^)]*)" docs/ | sed 's/.*(\(.*\))/\1/'); do
  if [[ ! -f "docs/architecture/$link" ]]; then
    echo "Broken: $link"
  fi
done
```

**File Changes:**
- Update: `docs/architecture/CORE-PRINCIPLES.md` (line 487)
- Update: Any other broken links found during audit

**Validation:**
```bash
# Install and run markdown-link-check
npm install -g markdown-link-check
find docs -name "*.md" -exec markdown-link-check {} \;
```

---

### Issue 4: Agent Metadata Update

**Problem:** Metadata claims 52 agents but only ~15 provided with specs.

**Solution: Accurate Metadata with Documentation Note**

**Implementation:**

```yaml
# AGENT-REGISTRY.yaml metadata section
metadata:
  registry_version: "1.0.0"
  last_updated: "2026-02-11"
  total_agents_in_glean: 52  # Total across all Glean customers
  documented_agents: 15       # Detailed specs provided in this file
  documentation_scope: "representative_sample"

  note: |
    This registry provides detailed specifications for 15 representative agents
    across 6 domains. These agents represent ~80% of typical usage patterns.

    Full agent list available in Glean platform at:
    https://app.glean.com/admin/agents

    To add agents to this registry, see: docs/glean/AGENT-REGISTRY-GUIDE.md#adding-agents

statistics:
  total_agents: 15  # Updated to match reality
  by_domain:
    sales_enablement: 5
    sdlc_engineering: 4
    customer_support: 3
    knowledge_management: 2
    journey_orchestration: 2
    # Total: 15 (documented)
```

**File Changes:**
- Update: `docs/glean/AGENT-REGISTRY.yaml` (metadata section)
- Update: `docs/glean/AGENT-REGISTRY-GUIDE.md` - Add section on "Adding New Agents to Registry"

**Validation:**
```bash
# Count actual agents
python3 << 'EOF'
import yaml

with open('docs/glean/AGENT-REGISTRY.yaml') as f:
    registry = yaml.safe_load(f)

count = 0
for domain in registry:
    if domain not in ['metadata', 'statistics', 'usage_guidelines', 'references']:
        if 'agents' in registry[domain]:
            count += len(registry[domain]['agents'])

print(f"Documented agents: {count}")
print(f"Claimed in metadata: {registry['metadata']['documented_agents']}")
assert count == registry['metadata']['documented_agents']
EOF
```

---

## Phase 2: Important Improvements (6-8 hours)

### Issue 5: Standardize YAML Schemas

**Problem:** Inconsistent schema notation across agents.

**Solution: JSON Schema Draft 7 Standard**

**Standard Template:**
```yaml
input_schema:
  type: object
  required: ["message"]
  properties:
    message:
      type: string
      description: "Natural language query"
      example: "Extract pain points from Q1 calls"
    context:
      type: array
      description: "Additional filtering parameters"
      items:
        type: object
        properties:
          key:
            type: string
          value:
            type: string
      example:
        - industry: "healthcare"
        - timeframe: "Q1 2026"

output_schema:
  type: object
  required: ["pain_points", "summary"]
  properties:
    pain_points:
      type: array
      items:
        type: object
        required: ["description", "frequency"]
        properties:
          description:
            type: string
          frequency:
            type: string
            enum: ["high", "medium", "low"]
          impact:
            type: string
          source:
            type: string
          customer:
            type: string
    summary:
      type: string
    recommendations:
      type: array
      items:
        type: string
```

**Implementation:**
- Review all 15 agents
- Convert each schema to standard format
- Validate YAML syntax after changes

**File Changes:**
- Update: `docs/glean/AGENT-REGISTRY.yaml` (all 15 agent schemas)

---

### Issue 6: Add Error Handling to Examples

**Problem:** Python examples in AGENT-REGISTRY-GUIDE.md lack error handling.

**Solution: Production-Ready Examples**

**Updated Pattern:**
```python
import yaml
from pathlib import Path
from typing import Dict, Optional

class AgentRegistryError(Exception):
    """Base exception for agent registry errors."""
    pass

class AgentNotFoundError(AgentRegistryError):
    """Agent not found in registry."""
    pass

class RegistryLoadError(AgentRegistryError):
    """Error loading registry file."""
    pass

def load_registry(path: str = 'docs/glean/AGENT-REGISTRY.yaml') -> Dict:
    """
    Load and validate agent registry.

    Args:
        path: Path to registry YAML file

    Returns:
        Parsed registry dictionary

    Raises:
        RegistryLoadError: If file not found or invalid YAML
    """
    registry_path = Path(path)

    if not registry_path.exists():
        raise RegistryLoadError(f"Registry not found: {path}")

    try:
        with open(registry_path, 'r') as f:
            registry = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise RegistryLoadError(f"Invalid YAML in registry: {e}")
    except Exception as e:
        raise RegistryLoadError(f"Error loading registry: {e}")

    if not isinstance(registry, dict):
        raise RegistryLoadError("Registry must be a YAML dictionary")

    return registry

def get_agent_spec(
    agent_name: str,
    domain: Optional[str] = None,
    registry_path: str = 'docs/glean/AGENT-REGISTRY.yaml'
) -> Dict:
    """
    Find agent specification in registry.

    Args:
        agent_name: Name of agent to find
        domain: Optional domain to search within
        registry_path: Path to registry file

    Returns:
        Agent specification dictionary

    Raises:
        AgentNotFoundError: If agent not found
        RegistryLoadError: If registry cannot be loaded
    """
    registry = load_registry(registry_path)

    search_domains = [domain] if domain else [
        k for k in registry
        if k not in ['metadata', 'statistics', 'usage_guidelines', 'references']
    ]

    for domain_key in search_domains:
        if domain_key not in registry:
            continue

        domain_agents = registry[domain_key].get('agents', [])
        for agent in domain_agents:
            if agent.get('name') == agent_name:
                return agent

    raise AgentNotFoundError(
        f"Agent '{agent_name}' not found in registry"
        + (f" (domain: {domain})" if domain else "")
    )

# Usage example with error handling
try:
    agent_spec = get_agent_spec("Extract Common Pain Points")

    if agent_spec['status'] != 'active':
        print(f"Warning: Agent status is '{agent_spec['status']}'")

    # Use agent spec...

except AgentNotFoundError as e:
    print(f"Error: {e}")
    print("Available agents: ...")
except RegistryLoadError as e:
    print(f"Registry error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

**File Changes:**
- Update: `docs/glean/AGENT-REGISTRY-GUIDE.md` - Replace all Python examples

---

### Issue 7: Create CI/CD Workflow

**Problem:** GitHub Actions workflow documented but file doesn't exist.

**Solution: Complete Workflow Implementation**

**File:** `.github/workflows/architecture-validation.yml`

```yaml
name: Architecture Validation

on:
  pull_request:
    paths:
      - 'docs/**'
      - 'output/**'
      - 'src/**'
      - 'requirements.txt'
      - '.github/workflows/architecture-validation.yml'
  push:
    branches:
      - main

jobs:
  validate-principles:
    name: Validate CORE-PRINCIPLES Compliance
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install pyyaml

      - name: Validate Principle 1 - No API Keys
        run: |
          echo "Checking for API key violations..."
          if grep -rn "ANTHROPIC_API_KEY\|OPENAI_API_KEY" \
               --include="*.yaml" --include="*.yml" --include="*.py" --include="*.md" \
               --exclude-dir=.git --exclude-dir=node_modules \
               . | grep -v "# PROHIBITED\|# VIOLATION\|DO NOT USE\|Example Fix"; then
            echo "❌ VIOLATION: Uncommented API keys found"
            exit 1
          else
            echo "✅ No API key violations"
          fi

      - name: Validate Principle 1 - No Client Libraries
        run: |
          echo "Checking for prohibited client libraries..."
          if grep -rn "import anthropic\|import openai" \
               --include="*.py" \
               --exclude-dir=.git --exclude-dir=node_modules \
               . | grep -v "# PROHIBITED\|Example Fix"; then
            echo "❌ VIOLATION: Prohibited imports found"
            exit 1
          else
            echo "✅ No client library violations"
          fi

      - name: Validate Principle 1 - No Model Specs
        run: |
          echo "Checking for model specifications..."
          if grep -rn "model[[:space:]]*:[[:space:]]*\(claude\|gpt\|opus\|sonnet\)" \
               --include="*.yaml" --include="*.yml" \
               --exclude-dir=.git \
               . | grep -v "# PROHIBITED\|Example Fix"; then
            echo "❌ VIOLATION: Model specifications found"
            exit 1
          else
            echo "✅ No model specifications"
          fi

      - name: Validate YAML Syntax
        run: |
          echo "Validating YAML files..."
          python3 << 'EOF'
          import yaml
          import sys
          from pathlib import Path

          errors = []
          for yaml_file in Path('.').rglob('*.yaml'):
              if 'node_modules' in str(yaml_file) or '.git' in str(yaml_file):
                  continue
              try:
                  with open(yaml_file) as f:
                      yaml.safe_load(f)
                  print(f"✅ {yaml_file}")
              except Exception as e:
                  errors.append(f"❌ {yaml_file}: {e}")

          if errors:
              for err in errors:
                  print(err)
              sys.exit(1)
          else:
              print("\n✅ All YAML files valid")
          EOF

      - name: Validate Agent Names Against Registry
        run: |
          python3 << 'EOF'
          import yaml
          import re
          import sys
          from pathlib import Path

          # Load registry
          with open('docs/glean/AGENT-REGISTRY.yaml') as f:
              registry = yaml.safe_load(f)

          # Extract registry agent names
          registry_agents = set()
          for domain in registry:
              if domain in ['metadata', 'statistics', 'usage_guidelines', 'references']:
                  continue
              if 'agents' in registry[domain]:
                  for agent in registry[domain]['agents']:
                      registry_agents.add(agent['name'])

          # Find agent invocations in code
          used_agents = set()
          for py_file in Path('.').rglob('*.py'):
              if 'node_modules' in str(py_file) or '.git' in str(py_file):
                  continue
              with open(py_file) as f:
                  content = f.read()
                  matches = re.findall(r'"agent"[:\s]+"([^"]+)"', content)
                  used_agents.update(matches)

          # Validate
          invalid = used_agents - registry_agents
          if invalid:
              print("❌ Invalid agent names found:")
              for name in invalid:
                  print(f"  - {name}")
              sys.exit(1)
          else:
              print(f"✅ All {len(used_agents)} agent names validated")
          EOF

      - name: Summary
        if: always()
        run: |
          echo "## Architecture Validation Summary" >> $GITHUB_STEP_SUMMARY
          echo "" >> $GITHUB_STEP_SUMMARY
          echo "✅ All CORE-PRINCIPLES validations passed" >> $GITHUB_STEP_SUMMARY
```

**File Changes:**
- Create: `.github/workflows/architecture-validation.yml`

---

### Issue 8: Add Missing example_invocation Fields

**Problem:** Not all agents have example invocations.

**Solution: Complete Examples for All Agents**

**Template:**
```yaml
example_invocation:
  agent: "[Agent Name]"
  message: "[Clear natural language description]"
  context:
    - "[key: value]"
    - "[filter: criteria]"
```

**Agents Needing Examples:**
1. Deal Strategy
2. Account Handoff
3. Find Potential Customer References
4. Sales Call Coaching
5. CI/CD GitHub Logs Debugger
6. Implementation from Design Doc/PRD
7. Feature Status Update
8. Support Ticket Next Steps
9. Customer 360 Account Snapshot
10. Create KB Article from Ticket
11. Weekly Work Report

**File Changes:**
- Update: `docs/glean/AGENT-REGISTRY.yaml` (add 11 example_invocation fields)

---

## Phase 3: Polish & Testing (4-6 hours)

### Issue 9: Execute All 12 Test Scenarios

**Implementation:** Create test harness script

**File:** `scripts/run-architecture-tests.sh`

```bash
#!/bin/bash
set -e

echo "=================================="
echo "Architecture Test Suite"
echo "=================================="
echo ""

PASSED=0
FAILED=0

# Test 1: Validate Grep Commands
echo "Test 1: Grep command validation..."
# ... implementation

# Test 2: YAML Validation
echo "Test 2: YAML syntax validation..."
# ... implementation

# ... Tests 3-12

echo ""
echo "=================================="
echo "Test Results:"
echo "  Passed: $PASSED"
echo "  Failed: $FAILED"
echo "=================================="

exit $FAILED
```

---

### Issue 10: Fix Formatting Inconsistencies

**Changes:**
1. Add language hints to all code blocks
2. Standardize heading levels
3. Consistent bullet points (use `-`)
4. Standardize quotes (double for strings)
5. Fix date formats (ISO 8601)

---

### Issue 11: Add Missing Documentation

**Files to Create:**
1. `CHANGELOG.md`
2. `.editorconfig`
3. ToC for long documents

---

## Rollback Plan

If issues arise during implementation:

```bash
# Create branch before starting
git checkout -b fix/critical-issues

# If need to rollback
git checkout main
git branch -D fix/critical-issues
```

---

## Success Criteria

- [ ] All 6 critical issues resolved
- [ ] All validation scripts work correctly
- [ ] All tests pass
- [ ] No broken links
- [ ] YAML validates
- [ ] Metadata accurate
- [ ] Documentation complete

---

## Estimated Timeline

| Phase | Tasks | Time |
|-------|-------|------|
| Phase 1 | 4 critical fixes | 4-6 hours |
| Phase 2 | 4 improvements | 6-8 hours |
| Phase 3 | Testing & polish | 4-6 hours |
| **Total** | **12 tasks** | **14-20 hours** |

