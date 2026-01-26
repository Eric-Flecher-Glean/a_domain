#!/bin/bash
# Validates workflow structure against the official standard
# Usage: ./scripts/validate-workflow-structure.sh <workflow-directory>

set -e

WORKFLOW_DIR="$1"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

if [ -z "$WORKFLOW_DIR" ]; then
  echo -e "${RED}Error: No workflow directory specified${NC}"
  echo "Usage: $0 <workflow-directory>"
  echo "Example: $0 workflow-orchestration/workflows/prompt-generation"
  exit 1
fi

if [ ! -d "$WORKFLOW_DIR" ]; then
  echo -e "${RED}Error: Directory does not exist: $WORKFLOW_DIR${NC}"
  exit 1
fi

ERRORS=0
WARNINGS=0

# Check if a file exists
check_file() {
  local filepath="$1"
  local required="$2"  # "required" or "optional"

  if [ ! -f "$WORKFLOW_DIR/$filepath" ]; then
    if [ "$required" = "required" ]; then
      echo -e "${RED}❌ Missing required file: $filepath${NC}"
      ((ERRORS++))
    else
      echo -e "${YELLOW}⚠️  Missing optional file: $filepath${NC}"
      ((WARNINGS++))
    fi
  else
    echo -e "${GREEN}✅ Found: $filepath${NC}"
  fi
}

# Check if a directory exists
check_dir() {
  local dirpath="$1"
  local required="$2"  # "required" or "optional"

  if [ ! -d "$WORKFLOW_DIR/$dirpath" ]; then
    if [ "$required" = "required" ]; then
      echo -e "${RED}❌ Missing required directory: $dirpath${NC}"
      ((ERRORS++))
    else
      echo -e "${YELLOW}⚠️  Missing optional directory: $dirpath${NC}"
      ((WARNINGS++))
    fi
  else
    echo -e "${GREEN}✅ Found directory: $dirpath${NC}"
  fi
}

# Validate JSON file
validate_json() {
  local filepath="$1"

  if [ -f "$WORKFLOW_DIR/$filepath" ]; then
    if ! python3 -m json.tool "$WORKFLOW_DIR/$filepath" > /dev/null 2>&1; then
      echo -e "${RED}❌ Invalid JSON: $filepath${NC}"
      ((ERRORS++))
    fi
  fi
}

# Check if stage naming follows convention (NN-stage-name)
validate_stage_naming() {
  local stage_dir="$1"

  if [[ ! "$stage_dir" =~ ^[0-9]{2}- ]]; then
    echo -e "${RED}❌ Invalid stage naming: $stage_dir (must start with NN-)${NC}"
    ((ERRORS++))
  fi
}

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Workflow Structure Validation                             ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo
echo -e "${BLUE}Validating:${NC} $WORKFLOW_DIR"
echo

# === Root Level Required Files ===
echo -e "${BLUE}━━━ Root Level Files ━━━${NC}"
check_file "workflow-metadata.json" "required"
check_file "README.md" "required"
validate_json "workflow-metadata.json"
echo

# === Config Directory ===
echo -e "${BLUE}━━━ Config Directory ━━━${NC}"
check_dir "config" "required"
check_file "config/workflow-settings.json" "required"
validate_json "config/workflow-settings.json"
echo

# === Examples Directory (Optional) ===
echo -e "${BLUE}━━━ Examples Directory (Optional) ━━━${NC}"
check_dir "examples" "optional"
if [ -d "$WORKFLOW_DIR/examples" ]; then
  check_dir "examples/good" "optional"
  check_dir "examples/bad" "optional"
fi
echo

# === Stages Directory ===
echo -e "${BLUE}━━━ Stages Directory ━━━${NC}"
check_dir "stages" "required"
echo

# === Individual Stages ===
if [ -d "$WORKFLOW_DIR/stages" ]; then
  STAGE_COUNT=0

  for stage_dir in "$WORKFLOW_DIR/stages"/*; do
    if [ -d "$stage_dir" ]; then
      stage_name=$(basename "$stage_dir")
      ((STAGE_COUNT++))

      echo -e "${BLUE}━━━ Stage: $stage_name ━━━${NC}"

      # Validate stage naming convention
      validate_stage_naming "$stage_name"

      # Required stage files
      check_file "stages/$stage_name/stage-config.json" "required"
      check_file "stages/$stage_name/instructions.md" "required"
      check_file "stages/$stage_name/validation-rules.json" "required"

      # Validate JSON files
      validate_json "stages/$stage_name/stage-config.json"
      validate_json "stages/$stage_name/validation-rules.json"

      # Optional stage examples
      check_dir "stages/$stage_name/examples" "optional"
      if [ -d "$WORKFLOW_DIR/stages/$stage_name/examples" ]; then
        check_dir "stages/$stage_name/examples/good" "optional"
        check_dir "stages/$stage_name/examples/bad" "optional"
      fi

      echo
    fi
  done

  if [ $STAGE_COUNT -eq 0 ]; then
    echo -e "${RED}❌ No stages found in stages/ directory${NC}"
    ((ERRORS++))
  else
    echo -e "${GREEN}✅ Found $STAGE_COUNT stage(s)${NC}"
    echo
  fi
fi

# === Field Validation (workflow-metadata.json) ===
if [ -f "$WORKFLOW_DIR/workflow-metadata.json" ]; then
  echo -e "${BLUE}━━━ Metadata Field Validation ━━━${NC}"

  # Check required fields using python
  python3 << EOF
import json
import sys

try:
    with open("$WORKFLOW_DIR/workflow-metadata.json", "r") as f:
        metadata = json.load(f)

    required_fields = [
        "workflow_id",
        "version",
        "name",
        "description",
        "pattern",
        "created",
        "updated",
        "status",
        "stages"
    ]

    errors = 0
    for field in required_fields:
        if field not in metadata:
            print(f"\033[0;31m❌ Missing required field in workflow-metadata.json: {field}\033[0m")
            errors += 1
        else:
            print(f"\033[0;32m✅ Field present: {field}\033[0m")

    # Validate version format (semantic versioning)
    if "version" in metadata:
        import re
        if not re.match(r'^\d+\.\d+\.\d+$', metadata["version"]):
            print(f"\033[0;31m❌ Invalid version format (must be MAJOR.MINOR.PATCH): {metadata['version']}\033[0m")
            errors += 1

    # Validate status values
    if "status" in metadata:
        valid_statuses = ["active", "deprecated", "testing"]
        if metadata["status"] not in valid_statuses:
            print(f"\033[0;31m❌ Invalid status (must be active/deprecated/testing): {metadata['status']}\033[0m")
            errors += 1

    # Validate stages is not empty
    if "stages" in metadata:
        if not isinstance(metadata["stages"], list) or len(metadata["stages"]) == 0:
            print(f"\033[0;31m❌ stages field must be a non-empty array\033[0m")
            errors += 1

    sys.exit(errors)

except Exception as e:
    print(f"\033[0;31m❌ Error validating metadata: {e}\033[0m")
    sys.exit(1)
EOF

  if [ $? -ne 0 ]; then
    ((ERRORS+=$?))
  fi

  echo
fi

# === Summary ===
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Validation Summary                                        ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
  echo -e "${GREEN}✅ Workflow structure is valid!${NC}"
  echo -e "${GREEN}   No errors or warnings found.${NC}"
  exit 0
elif [ $ERRORS -eq 0 ]; then
  echo -e "${YELLOW}⚠️  Workflow structure is valid with warnings${NC}"
  echo -e "${YELLOW}   Warnings: $WARNINGS${NC}"
  echo
  echo -e "${YELLOW}Warnings indicate missing optional files or directories.${NC}"
  echo -e "${YELLOW}These do not prevent the workflow from functioning.${NC}"
  exit 0
else
  echo -e "${RED}❌ Workflow structure validation failed${NC}"
  echo -e "${RED}   Errors: $ERRORS${NC}"
  if [ $WARNINGS -gt 0 ]; then
    echo -e "${YELLOW}   Warnings: $WARNINGS${NC}"
  fi
  echo
  echo -e "${RED}Please fix the errors above to comply with the standard.${NC}"
  echo -e "${BLUE}See: workflow-orchestration/WORKFLOW-STRUCTURE-STANDARD.md${NC}"
  exit 1
fi
