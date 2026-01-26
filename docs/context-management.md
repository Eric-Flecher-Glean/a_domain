# Context Management in Prompt Engineering Workflow

## Problem Statement

Current workflow generates XML prompts but doesn't:
1. Identify what inputs/context the prompt needs when executed
2. Specify where context should come from (user, Glean, APIs, etc.)
3. Validate that required context is available
4. Support runtime context injection

## Proposed Solution

### Enhanced XML Structure

Add `<input_specification>` and `<context_requirements>` sections to generated prompts:

```xml
<metadata>
  <name>mtg-sum-001</name>
  <version>1.0.0</version>
</metadata>

<primary_goal>
Summarize meeting transcripts into actionable insights
</primary_goal>

<!-- NEW: Input Specification -->
<input_specification>
  <input>
    <name>meeting_transcript</name>
    <type>string</type>
    <required>true</required>
    <description>Full text transcript of the meeting</description>
    <source>user_provided</source>
    <validation>
      <min_length>100</min_length>
      <format>plain_text</format>
    </validation>
  </input>

  <input>
    <name>attendee_list</name>
    <type>array</type>
    <required>true</required>
    <description>List of meeting attendees</description>
    <source>user_provided</source>
    <validation>
      <min_items>1</min_items>
      <item_format>email_or_name</item_format>
    </validation>
  </input>

  <input>
    <name>meeting_date</name>
    <type>string</type>
    <required>false</required>
    <description>Date of the meeting</description>
    <source>user_provided</source>
    <default>today</default>
  </input>
</input_specification>

<!-- NEW: Context Requirements -->
<context_requirements>
  <context>
    <name>company_context</name>
    <description>Company-specific terminology and acronyms</description>
    <source>glean_search</source>
    <query>company glossary OR acronym list</query>
    <required>false</required>
    <cache_duration>7d</cache_duration>
  </context>

  <context>
    <name>previous_meetings</name>
    <description>Previous meeting summaries for continuity</description>
    <source>glean_meeting_lookup</source>
    <query>
      participants:{{attendee_list}}
      after:{{meeting_date}}-30d
      extract_transcript:false
    </query>
    <required>false</required>
  </context>

  <context>
    <name>action_items_template</name>
    <description>Standard format for action items</description>
    <source>glean_document</source>
    <document_url>glean://docs/templates/action-items</document_url>
    <required>false</required>
  </context>
</context_requirements>

<role>
You are an expert meeting summarizer...
</role>

<!-- ... rest of prompt ... -->
```

## Workflow Enhancements

### Phase 1: Generate with Context Awareness

Update `prompt-generator-001` to:

1. **Analyze the task** to identify required inputs:
   - "Summarize meeting transcripts" → needs `transcript` input
   - "Code review" → needs `code_file`, `language`, `review_criteria`
   - "Email draft" → needs `purpose`, `recipient`, `context`

2. **Identify context sources**:
   - User-provided (explicit inputs)
   - Glean search (company knowledge)
   - Glean documents (templates, guidelines)
   - External APIs (if needed)

3. **Generate input specifications** with validation rules

### Phase 2: Validate Context Completeness

Update `prompt-validator-001` to check:

```javascript
validation_checks:
  context_completeness:
    - input_specification_present: true
    - all_required_inputs_defined: true
    - context_sources_valid: true
    - validation_rules_present: true
    - source_accessibility_check: true
```

### Phase 3: Runtime Context Injection

Add new tool: `prepare_prompt_execution`

```json
{
  "tool_name": "prepare_prompt_execution",
  "input": {
    "prompt_name": "mtg-sum-001",
    "user_inputs": {
      "meeting_transcript": "...",
      "attendee_list": ["alice@co.com", "bob@co.com"]
    }
  },
  "output": {
    "executable_prompt": "Fully assembled prompt with all context",
    "context_retrieved": {
      "company_context": "... from Glean ...",
      "previous_meetings": "... from Glean ...",
      "action_items_template": "... from Glean ..."
    },
    "validation_status": "ready",
    "missing_required_inputs": []
  }
}
```

## Implementation Strategy

### 1. Enhanced Generator Agent

Update agent spec to include:

```yaml
output_contract:
  xml_prompt:
    type: string
    required: true
    must_include:
      - input_specification
      - context_requirements

  input_analysis:
    type: object
    properties:
      required_inputs: {type: array}
      optional_inputs: {type: array}
      context_sources: {type: array}
      validation_rules: {type: object}
```

### 2. Enhanced Validator Agent

Add validation rules:

```json
{
  "context_validation": {
    "rules": [
      {
        "rule_id": "inputs_defined",
        "check": "input_specification section exists",
        "severity": "error",
        "score_impact": -15
      },
      {
        "rule_id": "required_inputs_marked",
        "check": "At least one required input specified",
        "severity": "warning",
        "score_impact": -5
      },
      {
        "rule_id": "context_sources_valid",
        "check": "All context sources are accessible",
        "severity": "error",
        "score_impact": -20
      },
      {
        "rule_id": "validation_rules_present",
        "check": "Required inputs have validation rules",
        "severity": "warning",
        "score_impact": -5
      }
    ]
  }
}
```

### 3. New MCP Tool: Context Retrieval

```json
{
  "tool_name": "retrieve_prompt_context",
  "description": "Retrieve context from Glean for prompt execution",
  "input_schema": {
    "prompt_name": "string",
    "context_requirements": "array",
    "user_provided_inputs": "object"
  },
  "output_schema": {
    "context_data": "object",
    "retrieval_status": "object",
    "cache_info": "object"
  }
}
```

## Context Source Types

### Supported Sources

1. **user_provided**: Direct user input
   - Validated against schema
   - Required/optional marking
   - Type checking

2. **glean_search**: Glean knowledge search
   - Semantic search queries
   - Result filtering
   - Relevance scoring

3. **glean_document**: Specific Glean documents
   - Document URLs
   - Version tracking
   - Access control

4. **glean_meeting_lookup**: Meeting data
   - Transcript extraction
   - Participant filtering
   - Date range queries

5. **glean_code_search**: Code context
   - Repository search
   - File content
   - Function/class definitions

6. **external_api**: External data sources
   - API endpoint specs
   - Authentication
   - Rate limiting

## Workflow Example

### User Request
```bash
make xml-prompt TASK="Create a prompt for summarizing customer feedback"
```

### Generated Output (Enhanced)

```xml
<input_specification>
  <input>
    <name>customer_feedback</name>
    <type>string</type>
    <required>true</required>
    <source>user_provided</source>
    <description>Raw customer feedback text</description>
    <validation>
      <min_length>50</min_length>
    </validation>
  </input>

  <input>
    <name>product_name</name>
    <type>string</type>
    <required>true</required>
    <source>user_provided</source>
    <description>Name of the product being reviewed</description>
  </input>
</input_specification>

<context_requirements>
  <context>
    <name>product_info</name>
    <description>Product details and known issues</description>
    <source>glean_search</source>
    <query>product:{{product_name}} type:specification OR type:known_issues</query>
    <required>false</required>
  </context>

  <context>
    <name>sentiment_guidelines</name>
    <description>Company sentiment analysis guidelines</description>
    <source>glean_document</source>
    <document_url>glean://docs/analytics/sentiment-guidelines</document_url>
    <required>true</required>
  </context>
</context_requirements>
```

### Validation Report (Enhanced)

```json
{
  "isValid": true,
  "qualityScore": 92,
  "context_validation": {
    "inputs_defined": "pass",
    "required_inputs_count": 2,
    "context_sources_count": 2,
    "all_sources_accessible": true,
    "validation_rules_coverage": "100%"
  },
  "input_analysis": {
    "required_inputs": ["customer_feedback", "product_name"],
    "optional_inputs": [],
    "user_provided_count": 2,
    "glean_retrieved_count": 2
  }
}
```

## Benefits

1. **Clear Input Requirements**: Users know exactly what to provide
2. **Automated Context Retrieval**: Fetch company context from Glean automatically
3. **Validation**: Ensure all required context is available before execution
4. **Consistency**: Standardized input/context specification
5. **Reusability**: Prompts are self-documenting and portable
6. **Integration**: Seamless Glean MCP integration

## Next Steps

1. Update agent specs with input_specification and context_requirements
2. Enhance validation rules to check context completeness
3. Create `retrieve_prompt_context` MCP tool
4. Add context injection to runtime execution
5. Update documentation and examples
