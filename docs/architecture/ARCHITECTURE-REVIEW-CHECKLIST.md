# Architecture Review Checklist

**Version:** 1.0
**Last Updated:** 2026-02-11
**Purpose:** Pre-merge validation for architecture documents and implementations

---

## Overview

This checklist ensures all architecture documents and implementations comply with [CORE-PRINCIPLES.md](./CORE-PRINCIPLES.md) before being merged to the main branch.

### Usage

**When to Use:**
- Before submitting architecture documents for review
- Before merging feature implementations
- During code review process
- As part of CI/CD validation

**How to Use:**
1. Run automated validation commands for each applicable section
2. Manually verify checklist items
3. Document any findings requiring remediation
4. Obtain approval only after ALL items pass

---

## Section 1: CORE PRINCIPLES COMPLIANCE

### Principle 1: Centralized LLM Compute

**Automated Validation:**

```bash
# Command 1: Search for prohibited API keys
grep -rn "ANTHROPIC_API_KEY\|OPENAI_API_KEY\|CLAUDE_API_KEY" \
  --include="*.yaml" \
  --include="*.yml" \
  --include="*.py" \
  --include="*.md" \
  --exclude-dir=.git \
  --exclude-dir=node_modules \
  .

# Expected: NO MATCHES (exit code 1)
# If matches found: VIOLATION - must remediate before proceeding
```

```bash
# Command 2: Search for prohibited client libraries
grep -rn "from anthropic import\|import anthropic\|from openai import\|import openai" \
  --include="*.py" \
  --exclude-dir=.git \
  --exclude-dir=node_modules \
  .

# Expected: NO MATCHES (exit code 1)
# If matches found: VIOLATION - must remediate
```

```bash
# Command 3: Search for model specifications in configs
grep -rn "model.*claude-\|model.*gpt-\|model.*opus\|model.*sonnet" \
  --include="*.yaml" \
  --include="*.yml" \
  --exclude-dir=.git \
  .

# Expected: NO MATCHES (exit code 1)
# Exceptions: Documentation/examples marked with PROHIBITED comments
```

```bash
# Command 4: Search for fallback model configurations
grep -rn "fallback_model\|fallback.*claude\|fallback.*gpt" \
  --include="*.yaml" \
  --include="*.yml" \
  --exclude-dir=.git \
  .

# Expected: NO MATCHES (exit code 1)
```

```bash
# Command 5: Validate explicit agent names against registry
# Extract agent names from code and check against registry
grep -rn '"agent":\s*"' --include="*.py" --include="*.yaml" --include="*.yml" . | \
  sed -E 's/.*"agent":\s*"([^"]+)".*/\1/' | \
  sort -u | \
  while read agent_name; do
    if ! grep -q "name: \"$agent_name\"" docs/glean/AGENT-REGISTRY.yaml 2>/dev/null; then
      echo "⚠️  Agent '$agent_name' not found in registry"
    else
      echo "✅ Agent '$agent_name' validated"
    fi
  done

# Expected: All agents validated (✅) with no warnings
```

**Manual Checklist:**

Architecture Documents:
- [ ] No `ANTHROPIC_API_KEY` in environment variable sections
- [ ] No `anthropic` client library in dependencies lists
- [ ] No `openai` or other LLM libraries in dependencies
- [ ] No model specifications (`claude-sonnet-4-5`, `gpt-4`, etc.)
- [ ] No `fallback_model` configurations
- [ ] All LLM operations use `mcp__glean__chat` tool
- [ ] All agent workflows use Claude Code Task tool
- [ ] Prompt templates stored in `sdlc/` directory structure
- [ ] Explicit agent names validated against [Glean Agent Registry](../glean/AGENT-REGISTRY.yaml)
- [ ] Agent invocations use correct input/output schemas from registry

Implementation Code:
- [ ] No `import anthropic` statements
- [ ] No `import openai` statements
- [ ] No `Anthropic()` client instantiation
- [ ] No `OpenAI()` client instantiation
- [ ] No API key environment variable access
- [ ] All LLM calls use MCP client
- [ ] All agent calls use Task tool/CLI

Configuration Files:
- [ ] `requirements.txt` does not include `anthropic`
- [ ] `requirements.txt` does not include `openai`
- [ ] `package.json` does not include anthropic/openai clients
- [ ] Docker/compose files do not inject API keys
- [ ] Environment templates use `GLEAN_MCP_CONFIG` only

---

## Section 2: Common Violations & Fixes

### Violation Table

| Violation Pattern | Location | Fix |
|-------------------|----------|-----|
| `model: claude-sonnet-4-5` | YAML config | Replace with `tool: mcp__glean__chat` |
| `ANTHROPIC_API_KEY=${...}` | Environment vars | Replace with `GLEAN_MCP_CONFIG=${...}` |
| `from anthropic import Anthropic` | Python imports | Replace with `from mcp_client import MCPClient` |
| `fallback_model: claude-opus-4-6` | YAML config | Remove entirely |
| `client = Anthropic(api_key=...)` | Python code | Replace with `client = MCPClient()` |
| `anthropic==0.20.0` | requirements.txt | Remove dependency |
| `temperature: 0.3` in LLM config | YAML config | Move to prompt template |

### Example Fixes

**Fix 1: Remove Model Configuration**

```yaml
# BEFORE (VIOLATION)
llm:
  model: claude-sonnet-4-5
  temperature: 0.3
  max_tokens: 2048

# AFTER (COMPLIANT)
agent:
  tool: mcp__glean__chat
  prompt_template: sdlc/prompts/analysis-prompt.xml
```

**Fix 2: Replace API Key Environment Variable**

```yaml
# BEFORE (VIOLATION)
environment:
  - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
  - DATABASE_URL=${DATABASE_URL}

# AFTER (COMPLIANT)
environment:
  - GLEAN_MCP_CONFIG=${GLEAN_MCP_CONFIG}
  - DATABASE_URL=${DATABASE_URL}
```

**Fix 3: Update Python Client Usage**

```python
# BEFORE (VIOLATION)
from anthropic import Anthropic

client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
response = client.messages.create(
    model="claude-sonnet-4-5",
    messages=[{"role": "user", "content": prompt}]
)
result = response.content[0].text

# AFTER (COMPLIANT)
from mcp_client import MCPClient

client = MCPClient()
response = client.call_tool(
    "mcp__glean__chat",
    {"message": prompt}
)
result = response["content"]
```

**Fix 4: Remove Fallback Models**

```yaml
# BEFORE (VIOLATION)
llm_integration:
  primary: Glean MCP chat tool
  fallback_model: claude-sonnet-4-5
  timeout: 30s

# AFTER (COMPLIANT)
llm_integration:
  tool: mcp__glean__chat
  prompt_template: sdlc/requirements/extract-requirements.xml
  timeout: 30s
```

**Fix 5: Update Dependencies**

```txt
# BEFORE (VIOLATION in requirements.txt)
fastapi==0.110.0
anthropic==0.20.0
pydantic==2.6.0

# AFTER (COMPLIANT)
fastapi==0.110.0
pydantic==2.6.0
# anthropic removed - using Glean MCP instead
```

---

## Section 3: File-Specific Validation

### Architecture Documents

**Files to Check:**
- `docs/architecture/**/*.md`
- `docs/recap/**/*.md`
- `output/figma/**/*.yaml`
- `output/figma/**/*.md`

**Validation Command:**

```bash
# Run for each architecture file
FILE="docs/architecture/your-file.md"

# Check for violations
grep -i "ANTHROPIC_API_KEY\|anthropic.*client\|claude-sonnet-4-5\|fallback_model" "$FILE"

# Expected: NO OUTPUT
# If output found: Review and remediate violations
```

### Python Implementation Files

**Files to Check:**
- `src/**/*.py`
- `tests/**/*.py`
- `scripts/**/*.py`

**Validation Command:**

```bash
# Check all Python files
find src tests scripts -name "*.py" -exec grep -l "import anthropic\|import openai\|Anthropic()\|OpenAI()" {} \;

# Expected: NO OUTPUT
# If files listed: Review imports and client usage
```

### Configuration Files

**Files to Check:**
- `requirements.txt`
- `pyproject.toml`
- `package.json`
- `docker-compose.yml`
- `.env.template`

**Validation Commands:**

```bash
# Check requirements
grep -i "anthropic\|openai" requirements.txt

# Check environment template
grep -i "ANTHROPIC_API_KEY\|OPENAI_API_KEY" .env.template

# Expected: NO OUTPUT for both
```

### Agent Name Validation

**Purpose:** Ensure explicit agent names match entries in [Glean Agent Registry](../glean/AGENT-REGISTRY.yaml)

**Files to Check:**
- `src/**/*.py` (Python code with `mcp__glean__chat` calls)
- `docs/**/*.yaml` (Architecture specifications)
- `output/**/*.yaml` (Design specifications)

**Validation Script:**

```bash
# Extract all explicit agent names from code/config
echo "Validating agent names against registry..."

# Find all agent invocations
grep -rn '"agent":\s*"' \
  --include="*.py" \
  --include="*.yaml" \
  --include="*.yml" \
  --exclude-dir=.git \
  --exclude-dir=node_modules \
  . | \
  sed -E 's/.*"agent":\s*"([^"]+)".*/\1/' | \
  sort -u > /tmp/used_agents.txt

# Load registry agent names
grep -E '^\s+- name:' docs/glean/AGENT-REGISTRY.yaml | \
  sed -E 's/.*name:\s*"?([^"]+)"?.*/\1/' | \
  sort -u > /tmp/registry_agents.txt

# Compare
echo ""
echo "Agent Name Validation Results:"
echo "==============================="

while read agent_name; do
  if grep -qF "$agent_name" /tmp/registry_agents.txt; then
    echo "✅ '$agent_name' - Valid (found in registry)"
  else
    echo "❌ '$agent_name' - INVALID (not in registry)"
    echo "   Fix: Check spelling or update registry at docs/glean/AGENT-REGISTRY.yaml"
  fi
done < /tmp/used_agents.txt

# Cleanup
rm -f /tmp/used_agents.txt /tmp/registry_agents.txt
```

**Expected Output:**
All agent names should show ✅ Valid. Any ❌ INVALID indicates:
- Typo in agent name (fix code)
- Missing agent in registry (update registry)
- Deprecated agent (update code to use active agent)

**Common Issues:**

| Issue | Example | Fix |
|-------|---------|-----|
| Case mismatch | `"extract common pain points"` | `"Extract Common Pain Points"` (match registry) |
| Typo | `"Extract Pain Point"` | `"Extract Common Pain Points"` (add 's') |
| Truncated name | `"Deal Strategy Agent"` | `"Deal Strategy"` (remove "Agent") |
| Not in registry | `"Custom Agent Name"` | Add to registry or use auto-routing |

---

## Section 4: Automation

### Pre-Commit Hook

Create `.git/hooks/pre-commit`:

```bash
#!/bin/bash
# Pre-commit hook: Validate CORE-PRINCIPLES compliance

echo "🔍 Validating CORE-PRINCIPLES compliance..."

# Check for API keys
if git diff --cached --name-only | xargs grep -l "ANTHROPIC_API_KEY\|OPENAI_API_KEY" 2>/dev/null; then
    echo "❌ VIOLATION: API keys found in staged files"
    echo "   See: docs/architecture/CORE-PRINCIPLES.md#principle-1"
    exit 1
fi

# Check for prohibited imports
if git diff --cached --name-only | grep "\.py$" | xargs grep -l "import anthropic\|import openai" 2>/dev/null; then
    echo "❌ VIOLATION: Prohibited LLM client imports found"
    echo "   See: docs/architecture/CORE-PRINCIPLES.md#prohibited-patterns"
    exit 1
fi

# Check for model specifications
if git diff --cached --name-only | grep -E "\.(yaml|yml)$" | xargs grep -l "model.*claude-\|fallback_model" 2>/dev/null; then
    echo "❌ VIOLATION: Model specifications found in configs"
    echo "   See: docs/architecture/CORE-PRINCIPLES.md#approved-pattern-1"
    exit 1
fi

echo "✅ CORE-PRINCIPLES compliance validated"
exit 0
```

**Installation:**

```bash
chmod +x .git/hooks/pre-commit
```

### CI/CD Validation

**GitHub Actions Example** (`.github/workflows/architecture-validation.yml`):

```yaml
name: Architecture Validation

on:
  pull_request:
    paths:
      - 'docs/architecture/**'
      - 'output/figma/**'
      - 'src/**'
      - 'requirements.txt'

jobs:
  validate-principles:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Validate Principle 1 - No API Keys
        run: |
          if grep -rn "ANTHROPIC_API_KEY\|OPENAI_API_KEY" \
               --include="*.yaml" --include="*.yml" --include="*.py" \
               --exclude-dir=.git .; then
            echo "VIOLATION: API keys found"
            exit 1
          fi

      - name: Validate Principle 1 - No Client Libraries
        run: |
          if grep -rn "import anthropic\|import openai" --include="*.py" .; then
            echo "VIOLATION: Prohibited client libraries found"
            exit 1
          fi

      - name: Validate Principle 1 - No Model Specs
        run: |
          if grep -rn "model.*claude-\|fallback_model" \
               --include="*.yaml" --include="*.yml" .; then
            echo "VIOLATION: Model specifications found"
            exit 1
          fi

      - name: Success
        run: echo "✅ All CORE-PRINCIPLES validations passed"
```

---

## Section 5: Review Sign-Off

### Reviewer Checklist

Before approving any PR:

- [ ] Automated validation commands executed with NO violations
- [ ] Manual checklist items verified
- [ ] Common violation patterns checked
- [ ] File-specific validation completed
- [ ] Changes comply with CORE-PRINCIPLES.md
- [ ] No workarounds or "temporary" violations present
- [ ] Documentation updated if patterns changed

### Sign-Off Template

```markdown
## Architecture Review

**Reviewer:** [Your Name]
**Date:** [YYYY-MM-DD]
**PR:** #[PR Number]

### CORE-PRINCIPLES Validation

- [ ] Principle 1 (LLM Compute): COMPLIANT
- [ ] Automated checks: PASSED
- [ ] Manual review: PASSED

**Violations Found:** [None | List violations]
**Remediation Required:** [None | Required actions]

**Approval:** [APPROVED | CHANGES REQUESTED]
```

---

## Section 6: Escalation Process

### When Violations Are Found

1. **Document the Violation:**
   - File path and line number
   - Violation type (API key, client library, model spec, etc.)
   - Severity (blocking, warning, informational)

2. **Notify Author:**
   - Reference specific section in CORE-PRINCIPLES.md
   - Provide fix example from this checklist
   - Set deadline for remediation

3. **Track Remediation:**
   - Create GitHub issue for tracking
   - Link to PR with violation
   - Verify fix before closing

4. **Update Checklist:**
   - If new violation pattern found, add to Section 2
   - Update automation scripts to catch in future
   - Communicate pattern to team

### Exception Requests

**No exceptions permitted for Principle 1.**

If a legitimate use case cannot be satisfied:
1. Contact architecture team via Slack #architecture
2. Document use case and constraints
3. Explore platform enhancement options
4. Escalate to executive level if critical

---

## Document Maintenance

### Changelog

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2026-02-11 | Initial creation with Principle 1 validation | Architecture Team |

### Review Schedule

- **Monthly:** Update common violations based on findings
- **Quarterly:** Review automation effectiveness
- **After Each Violation:** Update checklist with new patterns
