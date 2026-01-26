# Observation and Testing in the Workflow

**How testing and observability are built into every stage of the prompt engineering workflow**

---

## Overview

The Integrated A/B Prompt Engineering System is designed with **testing and observability as first-class concerns**. Every workflow execution is:

- ✅ **Traceable** - Complete execution history with correlation IDs
- ✅ **Observable** - Real-time visibility into agent decisions
- ✅ **Testable** - Multiple test levels from unit to end-to-end
- ✅ **Debuggable** - Event sourcing enables time-travel debugging
- ✅ **Measurable** - Quality metrics and performance data

---

## Testing & Observation Integration

```
┌─────────────────────────────────────────────────────────────────┐
│  WORKFLOW EXECUTION WITH OBSERVATION POINTS                     │
└─────────────────────────────────────────────────────────────────┘

User Request: "Create a prompt for meeting summarization"
    │
    ├─► [OBSERVATION] Session ID assigned: session-abc-123
    ├─► [TRACE] Correlation ID: corr-456-def
    │
    ▼
┌───────────────────────────────────────────────────────────────┐
│ HOP 1: Context Discovery                                     │
│   ├─► [EVENT] TaskAnalyzed                                   │
│   ├─► [METRIC] Duration: 1200ms                              │
│   ├─► [TEST] ✓ Required inputs identified                    │
│   └─► [LOG] Found 2 required inputs, 1 context source        │
└───────────────────────────────────────────────────────────────┘
    │
    ▼
┌───────────────────────────────────────────────────────────────┐
│ HOP 2: Agent A Generation (Attempt 1)                        │
│   ├─► [EVENT] AttemptInitiated (attempt: 1)                  │
│   ├─► [EVENT] PromptGenerated                                │
│   ├─► [METRIC] Duration: 2000ms                              │
│   ├─► [TEST] ✓ XML well-formed                               │
│   ├─► [TEST] ✓ All required sections present                 │
│   └─► [LOG] Generated 2450 characters                        │
└───────────────────────────────────────────────────────────────┘
    │
    ▼
┌───────────────────────────────────────────────────────────────┐
│ HOP 3: Agent B Validation (Attempt 1)                        │
│   ├─► [EVENT] PromptValidated                                │
│   ├─► [METRIC] Duration: 1500ms, Score: 85/100               │
│   ├─► [TEST] ✗ Score below threshold (90)                    │
│   ├─► [VALIDATION] 12 checks run: 9 passed, 3 failed         │
│   ├─► [FEEDBACK] 3 items generated                           │
│   └─► [LOG] Status: FAIL, retry needed                       │
└───────────────────────────────────────────────────────────────┘
    │
    ├─► [OBSERVATION] Feedback loop triggered
    │
    ▼
┌───────────────────────────────────────────────────────────────┐
│ HOP 4: Feedback Loop (Agent B → Agent A)                     │
│   ├─► [EVENT] FeedbackCycleStarted                           │
│   ├─► [EVENT] FeedbackApplied                                │
│   ├─► [METRIC] Duration: 2000ms                              │
│   ├─► [TEST] ✓ Feedback addressed (3/3 items)                │
│   └─► [LOG] Refinements applied                              │
└───────────────────────────────────────────────────────────────┘
    │
    ▼
┌───────────────────────────────────────────────────────────────┐
│ HOP 5: Agent A Refinement (Attempt 2)                        │
│   ├─► [EVENT] AttemptInitiated (attempt: 2)                  │
│   ├─► [EVENT] PromptGenerated                                │
│   ├─► [METRIC] Duration: 2000ms                              │
│   ├─► [TEST] ✓ Changes applied correctly                     │
│   └─► [LOG] Generated 2850 characters (+400)                 │
└───────────────────────────────────────────────────────────────┘
    │
    ▼
┌───────────────────────────────────────────────────────────────┐
│ HOP 6: Agent B Re-Validation (Attempt 2)                     │
│   ├─► [EVENT] PromptValidated                                │
│   ├─► [EVENT] PromptApproved                                 │
│   ├─► [METRIC] Duration: 1500ms, Score: 95/100               │
│   ├─► [TEST] ✓ Score above threshold                         │
│   ├─► [VALIDATION] 12 checks run: 12 passed, 0 failed        │
│   └─► [LOG] Status: PASS                                     │
└───────────────────────────────────────────────────────────────┘
    │
    ▼
┌───────────────────────────────────────────────────────────────┐
│ OUTPUT: Files Saved                                          │
│   ├─► [EVENT] WorkflowSessionCompleted                       │
│   ├─► [METRIC] Total duration: 9000ms                        │
│   ├─► [TEST] ✓ XML file created                              │
│   ├─► [TEST] ✓ Report file created                           │
│   └─► [ANALYTICS] Session stats recorded                     │
└───────────────────────────────────────────────────────────────┘

═══════════════════════════════════════════════════════════════

COMPLETE OBSERVABILITY:
  • 13 Domain Events recorded
  • 6 Hops traced with correlation IDs
  • 12 Validation checks executed
  • 15+ Test assertions passed
  • Performance metrics captured at each stage
  • Full audit trail in event store
```

---

## Testing Levels

```
┌─────────────────────────────────────────────────────────────────┐
│  Testing Pyramid                                                │
│                                                                 │
│                    ▲                                            │
│                   ╱ ╲                                           │
│                  ╱   ╲        E2E Tests                         │
│                 ╱     ╲       (Workflow)                        │
│                ╱───────╲                                        │
│               ╱         ╲                                       │
│              ╱           ╲    Integration Tests                 │
│             ╱             ╲   (Agent A/B + Validation)          │
│            ╱───────────────╲                                    │
│           ╱                 ╲                                   │
│          ╱                   ╲  Unit Tests                      │
│         ╱                     ╲ (Artifacts, Rules, Schemas)     │
│        ╱───────────────────────╲                                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 1. End-to-End Workflow Testing

### **Command: Test Complete Workflow**

```bash
# Run all test scenarios
make test-ab-workflow

# Test specific scenario
make xml-prompt-ab TASK="Create a prompt for meeting summarization"
```

### **What Gets Tested**

```
Test Workflow Execution:
│
├─ 1. Context Discovery
│  ├─ ✓ Identifies required inputs correctly
│  ├─ ✓ Identifies optional inputs
│  ├─ ✓ Maps context sources to Glean tools
│  └─ ✓ Generates valid query templates
│
├─ 2. Agent A Generation
│  ├─ ✓ Produces well-formed XML
│  ├─ ✓ Includes all required sections
│  ├─ ✓ Uses correct prompt name format
│  ├─ ✓ Incorporates input analysis
│  └─ ✓ Includes context requirements
│
├─ 3. Agent B Validation
│  ├─ ✓ Runs all validation checks
│  ├─ ✓ Calculates accurate scores
│  ├─ ✓ Generates actionable feedback (if needed)
│  └─ ✓ Validates context specifications
│
├─ 4. Feedback Loop (if score < 90)
│  ├─ ✓ Feedback reaches Agent A
│  ├─ ✓ Agent A addresses feedback items
│  ├─ ✓ XML evolves correctly
│  └─ ✓ Retry logic works (max 3 attempts)
│
└─ 5. Output Generation
   ├─ ✓ XML file created
   ├─ ✓ Report file created
   ├─ ✓ Files are valid
   └─ ✓ Session completes successfully
```

### **Test Output Example**

```bash
$ make test-ab-workflow

Running test scenarios...

[1/3] Testing: Meeting Summarization
  ✓ Context discovery identified 2 required inputs
  ✓ Context discovery identified 1 context source
  ✓ Agent A generated valid XML (attempt 1)
  ✓ Agent B validation score: 100/100
  ✓ No feedback loop needed (first attempt success)
  ✓ Output files created
  Duration: 2.3s
  Status: PASS ✓

[2/3] Testing: Code Review
  ✓ Context discovery identified 2 required inputs
  ✓ Context discovery identified 2 context sources
  ✓ Agent A generated valid XML (attempt 1)
  ✓ Agent B validation score: 100/100
  ✓ No feedback loop needed (first attempt success)
  ✓ Output files created
  Duration: 2.1s
  Status: PASS ✓

[3/3] Testing: Customer Feedback Analysis
  ✓ Context discovery identified 1 required input
  ✓ Context discovery identified 2 context sources
  ✓ Agent A generated valid XML (attempt 1)
  ✓ Agent B validation score: 100/100
  ✓ No feedback loop needed (first attempt success)
  ✓ Output files created
  Duration: 2.5s
  Status: PASS ✓

========================================
All tests passed! (3/3)
Total duration: 6.9s
========================================
```

---

## 2. Observability Features

### **2.1 Execution Trace with Correlation IDs**

Every workflow execution is fully traceable:

```json
{
  "session_id": "session-abc-123-xyz",
  "correlation_id": "corr-456-def-ghi",
  "trace": [
    {
      "hop": 1,
      "timestamp": "2026-01-26T14:30:01.000Z",
      "from": "START",
      "to": "ContextDiscoveryNode",
      "duration_ms": 1200,
      "payload_type": "UserRequest",
      "result_type": "InputAnalysis",
      "status": "success"
    },
    {
      "hop": 2,
      "timestamp": "2026-01-26T14:30:03.000Z",
      "from": "ContextDiscoveryNode",
      "to": "AgentANode",
      "duration_ms": 2000,
      "payload_type": "GenerationRequest",
      "result_type": "PromptSpecification",
      "status": "success"
    },
    {
      "hop": 3,
      "timestamp": "2026-01-26T14:30:05.500Z",
      "from": "AgentANode",
      "to": "AgentBNode",
      "duration_ms": 1500,
      "payload_type": "ValidationRequest",
      "result_type": "ValidationResult",
      "status": "success",
      "score": 85,
      "isValid": false
    },
    {
      "hop": 4,
      "timestamp": "2026-01-26T14:30:07.000Z",
      "from": "AgentBNode",
      "to": "AgentANode",
      "duration_ms": 2000,
      "payload_type": "RefinementRequest",
      "result_type": "PromptSpecification",
      "status": "success",
      "note": "FEEDBACK_LOOP"
    },
    {
      "hop": 5,
      "timestamp": "2026-01-26T14:30:09.500Z",
      "from": "AgentANode",
      "to": "AgentBNode",
      "duration_ms": 1500,
      "payload_type": "ValidationRequest",
      "result_type": "ValidationResult",
      "status": "success",
      "score": 95,
      "isValid": true
    },
    {
      "hop": 6,
      "timestamp": "2026-01-26T14:30:10.000Z",
      "from": "AgentBNode",
      "to": "OutputNode",
      "duration_ms": 500,
      "payload_type": "SaveRequest",
      "result_type": "FilesCreated",
      "status": "success"
    }
  ],
  "total_hops": 6,
  "total_duration_ms": 9000,
  "attempts": 2,
  "final_status": "SUCCESS"
}
```

**Observability Benefits**:
- ✅ Track execution flow through all hops
- ✅ Identify performance bottlenecks
- ✅ Debug failures at specific hop
- ✅ Correlate events across distributed system

---

### **2.2 Real-Time Workflow Monitoring**

During execution, you can observe:

```bash
$ make xml-prompt-ab TASK="Create a prompt for meeting summarization"

[14:30:01] → Starting workflow session: session-abc-123
[14:30:01] → HOP 1: Context Discovery
           Analyzing task: "Create a prompt for meeting summarization"

[14:30:02] ✓ Context Discovery Complete
           Required inputs: 2 (meeting_transcript, attendee_list)
           Context sources: 1 (previous_meetings)
           Glean tools: mcp__glean__meeting_lookup

[14:30:03] → HOP 2: Agent A Generation (Attempt 1)
           Generating XML prompt with context analysis...

[14:30:05] ✓ Generation Complete
           Prompt name: m3t-4ng-s1m
           XML size: 2,450 characters
           Sections: 8/8 required

[14:30:05] → HOP 3: Agent B Validation (Attempt 1)
           Running validation checks...

[14:30:07] ⚠ Validation: Score 85/100 (threshold: 90)
           Status: FAIL
           Feedback items: 3
           - Add at least one more good example
           - Add validation rules for all required inputs
           - Improve specificity in instructions

[14:30:07] → HOP 4: Feedback Loop Initiated
           Sending feedback to Agent A...

[14:30:07] → HOP 5: Agent A Refinement (Attempt 2)
           Addressing feedback items...

[14:30:09] ✓ Refinement Complete
           Changes applied: 3/3 feedback items
           - Added 2nd good example ✓
           - Added detailed validation rules ✓
           - Enhanced instruction specificity ✓

[14:30:09] → HOP 6: Agent B Re-Validation (Attempt 2)
           Running validation checks...

[14:30:11] ✓ Validation: Score 95/100
           Status: PASS
           All checks passed!

[14:30:11] → Saving output files...
[14:30:11] ✓ Files saved:
           - output/ab-prompt.xml
           - output/ab-prompt-ab-report.json

[14:30:11] ✓ Session completed successfully!

Summary:
- Session ID: session-abc-123
- Final Score: 95/100
- Attempts: 2
- Duration: 9.0 seconds
- Hops: 6
```

---

### **2.3 Event Sourcing for Time-Travel Debugging**

All domain events are recorded:

```
Event Stream: session-abc-123
│
├─ [1] WorkflowSessionStarted
│      timestamp: 2026-01-26T14:30:01.000Z
│      user_request: "Create a prompt for meeting summarization"
│
├─ [2] TaskAnalyzed
│      required_inputs: ["meeting_transcript", "attendee_list"]
│      context_sources: ["previous_meetings"]
│
├─ [3] AttemptInitiated
│      attempt_number: 1
│
├─ [4] PromptGenerated
│      prompt_name: "m3t-4ng-s1m"
│      xml_size: 2450
│      generation_metadata: {...}
│
├─ [5] PromptValidated
│      quality_score: 85
│      is_valid: false
│      checks_passed: 9/12
│
├─ [6] FeedbackGenerated
│      feedback_items: [
│        "Add at least one more good example",
│        "Add validation rules for all required inputs",
│        "Improve specificity in instructions"
│      ]
│
├─ [7] FeedbackCycleStarted
│      cycle_number: 1
│
├─ [8] FeedbackApplied
│      refinements: ["Added 2nd good example", ...]
│
├─ [9] AttemptInitiated
│      attempt_number: 2
│
├─ [10] PromptGenerated
│       prompt_name: "m3t-4ng-s1m"
│       xml_size: 2850
│       changes_from_previous: [...]
│
├─ [11] PromptValidated
│       quality_score: 95
│       is_valid: true
│       checks_passed: 12/12
│
├─ [12] PromptApproved
│       approval_reason: "Score >= 90 AND no errors"
│
└─ [13] WorkflowSessionCompleted
       final_score: 95
       total_attempts: 2
       duration_ms: 9000
```

**Debug Capabilities**:
- ✅ **Replay workflow** from any point
- ✅ **Inspect state** at each event
- ✅ **Compare attempts** to see what changed
- ✅ **Audit trail** for compliance

**Example: Time-Travel Query**

```typescript
// Get workflow state at specific point in time
const stateAfterFirstAttempt = reconstructAggregate(
  "session-abc-123",
  upToEvent: 5  // After PromptValidated (attempt 1)
);

console.log(stateAfterFirstAttempt.currentPrompt.xmlContent);
console.log(stateAfterFirstAttempt.validationResult.qualityScore); // 85

// Compare with final state
const finalState = reconstructAggregate("session-abc-123");
console.log(finalState.validationResult.qualityScore); // 95

// See exact changes
const diff = compareXML(
  stateAfterFirstAttempt.currentPrompt.xmlContent,
  finalState.currentPrompt.xmlContent
);
```

---

### **2.4 Validation Report Analytics**

Every validation produces detailed metrics:

```json
{
  "validation_id": "val-789-jkl",
  "timestamp": "2026-01-26T14:30:09.500Z",
  "attempt_number": 2,

  "overall_result": {
    "is_valid": true,
    "quality_score": 95,
    "pass_threshold": 90
  },

  "score_breakdown": {
    "structural": {
      "score": 35,
      "max": 35,
      "percentage": 100,
      "checks": {
        "xml_well_formed": {"status": "pass", "points": 10},
        "required_sections_present": {"status": "pass", "points": 15},
        "tag_hierarchy": {"status": "pass", "points": 10},
        "naming_convention": {"status": "pass", "points": 5}
      }
    },
    "completeness": {
      "score": 30,
      "max": 30,
      "percentage": 100,
      "checks": {
        "section_content": {"status": "pass", "points": 15},
        "examples_quality": {"status": "pass", "points": 10},
        "instructions_structure": {"status": "pass", "points": 5}
      }
    },
    "quality": {
      "score": 25,
      "max": 25,
      "percentage": 100,
      "checks": {
        "clarity_and_specificity": {"status": "pass", "points": 10},
        "examples_effectiveness": {"status": "pass", "points": 10},
        "constraints_and_validation": {"status": "pass", "points": 5}
      }
    },
    "context_quality": {
      "score": 10,
      "max": 10,
      "percentage": 100,
      "checks": {
        "required_inputs_defined": {"status": "pass", "points": 3},
        "input_descriptions_clear": {"status": "pass", "points": 2},
        "glean_queries_valid": {"status": "pass", "points": 3},
        "context_sources_accessible": {"status": "pass", "points": 2}
      }
    }
  },

  "checks_summary": {
    "total": 12,
    "passed": 12,
    "failed": 0,
    "warnings": 0
  },

  "performance_metrics": {
    "validation_duration_ms": 1500,
    "xml_parse_time_ms": 50,
    "checks_execution_time_ms": 1200,
    "feedback_generation_time_ms": 250
  },

  "comparison_to_previous": {
    "score_delta": +10,
    "new_issues": 0,
    "resolved_issues": 3,
    "improvements": [
      "Added 2nd good example",
      "Added detailed validation rules",
      "Enhanced instruction specificity"
    ]
  }
}
```

**Analytics Use Cases**:
- 📊 Track quality trends over time
- 📈 Identify common failure patterns
- 🎯 Optimize validation rules
- 🔍 Debug specific check failures

---

## 3. Testing Validation Rules

### **Test New Validation Rules**

Before deploying new rules, test them:

```bash
# Create test validation rules
cp validation-rules.json validation-rules-test.json

# Edit validation-rules-test.json
# - Change threshold: 90 → 95
# - Add new check: "domain_knowledge_present"
# - Update points: examples_quality: 10 → 15

# Test with new rules
make xml-prompt-ab \
  TASK="Create a prompt for meeting summarization" \
  VALIDATION_RULES=validation-rules-test.json

# Compare results
diff output/ab-prompt-ab-report.json output/ab-prompt-ab-report-test.json
```

**Validation Rule Testing Checklist**:
- ✅ Does the new rule improve quality?
- ✅ Does it cause false positives?
- ✅ Is the scoring fair?
- ✅ Can agents address the feedback?
- ✅ Does it align with organization standards?

---

## 4. Testing Examples

### **Test Example Quality**

Validate that examples meet standards:

```bash
# Validate a good example
make validate-prompt FILE="workflow-orchestration/global/examples/good/well-structured-prompts/example-001-meeting-summary.xml"

Expected output:
✓ Score: 95-100/100
✓ Status: PASS
✓ All checks passed

# Validate a bad example (should fail)
make validate-prompt FILE="workflow-orchestration/global/examples/bad/anti-patterns/example-001-flat-structure.xml"

Expected output:
✗ Score: 40-60/100
✗ Status: FAIL
✗ Issues identified: [list of problems]
```

### **Add New Examples with Testing**

```bash
# 1. Create new example
vim workflow-orchestration/global/examples/good/my-new-example.xml

# 2. Test it validates correctly
make validate-prompt FILE="workflow-orchestration/global/examples/good/my-new-example.xml"

# 3. Update metadata
vim workflow-orchestration/global/examples/good/_metadata.json

# 4. Test discovery
make list-examples

# 5. Test agent can use it
make xml-prompt-ab TASK="Similar to my new example"
```

---

## 5. Agent Testing

### **5.1 Test Agent A (Generator)**

```bash
# Test generation without validation
make test-agent-a TASK="Create a prompt for meeting summarization"

# Checks:
# ✓ XML is well-formed
# ✓ All required sections present
# ✓ Context analysis performed
# ✓ Input specifications generated
```

### **5.2 Test Agent B (Validator)**

```bash
# Test validation with known good prompt
make test-agent-b FILE="examples/good/example-001.xml"

# Expected: Score 95-100, PASS

# Test validation with known bad prompt
make test-agent-b FILE="examples/bad/example-001.xml"

# Expected: Score <90, FAIL with specific feedback
```

### **5.3 Test Feedback Loop**

```bash
# Test that feedback improves quality
make test-feedback-loop TASK="Create a prompt for meeting summarization"

# Monitors:
# ✓ Attempt 1: Score < 90
# ✓ Feedback generated with specific items
# ✓ Attempt 2: Score >= 90
# ✓ Feedback items addressed
# ✓ XML evolved correctly
```

---

## 6. Integration Testing

### **Test Glean MCP Integration**

```bash
# Test that Glean tools are correctly identified
make test-glean-integration TASK="Create a prompt for meeting summarization"

# Checks:
# ✓ Correct Glean tools identified (mcp__glean__meeting_lookup)
# ✓ Query templates generated
# ✓ Context sources mapped
```

### **Test Event Store**

```bash
# Test event persistence
make test-event-store

# Checks:
# ✓ Events written correctly
# ✓ Events retrievable by session ID
# ✓ Event ordering preserved
# ✓ Aggregate reconstruction works
```

---

## 7. Performance Testing

### **Measure Workflow Performance**

```bash
# Run performance benchmark
make benchmark

Output:
┌─────────────────────────────┬──────────┬──────────┬──────────┐
│ Scenario                    │ Avg (ms) │ Min (ms) │ Max (ms) │
├─────────────────────────────┼──────────┼──────────┼──────────┤
│ Context Discovery           │ 1,200    │ 1,000    │ 1,500    │
│ Agent A Generation (1st)    │ 2,000    │ 1,800    │ 2,500    │
│ Agent B Validation          │ 1,500    │ 1,200    │ 2,000    │
│ Agent A Refinement (2nd)    │ 2,000    │ 1,800    │ 2,500    │
│ Agent B Re-validation       │ 1,500    │ 1,200    │ 2,000    │
│ File Output                 │ 500      │ 300      │ 800      │
├─────────────────────────────┼──────────┼──────────┼──────────┤
│ Total (1 attempt)           │ 5,200    │ 4,500    │ 6,500    │
│ Total (2 attempts)          │ 9,000    │ 8,000    │ 11,000   │
└─────────────────────────────┴──────────┴──────────┴──────────┘

✓ All scenarios within acceptable latency
✓ P95: 10.5 seconds
✓ P99: 12.0 seconds
```

---

## 8. Debugging Workflows

### **Debug Failed Workflow**

```bash
# Run with verbose logging
make xml-prompt-ab TASK="..." DEBUG=true

# Output shows:
# - Full event stream
# - Agent request/response payloads
# - Validation check details
# - Error stack traces

# Inspect specific session
make inspect-session SESSION_ID=session-abc-123

# Shows:
# - All events in order
# - Full execution trace
# - State at each hop
# - Performance metrics
```

### **Common Debugging Scenarios**

**Scenario 1: Low Quality Score**
```bash
# 1. Check validation report
cat output/ab-prompt-ab-report.json | jq '.scoreBreakdown'

# 2. Identify failing checks
cat output/ab-prompt-ab-report.json | jq '.checks[] | select(.status == "fail")'

# 3. Review feedback
cat output/ab-prompt-ab-report.json | jq '.feedback'

# 4. Compare to good examples
diff output/ab-prompt.xml workflow-orchestration/global/examples/good/example-001.xml
```

**Scenario 2: Infinite Loop (Max Attempts)**
```bash
# Check if feedback is being addressed
make inspect-session SESSION_ID=session-abc-123 | grep "FeedbackApplied"

# Review XML evolution
make compare-attempts SESSION_ID=session-abc-123

# Shows side-by-side diff of attempts
```

**Scenario 3: Wrong Context Identified**
```bash
# Debug context discovery
make debug-context TASK="..."

# Shows:
# - Pattern matching results
# - Input detection logic
# - Context source selection
# - Glean tool mapping
```

---

## 9. Continuous Testing

### **Pre-Commit Hooks**

```bash
#!/bin/bash
# .git/hooks/pre-commit

# Run validation rule tests
make test-validation-rules || exit 1

# Test all examples still validate
make test-all-examples || exit 1

# Run quick workflow test
make test-ab-workflow-quick || exit 1

echo "✓ All pre-commit tests passed"
```

### **CI/CD Pipeline**

```yaml
# .github/workflows/test.yml
name: Test Workflow

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Install dependencies
        run: npm install

      - name: Test validation rules
        run: make test-validation-rules

      - name: Test examples
        run: make test-all-examples

      - name: Test workflows
        run: make test-ab-workflow

      - name: Performance benchmark
        run: make benchmark

      - name: Upload reports
        uses: actions/upload-artifact@v2
        with:
          name: test-reports
          path: output/*.json
```

---

## 10. Monitoring in Production

### **Metrics to Track**

```javascript
// Prometheus metrics
workflow_executions_total{status="success"}
workflow_executions_total{status="failure"}
workflow_duration_seconds{percentile="p95"}
workflow_attempts_count{attempt="1"}
workflow_attempts_count{attempt="2"}
workflow_attempts_count{attempt="3"}
validation_score_average
validation_checks_failed_total{check="examples_quality"}
feedback_loop_triggered_total
```

### **Alerting Rules**

```yaml
# alerting-rules.yml
groups:
  - name: workflow_quality
    rules:
      - alert: HighFailureRate
        expr: rate(workflow_executions_total{status="failure"}[5m]) > 0.1
        for: 5m
        annotations:
          summary: "Workflow failure rate above 10%"

      - alert: LowQualityScores
        expr: validation_score_average < 85
        for: 10m
        annotations:
          summary: "Average validation score below 85"

      - alert: SlowWorkflows
        expr: workflow_duration_seconds{percentile="p95"} > 15
        for: 5m
        annotations:
          summary: "P95 latency above 15 seconds"
```

---

## Summary

### Testing Coverage

| Test Level | What's Tested | How Often |
|------------|---------------|-----------|
| **Unit Tests** | Validation rules, schemas, artifacts | Every commit |
| **Integration Tests** | Agent A/B, validation, context discovery | Every commit |
| **E2E Tests** | Complete workflow scenarios | Every commit |
| **Performance Tests** | Latency, throughput | Daily |
| **Regression Tests** | Known good/bad examples | Every commit |

### Observability Features

| Feature | Benefit | Implementation |
|---------|---------|----------------|
| **Correlation IDs** | Trace requests across hops | Event metadata |
| **Event Sourcing** | Complete audit trail | Event store |
| **Validation Reports** | Quality insights | JSON reports |
| **Execution Trace** | Debug failures | Hop logging |
| **Performance Metrics** | Optimize latency | Prometheus |

### Key Insights

✅ **Everything is Observable** - Every hop, every decision, every validation check is logged and traceable

✅ **Everything is Testable** - From individual validation rules to complete workflows

✅ **Everything is Debuggable** - Event sourcing enables time-travel debugging

✅ **Everything is Measurable** - Quality scores, performance metrics, success rates

**Result**: A system that's not just production-ready, but production-observable and production-testable.

---

**Last Updated:** 2026-01-26
**Version:** 1.0.0
**Status:** ✅ Production Ready
