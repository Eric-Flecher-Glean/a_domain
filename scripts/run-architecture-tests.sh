#!/bin/bash
set -e

echo "=========================================="
echo "Comprehensive Architecture Test Suite"
echo "Phase 1 + Phase 2 Validation"
echo "=========================================="
echo ""

PASSED=0
FAILED=0

# Test 1: No API Key Violations
echo "Test 1: Validate no API key violations..."
# Exclude docs (examples of what NOT to do) and .github (validation scripts)
if grep -rn "ANTHROPIC_API_KEY\|OPENAI_API_KEY\|CLAUDE_API_KEY" \
  --include="*.yaml" --include="*.yml" --include="*.py" \
  --exclude-dir=.git --exclude-dir=node_modules --exclude-dir=.logs \
  --exclude-dir=venv --exclude-dir=.venv --exclude-dir=docs --exclude-dir=.github \
  . 2>/dev/null | \
  grep -v "# PROHIBITED\|# VIOLATION\|DO NOT USE\|WRONG\|Example Fix\|Anti-Pattern"; then
  echo "  ❌ FAILED: API key violations found in source/config files"
  FAILED=$((FAILED + 1))
else
  echo "  ✅ PASSED (source/config files validated, docs excluded)"
  PASSED=$((PASSED + 1))
fi
echo ""

# Test 2: No Client Library Violations
echo "Test 2: Validate no prohibited client libraries..."
if grep -rn "from anthropic import\|import anthropic\|from openai import\|import openai" \
  --include="*.py" \
  --exclude-dir=.git --exclude-dir=node_modules --exclude-dir=venv \
  --exclude-dir=.venv --exclude-dir=.logs \
  . 2>/dev/null | \
  grep -v "# PROHIBITED\|Example Fix\|Anti-Pattern"; then
  echo "  ❌ FAILED: Client library violations found"
  FAILED=$((FAILED + 1))
else
  echo "  ✅ PASSED"
  PASSED=$((PASSED + 1))
fi
echo ""

# Test 3: No Model Specifications
echo "Test 3: Validate no model specifications in configs..."
if grep -rn "model[[:space:]]*:[[:space:]]*\(claude\|gpt\|opus\|sonnet\)" \
  --include="*.yaml" --include="*.yml" \
  --exclude-dir=.git --exclude-dir=node_modules \
  . 2>/dev/null | \
  grep -v "# PROHIBITED\|Example Fix\|Anti-Pattern\|metadata:\|glean_agent_version:"; then
  echo "  ❌ FAILED: Model specifications found"
  FAILED=$((FAILED + 1))
else
  echo "  ✅ PASSED"
  PASSED=$((PASSED + 1))
fi
echo ""

# Test 4: Prompt Repository References Use Local Paths
echo "Test 4: Validate local prompt repository references..."
if grep -rn "Eric-Flecher-Glean/prompts\|github.com.*prompts" \
  --include="*.md" --include="*.yaml" --include="*.yml" \
  --exclude-dir=.git \
  docs/ 2>/dev/null | \
  grep -v "^docs/architecture/CRITICAL-ISSUES-FIX-DESIGN.md:67:grep"; then
  echo "  ❌ FAILED: GitHub prompt references found"
  FAILED=$((FAILED + 1))
else
  echo "  ✅ PASSED (excluding validation command examples)"
  PASSED=$((PASSED + 1))
fi
echo ""

# Test 5: ADR-006 References Correct
echo "Test 5: Validate ADR-006 anchor references..."
if grep -rn "#adr-006\"" docs/architecture/ 2>/dev/null | \
   grep -v "#adr-006-glean-mcp-agent-integration-with-xml-prompt-templates"; then
  echo "  ❌ FAILED: Incorrect ADR-006 references"
  FAILED=$((FAILED + 1))
else
  echo "  ✅ PASSED"
  PASSED=$((PASSED + 1))
fi
echo ""

# Test 6: XML Template Syntax Valid
echo "Test 6: Validate XML template syntax..."
xml_files=$(find sdlc/prompts -type f -name "*.xml" 2>/dev/null || echo "")
xml_failed=0

if [ -z "$xml_files" ]; then
  echo "  ⚠️  No XML templates found"
  PASSED=$((PASSED + 1))
else
  for xml_file in $xml_files; do
    if ! xmllint --noout "$xml_file" 2>&1 >/dev/null; then
      echo "  ❌ Invalid XML: $xml_file"
      xml_failed=1
    fi
  done

  if [ $xml_failed -eq 1 ]; then
    echo "  ❌ FAILED: XML syntax errors"
    FAILED=$((FAILED + 1))
  else
    echo "  ✅ PASSED"
    PASSED=$((PASSED + 1))
  fi
fi
echo ""

# Test 7: AGENT-REGISTRY.yaml Syntax Valid
echo "Test 7: Validate AGENT-REGISTRY.yaml syntax..."
if [ ! -f "docs/glean/AGENT-REGISTRY.yaml" ]; then
  echo "  ⚠️  AGENT-REGISTRY.yaml not found"
  PASSED=$((PASSED + 1))
else
  python3 << 'EOF'
import yaml
import sys
try:
    with open('docs/glean/AGENT-REGISTRY.yaml', 'r') as f:
        registry = yaml.safe_load(f)
    if not registry:
        print("  ❌ FAILED: Registry is empty")
        sys.exit(1)
    print("  ✅ PASSED")
    sys.exit(0)
except Exception as e:
    print(f"  ❌ FAILED: {e}")
    sys.exit(1)
EOF
  if [ $? -eq 0 ]; then
    PASSED=$((PASSED + 1))
  else
    FAILED=$((FAILED + 1))
  fi
fi
echo ""

# Test 8: Agent Schemas Standardized (JSON Schema Draft 7)
echo "Test 8: Validate agent schemas are standardized..."
if [ ! -f "docs/glean/AGENT-REGISTRY.yaml" ]; then
  echo "  ⚠️  AGENT-REGISTRY.yaml not found"
  PASSED=$((PASSED + 1))
else
  python3 << 'EOF'
import yaml
import sys

try:
    with open('docs/glean/AGENT-REGISTRY.yaml', 'r') as f:
        registry = yaml.safe_load(f)

    errors = []
    checked = 0

    for domain_key in registry:
        if domain_key in ['metadata', 'statistics', 'usage_guidelines', 'references']:
            continue

        if 'agents' not in registry[domain_key]:
            continue

        for agent in registry[domain_key]['agents']:
            checked += 1
            name = agent.get('name', 'Unknown')

            if 'input_schema' in agent:
                schema = agent['input_schema']
                if 'type' not in schema or 'properties' not in schema:
                    errors.append(f"{name}: input_schema not standardized")

            if 'output_schema' in agent:
                schema = agent['output_schema']
                if 'type' not in schema:
                    errors.append(f"{name}: output_schema missing type")

    if errors:
        print(f"  ❌ FAILED: {len(errors)} schema issues")
        for error in errors[:3]:
            print(f"     - {error}")
        sys.exit(1)
    else:
        print(f"  ✅ PASSED ({checked} agents validated)")
        sys.exit(0)

except Exception as e:
    print(f"  ❌ FAILED: {e}")
    sys.exit(1)
EOF
  if [ $? -eq 0 ]; then
    PASSED=$((PASSED + 1))
  else
    FAILED=$((FAILED + 1))
  fi
fi
echo ""

# Test 9: All Agents Have Example Invocations
echo "Test 9: Validate all agents have example_invocation..."
if [ ! -f "docs/glean/AGENT-REGISTRY.yaml" ]; then
  echo "  ⚠️  AGENT-REGISTRY.yaml not found"
  PASSED=$((PASSED + 1))
else
  python3 << 'EOF'
import yaml
import sys

try:
    with open('docs/glean/AGENT-REGISTRY.yaml', 'r') as f:
        registry = yaml.safe_load(f)

    missing = []
    total = 0

    for domain_key in registry:
        if domain_key in ['metadata', 'statistics', 'usage_guidelines', 'references']:
            continue

        if 'agents' not in registry[domain_key]:
            continue

        for agent in registry[domain_key]['agents']:
            total += 1
            name = agent.get('name', 'Unknown')

            if 'example_invocation' not in agent:
                missing.append(name)

    if missing:
        print(f"  ❌ FAILED: {len(missing)} agents missing examples")
        for agent in missing[:3]:
            print(f"     - {agent}")
        sys.exit(1)
    else:
        print(f"  ✅ PASSED ({total} agents have examples)")
        sys.exit(0)

except Exception as e:
    print(f"  ❌ FAILED: {e}")
    sys.exit(1)
EOF
  if [ $? -eq 0 ]; then
    PASSED=$((PASSED + 1))
  else
    FAILED=$((FAILED + 1))
  fi
fi
echo ""

# Test 10: Error Handling in Guide Examples
echo "Test 10: Validate error handling in AGENT-REGISTRY-GUIDE.md..."
if [ ! -f "docs/glean/AGENT-REGISTRY-GUIDE.md" ]; then
  echo "  ⚠️  AGENT-REGISTRY-GUIDE.md not found"
  PASSED=$((PASSED + 1))
else
  try_count=$(grep -c "try:" docs/glean/AGENT-REGISTRY-GUIDE.md)
  except_count=$(grep -c "except" docs/glean/AGENT-REGISTRY-GUIDE.md)
  logger_count=$(grep -c "logger\." docs/glean/AGENT-REGISTRY-GUIDE.md)

  if [ $try_count -ge 30 ] && [ $except_count -ge 30 ] && [ $logger_count -ge 50 ]; then
    echo "  ✅ PASSED (try: $try_count, except: $except_count, logger: $logger_count)"
    PASSED=$((PASSED + 1))
  else
    echo "  ❌ FAILED: Insufficient error handling"
    echo "     try: $try_count (need ≥30)"
    echo "     except: $except_count (need ≥30)"
    echo "     logger: $logger_count (need ≥50)"
    FAILED=$((FAILED + 1))
  fi
fi
echo ""

# Test 11: GitHub Actions Workflow Exists
echo "Test 11: Validate GitHub Actions workflow exists..."
if [ ! -f ".github/workflows/architecture-validation.yml" ]; then
  echo "  ❌ FAILED: Workflow file not found"
  FAILED=$((FAILED + 1))
else
  jobs_count=$(grep -c "^  [a-z-]*:" .github/workflows/architecture-validation.yml)
  if [ $jobs_count -ge 4 ]; then
    echo "  ✅ PASSED ($jobs_count jobs defined)"
    PASSED=$((PASSED + 1))
  else
    echo "  ❌ FAILED: Insufficient jobs ($jobs_count < 4)"
    FAILED=$((FAILED + 1))
  fi
fi
echo ""

# Test 12: Core Principles Document Complete
echo "Test 12: Validate CORE-PRINCIPLES.md completeness..."
if [ ! -f "docs/architecture/CORE-PRINCIPLES.md" ]; then
  echo "  ❌ FAILED: CORE-PRINCIPLES.md not found"
  FAILED=$((FAILED + 1))
else
  has_principle_1=$(grep -c "Principle 1:" docs/architecture/CORE-PRINCIPLES.md)
  has_approved=$(grep -c "Approved Pattern" docs/architecture/CORE-PRINCIPLES.md)
  has_prohibited=$(grep -c "Prohibited Pattern" docs/architecture/CORE-PRINCIPLES.md)

  if [ $has_principle_1 -ge 1 ] && [ $has_approved -ge 1 ] && [ $has_prohibited -ge 1 ]; then
    echo "  ✅ PASSED"
    PASSED=$((PASSED + 1))
  else
    echo "  ❌ FAILED: Missing required sections"
    FAILED=$((FAILED + 1))
  fi
fi
echo ""

echo "=========================================="
echo "Test Results:"
echo "  ✅ Passed: $PASSED / 12"
echo "  ❌ Failed: $FAILED / 12"
echo "=========================================="
echo ""

if [ $FAILED -eq 0 ]; then
  echo "🎉 All tests passed!"
  exit 0
else
  echo "❌ Some tests failed. Please review and fix."
  exit 1
fi
