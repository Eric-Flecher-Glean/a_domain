# Context Management Workflow - How It Works

## Your Question

> How does this workflow support adding or retrieving context required to execute a prompt? How does it identify what the user should provide?

## Answer: Enhanced Workflow with Context Analysis

The **enhanced workflow** (`make xml-prompt-enhanced`) now:

1. ✅ **Analyzes the task** to identify required inputs
2. ✅ **Identifies context sources** (Glean, user-provided, documents)
3. ✅ **Generates input specifications** in the XML prompt
4. ✅ **Specifies Glean MCP integrations** needed for context retrieval
5. ✅ **Validates context completeness** as part of quality score

## Example: Meeting Summarization

### Command
```bash
make xml-prompt-enhanced TASK="Create a prompt for summarizing meeting transcripts"
```

### Step 1: Automatic Input Analysis

The system analyzes the task and identifies:

```
🔍 Analyzing task for input requirements...
   Required inputs: 2
     - meeting_transcript (string): Full text transcript of the meeting
     - attendee_list (array): List of meeting attendees
   Optional inputs: 1
     - meeting_date (string, default: today)
   Context sources: 1
     - previous_meetings via glean_meeting_lookup
   Glean MCP tools needed: mcp__glean__meeting_lookup
```

### Step 2: Generated XML with Input Specification

```xml
<input_specification>
  <input>
    <name>meeting_transcript</name>
    <type>string</type>
    <required>true</required>
    <description>Full text transcript of the meeting</description>
    <source>user_provided</source>
  </input>

  <input>
    <name>attendee_list</name>
    <type>array</type>
    <required>true</required>
    <description>List of meeting attendees</description>
    <source>user_provided</source>
  </input>

  <input>
    <name>meeting_date</name>
    <type>string</type>
    <required>false</required>
    <source>user_provided</source>
    <default>today</default>
  </input>
</input_specification>

<context_requirements>
  <context>
    <name>previous_meetings</name>
    <source>glean_meeting_lookup</source>
    <query>participants:{{attendee_list}} after:{{meeting_date}}-30d</query>
    <required>false</required>
  </context>
</context_requirements>
```

### Step 3: Context Report

```json
{
  "input_analysis": {
    "required_inputs": [
      {
        "name": "meeting_transcript",
        "type": "string",
        "source": "user_provided",
        "description": "Full text transcript of the meeting"
      },
      {
        "name": "attendee_list",
        "type": "array",
        "source": "user_provided",
        "description": "List of meeting attendees"
      }
    ],
    "optional_inputs": [
      {
        "name": "meeting_date",
        "type": "string",
        "source": "user_provided",
        "default": "today"
      }
    ],
    "context_sources": [
      {
        "name": "previous_meetings",
        "source": "glean_meeting_lookup",
        "query": "participants:{{attendee_list}} after:{{meeting_date}}-30d"
      }
    ],
    "glean_integrations": [
      "mcp__glean__meeting_lookup"
    ]
  },
  "glean_integrations_needed": [
    "mcp__glean__meeting_lookup"
  ]
}
```

## How It Identifies User Inputs

The system uses **pattern matching** on the task description:

### Meeting-related Tasks
**Trigger**: Keywords like "meeting", "summarize meeting"

**Identified Inputs**:
- ✅ `meeting_transcript` (required, user-provided)
- ✅ `attendee_list` (required, user-provided)
- ✅ `meeting_date` (optional, defaults to "today")

**Context Sources**:
- 🔍 Previous meetings via `glean_meeting_lookup`

### Code Review Tasks
**Trigger**: Keywords like "code", "review"

**Identified Inputs**:
- ✅ `code_content` (required, user-provided)
- ✅ `language` (required, user-provided)

**Context Sources**:
- 🔍 Coding standards via `glean_search`
- 🔍 Similar code via `glean_code_search`

### Customer Feedback Tasks
**Trigger**: Keywords like "customer", "feedback", "sentiment"

**Identified Inputs**:
- ✅ `feedback_text` (required, user-provided)
- ✅ `product_name` (optional, user-provided)

**Context Sources**:
- 🔍 Product info via `glean_search`
- 🔍 Sentiment guidelines via `glean_document`

## Source Types Explained

### 1. user_provided
User must supply this value directly:
```xml
<input>
  <name>meeting_transcript</name>
  <source>user_provided</source>
  <required>true</required>
</input>
```

### 2. glean_search
Retrieved via Glean semantic search:
```xml
<context>
  <name>coding_standards</name>
  <source>glean_search</source>
  <query>coding standards OR style guide language:{{language}}</query>
</context>
```

### 3. glean_meeting_lookup
Retrieved from calendar/meetings:
```xml
<context>
  <name>previous_meetings</name>
  <source>glean_meeting_lookup</source>
  <query>participants:{{attendee_list}} after:{{meeting_date}}-30d</query>
</context>
```

### 4. glean_code_search
Retrieved from code repositories:
```xml
<context>
  <name>similar_code</name>
  <source>glean_code_search</source>
  <query>{{code_pattern}}</query>
</context>
```

### 5. glean_document
Retrieved from specific documents:
```xml
<context>
  <name>sentiment_guidelines</name>
  <source>glean_document</source>
  <document_url>docs/analytics/sentiment-guidelines</document_url>
</context>
```

## Comparison: Basic vs Enhanced

### Basic Workflow (`make xml-prompt`)
```bash
make xml-prompt TASK="Create a prompt for meeting summarization"
```
- ❌ No input identification
- ❌ No context requirements
- ❌ No Glean integration specs
- ✅ Basic XML structure validation

**Output**: Generic XML prompt

### Enhanced Workflow (`make xml-prompt-enhanced`)
```bash
make xml-prompt-enhanced TASK="Create a prompt for meeting summarization"
```
- ✅ Automatic input identification
- ✅ Context requirements with Glean queries
- ✅ Glean MCP tool specifications
- ✅ Context-aware validation
- ✅ Input/context analysis report

**Output**:
- XML prompt with `<input_specification>` and `<context_requirements>`
- Context analysis report (JSON)
- List of required Glean MCP tools

## Test Results

### Test 1: Meeting Summarization
```
Required inputs: 2 (meeting_transcript, attendee_list)
Optional inputs: 1 (meeting_date)
Context sources: 1 (previous_meetings)
Glean tools: mcp__glean__meeting_lookup
Score: 100/100 ✓
```

### Test 2: Code Review
```
Required inputs: 2 (code_content, language)
Context sources: 2 (coding_standards, similar_code)
Glean tools: mcp__glean__search, mcp__glean__code_search
Score: 100/100 ✓
```

### Test 3: Customer Feedback
```
Required inputs: 1 (feedback_text)
Optional inputs: 1 (product_name)
Context sources: 2 (product_info, sentiment_guidelines)
Glean tools: mcp__glean__search, mcp__glean__read_document
Score: 100/100 ✓
```

## Usage

### Generate with Context Analysis
```bash
make xml-prompt-enhanced TASK="your task here"
```

### View Generated Files
```bash
# XML prompt with input/context specifications
cat output/enhanced-prompt.xml

# Context analysis report
cat output/enhanced-prompt-context-report.json
```

### Run Test Suite
```bash
make test-context-analysis
```

## Next Steps

To make this production-ready:

1. **Expand Pattern Matching**: Add more task patterns (email drafting, data analysis, etc.)

2. **Implement Context Retrieval**: Create a tool to actually fetch context from Glean:
   ```javascript
   async function retrieveContext(contextRequirements, userInputs) {
     // Call Glean MCP APIs
     // Return populated context
   }
   ```

3. **Runtime Validation**: Validate that required inputs are provided before execution

4. **Context Caching**: Cache frequently-used context (company glossary, templates)

5. **Template Variables**: Support variable substitution in context queries:
   ```xml
   <query>participants:{{attendee_list}} after:{{meeting_date}}-30d</query>
   ```

## Key Benefits

1. **Self-Documenting Prompts**: Anyone can see what inputs are needed
2. **Automated Context Retrieval**: Fetch company knowledge from Glean automatically
3. **Validation**: Ensure all required data is available before execution
4. **Discoverability**: Know which Glean MCP tools you need
5. **Consistency**: Standardized input/context specification format
