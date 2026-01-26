# Integrating Context Analysis with A/B Agent System

## Current State

### What Works ✅
- **Basic Workflow**: A/B agent system (simulated)
  - Agent A: `prompt-generator-001` generates XML
  - Agent B: `prompt-validator-001` validates and provides feedback
  - Iterative refinement loop (up to 3 attempts)

- **Enhanced Workflow**: Context analysis (direct implementation)
  - Analyzes task for required inputs
  - Identifies Glean context sources
  - Generates input/context specifications

### What's Missing ❌
- Context analysis is **NOT integrated** with the A/B agent system
- Enhanced workflow **bypasses the agents entirely**
- Agents don't know about input specifications or context requirements

## The Right Architecture

### Updated Agent A: `prompt-generator-001` with Context Awareness

```yaml
# agents/prompt-generator/agent-spec.yaml

input_contract:
  user_request:
    type: string
    required: true
    description: "Natural language prompt request"

  # NEW: Enable context analysis
  analyze_context:
    type: boolean
    required: false
    default: true
    description: "Analyze task to identify required inputs and context"

  feedback:
    type: array
    required: false
    items:
      type: string

output_contract:
  xml_prompt:
    type: string
    required: true

  prompt_name:
    type: string
    required: true

  # NEW: Input analysis output
  input_analysis:
    type: object
    required: false
    description: "Analysis of required inputs and context sources"
    properties:
      required_inputs:
        type: array
        items:
          type: object
          properties:
            name: {type: string}
            type: {type: string}
            source: {type: string}
            description: {type: string}

      optional_inputs:
        type: array

      context_sources:
        type: array
        items:
          type: object
          properties:
            name: {type: string}
            source: {type: string}
            query: {type: string}

      glean_integrations:
        type: array
        items: {type: string}

system_instructions: |
  You are an expert prompt engineer specializing in XML-structured prompts.

  PHASE 1: INPUT ANALYSIS (if analyze_context=true)
  1. Analyze the user_request to identify:
     - What inputs are needed from the user
     - What context can be retrieved from Glean
     - Which Glean MCP tools to use

  2. Pattern matching for common scenarios:
     - Meeting tasks → meeting_transcript, attendee_list, meeting_date
     - Code tasks → code_content, language, review_criteria
     - Customer feedback → feedback_text, product_name

  3. Map to context sources:
     - glean_search → semantic search
     - glean_meeting_lookup → calendar/meetings
     - glean_code_search → code repositories
     - glean_document → specific documents
     - user_provided → direct user input

  PHASE 2: XML GENERATION
  1. Generate <metadata>, <primary_goal>, <role>, <task>

  2. Generate <input_specification> section:
     - List all required and optional inputs
     - Include type, source, description
     - Add validation rules

  3. Generate <context_requirements> section:
     - List all context sources
     - Include Glean queries with variable substitution
     - Mark required/optional

  4. Generate <instructions>, <output_format>, <examples>

  If feedback is provided, apply it to refine the prompt.
```

### Updated Agent B: `prompt-validator-001` with Context Validation

```yaml
# agents/prompt-validator/agent-spec.yaml

validation_checks:
  structural:
    - xml_well_formed
    - required_sections_present
    - tag_hierarchy
    - naming_convention

  completeness:
    - section_content
    - examples_quality
    - instructions_structure
    # NEW: Context validation
    - input_specification_present
    - required_inputs_defined
    - context_sources_specified

  quality:
    - clarity_and_specificity
    - examples_effectiveness
    - constraints_and_validation
    - overall_coherence
    # NEW: Context quality
    - glean_queries_valid
    - input_descriptions_clear
    - validation_rules_present

scoring:
  success_threshold: 90

  weights:
    structural: 0.35      # Reduced from 0.4
    completeness: 0.30    # Same
    quality: 0.25         # Reduced from 0.3
    context_quality: 0.10 # NEW: Context-specific score

  # NEW: Context validation penalties
  context_penalties:
    missing_input_specification: -15
    no_required_inputs: -5
    invalid_glean_queries: -10
    missing_input_descriptions: -5

output_contract:
  isValid:
    type: boolean

  qualityScore:
    type: number

  # NEW: Context validation results
  context_validation:
    type: object
    properties:
      input_specification_present: {type: boolean}
      required_inputs_count: {type: integer}
      context_sources_count: {type: integer}
      glean_integrations: {type: array}
      validation_issues: {type: array}

  feedback:
    type: array
    # Will include context-specific feedback like:
    # - "Add input specification section"
    # - "Define required inputs for X"
    # - "Add Glean query for Y context"
```

## Integrated Workflow

### Architecture Diagram

```
User Request: "Create a prompt for meeting summarization"
        ↓
┌───────────────────────────────────────────────────────┐
│  Workflow Orchestrator (run-mcp-workflow-ab.js)      │
└───────────────────────────────────────────────────────┘
        ↓
        ├─→ Attempt 1
        │   ┌─────────────────────────────────────────┐
        │   │  Agent A: prompt-generator-001          │
        │   │  ┌────────────────────────────────────┐ │
        │   │  │ 1. Analyze Context                 │ │
        │   │  │    - Identify: meeting_transcript  │ │
        │   │  │    - Identify: attendee_list       │ │
        │   │  │    - Context: glean_meeting_lookup │ │
        │   │  └────────────────────────────────────┘ │
        │   │  ┌────────────────────────────────────┐ │
        │   │  │ 2. Generate XML with:              │ │
        │   │  │    - <input_specification>         │ │
        │   │  │    - <context_requirements>        │ │
        │   │  └────────────────────────────────────┘ │
        │   └─────────────────────────────────────────┘
        │           ↓
        │   ┌─────────────────────────────────────────┐
        │   │  Agent B: prompt-validator-001          │
        │   │  ┌────────────────────────────────────┐ │
        │   │  │ 1. Structural Validation (35%)     │ │
        │   │  │ 2. Completeness Validation (30%)   │ │
        │   │  │ 3. Quality Validation (25%)        │ │
        │   │  │ 4. Context Validation (10%)        │ │
        │   │  │    - Input spec present?           │ │
        │   │  │    - Required inputs defined?      │ │
        │   │  │    - Glean queries valid?          │ │
        │   │  └────────────────────────────────────┘ │
        │   │  Score: 88/100 → FAIL                   │
        │   │  Feedback:                              │
        │   │  - "Add validation rules for inputs"   │
        │   │  - "Improve context query specificity"  │
        │   └─────────────────────────────────────────┘
        │
        ├─→ Attempt 2 (with feedback)
        │   ┌─────────────────────────────────────────┐
        │   │  Agent A: prompt-generator-001          │
        │   │  - Apply feedback                       │
        │   │  - Add input validation rules           │
        │   │  - Refine context queries               │
        │   └─────────────────────────────────────────┘
        │           ↓
        │   ┌─────────────────────────────────────────┐
        │   │  Agent B: prompt-validator-001          │
        │   │  Score: 94/100 → PASS ✓                 │
        │   └─────────────────────────────────────────┘
        │
        └─→ Success!
            - XML prompt with input/context specs
            - Input analysis report
            - Validation history
```

## Implementation

### Updated Workflow Script

```javascript
// scripts/run-mcp-workflow-ab.js

async function runABWorkflowWithContext(task, outputPath, maxAttempts) {
  log('🚀 Starting A/B Agent Workflow with Context Analysis', 'green');

  let currentAttempt = 1;
  let feedback = [];
  let previousAttempt = null;
  let validationHistory = [];

  while (currentAttempt <= maxAttempts) {
    log(`\n📝 Agent A: Generating XML (attempt ${currentAttempt})...`, 'blue');

    // AGENT A: Generate with context analysis
    const genResult = await callAgentA({
      user_request: task,
      analyze_context: true,  // Enable context analysis
      feedback: feedback,
      previous_attempt: previousAttempt,
      attempt_number: currentAttempt
    });

    const { xml_prompt, prompt_name, input_analysis } = genResult;

    log(`✓ Generated: ${prompt_name}`, 'green');
    if (input_analysis) {
      log(`  Required inputs: ${input_analysis.required_inputs.length}`, 'cyan');
      log(`  Context sources: ${input_analysis.context_sources.length}`, 'cyan');
      log(`  Glean tools: ${input_analysis.glean_integrations.join(', ')}`, 'magenta');
    }

    // AGENT B: Validate with context checks
    log(`\n✓ Agent B: Validating quality (attempt ${currentAttempt})...`, 'blue');

    const valResult = await callAgentB({
      xml_prompt: xml_prompt,
      previous_validation_results: validationHistory,
      attempt_number: currentAttempt
    });

    validationHistory.push(valResult);

    log(`\n📊 Validation Results:`, 'cyan');
    log(`   Overall Score: ${valResult.qualityScore}/100`,
        valResult.isValid ? 'green' : 'yellow');
    log(`   Structural:   ${valResult.scoreBreakdown.structural}/35`, 'cyan');
    log(`   Completeness: ${valResult.scoreBreakdown.completeness}/30`, 'cyan');
    log(`   Quality:      ${valResult.scoreBreakdown.quality}/25`, 'cyan');
    log(`   Context:      ${valResult.scoreBreakdown.context_quality}/10`, 'magenta');

    if (valResult.context_validation) {
      log(`\n   Context Validation:`, 'magenta');
      log(`     Input spec: ${valResult.context_validation.input_specification_present ? '✓' : '✗'}`, 'cyan');
      log(`     Required inputs: ${valResult.context_validation.required_inputs_count}`, 'cyan');
      log(`     Context sources: ${valResult.context_validation.context_sources_count}`, 'cyan');
    }

    if (valResult.isValid) {
      log(`\n✅ SUCCESS! Both agents approved.`, 'green');

      // Save results
      saveResults(outputPath, {
        xml_prompt,
        prompt_name,
        input_analysis,
        validation_history: validationHistory
      });

      return;
    }

    if (currentAttempt < maxAttempts) {
      log(`\n⚠️  Agent B rejected. Sending feedback to Agent A...`, 'yellow');
      feedback = valResult.feedback;
      previousAttempt = { xml_prompt, prompt_name };
      currentAttempt++;
    } else {
      log(`\n❌ Max attempts reached. Best score: ${valResult.qualityScore}/100`, 'red');
      break;
    }
  }
}

async function callAgentA(input) {
  // TODO: Replace with actual Glean Agent API call
  // POST to Glean MCP server: /tools/generate_xml_prompt
  return await fetch(GLEAN_MCP_ENDPOINT, {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${GLEAN_API_KEY}` },
    body: JSON.stringify({
      tool: 'generate_xml_prompt',
      input: input
    })
  }).then(r => r.json());
}

async function callAgentB(input) {
  // TODO: Replace with actual Glean Agent API call
  // POST to Glean MCP server: /tools/validate_prompt_quality
  return await fetch(GLEAN_MCP_ENDPOINT, {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${GLEAN_API_KEY}` },
    body: JSON.stringify({
      tool: 'validate_prompt_quality',
      input: input
    })
  }).then(r => r.json());
}
```

## Benefits of Integration

### Keeping A/B Agent System ✅

1. **Iterative Refinement**: Agent B can request improvements to context specs
2. **Quality Assurance**: Two independent perspectives (generation vs validation)
3. **Specialization**: Each agent focuses on its domain
4. **Scalability**: Can add more agents (e.g., security validator, performance optimizer)

### Adding Context Awareness ✅

5. **Input Identification**: Automatic discovery of required inputs
6. **Glean Integration**: Specs for context retrieval
7. **Validation**: Ensures context requirements are complete
8. **Documentation**: Self-documenting prompts with input/context specs

## Next Steps

1. **Update Agent Specs** (`agent-spec.yaml` files)
   - Add input_analysis to outputs
   - Add context validation rules
   - Update scoring weights

2. **Update Agent Instructions**
   - Add context analysis steps to generator
   - Add context validation checks to validator

3. **Update MCP Server Config**
   - Register updated tool schemas
   - Add context-related parameters

4. **Implement Glean API Integration**
   - Replace simulated calls with real API calls
   - Add authentication
   - Handle errors and retries

5. **Test End-to-End**
   - Deploy agents to Glean
   - Test with real tasks
   - Validate context retrieval works

## Comparison

| Feature | Basic (A/B Agents) | Enhanced (Direct) | Integrated (A/B + Context) |
|---------|-------------------|-------------------|---------------------------|
| Uses Agent A/B | ✅ | ❌ | ✅ |
| Iterative Refinement | ✅ | ❌ | ✅ |
| Context Analysis | ❌ | ✅ | ✅ |
| Input Identification | ❌ | ✅ | ✅ |
| Glean Integration | ❌ | ✅ | ✅ |
| Production-Ready | ⚠️ (needs API) | ❌ (bypasses agents) | ✅ |

## Summary

The enhanced workflow I created is a **prototype to demonstrate context analysis**, but it should be **integrated into the A/B agent system** for production use. This gives you:

- The power of two-agent validation
- The intelligence of context analysis
- The scalability of Glean's agent platform
- The quality of iterative refinement
