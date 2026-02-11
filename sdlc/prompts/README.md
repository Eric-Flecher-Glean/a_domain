# XML Prompt Templates

**Version:** 1.0.0
**Last Updated:** 2026-02-11
**Purpose:** Structured message templates for Glean MCP agent invocations

---

## Overview

This directory contains XML prompt templates used to structure messages sent to Glean agents via `mcp__glean__chat`. These templates are NOT standalone agents—they format the input messages you send to existing Glean agents.

**Key Concept:** All agent capabilities come from Glean platform. XML templates just structure how you ask for those capabilities.

---

## Directory Structure

```
sdlc/prompts/
├── README.md                           # This file
├── requirements/                       # Requirements analysis templates
│   ├── extract-acceptance-criteria.xml
│   ├── extract-requirements.xml
│   └── analyze-requirements.xml
├── design/                             # Design generation templates
│   └── generate-figma-specs.xml
└── testing/                            # Test case generation templates
    └── generate-test-cases.xml
```

---

## Usage

### 1. Load Template

```python
from pathlib import Path
import xml.etree.ElementTree as ET

def load_prompt_template(template_path):
    """Load XML prompt template."""
    with open(template_path, 'r') as f:
        tree = ET.parse(f)
        root = tree.getroot()
    return root

# Example
template = load_prompt_template('sdlc/prompts/requirements/extract-acceptance-criteria.xml')
```

### 2. Format Message

```python
def format_message(template, **kwargs):
    """Format template with input variables."""
    # Extract task and instructions from template
    task = template.find('task').text
    instructions = '\n'.join([step.text for step in template.find('instructions')])

    # Build formatted message
    message = f"{task}\n\nInstructions:\n{instructions}"

    # Substitute variables
    for key, value in kwargs.items():
        message = message.replace(f"{{{key}}}", str(value))

    return message
```

### 3. Invoke Glean Agent

```python
from mcp_client import MCPClient

client = MCPClient()

# Format message using template
message = format_message(template, user_story=story_text)

# Send to Glean agent
response = client.call_tool(
    "mcp__glean__chat",
    {
        "message": message,
        "context": ["domain: requirements_analysis"]
    }
)
```

---

## Template Structure

All XML prompts follow this standardized structure:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<prompt>
  <metadata>
    <name>prompt-name</name>
    <version>1.0.0</version>
    <domain>category/subcategory</domain>
    <author>Your Name</author>
    <created>2026-02-11</created>
    <tags>
      <tag>keyword1</tag>
      <tag>keyword2</tag>
    </tags>
    <description>What this prompt does</description>
  </metadata>

  <role>
    Define who is executing this prompt and their expertise
  </role>

  <task>
    What needs to be accomplished - be specific and clear
  </task>

  <instructions>
    <step1>First step to execute</step1>
    <step2>Second step to execute</step2>
    <step3>Third step to execute</step3>
  </instructions>

  <output_format>
    <section name="Section Name">
      Expected format and structure
    </section>
  </output_format>

  <constraints>
    <constraint>Rule or limitation</constraint>
    <constraint>Another rule</constraint>
  </constraints>

  <examples>
    <example>
      <input>Sample input</input>
      <output>Expected output</output>
    </example>
  </examples>

  <validation_rules>
    <rule>Quality criteria</rule>
    <rule>Validation check</rule>
  </validation_rules>
</prompt>
```

---

## Creating New Templates

### 1. Copy Template Structure

```bash
# Copy existing template as starting point
cp sdlc/prompts/requirements/extract-acceptance-criteria.xml \
   sdlc/prompts/your-domain/your-template.xml
```

### 2. Update Metadata

```xml
<metadata>
  <name>your-template-name</name>
  <version>1.0.0</version>
  <domain>your-domain/category</domain>
  <author>Your Name</author>
  <created>2026-02-11</created>
  <description>Clear description of what this template does</description>
</metadata>
```

### 3. Define Role, Task, Instructions

Be specific about:
- **Role:** Expertise and perspective
- **Task:** Clear objective
- **Instructions:** Step-by-step process

### 4. Specify Output Format

Define expected structure:
```xml
<output_format>
  <section name="Results">
    Format: YAML
    Structure:
      - field1: type
      - field2: type
  </section>
</output_format>
```

### 5. Add Constraints and Examples

```xml
<constraints>
  <constraint>Must be testable</constraint>
  <constraint>Must use specific format</constraint>
</constraints>

<examples>
  <example>
    <input>Sample input text</input>
    <output>Expected output format</output>
  </example>
</examples>
```

---

## Best Practices

### 1. Clear Role Definition

❌ **Vague:**
```xml
<role>You are helpful</role>
```

✅ **Specific:**
```xml
<role>
  You are an expert requirements analyst and QA engineer with expertise in:
  - INVEST principles for user stories
  - BDD and Given-When-Then format
  - Test automation and quality gates
</role>
```

### 2. Structured Instructions

❌ **Single block:**
```xml
<instructions>
  Read the story and extract criteria.
</instructions>
```

✅ **Step-by-step:**
```xml
<instructions>
  <step1>Read user story and identify primary goal</step1>
  <step2>Extract explicit requirements from story text</step2>
  <step3>Infer implicit requirements based on domain knowledge</step3>
  <step4>Formulate each as testable criterion (AC1, AC2, etc.)</step4>
  <step5>Validate criteria are independent and measurable</step5>
</instructions>
```

### 3. Concrete Examples

Always include at least one complete example showing input → output transformation.

---

## Versioning

Templates use semantic versioning:

- **MAJOR** (1.0.0 → 2.0.0): Breaking changes to output format
- **MINOR** (1.0.0 → 1.1.0): New features, backward compatible
- **PATCH** (1.0.0 → 1.0.1): Bug fixes, clarifications

Update version in `<metadata>` when changing template.

---

## References

- [CORE-PRINCIPLES.md](../../docs/architecture/CORE-PRINCIPLES.md#approved-pattern-1b-glean-mcp-with-xml-prompt-templates) - Pattern documentation
- [XML Prompt Agent Pattern Guide](../../docs/guides/xml-prompt-agent-pattern.md) - Detailed guide
- [Glean Agent Registry](../../docs/glean/AGENT-REGISTRY.yaml) - Available Glean agents

---

## Contributing

1. Create new template following structure above
2. Test with actual Glean agent invocation
3. Document in this README
4. Submit PR with template + usage example

---

**Last Updated:** 2026-02-11
**Maintained By:** Architecture Team
