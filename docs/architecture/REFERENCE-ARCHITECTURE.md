# Reference Architecture: Integrated A/B Prompt Engineering System

## Executive Summary

A **Domain-Driven Design (DDD)** architecture for an event-driven, two-agent prompt engineering system with context analysis and Glean integration.

### Core Bounded Contexts
1. **PromptEngineering** - Core domain for XML prompt generation and validation
2. **ContextDiscovery** - Identifying inputs and context sources
3. **GleanIntegration** - Integration with Glean MCP services
4. **WorkflowOrchestration** - Agent coordination and feedback loops

---

## 1. System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          PRESENTATION LAYER                             │
│                                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                │
│  │  CLI Client  │  │ REST API     │  │  Web UI      │                │
│  │  (Make)      │  │  (Future)    │  │  (Future)    │                │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘                │
│         │                  │                  │                         │
│         └──────────────────┴──────────────────┘                         │
└─────────────────────────────┬───────────────────────────────────────────┘
                              │
                              │ Command: GeneratePrompt
                              │
┌─────────────────────────────▼───────────────────────────────────────────┐
│                      APPLICATION LAYER                                  │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │         Workflow Orchestrator (Application Service)              │  │
│  │  - Coordinates Agent A & Agent B                                 │  │
│  │  - Manages attempt loops                                         │  │
│  │  - Handles feedback cycles                                       │  │
│  │  - Publishes domain events                                       │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │         Event Bus (In-Process / Future: Message Queue)           │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────┬───────────────────────────────────────────┘
                              │
                              │ Domain Events
                              │
┌─────────────────────────────▼───────────────────────────────────────────┐
│                         DOMAIN LAYER                                    │
│                                                                         │
│  ┌──────────────────────┐  ┌──────────────────────┐                   │
│  │  BOUNDED CONTEXT:    │  │  BOUNDED CONTEXT:    │                   │
│  │  PromptEngineering   │  │  ContextDiscovery    │                   │
│  │                      │  │                      │                   │
│  │  Aggregates:         │  │  Aggregates:         │                   │
│  │  - PromptSpecification│ │  - InputAnalysis     │                   │
│  │  - ValidationResult  │  │  - ContextSource     │                   │
│  │                      │  │                      │                   │
│  │  Domain Services:    │  │  Domain Services:    │                   │
│  │  - PromptGenerator   │  │  - TaskAnalyzer      │                   │
│  │  - PromptValidator   │  │  - ContextMapper     │                   │
│  └──────────────────────┘  └──────────────────────┘                   │
│                                                                         │
│  ┌──────────────────────┐  ┌──────────────────────┐                   │
│  │  BOUNDED CONTEXT:    │  │  BOUNDED CONTEXT:    │                   │
│  │  GleanIntegration    │  │  WorkflowOrchestration│                  │
│  │                      │  │                      │                   │
│  │  Aggregates:         │  │  Aggregates:         │                   │
│  │  - GleanQuery        │  │  - WorkflowSession   │                   │
│  │  - ContextRetrieval  │  │  - AttemptHistory    │                   │
│  │                      │  │                      │                   │
│  │  Domain Services:    │  │  Domain Services:    │                   │
│  │  - GleanConnector    │  │  - FeedbackLoop      │                   │
│  │  - ToolMapper        │  │  - QualityGate       │                   │
│  └──────────────────────┘  └──────────────────────┘                   │
└─────────────────────────────┬───────────────────────────────────────────┘
                              │
                              │ Repository Pattern
                              │
┌─────────────────────────────▼───────────────────────────────────────────┐
│                    INFRASTRUCTURE LAYER                                 │
│                                                                         │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐    │
│  │  Agent A         │  │  Agent B         │  │  Glean MCP       │    │
│  │  (External)      │  │  (External)      │  │  (External)      │    │
│  │                  │  │                  │  │                  │    │
│  │  - Generation    │  │  - Validation    │  │  - Search        │    │
│  │  - Context       │  │  - Scoring       │  │  - Meetings      │    │
│  │    Analysis      │  │  - Feedback      │  │  - Code          │    │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘    │
│                                                                         │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐    │
│  │  File System     │  │  Event Store     │  │  Logging         │    │
│  │  (Persistence)   │  │  (Future)        │  │  (Observability) │    │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Bounded Contexts (DDD)

### 2.1 PromptEngineering Context

**Responsibility**: Core domain logic for prompt generation and validation

**Aggregates**:
- `PromptSpecification` (Root)
  - `PromptName` (Value Object)
  - `XmlContent` (Value Object)
  - `Metadata` (Value Object)
  - `InputSpecification` (Entity)
  - `ContextRequirements` (Entity)

- `ValidationResult` (Root)
  - `QualityScore` (Value Object)
  - `ValidationCheck` (Entity collection)
  - `Feedback` (Value Object collection)
  - `ScoreBreakdown` (Value Object)

**Domain Events**:
```
- PromptGenerationRequested
- PromptGenerated
- PromptValidationRequested
- PromptValidated
- PromptRejected
- PromptApproved
- FeedbackGenerated
```

**Ubiquitous Language**:
- Prompt Specification
- XML Prompt
- Quality Score
- Validation Check
- Feedback Loop
- Attempt

---

### 2.2 ContextDiscovery Context

**Responsibility**: Analyzing tasks to identify required inputs and context sources

**Aggregates**:
- `InputAnalysis` (Root)
  - `RequiredInput` (Entity collection)
  - `OptionalInput` (Entity collection)
  - `ContextSource` (Entity collection)
  - `GleanIntegration` (Value Object collection)

- `TaskPattern` (Root)
  - `PatternMatcher` (Value Object)
  - `InputMapping` (Value Object)

**Domain Events**:
```
- TaskAnalysisRequested
- TaskAnalyzed
- InputsIdentified
- ContextSourcesDiscovered
- GleanToolsMapped
```

**Ubiquitous Language**:
- Input Analysis
- Required Input
- Optional Input
- Context Source
- User-Provided
- Glean-Retrieved
- Task Pattern

---

### 2.3 GleanIntegration Context

**Responsibility**: Integration with Glean MCP services and tools

**Aggregates**:
- `GleanQuery` (Root)
  - `QueryText` (Value Object)
  - `SourceType` (Enumeration)
  - `ResultSet` (Entity collection)

- `ContextRetrieval` (Root)
  - `RetrievalRequest` (Value Object)
  - `RetrievedContext` (Entity collection)
  - `CacheInfo` (Value Object)

**Domain Events**:
```
- GleanQueryIssued
- ContextRetrieved
- GleanToolInvoked
- ContextCached
- RetrievalFailed
```

**Ubiquitous Language**:
- Glean Query
- Context Retrieval
- MCP Tool
- Source Type (search, meeting_lookup, code_search, document)

---

### 2.4 WorkflowOrchestration Context

**Responsibility**: Coordinating agent interactions and feedback loops

**Aggregates**:
- `WorkflowSession` (Root)
  - `SessionId` (Value Object)
  - `CurrentAttempt` (Value Object)
  - `AttemptHistory` (Entity collection)
  - `Status` (Enumeration)

- `FeedbackCycle` (Root)
  - `SourceAgent` (Value Object)
  - `TargetAgent` (Value Object)
  - `FeedbackItems` (Value Object collection)

**Domain Events**:
```
- WorkflowSessionStarted
- AttemptInitiated
- AgentInvoked
- FeedbackCycleStarted
- FeedbackApplied
- WorkflowSessionCompleted
- WorkflowSessionFailed
- MaxAttemptsReached
```

**Ubiquitous Language**:
- Workflow Session
- Attempt
- Feedback Cycle
- Agent Invocation
- Quality Gate

---

## 3. Domain Events Architecture

### Event Flow Diagram

```
┌──────────────┐
│  User        │
│  Request     │
└──────┬───────┘
       │
       │ Command: GeneratePrompt
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│  Application Service: WorkflowOrchestrator                   │
└──────┬───────────────────────────────────────────────────────┘
       │
       │ Event: WorkflowSessionStarted
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│  EVENT STREAM (Attempt 1)                                    │
│                                                              │
│  1. AttemptInitiated                                        │
│     ├─ attemptNumber: 1                                     │
│     ├─ sessionId: "abc-123"                                 │
│     └─ timestamp: "2026-01-26T..."                          │
│                                                              │
│  2. TaskAnalysisRequested ──────────────────────┐           │
│     ├─ userRequest: "Create prompt for..."      │           │
│     └─ analyzeContext: true                     │           │
│                                                  ▼           │
│                                         ┌────────────────┐  │
│                                         │ ContextDiscovery│ │
│                                         │    Context     │  │
│                                         └────────┬───────┘  │
│                                                  │           │
│  3. TaskAnalyzed ◄───────────────────────────────┘          │
│     ├─ requiredInputs: [...]                                │
│     ├─ optionalInputs: [...]                                │
│     ├─ contextSources: [...]                                │
│     └─ gleanIntegrations: [...]                             │
│                                                              │
│  4. PromptGenerationRequested ──────────────────┐           │
│     ├─ userRequest: "..."                       │           │
│     ├─ inputAnalysis: {...}                     │           │
│     └─ attemptNumber: 1                         │           │
│                                                  ▼           │
│                                         ┌────────────────┐  │
│                                         │PromptEngineering│ │
│                                         │    Context     │  │
│                                         │   (Agent A)    │  │
│                                         └────────┬───────┘  │
│                                                  │           │
│  5. PromptGenerated ◄────────────────────────────┘          │
│     ├─ promptName: "abc-def-123"                            │
│     ├─ xmlContent: "<metadata>...</metadata>..."            │
│     ├─ inputAnalysis: {...}                                 │
│     └─ metadata: {...}                                      │
│                                                              │
│  6. PromptValidationRequested ──────────────────┐           │
│     ├─ xmlPrompt: "..."                         │           │
│     ├─ attemptNumber: 1                         │           │
│     └─ previousResults: []                      │           │
│                                                  ▼           │
│                                         ┌────────────────┐  │
│                                         │PromptEngineering│ │
│                                         │    Context     │  │
│                                         │   (Agent B)    │  │
│                                         └────────┬───────┘  │
│                                                  │           │
│  7. PromptValidated ◄────────────────────────────┘          │
│     ├─ isValid: false                                       │
│     ├─ qualityScore: 85                                     │
│     ├─ checks: [...]                                        │
│     ├─ feedback: ["Add input spec", ...]                    │
│     └─ contextValidation: {...}                             │
│                                                              │
│  8. PromptRejected                                          │
│     ├─ reason: "Quality score below threshold"              │
│     ├─ score: 85                                            │
│     └─ threshold: 90                                        │
│                                                              │
│  9. FeedbackGenerated                                       │
│     ├─ sourceAgent: "prompt-validator-001"                  │
│     ├─ targetAgent: "prompt-generator-001"                  │
│     ├─ feedbackItems: ["Add input spec", ...]               │
│     └─ attemptNumber: 1                                     │
│                                                              │
│  10. FeedbackCycleStarted                                   │
│      ├─ feedback: [...]                                     │
│      └─ nextAttemptNumber: 2                                │
└──────────────────────────────────────────────────────────────┘
       │
       │ (Loop continues for Attempt 2)
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│  EVENT STREAM (Attempt 2)                                    │
│                                                              │
│  11. AttemptInitiated (attempt: 2)                          │
│  12. PromptGenerationRequested (with feedback)              │
│  13. FeedbackApplied                                        │
│      ├─ feedbackItems: [...]                                │
│      └─ refinementsApplied: [...]                           │
│  14. PromptGenerated (revised)                              │
│  15. PromptValidationRequested                              │
│  16. PromptValidated                                        │
│      ├─ isValid: true                                       │
│      ├─ qualityScore: 95                                    │
│      └─ contextValidation: {...}                            │
│  17. PromptApproved ✓                                       │
│      ├─ finalScore: 95                                      │
│      └─ totalAttempts: 2                                    │
│  18. WorkflowSessionCompleted ✓                             │
│      ├─ status: "SUCCESS"                                   │
│      ├─ promptName: "abc-def-123"                           │
│      └─ duration: "2.3s"                                    │
└──────────────────────────────────────────────────────────────┘
```

---

## 4. Data Flow Architecture

### 4.1 Complete Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          INPUT LAYER                                    │
│                                                                         │
│  User Request: "Create a prompt for meeting summarization"             │
│                                                                         │
│  {                                                                      │
│    command: "GeneratePrompt",                                           │
│    task: "Create a prompt for meeting summarization",                  │
│    options: {                                                           │
│      analyzeContext: true,                                              │
│      maxAttempts: 3                                                     │
│    }                                                                    │
│  }                                                                      │
└─────────────────────────────┬───────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    WORKFLOW ORCHESTRATOR                                │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────┐      │
│  │  1. Create WorkflowSession                                  │      │
│  │     session = new WorkflowSession(                          │      │
│  │       sessionId: UUID.generate(),                           │      │
│  │       task: userRequest,                                    │      │
│  │       maxAttempts: 3                                        │      │
│  │     )                                                       │      │
│  │     publish(WorkflowSessionStarted)                         │      │
│  └─────────────────────────────────────────────────────────────┘      │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────┐      │
│  │  2. Start Attempt Loop                                      │      │
│  │     for attempt in 1..maxAttempts:                          │      │
│  │       publish(AttemptInitiated)                             │      │
│  └─────────────────────────────────────────────────────────────┘      │
└─────────────────────────────┬───────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    CONTEXT DISCOVERY PHASE                              │
│                                                                         │
│  Input Data:                                                            │
│  ┌──────────────────────────────────────────────────────────┐          │
│  │ {                                                        │          │
│  │   userRequest: "Create a prompt for meeting summarization",│        │
│  │   analyzeContext: true                                   │          │
│  │ }                                                        │          │
│  └──────────────────────────────────────────────────────────┘          │
│                              │                                          │
│                              ▼                                          │
│  ┌──────────────────────────────────────────────────────────┐          │
│  │  TaskAnalyzer.analyze(userRequest)                       │          │
│  │  ├─ Pattern Matching: "meeting" detected                │          │
│  │  ├─ Input Mapping: meeting → [transcript, attendees]    │          │
│  │  └─ Context Mapping: meeting → [previous_meetings]      │          │
│  └──────────────────────────────────────────────────────────┘          │
│                              │                                          │
│                              ▼                                          │
│  Output Data (InputAnalysis aggregate):                                │
│  ┌──────────────────────────────────────────────────────────┐          │
│  │ {                                                        │          │
│  │   requiredInputs: [                                     │          │
│  │     {                                                   │          │
│  │       name: "meeting_transcript",                       │          │
│  │       type: "string",                                   │          │
│  │       source: "user_provided",                          │          │
│  │       description: "Full text transcript..."            │          │
│  │     },                                                  │          │
│  │     {                                                   │          │
│  │       name: "attendee_list",                            │          │
│  │       type: "array",                                    │          │
│  │       source: "user_provided",                          │          │
│  │       description: "List of attendees..."               │          │
│  │     }                                                   │          │
│  │   ],                                                    │          │
│  │   optionalInputs: [                                     │          │
│  │     {                                                   │          │
│  │       name: "meeting_date",                             │          │
│  │       type: "string",                                   │          │
│  │       source: "user_provided",                          │          │
│  │       default: "today"                                  │          │
│  │     }                                                   │          │
│  │   ],                                                    │          │
│  │   contextSources: [                                     │          │
│  │     {                                                   │          │
│  │       name: "previous_meetings",                        │          │
│  │       source: "glean_meeting_lookup",                   │          │
│  │       query: "participants:{{attendee_list}} after:..."  │         │
│  │     }                                                   │          │
│  │   ],                                                    │          │
│  │   gleanIntegrations: ["mcp__glean__meeting_lookup"]     │          │
│  │ }                                                        │          │
│  └──────────────────────────────────────────────────────────┘          │
│                              │                                          │
│                              │ publish(TaskAnalyzed)                    │
└──────────────────────────────┼──────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    AGENT A: PROMPT GENERATION                           │
│                                                                         │
│  Input Data:                                                            │
│  ┌──────────────────────────────────────────────────────────┐          │
│  │ {                                                        │          │
│  │   user_request: "Create a prompt for meeting summarization",│      │
│  │   analyze_context: true,                                 │          │
│  │   input_analysis: {/* from context discovery */},        │          │
│  │   feedback: [],  // empty on first attempt              │          │
│  │   previous_attempt: null,                                │          │
│  │   attempt_number: 1                                      │          │
│  │ }                                                        │          │
│  └──────────────────────────────────────────────────────────┘          │
│                              │                                          │
│                              ▼                                          │
│  ┌──────────────────────────────────────────────────────────┐          │
│  │  PromptGenerator.generate()                              │          │
│  │  │                                                       │          │
│  │  ├─ Phase 1: Apply InputAnalysis                        │          │
│  │  │   └─ Generate <input_specification>                  │          │
│  │  │   └─ Generate <context_requirements>                 │          │
│  │  │                                                       │          │
│  │  ├─ Phase 2: Generate Core XML                          │          │
│  │  │   └─ <metadata>, <primary_goal>, <role>, <task>      │          │
│  │  │   └─ <instructions>, <output_format>                 │          │
│  │  │   └─ <examples> (2 good, 1 bad)                      │          │
│  │  │                                                       │          │
│  │  └─ Create PromptSpecification aggregate                │          │
│  └──────────────────────────────────────────────────────────┘          │
│                              │                                          │
│                              ▼                                          │
│  Output Data (PromptSpecification aggregate):                          │
│  ┌──────────────────────────────────────────────────────────┐          │
│  │ {                                                        │          │
│  │   prompt_name: "abc-def-123",                            │          │
│  │   xml_prompt: `                                          │          │
│  │     <metadata>                                           │          │
│  │       <name>abc-def-123</name>                           │          │
│  │       <version>1.0.0</version>                           │          │
│  │     </metadata>                                          │          │
│  │     <primary_goal>...</primary_goal>                     │          │
│  │     <role>...</role>                                     │          │
│  │     <task>...</task>                                     │          │
│  │     <input_specification>                                │          │
│  │       <input>                                            │          │
│  │         <name>meeting_transcript</name>                  │          │
│  │         <type>string</type>                              │          │
│  │         <required>true</required>                        │          │
│  │         ...                                              │          │
│  │       </input>                                           │          │
│  │       ...                                                │          │
│  │     </input_specification>                               │          │
│  │     <context_requirements>                               │          │
│  │       <context>                                          │          │
│  │         <name>previous_meetings</name>                   │          │
│  │         <source>glean_meeting_lookup</source>            │          │
│  │         <query>participants:{{attendee_list}}...</query> │          │
│  │       </context>                                         │          │
│  │     </context_requirements>                              │          │
│  │     <instructions>...</instructions>                     │          │
│  │     <output_format>...</output_format>                   │          │
│  │     <examples>                                           │          │
│  │       <good>...</good>                                   │          │
│  │       <good>...</good>                                   │          │
│  │       <bad>...</bad>                                     │          │
│  │     </examples>                                          │          │
│  │   `,                                                     │          │
│  │   input_analysis: {/* preserved */},                     │          │
│  │   generation_metadata: {                                 │          │
│  │     attempt: 1,                                          │          │
│  │     timestamp: "2026-01-26T...",                         │          │
│  │     context_analysis_performed: true                     │          │
│  │   }                                                      │          │
│  │ }                                                        │          │
│  └──────────────────────────────────────────────────────────┘          │
│                              │                                          │
│                              │ publish(PromptGenerated)                 │
└──────────────────────────────┼──────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    AGENT B: PROMPT VALIDATION                           │
│                                                                         │
│  Input Data:                                                            │
│  ┌──────────────────────────────────────────────────────────┐          │
│  │ {                                                        │          │
│  │   xml_prompt: "<metadata>...</metadata>...",             │          │
│  │   previous_validation_results: [],                       │          │
│  │   attempt_number: 1                                      │          │
│  │ }                                                        │          │
│  └──────────────────────────────────────────────────────────┘          │
│                              │                                          │
│                              ▼                                          │
│  ┌──────────────────────────────────────────────────────────┐          │
│  │  PromptValidator.validate()                              │          │
│  │  │                                                       │          │
│  │  ├─ Parse XML                                            │          │
│  │  │                                                       │          │
│  │  ├─ Structural Validation (35%)                          │          │
│  │  │   ├─ xml_well_formed: pass (0 points)                │          │
│  │  │   ├─ required_sections: pass (0 points)              │          │
│  │  │   ├─ tag_hierarchy: pass (0 points)                  │          │
│  │  │   └─ Score: 35/35                                    │          │
│  │  │                                                       │          │
│  │  ├─ Completeness Validation (30%)                        │          │
│  │  │   ├─ section_content: pass (0 points)                │          │
│  │  │   ├─ examples_quality: pass (0 points)               │          │
│  │  │   ├─ input_specification_present: pass (0 points)    │          │
│  │  │   └─ Score: 30/30                                    │          │
│  │  │                                                       │          │
│  │  ├─ Quality Validation (25%)                             │          │
│  │  │   ├─ clarity: pass (0 points)                        │          │
│  │  │   ├─ examples_effectiveness: pass (0 points)         │          │
│  │  │   └─ Score: 25/25                                    │          │
│  │  │                                                       │          │
│  │  ├─ Context Validation (10%) [NEW]                       │          │
│  │  │   ├─ required_inputs_defined: pass (0 points)        │          │
│  │  │   ├─ input_descriptions_clear: pass (0 points)       │          │
│  │  │   ├─ glean_queries_valid: pass (0 points)            │          │
│  │  │   └─ Score: 10/10                                    │          │
│  │  │                                                       │          │
│  │  └─ Create ValidationResult aggregate                    │          │
│  └──────────────────────────────────────────────────────────┘          │
│                              │                                          │
│                              ▼                                          │
│  Output Data (ValidationResult aggregate):                             │
│  ┌──────────────────────────────────────────────────────────┐          │
│  │ {                                                        │          │
│  │   isValid: true,                                         │          │
│  │   qualityScore: 100,  // 35+30+25+10                    │          │
│  │   checks: [                                              │          │
│  │     {                                                   │          │
│  │       rule_id: "xml_well_formed",                       │          │
│  │       status: "pass",                                   │          │
│  │       message: "XML is well-formed",                    │          │
│  │       severity: "info",                                 │          │
│  │       section: "structural",                            │          │
│  │       score_impact: 0                                   │          │
│  │     },                                                  │          │
│  │     {                                                   │          │
│  │       rule_id: "input_specification_present",           │          │
│  │       status: "pass",                                   │          │
│  │       message: "Input specification defined",           │          │
│  │       severity: "info",                                 │          │
│  │       section: "completeness",                          │          │
│  │       score_impact: 0                                   │          │
│  │     },                                                  │          │
│  │     {                                                   │          │
│  │       rule_id: "required_inputs_defined",               │          │
│  │       status: "pass",                                   │          │
│  │       message: "2 required inputs defined",             │          │
│  │       severity: "info",                                 │          │
│  │       section: "context_quality",                       │          │
│  │       score_impact: 0                                   │          │
│  │     }                                                   │          │
│  │     // ... more checks                                 │          │
│  │   ],                                                    │          │
│  │   feedback: [],  // empty because isValid=true         │          │
│  │   scoreBreakdown: {                                     │          │
│  │     structural: 35,                                     │          │
│  │     completeness: 30,                                   │          │
│  │     quality: 25,                                        │          │
│  │     context_quality: 10                                 │          │
│  │   },                                                    │          │
│  │   contextValidation: {                                  │          │
│  │     input_specification_present: true,                  │          │
│  │     context_requirements_present: true,                 │          │
│  │     required_inputs_count: 2,                           │          │
│  │     context_sources_count: 1,                           │          │
│  │     glean_integrations: ["mcp__glean__meeting_lookup"]  │          │
│  │   }                                                     │          │
│  │ }                                                        │          │
│  └──────────────────────────────────────────────────────────┘          │
│                              │                                          │
│                              │ publish(PromptValidated)                 │
│                              │ publish(PromptApproved) // score >= 90   │
└──────────────────────────────┼──────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    QUALITY GATE DECISION                                │
│                                                                         │
│  if (validationResult.isValid && validationResult.qualityScore >= 90)  │
│    └─► SUCCESS → Exit loop                                             │
│  else                                                                   │
│    └─► FEEDBACK → Continue loop (if attempts remaining)                │
└─────────────────────────────┬───────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    OUTPUT LAYER                                         │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────┐           │
│  │  1. Persist PromptSpecification                         │           │
│  │     File: output/ab-prompt.xml                          │           │
│  │     Content: xml_prompt (final version)                 │           │
│  └─────────────────────────────────────────────────────────┘           │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────┐           │
│  │  2. Persist WorkflowReport                              │           │
│  │     File: output/ab-prompt-ab-report.json               │           │
│  │     Content: {                                          │           │
│  │       workflow_type: "integrated_ab_with_context",      │           │
│  │       prompt_name: "abc-def-123",                       │           │
│  │       task: "...",                                      │           │
│  │       attempts: 1,                                      │           │
│  │       final_score: 100,                                 │           │
│  │       input_analysis: {...},                            │           │
│  │       validation_history: [...],                        │           │
│  │       glean_integrations_needed: [...]                  │           │
│  │     }                                                   │           │
│  └─────────────────────────────────────────────────────────┘           │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────┐           │
│  │  3. Publish WorkflowSessionCompleted                    │           │
│  │     Event: {                                            │           │
│  │       sessionId: "...",                                 │           │
│  │       status: "SUCCESS",                                │           │
│  │       duration: "2.3s",                                 │           │
│  │       finalScore: 100,                                  │           │
│  │       attempts: 1                                       │           │
│  │     }                                                   │           │
│  └─────────────────────────────────────────────────────────┘           │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 5. Sequence Diagrams

### 5.1 Happy Path (Success on First Attempt)

```
User    Orchestrator  ContextDiscovery  AgentA    AgentB    FileSystem
 │           │              │             │         │           │
 │──Request──>│              │             │         │           │
 │           │              │             │         │           │
 │           │──Analyze────>│             │         │           │
 │           │              │             │         │           │
 │           │<─InputAnalysis──           │         │           │
 │           │              │             │         │           │
 │           │──────Generate────────────>│         │           │
 │           │              │             │         │           │
 │           │<─────XMLPrompt─────────────│         │           │
 │           │              │             │         │           │
 │           │──────────────Validate──────────────>│           │
 │           │              │             │         │           │
 │           │<──────────ValidationResult─────────│           │
 │           │              │             │         │           │
 │           │  [isValid=true, score=100]│         │           │
 │           │              │             │         │           │
 │           │─────────────────Save──────────────────────────>│
 │           │              │             │         │           │
 │<─Success──│              │             │         │           │
 │           │              │             │         │           │
```

### 5.2 Refinement Path (Feedback Loop)

```
User    Orchestrator  ContextDiscovery  AgentA    AgentB    FileSystem
 │           │              │             │         │           │
 │──Request──>│              │             │         │           │
 │           │              │             │         │           │
 │           │──Analyze────>│             │         │           │
 │           │<─InputAnalysis──           │         │           │
 │           │              │             │         │           │
 │           ├──────────────┐             │         │           │
 │           │ ATTEMPT 1    │             │         │           │
 │           ├──────────────┘             │         │           │
 │           │──────Generate────────────>│         │           │
 │           │<─────XMLPrompt(v1)────────│         │           │
 │           │──────────────Validate──────────────>│           │
 │           │<──────────ValidationResult─────────│           │
 │           │  [isValid=false, score=85]│         │           │
 │           │  [feedback: "Add more examples"]    │           │
 │           │              │             │         │           │
 │           ├──────────────┐             │         │           │
 │           │ ATTEMPT 2    │             │         │           │
 │           ├──────────────┘             │         │           │
 │           │──────Generate────────────>│         │           │
 │           │  [with feedback]           │         │           │
 │           │<─────XMLPrompt(v2)────────│         │           │
 │           │──────────────Validate──────────────>│           │
 │           │<──────────ValidationResult─────────│           │
 │           │  [isValid=true, score=95] │         │           │
 │           │              │             │         │           │
 │           │─────────────────Save──────────────────────────>│
 │<─Success──│              │             │         │           │
 │           │              │             │         │           │
```

---

## 6. Context Map (DDD)

```
┌────────────────────────────────────────────────────────────────────┐
│                     CONTEXT MAP                                    │
│                                                                    │
│  ┌──────────────────────┐         ┌──────────────────────┐       │
│  │  PromptEngineering   │         │  ContextDiscovery    │       │
│  │  (Core Domain)       │◄────────│  (Supporting)        │       │
│  │                      │  OHS    │                      │       │
│  │  - Generation        │         │  - Task Analysis     │       │
│  │  - Validation        │         │  - Input Mapping     │       │
│  └──────────┬───────────┘         └──────────────────────┘       │
│             │                                                     │
│             │ CF (Conformist)                                     │
│             │                                                     │
│             ▼                                                     │
│  ┌──────────────────────┐         ┌──────────────────────┐       │
│  │  GleanIntegration    │         │  WorkflowOrchestration│      │
│  │  (Generic)           │         │  (Core Domain)        │      │
│  │                      │         │                       │      │
│  │  - Query Execution   │◄────────│  - Session Mgmt      │       │
│  │  - Context Retrieval │  ACL    │  - Feedback Loops    │       │
│  └──────────────────────┘         └───────────────────────┘       │
│                                                                    │
│  Legend:                                                           │
│  OHS = Open Host Service (ContextDiscovery provides API)          │
│  CF  = Conformist (PromptEngineering conforms to Glean's model)   │
│  ACL = Anti-Corruption Layer (Workflow protects domain from Glean)│
└────────────────────────────────────────────────────────────────────┘
```

### Relationship Details

**PromptEngineering ← ContextDiscovery** (Open Host Service)
- ContextDiscovery publishes `TaskAnalyzed` event
- PromptEngineering consumes this event
- Shared language: InputAnalysis, RequiredInput, ContextSource

**PromptEngineering → GleanIntegration** (Conformist)
- PromptEngineering must use Glean's query format
- PromptEngineering adapts to Glean's MCP protocol
- No translation layer needed (conformist relationship)

**WorkflowOrchestration → GleanIntegration** (Anti-Corruption Layer)
- WorkflowOrchestration protects domain from Glean changes
- Translation layer converts domain events to Glean API calls
- Isolates domain from external service complexity

---

## 7. Component Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    WORKFLOW ORCHESTRATOR                            │
│                                                                     │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │  WorkflowSessionManager                                    │   │
│  │  - createSession()                                         │   │
│  │  - startAttemptLoop()                                      │   │
│  │  - terminateSession()                                      │   │
│  └────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │  FeedbackLoopManager                                       │   │
│  │  - initiateFeedbackCycle()                                 │   │
│  │  - applyFeedback()                                         │   │
│  │  - shouldRetry()                                           │   │
│  └────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │  QualityGate                                               │   │
│  │  - evaluateScore()                                         │   │
│  │  - approvePrompt()                                         │   │
│  │  - rejectPrompt()                                          │   │
│  └────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                    CONTEXT DISCOVERY                                │
│                                                                     │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │  TaskAnalyzer                                              │   │
│  │  - analyzeTask(userRequest): InputAnalysis                │   │
│  │  - matchPattern(text): TaskPattern                        │   │
│  │  - extractKeywords(text): string[]                        │   │
│  └────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │  InputMapper                                               │   │
│  │  - mapInputs(pattern): RequiredInput[]                    │   │
│  │  - identifyOptionalInputs(pattern): OptionalInput[]       │   │
│  └────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │  ContextMapper                                             │   │
│  │  - mapContextSources(pattern): ContextSource[]            │   │
│  │  - generateGleanQuery(source): string                     │   │
│  │  - identifyGleanTools(sources): string[]                  │   │
│  └────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                    PROMPT ENGINEERING                               │
│                                                                     │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │  PromptGenerator (Agent A Wrapper)                         │   │
│  │  - generate(request, inputAnalysis): PromptSpecification  │   │
│  │  - generateInputSpec(analysis): XmlElement                │   │
│  │  - generateContextReq(analysis): XmlElement               │   │
│  │  - applyFeedback(feedback, previous): PromptSpecification │   │
│  └────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │  PromptValidator (Agent B Wrapper)                         │   │
│  │  - validate(xmlPrompt): ValidationResult                  │   │
│  │  - checkStructural(xml): CheckResult[]                    │   │
│  │  - checkCompleteness(xml): CheckResult[]                  │   │
│  │  - checkQuality(xml): CheckResult[]                       │   │
│  │  - checkContext(xml): ContextValidation                   │   │
│  │  - calculateScore(checks): number                         │   │
│  │  - generateFeedback(checks): string[]                     │   │
│  └────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                    GLEAN INTEGRATION                                │
│                                                                     │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │  GleanConnector (Anti-Corruption Layer)                    │   │
│  │  - invokeAgent(agentId, input): AgentResponse             │   │
│  │  - search(query): SearchResult[]                          │   │
│  │  - lookupMeetings(query): Meeting[]                       │   │
│  │  - searchCode(query): CodeResult[]                        │   │
│  │  - readDocument(url): Document                            │   │
│  └────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │  ToolMapper                                                │   │
│  │  - mapToGleanTool(sourceType): string                     │   │
│  │  - buildQuery(template, vars): string                     │   │
│  └────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 8. Event Storming Results

### Domain Events Timeline

```
Time ──────────────────────────────────────────────────────────────>

[WorkflowSessionStarted]
         │
         ├─> [AttemptInitiated] (attempt: 1)
         │        │
         │        ├─> [TaskAnalysisRequested]
         │        │        │
         │        │        └─> [TaskAnalyzed]
         │        │                 │
         │        │                 └─> [InputsIdentified]
         │        │                      │
         │        │                      └─> [ContextSourcesDiscovered]
         │        │                           │
         │        │                           └─> [GleanToolsMapped]
         │        │
         │        ├─> [PromptGenerationRequested]
         │        │        │
         │        │        └─> [PromptGenerated]
         │        │
         │        ├─> [PromptValidationRequested]
         │        │        │
         │        │        ├─> [ValidationCheckExecuted] (x10)
         │        │        │
         │        │        └─> [PromptValidated]
         │        │                 │
         │        │                 ├─> IF score >= 90
         │        │                 │    └─> [PromptApproved]
         │        │                 │         │
         │        │                 │         └─> [WorkflowSessionCompleted]
         │        │                 │
         │        │                 └─> IF score < 90
         │        │                      └─> [PromptRejected]
         │        │                           │
         │        │                           └─> [FeedbackGenerated]
         │        │                                │
         │        │                                └─> [FeedbackCycleStarted]
         │        │
         │        └─> [AttemptCompleted]
         │
         ├─> [AttemptInitiated] (attempt: 2)
         │        │
         │        ├─> [FeedbackApplied]
         │        │
         │        ├─> [PromptGenerationRequested] (with feedback)
         │        │
         │        └─> ... (repeat validation cycle)
         │
         └─> [WorkflowSessionCompleted] OR [WorkflowSessionFailed]
```

### Command-Event-Read Model Mapping

| Command | Domain Events Triggered | Read Models Updated |
|---------|------------------------|---------------------|
| `GeneratePrompt` | WorkflowSessionStarted | WorkflowSessionList |
| `AnalyzeTask` | TaskAnalysisRequested, TaskAnalyzed, InputsIdentified | InputAnalysisCache |
| `GenerateXmlPrompt` | PromptGenerationRequested, PromptGenerated | PromptSpecificationStore |
| `ValidatePrompt` | PromptValidationRequested, PromptValidated, PromptApproved/Rejected | ValidationResultHistory |
| `ApplyFeedback` | FeedbackApplied | FeedbackCycleHistory |
| `CompleteWorkflow` | WorkflowSessionCompleted | WorkflowSessionArchive |

---

## 9. Integration Patterns

### 9.1 Agent Communication Pattern

```
┌─────────────────────────────────────────────────────────────────┐
│  REQUEST-RESPONSE PATTERN (Synchronous)                        │
│                                                                 │
│  Orchestrator                Agent A (External)                │
│       │                           │                            │
│       │──── HTTP POST ────────────>│                            │
│       │    /tools/generate_xml_prompt                          │
│       │    {                       │                            │
│       │      user_request: "...",  │                            │
│       │      analyze_context: true │                            │
│       │    }                       │                            │
│       │                            │                            │
│       │                            │ [Processing...]            │
│       │                            │ - Context Analysis         │
│       │                            │ - XML Generation           │
│       │                            │                            │
│       │<─── HTTP 200 ──────────────│                            │
│       │    {                       │                            │
│       │      xml_prompt: "...",    │                            │
│       │      prompt_name: "...",   │                            │
│       │      input_analysis: {...} │                            │
│       │    }                       │                            │
│       │                            │                            │
│       │ publish(PromptGenerated)   │                            │
│       │                            │                            │
└─────────────────────────────────────────────────────────────────┘
```

### 9.2 Event-Driven Pattern (Future Enhancement)

```
┌─────────────────────────────────────────────────────────────────┐
│  PUBLISH-SUBSCRIBE PATTERN (Asynchronous)                      │
│                                                                 │
│  Orchestrator         Event Bus          Subscriber            │
│       │                   │                    │               │
│       │───publish()──────>│                    │               │
│       │  PromptGenerated  │                    │               │
│       │                   │                    │               │
│       │                   │────notify()───────>│               │
│       │                   │                    │               │
│       │                   │                    │ handle()      │
│       │                   │                    │ - Index       │
│       │                   │                    │ - Cache       │
│       │                   │                    │ - Analytics   │
│       │                   │                    │               │
└─────────────────────────────────────────────────────────────────┘
```

---

## 10. Deployment Architecture (Future)

```
┌────────────────────────────────────────────────────────────────────┐
│                        PRODUCTION DEPLOYMENT                       │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │  Load Balancer (API Gateway)                                 │ │
│  └────────────────┬─────────────────────────────────────────────┘ │
│                   │                                                │
│                   ▼                                                │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │  Application Cluster (Kubernetes)                            │ │
│  │                                                              │ │
│  │  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐ │ │
│  │  │ Orchestrator   │  │ Orchestrator   │  │ Orchestrator   │ │ │
│  │  │ Pod (Replica 1)│  │ Pod (Replica 2)│  │ Pod (Replica 3)│ │ │
│  │  └────────────────┘  └────────────────┘  └────────────────┘ │ │
│  └──────────────┬───────────────────────────────────────────────┘ │
│                 │                                                  │
│                 ▼                                                  │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │  External Services                                           │ │
│  │                                                              │ │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────────────────┐ │ │
│  │  │ Glean      │  │ Glean      │  │ Glean                  │ │ │
│  │  │ Agent A    │  │ Agent B    │  │ MCP Services           │ │ │
│  │  │ (External) │  │ (External) │  │ (search, meetings,etc) │ │ │
│  │  └────────────┘  └────────────┘  └────────────────────────┘ │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │  Data Layer                                                  │ │
│  │                                                              │ │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────────────────┐ │ │
│  │  │ PostgreSQL │  │ Redis      │  │ Object Storage (S3)    │ │ │
│  │  │ (Metadata) │  │ (Cache)    │  │ (Generated Prompts)    │ │ │
│  │  └────────────┘  └────────────┘  └────────────────────────┘ │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │  Observability                                               │ │
│  │                                                              │ │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────────────────┐ │ │
│  │  │ Prometheus │  │ Grafana    │  │ ELK Stack              │ │ │
│  │  │ (Metrics)  │  │ (Dashboards│  │ (Logs & Events)        │ │ │
│  │  └────────────┘  └────────────┘  └────────────────────────┘ │ │
│  └──────────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────────┘
```

---

## Summary

This reference architecture represents a **production-ready, event-driven, DDD-based system** with:

✅ **4 Bounded Contexts** (PromptEngineering, ContextDiscovery, GleanIntegration, WorkflowOrchestration)
✅ **18+ Domain Events** (capturing all state transitions)
✅ **Complete Data Flow** (from user request to file persistence)
✅ **Sequence Diagrams** (happy path + refinement path)
✅ **Context Map** (showing relationships and integration patterns)
✅ **Component Architecture** (layered with clear responsibilities)
✅ **Event Timeline** (showing temporal ordering of events)
✅ **Integration Patterns** (request-response + pub-sub)
✅ **Deployment Architecture** (future cloud-native deployment)

The architecture is **scalable**, **maintainable**, and **ready for production deployment**.
