# XML Prompt Examples

This directory contains example XML prompts demonstrating the XML Prompt Agent implementation pattern.

## Production Storage

In production, XML prompts should be stored in the **Eric-Flecher-Glean/prompts** repository:

**Repository**: https://github.com/Eric-Flecher-Glean/prompts

**Directory Structure**:
```
Eric-Flecher-Glean/prompts/
├── sdlc/
│   ├── requirements/
│   │   ├── extract-acceptance-criteria.xml
│   │   ├── extract-user-stories.xml
│   │   └── prioritize-backlog.xml
│   ├── code-generation/
│   │   ├── generate-test-stubs.xml
│   │   └── scaffold-component.xml
│   └── documentation/
│       ├── generate-readme.xml
│       └── api-docs-from-code.xml
├── sales/
│   ├── pain-point-extraction.xml
│   ├── deal-strategy.xml
│   └── competitive-analysis.xml
└── README.md
```

## Local Examples

The prompts in this directory are local examples for demonstration purposes:

- `extract-acceptance-criteria.xml` - Extract testable ACs from user stories

## How to Store in Production Repository

### 1. Clone the Prompts Repository

```bash
git clone https://github.com/Eric-Flecher-Glean/prompts.git
cd prompts
```

### 2. Create Directory Structure

```bash
mkdir -p sdlc/requirements
```

### 3. Copy Prompt File

```bash
cp /path/to/examples/prompts/extract-acceptance-criteria.xml \\
   sdlc/requirements/extract-acceptance-criteria.xml
```

### 4. Commit with Semantic Versioning

```bash
git add sdlc/requirements/extract-acceptance-criteria.xml
git commit -m "Add extract-acceptance-criteria prompt v1.0.0

- Extract testable acceptance criteria from user stories
- Supports INVEST principles and BDD Given-When-Then format
- Includes example and validation rules"

git tag -a prompts/sdlc/requirements/extract-acceptance-criteria/v1.0.0 \\
  -m "Release v1.0.0 of extract-acceptance-criteria prompt"

git push origin main --tags
```

### 5. Reference in Code

```python
from xml_prompt_loader import load_prompt

prompt = load_prompt(
    repository="Eric-Flecher-Glean/prompts",
    path="sdlc/requirements/extract-acceptance-criteria.xml",
    version="1.0.0"  # Can also use "latest"
)
```

## XML Prompt Structure

All XML prompts follow this standardized structure:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<prompt>
  <metadata>
    <name>prompt-name</name>
    <version>1.0.0</version>
    <domain>category/subcategory</domain>
    <tags>...</tags>
  </metadata>

  <role>Who is executing this prompt</role>

  <task>What needs to be accomplished</task>

  <instructions>
    <step1>First step</step1>
    <step2>Second step</step2>
  </instructions>

  <output_format>
    Expected structure of output
  </output_format>

  <constraints>
    Rules and limitations
  </constraints>

  <examples>
    Sample inputs and outputs
  </examples>

  <validation_rules>
    Quality criteria
  </validation_rules>
</prompt>
```

## Versioning Strategy

### Semantic Versioning

Use semantic versioning (MAJOR.MINOR.PATCH):

- **MAJOR**: Breaking changes to prompt structure or output format
- **MINOR**: New features or significant improvements (backward compatible)
- **PATCH**: Bug fixes, clarifications, minor improvements

### Version Tags

```bash
# Tag format: prompts/{domain}/{name}/v{version}
git tag -a prompts/sdlc/requirements/extract-acceptance-criteria/v1.0.0
git tag -a prompts/sdlc/requirements/extract-acceptance-criteria/v1.1.0
git tag -a prompts/sdlc/requirements/extract-acceptance-criteria/v2.0.0
```

### Version in Metadata

Always update `<version>` in `<metadata>`:

```xml
<metadata>
  <name>extract-acceptance-criteria</name>
  <version>1.1.0</version>  <!-- Update this -->
  ...
</metadata>
```

## Deprecation Strategy

When deprecating a prompt version:

1. Add deprecation notice to prompt:
   ```xml
   <metadata>
     ...
     <deprecated>true</deprecated>
     <deprecation_message>Use v2.0.0 instead - improved accuracy</deprecation_message>
     <replacement_version>2.0.0</replacement_version>
   </metadata>
   ```

2. Keep old version for 2 releases before removing

3. Update references in code to new version

## Best Practices

1. **One Prompt, One Purpose**: Each prompt should do one thing well

2. **Clear Role Definition**: Specify expertise and context clearly

3. **Structured Instructions**: Break down into numbered steps

4. **Concrete Examples**: Include at least one full example

5. **Validation Rules**: Specify quality criteria and constraints

6. **Test Your Prompts**: Run with various inputs before committing

7. **Document Changes**: Use detailed commit messages

8. **Version Bumps**: Follow semantic versioning strictly

## Testing Prompts

Before committing, test your prompt:

```bash
# Test with sample input
uv run test_prompt.py \\
  --prompt sdlc/requirements/extract-acceptance-criteria.xml \\
  --input sample_user_story.txt

# Validate XML structure
xmllint --noout --schema prompt-schema.xsd extract-acceptance-criteria.xml

# Run quality checks
uv run validate_prompt.py extract-acceptance-criteria.xml
```

## Related Documentation

- **ADR-006**: Dual-Mode Agent Implementation Strategy
- **Pattern Guide**: `docs/guides/xml-prompt-agent-pattern.md`
- **Master Guide**: `docs/guides/agent-implementation-guide.md`
- **Example**: `examples/xml_prompt_agent_example.py`

---

**Note**: These are local examples. Production prompts should be stored in the Eric-Flecher-Glean/prompts repository for version control and team collaboration.
