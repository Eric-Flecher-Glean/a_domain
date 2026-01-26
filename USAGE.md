# Quick Start Guide: XML Prompt Generation

## Prerequisites

```bash
# Install Node.js if not already installed
# The scripts use Node.js for orchestration
```

## Basic Usage

### Generate an XML Prompt

```bash
make xml-prompt TASK="Create a prompt for meeting summarization"
```

This will:
1. Call the `generate_xml_prompt` tool with your task description
2. Validate the generated prompt with `validate_prompt_quality`
3. If score < 90, automatically refine with feedback (up to 3 attempts)
4. Save the final prompt to `output/generated-prompt.xml`
5. Save a validation report to `output/generated-prompt-report.json`

### Validate an Existing Prompt

```bash
make validate-prompt FILE="output/my-prompt.xml"
```

This will:
1. Load the XML file
2. Run quality validation
3. Display score breakdown and feedback

### Run Test Suite

```bash
make test-workflow
```

Tests the workflow with example tasks:
- Meeting summarization
- Code review
- Email drafting

### Clean Output

```bash
make clean
```

Removes all generated files from the `output/` directory.

## Examples

### Example 1: Meeting Summarizer

```bash
make xml-prompt TASK="Create a prompt for summarizing meeting transcripts"
```

**Output** (after 2 attempts):
```
🚀 Starting XML Prompt Generation Workflow
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📝 Calling generate_xml_prompt (attempt 1/3)...
   Request: Create a prompt for summarizing meeting transcripts
✓ Generated prompt: abc-def-123

✓ Calling validate_prompt_quality (attempt 1/3)...

📊 Validation Results (Attempt 1):
   Quality Score: 85/100
   Status: NEEDS IMPROVEMENT

   Score Breakdown:
     Structural:   40/40
     Completeness: 20/30
     Quality:      25/30

⚠️  Validation failed. Refining with feedback...

📝 Calling generate_xml_prompt (attempt 2/3)...
   Request: Create a prompt for summarizing meeting transcripts
   Feedback items: 3
     1. Add at least 2 good examples
     2. Add 1 bad example with explanation
     3. Improve instruction clarity
✓ Generated prompt: abc-def-123

✓ Calling validate_prompt_quality (attempt 2/3)...

📊 Validation Results (Attempt 2):
   Quality Score: 95/100
   Status: PASS ✓

   Score Breakdown:
     Structural:   40/40
     Completeness: 30/30
     Quality:      25/30

✅ SUCCESS! Prompt validated successfully.

💾 Saved to: output/generated-prompt.xml
📋 Report saved to: output/generated-prompt-report.json
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Example 2: Code Review Assistant

```bash
make xml-prompt TASK="Generate a prompt for performing code reviews with security focus"
```

### Example 3: Custom Validation

```bash
# Generate a prompt
make xml-prompt TASK="Create a sentiment analysis prompt"

# Later, validate it again
make validate-prompt FILE="output/generated-prompt.xml"
```

## Output Files

After running `make xml-prompt`, you'll find:

```
output/
├── generated-prompt.xml        # The final XML prompt
└── generated-prompt-report.json # Validation report
```

**generated-prompt-report.json** contains:
```json
{
  "prompt_name": "abc-def-123",
  "task": "Your original task description",
  "attempts": 2,
  "final_score": 95,
  "validation_history": [
    {
      "isValid": false,
      "qualityScore": 85,
      "checks": [...],
      "feedback": [...]
    },
    {
      "isValid": true,
      "qualityScore": 95,
      "checks": [...],
      "feedback": []
    }
  ]
}
```

## Advanced Usage

### Direct Script Usage

You can also call the Node.js script directly:

```bash
# Generate mode
node scripts/run-mcp-workflow.js \
  --mode generate \
  --task "Your task here" \
  --output custom-output.xml \
  --max-attempts 3

# Validate mode
node scripts/run-mcp-workflow.js \
  --mode validate \
  --file path/to/prompt.xml
```

### Custom Output Location

```bash
make xml-prompt TASK="..." OUTPUT="custom/path/prompt.xml"
```

## What Happens Under the Hood

The workflow orchestrates two Glean agents:

```
┌─────────────────────────────────────────────────────────────┐
│                    User Request                             │
│           "Create a prompt for X"                           │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │  Attempt Loop (1-3)   │
         └───────────┬───────────┘
                     │
                     ▼
         ┌─────────────────────────────┐
         │  Agent: prompt-generator-001│
         │  Tool: generate_xml_prompt  │
         │  • Parse request            │
         │  • Generate XML             │
         │  • Apply feedback (if any)  │
         └─────────────┬───────────────┘
                       │
                       ▼
         ┌─────────────────────────────┐
         │ Agent: prompt-validator-001 │
         │ Tool: validate_prompt_quality│
         │ • Check structure           │
         │ • Calculate score (0-100)   │
         │ • Generate feedback         │
         └─────────────┬───────────────┘
                       │
                       ▼
              ┌────────────────┐
              │ Score >= 90?   │
              └───┬────────┬───┘
                  │        │
               YES│        │NO
                  │        │
                  ▼        ▼
              ┌─────┐  ┌──────────────┐
              │DONE │  │Loop back with│
              │     │  │feedback      │
              └─────┘  └──────────────┘
```

## Integration with Glean

**Note**: The current implementation uses simulated agent calls. To connect to actual Glean MCP servers:

1. **Register the MCP server** in your Glean instance
2. **Update the API calls** in `scripts/run-mcp-workflow.js` to use Glean's MCP API
3. **Configure authentication** (OAuth tokens, API keys)

See the [MCP Server README](mcp-servers/prompt-engineering/README.md) for deployment instructions.

## Troubleshooting

### "node: command not found"

Install Node.js:
```bash
brew install node  # macOS
# or download from https://nodejs.org
```

### "TASK parameter required"

Make sure to quote your task:
```bash
make xml-prompt TASK="your task here"
# NOT: make xml-prompt TASK=your task here
```

### Max attempts reached

If the prompt doesn't pass validation after 3 attempts, check the report:
```bash
cat output/generated-prompt-report.json
```

Look at the feedback in `validation_history` to understand what's failing.

## Next Steps

- Review the [agent specifications](agents/) to understand the validation criteria
- Check [validation rules](workflow-orchestration/workflows/prompt-generation/stages/02-validate-quality/validation-rules.json)
- Explore [example prompts](workflow-orchestration/global/examples/)
