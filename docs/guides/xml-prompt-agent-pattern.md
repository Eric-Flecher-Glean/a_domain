# XML Prompt Agent Implementation Pattern

**Pattern Type**: XML Prompt Agent
**Purpose**: Create custom agents using structured XML prompts
**Repository**: Eric-Flecher-Glean/prompts (https://github.com/Eric-Flecher-Glean/prompts)
**Reference**: ADR-006 in `docs/architecture/ddd-specification.md`

---

## Overview

The XML Prompt Agent pattern enables rapid development of custom, domain-specific agents using version-controlled XML prompts. Unlike Glean MCP agents (which leverage existing capabilities), XML Prompt agents give you fine-grained control over prompt structure, instructions, and constraints.

### When to Use This Pattern

✅ **Use XML Prompt Agent when:**
- Custom domain-specific logic needed (not available in Glean)
- Rapid prototyping or experimentation required (minutes vs. days)
- Custom multi-step orchestration needed
- Building SDLC meta-agents (schema validation, story generation, etc.)
- Need fine-grained control over prompt structure
- Want version-controlled, reusable prompts

❌ **Don't use when:**
- Capability already exists in Glean platform (use Glean MCP Agent instead)
- Need multi-source data integration with enterprise systems
- Require Glean's agentic looping feature
- Want zero implementation cost

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│  Your Application                                        │
│  ┌───────────────────────────────────────────────────┐  │
│  │ Python/TypeScript Code                            │  │
│  │                                                    │  │
│  │  prompt = load_xml_prompt(                        │  │
│  │    repo="Eric-Flecher-Glean/prompts",            │  │
│  │    path="sdlc/requirements/extract-ac.xml",      │  │
│  │    version="1.0.0"                               │  │
│  │  )                                                │  │
│  │  result = execute_prompt(prompt, input_text)     │  │
│  └──────────────────┬────────────────────────────────┘  │
└─────────────────────┼────────────────────────────────────┘
                      │
                      ↓
┌─────────────────────────────────────────────────────────┐
│  Eric-Flecher-Glean/prompts Repository                  │
│  ┌───────────────────────────────────────────────────┐  │
│  │ Git Repository with Versioned XML Prompts         │  │
│  │ - sdlc/requirements/*.xml                         │  │
│  │ - sdlc/code-generation/*.xml                      │  │
│  │ - sales/*.xml                                     │  │
│  │ - Tagged releases (v1.0.0, v1.1.0, etc.)          │  │
│  └──────────────────┬────────────────────────────────┘  │
└─────────────────────┼────────────────────────────────────┘
                      │
                      ↓
┌─────────────────────────────────────────────────────────┐
│  LLM (Claude, GPT-4, etc.)                               │
│  Executes prompt and returns structured output          │
└─────────────────────────────────────────────────────────┘
```

---

## XML Prompt Structure

All XML prompts follow this standardized structure:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<prompt>
  <metadata>
    <name>prompt-name</name>
    <version>1.0.0</version>
    <domain>category/subcategory</domain>
    <author>Your Name</author>
    <created>2026-02-04</created>
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

## Implementation Steps

### 1. Create XML Prompt

```xml
<?xml version="1.0" encoding="UTF-8"?>
<prompt>
  <metadata>
    <name>extract-acceptance-criteria</name>
    <version>1.0.0</version>
    <domain>sdlc/requirements</domain>
  </metadata>

  <role>
    You are an expert requirements analyst extracting testable acceptance criteria.
  </role>

  <task>
    Extract clear, testable acceptance criteria from user story text.
    Number each as AC1, AC2, AC3, etc.
  </task>

  <instructions>
    <step1>Read the user story carefully</step1>
    <step2>Identify all requirements (explicit and implicit)</step2>
    <step3>Formulate each as testable criterion</step3>
    <step4>Validate criteria are INVEST compliant</step4>
  </instructions>

  <output_format>
    <section name="Acceptance Criteria">
      AC#: [Description]
      Type: [Functional|Non-functional|Edge Case]
      Priority: [P0|P1|P2]
    </section>
  </output_format>

  <constraints>
    <constraint>Each criterion must be testable</constraint>
    <constraint>Use AC# prefix (AC1, AC2, etc.)</constraint>
    <constraint>Include at least one edge case</constraint>
  </constraints>
</prompt>
```

### 2. Store in Repository

```bash
# Clone prompts repository
git clone https://github.com/Eric-Flecher-Glean/prompts.git
cd prompts

# Create directory structure
mkdir -p sdlc/requirements

# Copy your XML prompt
cp /path/to/extract-acceptance-criteria.xml sdlc/requirements/

# Commit with semantic versioning
git add sdlc/requirements/extract-acceptance-criteria.xml
git commit -m "Add extract-acceptance-criteria prompt v1.0.0"

# Tag release
git tag -a prompts/sdlc/requirements/extract-acceptance-criteria/v1.0.0 \\
  -m "Release v1.0.0"

git push origin main --tags
```

### 3. Load and Execute

```python
from xml_prompt_loader import XMLPromptLoader
from acceptance_criteria_extractor import AcceptanceCriteriaExtractor

# Load prompt from repository
prompt = XMLPromptLoader.load_from_repository(
    repo="Eric-Flecher-Glean/prompts",
    path="sdlc/requirements/extract-acceptance-criteria.xml",
    version="1.0.0"
)

# Execute with input
extractor = AcceptanceCriteriaExtractor(prompt)
result = extractor.extract(user_story_text)

# Parse results
acceptance_criteria = result['acceptance_criteria']
for ac in acceptance_criteria:
    print(f"{ac['id']}: {ac['description']}")
```

---

## Complete Example

See `examples/xml_prompt_agent_example.py` for a runnable demonstration.

### Run the Example

```bash
uv run examples/xml_prompt_agent_example.py
```

### Expected Output

```
🎯 XML PROMPT AGENT EXAMPLE
================================================================================
STEP 1: Load XML Prompt
================================================================================

✅ Prompt loaded successfully!
   Name: extract-acceptance-criteria
   Version: 1.0.0
   Domain: sdlc/requirements
   Tags: requirements, acceptance-criteria, user-stories, testing

================================================================================
STEP 2: Execute Prompt with User Story
================================================================================

✅ Extraction complete!

================================================================================
STEP 3: Parse and Display Results
================================================================================

📋 ACCEPTANCE CRITERIA EXTRACTION RESULTS
Total Criteria: 5
Coverage: 95%

✅ ACCEPTANCE CRITERIA
AC1: System returns matching results when search query is entered
  Type: Functional
  Priority: P0
  ...

🔗 BACKLOG INTEGRATION
acceptance_criteria:
  - 'AC1: System returns matching results when search query is entered'
  - 'AC2: System filters results based on selected criteria'
  ...

✅ Acceptance criteria ready to add to IMPLEMENTATION_BACKLOG.yaml
```

---

## Benefits

### Rapid Development
- Create new agent in **minutes** vs. days for full Glean agent
- Edit XML, re-run, validate - immediate feedback loop
- No deployment required - just commit to Git

### Fine-Grained Control
- Precise control over role, task, instructions
- Custom constraints and validation rules
- Tailored output format for your use case

### Version Control
- Every prompt version tracked in Git
- Easy rollback to previous versions
- Review changes via Git diff
- Semantic versioning (1.0.0, 1.1.0, 2.0.0)

### Reusability
- Prompts shareable across projects
- Build library of domain-specific agents
- Compose prompts into workflows

### Reviewability
- Human-readable XML format
- Clear structure makes review easy
- Document intent in metadata

---

## Limitations

### Manual Integration
- No built-in multi-source data integration
- Manual implementation of data fetching
- No automatic permission enforcement

### No Agentic Looping
- Single-pass execution (no iterative refinement)
- Must manually implement multi-step workflows
- No automatic quality improvement

### Development Required
- Need to write prompt loader
- Need to implement executor
- Need to handle LLM integration

### Not Battle-Tested
- New prompts need validation
- No usage metrics from other customers
- Potential for prompt engineering issues

---

## Best Practices

### 1. Clear Role Definition

❌ **Vague**:
```xml
<role>You are helpful</role>
```

✅ **Specific**:
```xml
<role>
  You are an expert requirements analyst and QA engineer with expertise in:
  - INVEST principles for user stories
  - BDD and Given-When-Then format
  - Test automation and quality gates
</role>
```

### 2. Structured Instructions

❌ **Single block**:
```xml
<instructions>
  Read the story and extract criteria.
</instructions>
```

✅ **Step-by-step**:
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

❌ **No examples**:
```xml
<examples></examples>
```

✅ **Full example**:
```xml
<examples>
  <example>
    <input>
      As a developer, I want to search by context so I can find agents.
    </input>
    <output>
      AC1: Search returns agents matching specified context
      AC2: Search supports partial context name matching
      AC3: Search returns empty list when no matches found
    </output>
  </example>
</examples>
```

### 4. Validation Rules

```xml
<validation_rules>
  <rule>Each criterion must be testable</rule>
  <rule>Avoid subjective terms (good, appropriate)</rule>
  <rule>At least one P0 criterion must exist</rule>
  <rule>Include edge cases and error conditions</rule>
</validation_rules>
```

---

## Versioning Strategy

### Semantic Versioning

- **MAJOR** (1.0.0 → 2.0.0): Breaking changes to output format or structure
- **MINOR** (1.0.0 → 1.1.0): New features, backward compatible improvements
- **PATCH** (1.0.0 → 1.0.1): Bug fixes, clarifications

### Version Tags

```bash
# Tag format: prompts/{domain}/{name}/v{version}
git tag -a prompts/sdlc/requirements/extract-acceptance-criteria/v1.0.0 \\
  -m "Initial release: Extract acceptance criteria from user stories"

git tag -a prompts/sdlc/requirements/extract-acceptance-criteria/v1.1.0 \\
  -m "Add support for BDD Given-When-Then format"

git tag -a prompts/sdlc/requirements/extract-acceptance-criteria/v2.0.0 \\
  -m "Breaking: New output format with priority and type"
```

### Metadata Version

Always update `<version>` in `<metadata>`:

```xml
<metadata>
  <name>extract-acceptance-criteria</name>
  <version>1.1.0</version>  <!-- Update this -->
  ...
</metadata>
```

---

## Comparison with Glean MCP Agent

| Aspect | Glean MCP Agent | XML Prompt Agent |
|--------|----------------|------------------|
| **Development Time** | 0 (already exists) | Minutes to hours |
| **Customization** | Limited | Full control |
| **Data Sources** | Pre-configured (5+) | Manual integration |
| **Security** | Built-in | Manual implementation |
| **Iteration Speed** | Slow (Glean release cycle) | Fast (edit XML, commit) |
| **Agentic Looping** | Built-in | Manual orchestration |
| **Cost** | Zero (existing investment) | Development time |
| **Battle-Tested** | Yes (222 customers) | No (new prompts) |
| **Use Case** | Existing capabilities | Custom logic, SDLC meta-agents |

---

## Integration with Domain Registry

Register XML Prompt agents in the Domain Registry:

```yaml
agent_id: "ac-extractor-v1"
name: "Acceptance Criteria Extractor"
bounded_context: "SDLC.RequirementsManagement"
implementation_type: "xml_prompt"
implementation:
  repository: "Eric-Flecher-Glean/prompts"
  prompt_path: "sdlc/requirements/extract-acceptance-criteria.xml"
  version: "1.0.0"
  llm_model: "claude-3-5-sonnet-20241022"  # LLM used to execute prompt
supported_intents:
  - "ExtractAcceptanceCriteria"
input_schema:
  type: "object"
  properties:
    user_story:
      type: "string"
      description: "User story text to extract criteria from"
output_schema:
  type: "object"
  properties:
    acceptance_criteria:
      type: "array"
      items:
        type: "object"
        properties:
          id: { type: "string" }
          description: { type: "string" }
          type: { type: "string" }
          priority: { type: "string" }
```

---

## Related Documentation

- **ADR-006**: Dual-Mode Agent Implementation Strategy (`docs/architecture/ddd-specification.md`)
- **Glean MCP Pattern**: `docs/guides/glean-mcp-agent-pattern.md`
- **Master Guide**: `docs/guides/agent-implementation-guide.md`
- **Example Code**: `examples/xml_prompt_agent_example.py`
- **Example Prompt**: `examples/prompts/extract-acceptance-criteria.xml`
- **Repository**: https://github.com/Eric-Flecher-Glean/prompts

---

## Next Steps

1. ✅ Review this guide
2. ✅ Run the example: `uv run examples/xml_prompt_agent_example.py`
3. ✅ Review example prompt: `examples/prompts/extract-acceptance-criteria.xml`
4. 🔄 Create your own XML prompt following the structure
5. 🔄 Store in Eric-Flecher-Glean/prompts repository
6. 🔄 Implement prompt loader and executor for your use case
7. 🔄 Register agent capability in Domain Registry

---

**Last Updated**: 2026-02-04
**Pattern Version**: 1.0.0
**Related Stories**: P1-EXAMPLE-001, P1-EXAMPLE-002
