# Workflow Patterns Reference

This document describes common workflow orchestration patterns used in the system.

## Pattern Catalog

### 1. stg-val-wkf (Staged Validation Workflow)

**Description:** A pattern where outputs from one stage are validated by another, with feedback loops for refinement.

**Structure:**
```
Stage 1 (Generator) → Stage 2 (Validator) → Quality Gate
                                                ↓
                                       Pass (≥threshold) → Output
                                                ↓
                                       Fail (<threshold) → Feedback Loop → Stage 1
```

**Characteristics:**
- **2+ stages**: Generator stage(s) + Validator stage(s)
- **Quality gates**: Success threshold (typically 90/100)
- **Feedback loops**: Failed validation triggers retry with feedback
- **Max attempts**: Configurable (typically 3)
- **Feedback enrichment**: Cumulative or latest-only

**Use Cases:**
- Content generation requiring quality assurance
- Multi-step transformations with validation
- Iterative refinement workflows
- Any process where output quality is critical

**Existing Examples:**
- `prompt-generation` workflow (2 stages: generate + validate)

**Configuration:**
```json
{
  "pattern": "stg-val-wkf",
  "orchestration": {
    "pattern": "sequential_with_loops",
    "loop_logic": {
      "on_validation_failure": "loop_to_generator",
      "max_total_attempts": 3,
      "feedback_enrichment": "cumulative"
    }
  }
}
```

**Pros:**
- High output quality through validation
- Automatic refinement without human intervention
- Clear separation of generation and validation concerns
- Trackable quality metrics

**Cons:**
- Higher latency (multiple LLM calls)
- More complex error handling
- Potential infinite loops (mitigated by max attempts)

**Best Practices:**
- Set realistic success thresholds (90-95)
- Limit max attempts to 3-5
- Use cumulative feedback for better refinement
- Track improvement across attempts
- Escalate to user if no improvement after 2 attempts

---

### 2. sequential (Linear Sequential Workflow)

**Description:** Stages execute in order, each consuming the previous stage's output. No feedback loops.

**Structure:**
```
Stage 1 → Stage 2 → Stage 3 → ... → Output
```

**Characteristics:**
- **Linear flow**: Stages run in fixed order
- **No loops**: Failed stages stop the workflow
- **Pass-through**: Each stage processes previous output
- **Deterministic**: Same input → same output (modulo LLM variance)

**Use Cases:**
- Data transformation pipelines
- Multi-step processing without refinement
- Workflows where each stage must succeed
- Simple orchestration needs

**Configuration:**
```json
{
  "pattern": "sequential",
  "orchestration": {
    "pattern": "linear",
    "on_stage_failure": "stop_workflow"
  }
}
```

**Pros:**
- Simple to understand and debug
- Predictable execution flow
- Lower latency (no retries)
- Easy to trace errors to specific stages

**Cons:**
- No quality refinement
- Single point of failure per stage
- Cannot recover from validation failures

**Best Practices:**
- Use for well-defined transformations
- Ensure each stage has clear input validation
- Add timeout handling per stage
- Log intermediate outputs for debugging

---

### 3. parallel (Parallel Execution Workflow)

**Description:** Multiple stages execute concurrently, then results are aggregated.

**Structure:**
```
              ┌→ Stage 1A ┐
Input → Fork ─┼→ Stage 1B ┼→ Aggregator → Output
              └→ Stage 1C ┘
```

**Characteristics:**
- **Concurrent execution**: Stages run in parallel
- **Independent processing**: Stages don't depend on each other
- **Aggregation**: Results combined after all complete
- **Performance**: Faster than sequential for independent tasks

**Use Cases:**
- Multiple independent analyses
- Parallel data processing
- A/B testing workflows
- Consensus-based validation

**Configuration:**
```json
{
  "pattern": "parallel",
  "orchestration": {
    "pattern": "concurrent",
    "aggregation_strategy": "merge_results",
    "wait_for_all": true
  }
}
```

**Pros:**
- Reduced total latency
- Independent failure isolation
- Natural for embarrassingly parallel tasks
- Can implement consensus logic

**Cons:**
- More complex orchestration
- Higher resource usage (concurrent API calls)
- Aggregation logic can be complex
- Race conditions possible

**Best Practices:**
- Ensure stages are truly independent
- Implement timeout for slowest stage
- Define clear aggregation rules
- Handle partial failures gracefully

---

### 4. custom (Custom Orchestration Pattern)

**Description:** User-defined orchestration logic that doesn't fit standard patterns.

**Structure:**
```
User-specified DAG (Directed Acyclic Graph)
```

**Characteristics:**
- **Flexible**: Any valid DAG structure
- **Conditional routing**: Stages can conditionally trigger others
- **Dynamic**: Runtime decisions affect flow
- **Complex**: Requires careful design

**Use Cases:**
- Complex business logic with conditionals
- Dynamic workflows based on runtime data
- Multi-path decision trees
- Advanced orchestration needs

**Configuration:**
```json
{
  "pattern": "custom",
  "orchestration": {
    "pattern": "dag",
    "conditional_logic": true,
    "stage_dependencies": {
      "stage-2": ["stage-1"],
      "stage-3": ["stage-1"],
      "stage-4": ["stage-2", "stage-3"]
    }
  }
}
```

**Pros:**
- Maximum flexibility
- Can model any business process
- Supports complex decision logic

**Cons:**
- High complexity
- Harder to debug
- Requires thorough testing
- Potential for circular dependencies

**Best Practices:**
- Draw workflow diagram before implementation
- Validate DAG for cycles
- Test all conditional branches
- Document decision logic clearly

---

## Pattern Selection Guide

### Decision Tree:

1. **Do you need quality validation with feedback loops?**
   - Yes → Use **stg-val-wkf**
   - No → Continue

2. **Are tasks independent and can run concurrently?**
   - Yes → Use **parallel**
   - No → Continue

3. **Is it a simple, linear transformation pipeline?**
   - Yes → Use **sequential**
   - No → Use **custom**

### Pattern Characteristics Comparison:

| Pattern      | Complexity | Latency | Quality | Flexibility | Use Case                  |
|--------------|-----------|---------|---------|-------------|---------------------------|
| stg-val-wkf  | Medium    | High    | High    | Medium      | Quality-critical outputs  |
| sequential   | Low       | Low     | Medium  | Low         | Simple transformations    |
| parallel     | Medium    | Low     | Medium  | Medium      | Independent processing    |
| custom       | High      | Varies  | Varies  | High        | Complex business logic    |

---

## Advanced Patterns (Future)

### Conditional Routing
Route to different stages based on runtime data:
```
Stage 1 → Classifier → [Route A | Route B | Route C] → Aggregator
```

### Scatter-Gather
Partition input, process in parallel, gather results:
```
Input → Partition → [Process 1..N] → Gather → Output
```

### Saga Pattern
Long-running transactions with compensation:
```
Stage 1 → Stage 2 → Stage 3
  ↓         ↓         ↓
Undo 1 ← Undo 2 ← Undo 3 (if failure)
```

### Human-in-the-Loop
Pause workflow for human approval:
```
Stage 1 → Human Review → [Approve → Stage 2 | Reject → Stage 1]
```

---

## Pattern Anti-Patterns

### Things to Avoid:

1. **Deeply Nested Loops**
   - More than 2 levels of feedback loops
   - Can cause exponential attempts

2. **Circular Dependencies**
   - Stage A depends on B, B depends on A
   - Causes deadlock

3. **Overuse of Custom**
   - Using custom pattern for simple sequential flows
   - Adds unnecessary complexity

4. **No Max Attempts**
   - Infinite loops on validation failure
   - Always set max_total_attempts

5. **Tight Coupling**
   - Stages directly referencing each other's internals
   - Use contracts and data mapping

6. **Synchronous Heavy Processing**
   - Blocking on long-running tasks
   - Use async patterns for >30s operations
