# Agent Nodes and Workflow Orchestration

## Overview

This document shows how **Agent A** and **Agent B** are implemented as **generalized nodes with tools**, and demonstrates the **back-and-forth workflow** with actual XML prompts flowing between them.

---

## 1. Agent as Generalized Nodes

### 1.1 Node Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     AGENT NODE (Generalized)                    │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  Node Interface                                           │ │
│  │  - nodeId: string                                         │ │
│  │  - nodeType: "generator" | "validator"                    │ │
│  │  - tools: Tool[]                                          │ │
│  │  - execute(input): Promise<output>                        │ │
│  └───────────────────────────────────────────────────────────┘ │
│                              │                                  │
│                              ▼                                  │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  Tool Interface                                           │ │
│  │  - toolId: string                                         │ │
│  │  - toolName: string                                       │ │
│  │  - inputSchema: JSONSchema                                │ │
│  │  - outputSchema: JSONSchema                               │ │
│  │  - invoke(params): Promise<result>                        │ │
│  └───────────────────────────────────────────────────────────┘ │
│                              │                                  │
│                              ▼                                  │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  Execution Layer                                          │ │
│  │  - Input validation                                       │ │
│  │  - Business logic execution                               │ │
│  │  - Output generation                                      │ │
│  │  - Error handling                                         │ │
│  └───────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 Agent A as Node (Generator)

```typescript
// Agent A Node Specification
const agentANode: AgentNode = {
  nodeId: "prompt-generator-001",
  nodeType: "generator",
  displayName: "XML Prompt Generator",
  version: "1.0.0",

  tools: [
    {
      toolId: "gen-xml-pmt",
      toolName: "generate_xml_prompt",
      description: "Generate XML prompt from natural language",

      inputSchema: {
        type: "object",
        required: ["user_request"],
        properties: {
          user_request: {
            type: "string",
            description: "Natural language task description",
            minLength: 10
          },
          analyze_context: {
            type: "boolean",
            default: true,
            description: "Enable context analysis"
          },
          feedback: {
            type: "array",
            items: { type: "string" },
            description: "Feedback from previous validation"
          },
          previous_attempt: {
            type: "object",
            properties: {
              xml_prompt: { type: "string" },
              prompt_name: { type: "string" }
            }
          },
          attempt_number: {
            type: "integer",
            minimum: 1,
            maximum: 3,
            default: 1
          }
        }
      },

      outputSchema: {
        type: "object",
        required: ["xml_prompt", "prompt_name"],
        properties: {
          xml_prompt: {
            type: "string",
            description: "Complete XML-structured prompt"
          },
          prompt_name: {
            type: "string",
            pattern: "^[a-z0-9]{3}-[a-z0-9]{3}-[a-z0-9]{3}$"
          },
          input_analysis: {
            type: "object",
            properties: {
              required_inputs: { type: "array" },
              optional_inputs: { type: "array" },
              context_sources: { type: "array" },
              glean_integrations: { type: "array" }
            }
          },
          generation_metadata: {
            type: "object",
            properties: {
              attempt: { type: "integer" },
              refinements_applied: { type: "array" },
              timestamp: { type: "string" },
              context_analysis_performed: { type: "boolean" }
            }
          }
        }
      },

      invoke: async (params) => {
        // Implementation calls Glean MCP API
        return await gleanMCP.invokeAgent("prompt-generator-001", params);
      }
    }
  ],

  execute: async (input) => {
    const tool = agentANode.tools[0];
    return await tool.invoke(input);
  }
};
```

### 1.3 Agent B as Node (Validator)

```typescript
// Agent B Node Specification
const agentBNode: AgentNode = {
  nodeId: "prompt-validator-001",
  nodeType: "validator",
  displayName: "Prompt Quality Validator",
  version: "1.0.0",

  tools: [
    {
      toolId: "val-pmt-qlt",
      toolName: "validate_prompt_quality",
      description: "Validate XML prompt quality and structure",

      inputSchema: {
        type: "object",
        required: ["xml_prompt"],
        properties: {
          xml_prompt: {
            type: "string",
            description: "XML prompt to validate",
            minLength: 50
          },
          previous_validation_results: {
            type: "array",
            description: "Results from previous attempts"
          },
          attempt_number: {
            type: "integer",
            minimum: 1,
            maximum: 3,
            default: 1
          }
        }
      },

      outputSchema: {
        type: "object",
        required: ["isValid", "qualityScore", "checks", "feedback"],
        properties: {
          isValid: {
            type: "boolean",
            description: "Overall validation result"
          },
          qualityScore: {
            type: "number",
            minimum: 0,
            maximum: 100
          },
          checks: {
            type: "array",
            items: {
              type: "object",
              properties: {
                rule_id: { type: "string" },
                status: { enum: ["pass", "fail"] },
                message: { type: "string" },
                severity: { enum: ["error", "warning", "info"] },
                section: { type: "string" },
                score_impact: { type: "number" }
              }
            }
          },
          feedback: {
            type: "array",
            items: { type: "string" },
            description: "Actionable feedback for improvement"
          },
          scoreBreakdown: {
            type: "object",
            properties: {
              structural: { type: "number" },
              completeness: { type: "number" },
              quality: { type: "number" },
              context_quality: { type: "number" }
            }
          },
          contextValidation: {
            type: "object",
            properties: {
              input_specification_present: { type: "boolean" },
              required_inputs_count: { type: "integer" },
              context_sources_count: { type: "integer" },
              glean_integrations: { type: "array" }
            }
          }
        }
      },

      invoke: async (params) => {
        // Implementation calls Glean MCP API
        return await gleanMCP.invokeAgent("prompt-validator-001", params);
      }
    }
  ],

  execute: async (input) => {
    const tool = agentBNode.tools[0];
    return await tool.invoke(input);
  }
};
```

---

## 2. Workflow Orchestration Graph

### 2.1 Workflow as Directed Graph

```
┌─────────────────────────────────────────────────────────────────┐
│                    WORKFLOW GRAPH                               │
│                                                                 │
│  START                                                          │
│    │                                                            │
│    ├─→ [Node 0: Input Validation]                              │
│    │     │                                                      │
│    │     ▼                                                      │
│    ├─→ [Node 1: Context Discovery]                             │
│    │     │                                                      │
│    │     ▼                                                      │
│    ├─→ [ATTEMPT LOOP] ◄───────────────┐                        │
│    │     │                             │                        │
│    │     ├─→ [Node 2: Agent A]         │                        │
│    │     │     │                       │                        │
│    │     │     │ (Generates XML)       │                        │
│    │     │     │                       │                        │
│    │     │     ▼                       │                        │
│    │     ├─→ [Node 3: Agent B]         │                        │
│    │     │     │                       │                        │
│    │     │     │ (Validates XML)       │                        │
│    │     │     │                       │                        │
│    │     │     ▼                       │                        │
│    │     └─→ [Decision: Score >= 90?] │                        │
│    │               │                   │                        │
│    │          YES  │  NO               │                        │
│    │               │  │                │                        │
│    │               │  └─ [Feedback] ───┘                        │
│    │               │                                            │
│    │               ▼                                            │
│    └─→ [Node 4: Save Results]                                  │
│          │                                                      │
│          ▼                                                      │
│        END                                                      │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Node Execution Sequence

```typescript
interface WorkflowNode {
  nodeId: string;
  nodeType: "input" | "agent" | "decision" | "output";
  execute: (context: WorkflowContext) => Promise<WorkflowContext>;
  nextNodes: WorkflowNode[];
}

interface WorkflowContext {
  sessionId: string;
  userRequest: string;
  currentAttempt: number;
  maxAttempts: number;

  // State passed between nodes
  inputAnalysis?: InputAnalysis;
  currentPrompt?: PromptSpecification;
  validationResult?: ValidationResult;
  feedback?: string[];

  // Execution trace
  executionTrace: ExecutionHop[];
}

interface ExecutionHop {
  hopNumber: number;
  timestamp: Date;
  fromNode: string;
  toNode: string;
  payload: any;
  result: any;
}
```

---

## 3. Back-and-Forth Workflow Execution

### 3.1 Execution Trace with XML Prompts

**Scenario**: Meeting Summarization Prompt (2 attempts)

```
┌─────────────────────────────────────────────────────────────────┐
│  EXECUTION TRACE: Session abc-123-xyz                          │
│  Task: "Create a prompt for meeting summarization"             │
└─────────────────────────────────────────────────────────────────┘

╔═══════════════════════════════════════════════════════════════╗
║  HOP 1: Start → Context Discovery                             ║
╚═══════════════════════════════════════════════════════════════╝

Timestamp: 2026-01-26T14:30:01.000Z
From: START
To: ContextDiscoveryNode
Direction: →

Input Payload:
{
  "user_request": "Create a prompt for meeting summarization",
  "analyze_context": true
}

Output Result:
{
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
  "glean_integrations": ["mcp__glean__meeting_lookup"]
}

═══════════════════════════════════════════════════════════════

╔═══════════════════════════════════════════════════════════════╗
║  HOP 2: Context Discovery → Agent A (Attempt 1)               ║
╚═══════════════════════════════════════════════════════════════╝

Timestamp: 2026-01-26T14:30:03.000Z
From: ContextDiscoveryNode
To: AgentANode (prompt-generator-001)
Direction: →

Input Payload:
{
  "user_request": "Create a prompt for meeting summarization",
  "analyze_context": true,
  "input_analysis": {
    "required_inputs": [...], // from HOP 1
    "optional_inputs": [...],
    "context_sources": [...],
    "glean_integrations": [...]
  },
  "feedback": [],  // empty on first attempt
  "previous_attempt": null,
  "attempt_number": 1
}

Output Result (Agent A generates XML):
{
  "prompt_name": "m3t-4ng-s1m",
  "xml_prompt": `<metadata>
  <name>m3t-4ng-s1m</name>
  <version>1.0.0</version>
  <description>Create a prompt for meeting summarization</description>
</metadata>

<primary_goal>
Summarize meeting transcripts into actionable insights with key decisions,
action items, and discussion points.
</primary_goal>

<role>
You are an expert meeting summarizer specializing in extracting actionable
insights from meeting transcripts.
</role>

<task>
Process meeting transcripts to generate comprehensive summaries that highlight
key decisions, action items, and important discussion points.
</task>

<input_specification>
  <input>
    <name>meeting_transcript</name>
    <type>string</type>
    <required>true</required>
    <description>Full text transcript of the meeting</description>
    <source>user_provided</source>
    <validation>
      <min_length>100</min_length>
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
    </validation>
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

<instructions>
1. Validate all required inputs are provided
2. Retrieve context from previous meetings if available
3. Parse the transcript to identify key themes
4. Extract specific action items with owners
5. Identify important decisions made
6. Generate clear, actionable summary
</instructions>

<output_format>
Provide a structured summary with:
- Executive Summary (2-3 sentences)
- Key Decisions (bulleted list)
- Action Items (with owners and deadlines)
- Discussion Points (main topics covered)
</output_format>

<examples>
  <good>
    <input>
      Transcript: "John: We need to decide on Q4 budget..."
      Attendees: ["John Smith", "Jane Doe"]
    </input>
    <output>
      Executive Summary: Team discussed Q4 budget allocation...
      Key Decisions:
      - Approved $50K for marketing
      Action Items:
      - John: Submit final budget by Friday
    </output>
    <explanation>Clear structure with actionable items</explanation>
  </good>

  <bad>
    <input>Transcript: "Meeting about stuff"</input>
    <output>The meeting covered various topics.</output>
    <explanation>Too vague, no specific insights or actions</explanation>
  </bad>
</examples>`,

  "input_analysis": {
    "required_inputs": [...],
    "optional_inputs": [...],
    "context_sources": [...],
    "glean_integrations": [...]
  },

  "generation_metadata": {
    "attempt": 1,
    "refinements_applied": [],
    "timestamp": "2026-01-26T14:30:05.000Z",
    "context_analysis_performed": true
  }
}

═══════════════════════════════════════════════════════════════

╔═══════════════════════════════════════════════════════════════╗
║  HOP 3: Agent A → Agent B (Attempt 1 Validation)              ║
╚═══════════════════════════════════════════════════════════════╝

Timestamp: 2026-01-26T14:30:05.500Z
From: AgentANode
To: AgentBNode (prompt-validator-001)
Direction: →

Input Payload:
{
  "xml_prompt": "<metadata>...</metadata>...", // full XML from HOP 2
  "previous_validation_results": [],
  "attempt_number": 1
}

Output Result (Agent B validates):
{
  "isValid": false,  // ❌ REJECTED
  "qualityScore": 85,  // Below 90 threshold

  "checks": [
    {
      "rule_id": "xml_well_formed",
      "status": "pass",
      "message": "XML is well-formed",
      "severity": "info",
      "section": "structural",
      "score_impact": 0
    },
    {
      "rule_id": "input_specification_present",
      "status": "pass",
      "message": "Input specification defined",
      "severity": "info",
      "section": "completeness",
      "score_impact": 0
    },
    {
      "rule_id": "examples_quality",
      "status": "fail",  // ❌ Problem here
      "message": "Need at least 2 good examples",
      "severity": "error",
      "section": "completeness",
      "score_impact": -10
    },
    {
      "rule_id": "context_validation",
      "status": "fail",  // ❌ Problem here
      "message": "Missing validation rules for required inputs",
      "severity": "warning",
      "section": "context_quality",
      "score_impact": -5
    }
  ],

  "feedback": [
    "Add at least one more good example with different scenario",
    "Add validation rules (format, constraints) for all required inputs",
    "Improve specificity in instructions (mention transcript parsing techniques)"
  ],

  "scoreBreakdown": {
    "structural": 35,     // 35/35 ✓
    "completeness": 20,   // 20/30 (missing 1 good example)
    "quality": 25,        // 25/25 ✓
    "context_quality": 5  // 5/10 (missing validation details)
  },

  "contextValidation": {
    "input_specification_present": true,
    "context_requirements_present": true,
    "required_inputs_count": 2,
    "context_sources_count": 1,
    "glean_integrations": ["mcp__glean__meeting_lookup"],
    "validation_issues": [
      "Missing detailed validation rules for required inputs"
    ]
  }
}

═══════════════════════════════════════════════════════════════

╔═══════════════════════════════════════════════════════════════╗
║  HOP 4: Agent B → Agent A (Attempt 2 with Feedback)           ║
╚═══════════════════════════════════════════════════════════════╝

Timestamp: 2026-01-26T14:30:07.000Z
From: AgentBNode
To: AgentANode (prompt-generator-001)
Direction: ← (FEEDBACK LOOP BACK)

Input Payload:
{
  "user_request": "Create a prompt for meeting summarization",
  "analyze_context": true,
  "input_analysis": {...}, // preserved from first attempt

  "feedback": [  // ⚠️ FEEDBACK FROM AGENT B
    "Add at least one more good example with different scenario",
    "Add validation rules (format, constraints) for all required inputs",
    "Improve specificity in instructions"
  ],

  "previous_attempt": {  // ⚠️ PREVIOUS VERSION
    "xml_prompt": "<metadata>...</metadata>...",
    "prompt_name": "m3t-4ng-s1m"
  },

  "attempt_number": 2  // ⚠️ RETRY
}

Output Result (Agent A refines XML):
{
  "prompt_name": "m3t-4ng-s1m",  // Same name, new version
  "xml_prompt": `<metadata>
  <name>m3t-4ng-s1m</name>
  <version>1.0.0</version>
  <description>Create a prompt for meeting summarization</description>
</metadata>

<primary_goal>
Summarize meeting transcripts into actionable insights with key decisions,
action items, and discussion points.
</primary_goal>

<role>
You are an expert meeting summarizer specializing in extracting actionable
insights from meeting transcripts.
</role>

<task>
Process meeting transcripts to generate comprehensive summaries that highlight
key decisions, action items, and important discussion points.
</task>

<input_specification>
  <input>
    <name>meeting_transcript</name>
    <type>string</type>
    <required>true</required>
    <description>Full text transcript of the meeting</description>
    <source>user_provided</source>
    <validation>
      <min_length>100</min_length>
      <format>plain_text</format>                    ← ✅ ADDED
      <no_pii>true</no_pii>                          ← ✅ ADDED
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
      <max_items>50</max_items>                      ← ✅ ADDED
      <item_format>email_or_name</item_format>       ← ✅ ADDED
    </validation>
  </input>

  <input>
    <name>meeting_date</name>
    <type>string</type>
    <required>false</required>
    <source>user_provided</source>
    <default>today</default>
    <validation>                                      ← ✅ ADDED
      <format>ISO8601_date</format>
    </validation>
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

<instructions>
1. Validate all required inputs are provided and meet validation criteria
2. Retrieve context from previous meetings if available
3. Parse the transcript using NLP techniques to identify:     ← ✅ MORE SPECIFIC
   - Speaker turns and attributions
   - Key themes and topics
   - Decision points and conclusions
4. Extract specific action items with:
   - Clear owner assignment
   - Deadline or timeframe
   - Success criteria
5. Identify important decisions with rationale
6. Generate clear, actionable summary in specified format
</instructions>

<output_format>
Provide a structured summary with:
- Executive Summary (2-3 sentences)
- Key Decisions (bulleted list with rationale)
- Action Items (with owners and deadlines)
- Discussion Points (main topics covered)
- Next Steps (if applicable)
</output_format>

<examples>
  <good>
    <input>
      Transcript: "John: We need to decide on Q4 budget. Based on projections..."
      Attendees: ["John Smith", "Jane Doe"]
      Date: "2026-01-15"
    </input>
    <output>
      Executive Summary: Team discussed Q4 budget allocation...
      Key Decisions:
      - Approved $50K for marketing (based on ROI projections)
      Action Items:
      - John Smith: Submit final budget by Friday 1/20
      - Jane Doe: Review vendor contracts by 1/18
    </output>
    <explanation>Clear structure with actionable items and context</explanation>
  </good>

  <good>                                              ← ✅ ADDED SECOND GOOD EXAMPLE
    <input>
      Transcript: "Sarah: Let's review the product roadmap. Mike suggested..."
      Attendees: ["Sarah Lee", "Mike Chen", "Alex Brown"]
      Date: "2026-01-20"
    </input>
    <output>
      Executive Summary: Product team aligned on Q2 roadmap priorities...
      Key Decisions:
      - Feature X delayed to Q3 (engineering capacity constraints)
      - Feature Y prioritized for Q2 launch
      Action Items:
      - Mike Chen: Draft technical spec for Feature Y by 1/25
      - Alex Brown: Schedule user research sessions by 1/27
      Discussion Points:
      - Customer feedback on current features
      - Resource allocation challenges
    </output>
    <explanation>Demonstrates handling of multiple attendees and priorities</explanation>
  </good>

  <bad>
    <input>Transcript: "Meeting about stuff"</input>
    <output>The meeting covered various topics.</output>
    <explanation>Too vague, no specific insights, missing required inputs</explanation>
  </bad>
</examples>`,

  "generation_metadata": {
    "attempt": 2,
    "refinements_applied": [                          ← ✅ TRACKS CHANGES
      "Added detailed validation rules for all inputs",
      "Added second good example with different scenario",
      "Enhanced instructions with specific parsing techniques"
    ],
    "timestamp": "2026-01-26T14:30:09.000Z",
    "feedback_addressed": [
      "Add at least one more good example with different scenario",
      "Add validation rules (format, constraints) for all required inputs",
      "Improve specificity in instructions"
    ],
    "context_analysis_performed": true
  }
}

═══════════════════════════════════════════════════════════════

╔═══════════════════════════════════════════════════════════════╗
║  HOP 5: Agent A → Agent B (Attempt 2 Validation)              ║
╚═══════════════════════════════════════════════════════════════╝

Timestamp: 2026-01-26T14:30:09.500Z
From: AgentANode
To: AgentBNode (prompt-validator-001)
Direction: →

Input Payload:
{
  "xml_prompt": "<metadata>...</metadata>...", // refined XML from HOP 4
  "previous_validation_results": [
    {
      "attempt": 1,
      "score": 85,
      "isValid": false,
      "feedback": [...]
    }
  ],
  "attempt_number": 2
}

Output Result (Agent B validates again):
{
  "isValid": true,  // ✅ APPROVED
  "qualityScore": 95,  // Above 90 threshold

  "checks": [
    {
      "rule_id": "xml_well_formed",
      "status": "pass",
      "message": "XML is well-formed",
      "severity": "info",
      "section": "structural",
      "score_impact": 0
    },
    {
      "rule_id": "input_specification_present",
      "status": "pass",
      "message": "Input specification defined with validation rules",
      "severity": "info",
      "section": "completeness",
      "score_impact": 0
    },
    {
      "rule_id": "examples_quality",
      "status": "pass",  // ✅ Fixed
      "message": "2 good examples and 1 bad example present",
      "severity": "info",
      "section": "completeness",
      "score_impact": 0
    },
    {
      "rule_id": "context_validation",
      "status": "pass",  // ✅ Fixed
      "message": "All required inputs have validation rules",
      "severity": "info",
      "section": "context_quality",
      "score_impact": 0
    }
  ],

  "feedback": [],  // ✅ No feedback, all good!

  "recommendations": [
    "Consider adding a third good example for edge cases",
    "Could add validation for meeting duration if relevant"
  ],

  "scoreBreakdown": {
    "structural": 35,     // 35/35 ✓
    "completeness": 30,   // 30/30 ✓ (improved from 20)
    "quality": 25,        // 25/25 ✓
    "context_quality": 10 // 10/10 ✓ (improved from 5)
  },

  "contextValidation": {
    "input_specification_present": true,
    "context_requirements_present": true,
    "required_inputs_count": 2,
    "context_sources_count": 1,
    "glean_integrations": ["mcp__glean__meeting_lookup"],
    "validation_issues": []  // ✅ All issues resolved
  }
}

═══════════════════════════════════════════════════════════════

╔═══════════════════════════════════════════════════════════════╗
║  HOP 6: Agent B → Output (Save Results)                       ║
╚═══════════════════════════════════════════════════════════════╝

Timestamp: 2026-01-26T14:30:10.000Z
From: AgentBNode
To: OutputNode
Direction: →

Input Payload:
{
  "prompt_name": "m3t-4ng-s1m",
  "xml_prompt": "<metadata>...</metadata>...", // final approved XML
  "validation_result": {...}, // from HOP 5
  "session_summary": {
    "total_attempts": 2,
    "final_score": 95,
    "duration_ms": 9000,
    "status": "SUCCESS"
  }
}

Output Result:
{
  "saved_files": [
    "output/ab-prompt.xml",
    "output/ab-prompt-ab-report.json"
  ],
  "prompt_name": "m3t-4ng-s1m",
  "final_score": 95,
  "success": true
}

═══════════════════════════════════════════════════════════════
```

---

## 4. Workflow Execution Summary

### 4.1 Hop Summary Table

| Hop | From | To | Direction | Payload Type | Result | Status |
|-----|------|-----|-----------|-------------|--------|--------|
| 1 | START | ContextDiscovery | → | User Request | InputAnalysis | ✓ |
| 2 | ContextDiscovery | Agent A | → | Request + Analysis | XML Prompt (v1) | ✓ |
| 3 | Agent A | Agent B | → | XML Prompt | Validation (score: 85) | ❌ FAIL |
| 4 | Agent B | Agent A | ← | Feedback | XML Prompt (v2) | ✓ |
| 5 | Agent A | Agent B | → | XML Prompt (refined) | Validation (score: 95) | ✅ PASS |
| 6 | Agent B | Output | → | Final Prompt | Saved Files | ✓ |

### 4.2 XML Evolution Across Hops

```
Attempt 1 (HOP 2 → HOP 3):
┌────────────────────────────────────┐
│  <input_specification>             │
│    <input>                         │
│      <validation>                  │
│        <min_length>100</min_length>│  ← Basic validation only
│      </validation>                 │
│    </input>                        │
│  </input_specification>            │
│  <examples>                        │
│    <good>...</good>                │  ← Only 1 good example
│    <bad>...</bad>                  │
│  </examples>                       │
└────────────────────────────────────┘
         │
         │ Agent B Feedback
         ▼
Attempt 2 (HOP 4 → HOP 5):
┌────────────────────────────────────┐
│  <input_specification>             │
│    <input>                         │
│      <validation>                  │
│        <min_length>100</min_length>│
│        <format>plain_text</format> │  ← ✅ Added
│        <no_pii>true</no_pii>       │  ← ✅ Added
│      </validation>                 │
│    </input>                        │
│  </input_specification>            │
│  <examples>                        │
│    <good>...</good>                │  ← ✅ First good example
│    <good>...</good>                │  ← ✅ Added second good example
│    <bad>...</bad>                  │
│  </examples>                       │
└────────────────────────────────────┘
```

---

## 5. Node Communication Protocol

### 5.1 Message Envelope

```typescript
interface NodeMessage {
  messageId: string;
  timestamp: Date;

  // Routing
  fromNodeId: string;
  toNodeId: string;
  hopNumber: number;

  // Correlation
  sessionId: string;
  correlationId: string;
  causationId?: string;  // Previous message that caused this

  // Payload
  payloadType: string;
  payload: any;

  // Metadata
  attemptNumber?: number;
  isFeedback?: boolean;
  isRetry?: boolean;
}
```

### 5.2 Example Message (HOP 4: Feedback)

```json
{
  "messageId": "msg-789-def",
  "timestamp": "2026-01-26T14:30:07.000Z",

  "fromNodeId": "prompt-validator-001",
  "toNodeId": "prompt-generator-001",
  "hopNumber": 4,

  "sessionId": "session-abc-123",
  "correlationId": "corr-456-ghi",
  "causationId": "msg-456-abc",

  "payloadType": "PromptGenerationRequest",
  "payload": {
    "user_request": "Create a prompt for meeting summarization",
    "analyze_context": true,
    "feedback": [
      "Add at least one more good example",
      "Add validation rules for all inputs"
    ],
    "previous_attempt": {
      "xml_prompt": "...",
      "prompt_name": "m3t-4ng-s1m"
    },
    "attempt_number": 2
  },

  "attemptNumber": 2,
  "isFeedback": true,
  "isRetry": true
}
```

---

## 6. Workflow Visualization

### 6.1 Time-Series Hop Diagram

```
Time ────────────────────────────────────────────────────────────>

0s        1s        3s        5s        7s        9s       10s
│         │         │         │         │         │         │
START     │         │         │         │         │        END
│         │         │         │         │         │         │
│         │         │         │         │         │         │
│ HOP 1   │         │         │         │         │         │
├─────────>         │         │         │         │         │
│  Context│         │         │         │         │         │
│ Discovery         │         │         │         │         │
│         │         │         │         │         │         │
│         │ HOP 2   │         │         │         │         │
│         ├─────────>         │         │         │         │
│         │  Agent A│         │         │         │         │
│         │  (Gen v1)         │         │         │         │
│         │         │         │         │         │         │
│         │         │ HOP 3   │         │         │         │
│         │         ├─────────>         │         │         │
│         │         │  Agent B│         │         │         │
│         │         │  (Val: 85/100)    │         │         │
│         │         │         │ ❌ FAIL │         │         │
│         │         │         │         │         │         │
│         │         │         │ HOP 4   │         │         │
│         │         │         ├<────────┤         │         │
│         │         │         │ Feedback│         │         │
│         │         │         │  Loop   │         │         │
│         │         │         │ Agent A │         │         │
│         │         │         │ (Gen v2)│         │         │
│         │         │         │         │         │         │
│         │         │         │         │ HOP 5   │         │
│         │         │         │         ├─────────>         │
│         │         │         │         │  Agent B│         │
│         │         │         │         │  (Val: 95/100)    │
│         │         │         │         │         │ ✅ PASS │
│         │         │         │         │         │         │
│         │         │         │         │         │ HOP 6   │
│         │         │         │         │         ├─────────>
│         │         │         │         │         │  Save   │
│         │         │         │         │         │         │
└─────────┴─────────┴─────────┴─────────┴─────────┴─────────┘
```

---

## 7. Summary

### Generalized Node Architecture
- ✅ Agents are **nodes** with tool interfaces
- ✅ Each node has **input/output schemas**
- ✅ Nodes communicate via **structured messages**
- ✅ Workflow is a **directed graph** of nodes

### Back-and-Forth Workflow
- ✅ **6 hops** in successful 2-attempt scenario
- ✅ **Feedback loop** (HOP 3 → HOP 4) when validation fails
- ✅ **XML evolves** based on Agent B feedback
- ✅ **Tracked execution** with hop number, timestamps, payloads

### Key Insights
- Agent A and B are **stateless nodes**
- Workflow orchestrator maintains **session state**
- XML prompt is the **primary data flowing between nodes**
- Feedback creates **backward hop** from Agent B to Agent A
- Each hop is **logged** for audit trail

**The workflow demonstrates a classic feedback loop pattern where Agent B's validation results directly influence Agent A's next generation attempt, creating an iterative refinement process.**
