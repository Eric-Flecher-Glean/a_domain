# Artifact-Driven Validation System

## Overview

The validation process for Agent B is **completely artifact-driven**, meaning all validation logic, rules, examples, and standards are defined in **external files** (artifacts) that can be loaded from the repository or external storage (Google Drive, S3, etc.).

This creates a **declarative, configurable validation system** where:
- ✅ No hardcoded validation logic in agent code
- ✅ All rules are data (JSON/YAML/XML files)
- ✅ Easy to update standards without changing code
- ✅ Version-controlled validation rules
- ✅ Shareable across teams via Google Drive
- ✅ AI agents load artifacts at runtime

---

## Artifact Repository Structure

```
workflow-orchestration/
│
├── global/                                    # Organization-wide artifacts
│   ├── config/
│   │   ├── validation-standards.json         # Global quality thresholds
│   │   └── global-settings.json              # System-wide configuration
│   │
│   └── examples/                              # Shared example library
│       ├── good/
│       │   ├── _metadata.json                 # Example catalog
│       │   └── well-structured-prompts/
│       │       ├── example-001-meeting-summary.xml
│       │       └── example-002-code-review.xml
│       │
│       └── bad/
│           ├── _metadata.json
│           └── anti-patterns/
│               ├── example-001-flat-structure.xml
│               └── example-002-missing-sections.xml
│
└── workflows/
    └── prompt-generation/                     # Workflow-specific artifacts
        ├── workflow-metadata.json             # Workflow definition
        │
        ├── config/
        │   └── workflow-settings.json         # Workflow configuration
        │
        ├── stages/
        │   ├── 01-generate-prompt/
        │   │   ├── stage-config.json          # Stage configuration
        │   │   ├── instructions.md            # Human-readable instructions
        │   │   ├── validation-rules.json      # Generation validation rules
        │   │   └── examples/
        │   │       ├── good/                  # Stage-specific good examples
        │   │       └── bad/                   # Stage-specific bad examples
        │   │
        │   └── 02-validate-quality/           # Agent B's artifacts
        │       ├── stage-config.json          # Stage configuration
        │       ├── instructions.md            # Validation process instructions
        │       ├── validation-rules.json      # Detailed validation logic
        │       └── examples/
        │           ├── good/                  # Examples of valid prompts
        │           └── bad/                   # Examples of invalid prompts
        │
        └── examples/                          # Workflow-level examples
            ├── good/
            └── bad/
```

---

## Artifact Types

### 1. **Configuration Artifacts** (JSON/YAML)

Define rules, thresholds, and settings that control agent behavior.

#### **Global Standards** (`global/config/validation-standards.json`)
```json
{
  "quality_thresholds": {
    "excellent": 95,
    "good": 90,              // Agent B uses this
    "acceptable": 85
  },
  "xml_validation": {
    "required_tags": ["metadata", "primary_goal", "role", "task", "instructions"],
    "max_nesting_depth": 3
  },
  "prompt_naming": {
    "pattern": "^[a-z0-9]{3}-[a-z0-9]{3}-[a-z0-9]{3}$"
  },
  "example_requirements": {
    "min_good_examples": 2,
    "min_bad_examples": 1
  }
}
```

**Purpose**: Organization-wide standards that ALL workflows must follow
**Scope**: Global
**Loaded by**: All agents in all workflows
**Storage**: Repo or Google Drive `/org-standards/`

#### **Validation Rules** (`stages/02-validate-quality/validation-rules.json`)
```json
{
  "success_threshold": 90,
  "structural_checks": {
    "xml_well_formed": {
      "points": 10,
      "severity": "error",
      "description": "XML must be parseable"
    },
    "required_sections_present": {
      "points": 15,
      "severity": "error"
    }
  },
  "completeness_checks": {
    "examples_quality": {
      "points": 10,
      "severity": "warning",
      "description": "Minimum 2 good, 1 bad example"
    }
  },
  "quality_checks": {
    "clarity_and_specificity": {
      "points": 10,
      "severity": "warning"
    }
  }
}
```

**Purpose**: Detailed validation logic for specific stage
**Scope**: Stage-specific (Agent B's validation)
**Loaded by**: Agent B only
**Storage**: Repo or Google Drive `/workflows/prompt-generation/stage-02/`

#### **Agent Spec** (`agents/prompt-validator/agent-spec.yaml`)
```yaml
configuration:
  validation_rules_source: "../../workflow-orchestration/workflows/prompt-generation/stages/02-validate-quality/validation-rules.json"
  examples_source: "../../workflow-orchestration/workflows/prompt-generation/stages/02-validate-quality/examples/"
  global_standards_source: "../../workflow-orchestration/global/config/validation-standards.json"
```

**Purpose**: Points to where artifacts are loaded from
**Scope**: Agent-specific
**Storage**: Always in repo (agent definition)

---

### 2. **Example Artifacts** (XML)

Real examples that demonstrate good/bad patterns.

#### **Good Example** (`global/examples/good/well-structured-prompts/example-001-meeting-summary.xml`)
```xml
<metadata>
  <name>mtg-sum-ext</name>
  <version>1.0</version>
</metadata>

<primary_goal>
  Extract and summarize key information from meeting transcripts...
</primary_goal>

<role>Meeting summarization specialist with expertise in information extraction</role>

<task>Parse meeting transcript and generate structured summary</task>

<instructions>
  <step1>Read the entire meeting transcript to understand context</step1>
  <step2>Identify explicit decisions</step2>
  <step3>Extract action items with owners and deadlines</step3>
  <step4>Capture next steps</step4>
  <step5>Format output using the specified structure</step5>
</instructions>

<examples>
  <good_example>
    Input: "We decided to move forward with Option B..."
    Output: **Decisions:** - Move forward with Option B
  </good_example>

  <bad_example>
    Output: Summary: The team talked about a redesign...
    Issue: Not structured; vague descriptions; missing owners
  </bad_example>
</examples>
```

**Purpose**: Reference examples for comparison
**Scope**: Can be global or stage-specific
**Loaded by**: Agent A (for generation patterns), Agent B (for validation comparison)
**Storage**: Repo or Google Drive `/examples/`

#### **Example Metadata** (`global/examples/good/_metadata.json`)
```json
{
  "example_set_name": "Well-Structured Prompts (Good Examples)",
  "total_examples": 2,
  "examples": [
    {
      "file": "well-structured-prompts/example-001-meeting-summary.xml",
      "name": "mtg-sum-ext",
      "demonstrates": [
        "Proper tag hierarchy",
        "Clear instructions with numbered steps",
        "Multiple good and bad examples"
      ],
      "quality_score": 95,
      "use_cases": ["Information extraction", "Structured summarization"]
    }
  ],
  "key_patterns": {
    "tag_hierarchy": "High-priority tags at outer level",
    "nesting": "Maximum 2-3 levels deep",
    "examples": "Isolated in dedicated <examples> section"
  }
}
```

**Purpose**: Catalog and index example files
**Scope**: Per example set
**Loaded by**: Agents to discover available examples
**Storage**: Repo or Google Drive (same location as examples)

---

### 3. **Instruction Artifacts** (Markdown)

Human-readable documentation for how validation works.

#### **Validation Instructions** (`stages/02-validate-quality/instructions.md`)
```markdown
# Stage 2: Quality Validation Instructions

## Objective
Validate the generated XML prompt against quality standards...

## Validation Checks

### 1. Structural Validation (40 points)
**XML Well-Formedness (10 points)**
- XML is parseable without errors
- All tags properly opened and closed

**Required Sections Present (15 points)**
- `<metadata>` with `<name>` and `<version>`
- `<primary_goal>`, `<role>`, `<task>`, etc.

### 2. Completeness Validation (30 points)
...

### 3. Quality Validation (30 points)
...

## Scoring Algorithm
```
base_score = 100
errors = count of error-severity failures
score = base_score - (errors × 20) - (warnings × 5) + bonuses
isValid = (score >= 90) AND (errors == 0)
```

## Reference Materials
- Load validation rules from: `validation-rules.json`
- Compare against examples: `examples/good/` and `examples/bad/`
```

**Purpose**: Documentation for how to perform validation
**Scope**: Stage-specific
**Loaded by**: Agent B (as system prompt enhancement)
**Storage**: Repo or Google Drive

---

## How Artifacts Are Loaded

### **Runtime Loading Process**

```
┌─────────────────────────────────────────────────────────────────┐
│  Agent B Initialization (When Agent is Called)                  │
└─────────────────────────────────────────────────────────────────┘

1. Load Agent Spec
   ├─ Read: agents/prompt-validator/agent-spec.yaml
   └─ Extract artifact source paths:
      ├─ validation_rules_source
      ├─ examples_source
      ├─ global_standards_source
      └─ instruction_source

2. Load Configuration Artifacts (JSON)
   ├─ Load Global Standards
   │  └─ Read: workflow-orchestration/global/config/validation-standards.json
   │     ├─ quality_thresholds → success_threshold = 90
   │     ├─ xml_validation → required_tags[]
   │     └─ example_requirements → min_good_examples = 2
   │
   └─ Load Validation Rules
      └─ Read: workflow-orchestration/.../02-validate-quality/validation-rules.json
         ├─ structural_checks → xml_well_formed, required_sections...
         ├─ completeness_checks → examples_quality...
         └─ quality_checks → clarity_and_specificity...

3. Load Instruction Artifacts (Markdown)
   └─ Read: workflow-orchestration/.../02-validate-quality/instructions.md
      └─ Append to system_instructions from agent spec

4. Discover Example Artifacts (XML + Metadata)
   ├─ Read: workflow-orchestration/.../02-validate-quality/examples/good/_metadata.json
   │  └─ Get list of good example files
   │
   ├─ Read: workflow-orchestration/.../02-validate-quality/examples/bad/_metadata.json
   │  └─ Get list of bad example files
   │
   ├─ Read: global/examples/good/_metadata.json
   │  └─ Get list of global good examples
   │
   └─ Load examples into memory (optional, for few-shot prompting)

5. Construct Agent B Runtime Context
   └─ Combine all artifacts into execution context:
      ├─ System Instructions (from spec + instructions.md)
      ├─ Validation Rules (merged global standards + stage rules)
      ├─ Example References (file paths or loaded content)
      └─ Scoring Configuration (thresholds, weights, penalties)

6. Ready to Execute
   └─ Agent B can now validate XML prompts using artifact-defined logic
```

---

## Artifact Loading Implementation

### **Python Example: Artifact Loader**

```python
import json
import yaml
from pathlib import Path
from typing import Dict, List, Any

class ArtifactLoader:
    """Loads validation artifacts from repository or external storage"""

    def __init__(self, storage_backend: str = "repo"):
        """
        Args:
            storage_backend: "repo" | "gdrive" | "s3"
        """
        self.backend = storage_backend
        self.cache = {}

    def load_agent_artifacts(self, agent_id: str) -> Dict[str, Any]:
        """Load all artifacts needed for an agent"""

        # 1. Load agent spec
        agent_spec = self._load_yaml(f"agents/{agent_id}/agent-spec.yaml")

        # 2. Load artifacts referenced in spec
        artifacts = {
            "agent_spec": agent_spec,
            "global_standards": self._load_json(
                agent_spec["configuration"]["global_standards_source"]
            ),
            "validation_rules": self._load_json(
                agent_spec["configuration"]["validation_rules_source"]
            ),
            "instructions": self._load_markdown(
                agent_spec["configuration"]["instruction_source"]
            ),
            "examples": self._load_examples(
                agent_spec["configuration"]["examples_source"],
                agent_spec["configuration"]["global_examples_source"]
            )
        }

        return artifacts

    def _load_json(self, path: str) -> Dict:
        """Load JSON file from storage backend"""
        if self.backend == "repo":
            return json.loads(Path(path).read_text())
        elif self.backend == "gdrive":
            return self._load_from_gdrive(path, format="json")
        elif self.backend == "s3":
            return self._load_from_s3(path, format="json")

    def _load_yaml(self, path: str) -> Dict:
        """Load YAML file from storage backend"""
        if self.backend == "repo":
            return yaml.safe_load(Path(path).read_text())
        elif self.backend == "gdrive":
            return self._load_from_gdrive(path, format="yaml")

    def _load_markdown(self, path: str) -> str:
        """Load Markdown file from storage backend"""
        if self.backend == "repo":
            return Path(path).read_text()
        elif self.backend == "gdrive":
            return self._load_from_gdrive(path, format="text")

    def _load_examples(self, stage_examples_path: str,
                       global_examples_path: str) -> Dict[str, List]:
        """Load example files from both stage and global locations"""

        examples = {
            "good": [],
            "bad": []
        }

        # Load stage-specific examples
        stage_good_meta = self._load_json(f"{stage_examples_path}/good/_metadata.json")
        stage_bad_meta = self._load_json(f"{stage_examples_path}/bad/_metadata.json")

        for ex in stage_good_meta["examples"]:
            file_path = f"{stage_examples_path}/good/{ex['file']}"
            examples["good"].append({
                "name": ex["name"],
                "content": self._load_xml(file_path),
                "metadata": ex
            })

        # Load global examples
        global_good_meta = self._load_json(f"{global_examples_path}/good/_metadata.json")

        for ex in global_good_meta["examples"]:
            file_path = f"{global_examples_path}/good/{ex['file']}"
            examples["good"].append({
                "name": ex["name"],
                "content": self._load_xml(file_path),
                "metadata": ex,
                "is_global": True
            })

        return examples

    def _load_from_gdrive(self, path: str, format: str) -> Any:
        """Load artifact from Google Drive"""
        # Implementation would use Google Drive API
        # Example: Convert path to Google Drive file ID
        # Download file content
        # Parse based on format
        pass

    def _load_from_s3(self, path: str, format: str) -> Any:
        """Load artifact from S3"""
        # Implementation would use boto3
        pass


# Usage in Agent B
loader = ArtifactLoader(storage_backend="repo")  # or "gdrive"
artifacts = loader.load_agent_artifacts("prompt-validator-001")

# Now artifacts contains all validation rules, examples, standards
validation_rules = artifacts["validation_rules"]
global_standards = artifacts["global_standards"]
examples = artifacts["examples"]
```

---

## External Storage Integration

### **Option 1: Google Drive Storage**

```
Google Drive Folder Structure:
/
├── OrgName-PromptEngineering/
    ├── global/
    │   ├── config/
    │   │   ├── validation-standards.json
    │   │   └── global-settings.json
    │   └── examples/
    │       ├── good/
    │       │   ├── _metadata.json
    │       │   └── well-structured-prompts/
    │       │       ├── example-001-meeting-summary.xml
    │       │       └── example-002-code-review.xml
    │       └── bad/
    │           └── anti-patterns/
    │               └── example-001-flat-structure.xml
    │
    └── workflows/
        └── prompt-generation/
            └── stages/
                └── 02-validate-quality/
                    ├── validation-rules.json
                    ├── instructions.md
                    └── examples/
```

**Benefits**:
- ✅ Easy collaboration across teams
- ✅ Non-technical users can update examples
- ✅ Version history via Google Drive
- ✅ Shared across entire organization
- ✅ No Git knowledge required

**Configuration**:
```yaml
# agents/prompt-validator/agent-spec.yaml
configuration:
  storage_backend: "gdrive"
  gdrive_folder_id: "1a2b3c4d5e6f7g8h9i"

  validation_rules_source: "workflows/prompt-generation/stages/02-validate-quality/validation-rules.json"
  examples_source: "workflows/prompt-generation/stages/02-validate-quality/examples/"
  global_standards_source: "global/config/validation-standards.json"
```

---

### **Option 2: Hybrid Storage**

```yaml
# Mix repo and Google Drive
configuration:
  # Agent specs and code: Always in repo
  agent_spec_source: "repo://agents/prompt-validator/agent-spec.yaml"

  # Organization standards: Google Drive (shared across teams)
  global_standards_source: "gdrive://global/config/validation-standards.json"

  # Workflow-specific rules: Repo (version controlled with code)
  validation_rules_source: "repo://workflow-orchestration/.../validation-rules.json"

  # Examples: Google Drive (easy to add new examples)
  examples_source: "gdrive://workflows/prompt-generation/.../examples/"
  global_examples_source: "gdrive://global/examples/"
```

**Benefits**:
- ✅ Best of both worlds
- ✅ Code and critical configs in Git
- ✅ Examples and docs in Google Drive
- ✅ Non-technical users can contribute examples
- ✅ Technical users use Git for rules

---

## Artifact Discovery and Caching

### **Discovery Process**

```python
class ArtifactDiscovery:
    """Discovers available artifacts from storage"""

    def discover_examples(self, examples_path: str) -> Dict:
        """Discover all available examples"""

        # Read metadata files
        good_meta = self._load_json(f"{examples_path}/good/_metadata.json")
        bad_meta = self._load_json(f"{examples_path}/bad/_metadata.json")

        return {
            "good_examples": [
                {
                    "name": ex["name"],
                    "file": ex["file"],
                    "demonstrates": ex["demonstrates"],
                    "quality_score": ex.get("quality_score"),
                    "use_cases": ex.get("use_cases", [])
                }
                for ex in good_meta["examples"]
            ],
            "bad_examples": [
                {
                    "name": ex["name"],
                    "file": ex["file"],
                    "anti_patterns": ex.get("anti_patterns", [])
                }
                for ex in bad_meta["examples"]
            ]
        }

    def search_examples_by_use_case(self, use_case: str) -> List[Dict]:
        """Find examples relevant to a specific use case"""
        all_examples = self.discover_examples("global/examples")

        return [
            ex for ex in all_examples["good_examples"]
            if use_case.lower() in [uc.lower() for uc in ex.get("use_cases", [])]
        ]
```

### **Caching Strategy**

```python
class ArtifactCache:
    """Cache artifacts to avoid repeated loads"""

    def __init__(self, ttl_seconds: int = 3600):
        self.cache = {}
        self.ttl = ttl_seconds

    def get_or_load(self, artifact_path: str, loader_func):
        """Get from cache or load if not present/expired"""

        cache_key = artifact_path

        if cache_key in self.cache:
            cached_item = self.cache[cache_key]
            if time.time() - cached_item["loaded_at"] < self.ttl:
                return cached_item["data"]

        # Load fresh
        data = loader_func(artifact_path)
        self.cache[cache_key] = {
            "data": data,
            "loaded_at": time.time()
        }

        return data
```

---

## Artifact Versioning

### **Version Control in Metadata**

```json
{
  "artifact_type": "validation_rules",
  "version": "2.1.0",
  "created": "2026-01-26",
  "last_modified": "2026-01-26",
  "changelog": [
    {
      "version": "2.1.0",
      "date": "2026-01-26",
      "changes": ["Added context_quality validation phase"]
    },
    {
      "version": "2.0.0",
      "date": "2026-01-20",
      "changes": ["Restructured scoring weights"]
    }
  ],
  "rules": { ... }
}
```

### **Agent Spec Version Pinning**

```yaml
configuration:
  validation_rules_source: "workflows/prompt-generation/.../validation-rules.json"
  validation_rules_version: "2.1.0"  # Pin to specific version

  # Or use semantic versioning
  validation_rules_version_constraint: "^2.0.0"  # Any 2.x version
```

---

## Benefits of Artifact-Driven Architecture

### **1. Separation of Concerns**
- ✅ Agent code = execution logic
- ✅ Artifacts = business rules and domain knowledge
- ✅ Change rules without changing code

### **2. Collaboration**
- ✅ Non-technical users can update examples in Google Drive
- ✅ Domain experts maintain validation rules
- ✅ Engineers maintain agent code

### **3. Flexibility**
- ✅ Different workflows can have different rules
- ✅ A/B test different validation strategies
- ✅ Easy to create workflow variations

### **4. Governance**
- ✅ Centralized standards in Google Drive
- ✅ Version history for audit trail
- ✅ Access control on sensitive artifacts

### **5. Scalability**
- ✅ Add new examples without code changes
- ✅ Share artifacts across multiple agents
- ✅ Reuse validation logic across workflows

---

## Summary

The validation process is **100% artifact-driven**:

| Artifact Type | Purpose | Storage | Loaded By |
|---------------|---------|---------|-----------|
| **validation-rules.json** | Detailed validation logic | Repo or GDrive | Agent B |
| **validation-standards.json** | Global quality thresholds | Repo or GDrive | All agents |
| **instructions.md** | Human-readable validation docs | Repo or GDrive | Agent B |
| **example-*.xml** | Reference examples | Repo or GDrive | Agent A, Agent B |
| **_metadata.json** | Example catalog and indexing | Repo or GDrive | Discovery service |
| **agent-spec.yaml** | Agent definition and artifact refs | Repo (always) | Orchestrator |

**Key Insight**: Agent B is a **validation engine** that executes rules defined in artifacts. The artifacts ARE the validation logic, not the agent code.

**Future State**: All artifacts can be stored in Google Drive, making it easy for non-technical teams to:
- Add new examples by uploading XML files
- Update validation rules by editing JSON files
- Change quality thresholds without touching code
- Share best practices across organization

---

**Last Updated:** 2026-01-26
**Version:** 1.0.0
**Status:** ✅ Production Ready
