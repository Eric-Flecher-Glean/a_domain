---
title: "Technical Specification: ddd-make-align"
version: 1.0
date: 2026-01-22
status: draft
purpose: "Documentation for Technical Specification: ddd-make-align"
---

# Technical Specification: ddd-make-align

**Prompt Name:** DDD Make Alignment
**Short Name:** `ddd-make-align`
**Version:** 1.0
**Stateful:** Yes
**SDLC Subdomain:** Planning

---

## 1. Purpose & Objectives

### Primary Goal

Align all make commands in the repository to Domain-Driven Design (DDD) bounded contexts, strategic layers, and domain entities. Extend MAKE_COMMAND_REGISTRY.yaml with DDD metadata and update architecture documentation with executable command references.

### Key Objectives

1. **Context Mapping** - Map each command to one bounded context
2. **Layer Assignment** - Classify as CORE/SUPPORTING/GENERIC
3. **Entity Linking** - Associate commands with domain entities
4. **Intent Documentation** - Document WHY each command belongs to its context
5. **Bidirectional Traceability** - Commands ↔ Architecture docs

---

## 2. Input/Output Schemas

### Input Sources

| Source Type | Description | Default Path |
|-------------|-------------|--------------|
| Make Registry | Existing command registry | `MAKE_COMMAND_REGISTRY.yaml` |
| Architecture Doc | DDD architecture reference | `docs/ARCHITECTURE_DDD.md` |
| Implementation Backlog | Story references | `IMPLEMENTATION_BACKLOG.yaml` |

### Input Format (Existing Registry Entry)

```yaml
domains:
  spike_development:
    commands:
      - name: spike07-extract-live
        target: extract-live
        file: spikes/spike-07-.../Makefile
        description: "Extract work units from live MCP data"
        dependencies: []
        backlog_refs:
          - "P0-F1-001"
```

### Output Schema (Extended Registry Entry)

```yaml
# NEW TOP-LEVEL SECTION
ddd_metadata:
  version: 1.0.0
  last_aligned: "2026-01-21T10:30:00Z"
  alignment_mode: bootstrap | incremental | validation

  bounded_contexts:
    work_unit_synthesis:
      description: "Groups events into work units via configurable strategies"
      strategic_layer: CORE
      domain_entities: [WorkUnit]
      command_count: 28
      pattern_rules: ["spike07-.*-live$", "assemble$"]

  strategic_layers:
    CORE:
      description: "Differentiating domain capabilities"
      expected_coverage: "60-70%"
      actual_coverage: "63%"
      command_count: 89

  manual_review_queue:
    - command: baseline-compare
      suggested_context: work_classification
      rationale: "Baseline comparison is classification concern"
      confidence: 0.72

  drift_alerts:
    - command: some-command
      current_context: context_a
      expected_context: context_b
      severity: MEDIUM

# EXTENDED COMMAND ENTRIES
domains:
  spike_development:
    commands:
      - name: spike07-extract-live
        # ... existing fields preserved ...

        # NEW DDD FIELDS:
        bounded_context: work_unit_synthesis
        domain_entity: WorkUnit
        strategic_layer: CORE
        intent: "Extracts work units from live Glean MCP data by querying user_activity and grouping events temporally"
        ddd_confidence: HIGH
```

---

## 3. Dependencies

### Required Inputs

| Dependency | Type | Description |
|------------|------|-------------|
| Make Registry | File | `MAKE_COMMAND_REGISTRY.yaml` |
| DDD Reference | Knowledge | Bounded context definitions |

### Runtime Dependencies

| Dependency | Purpose |
|------------|---------|
| `rep-mak-reg` | Base registry structure |
| YAML Parser | Read/write registry |

### Downstream Consumers

| Consumer | Purpose |
|----------|---------|
| Architecture Docs | References make commands |
| Governance System | Validates DDD alignment |
| Developers | Understands command purpose |

---

## 4. Execution Modes

### Bootstrap Mode

**Trigger:** Registry lacks `ddd_metadata` section

**Actions:**
1. Create complete `ddd_metadata` section
2. Define all 8 bounded contexts
3. Auto-map commands using pattern matching (target: 80% HIGH confidence)
4. Create manual review queue for low-confidence items
5. Document intent for CORE/SUPPORTING commands
6. Generate comprehensive report

### Incremental Mode

**Trigger:** `ddd_metadata` exists AND new commands detected

**Actions:**
1. Detect new commands since last alignment
2. Auto-map new commands to contexts
3. Update command counts in metadata
4. Validate strategic layer distribution
5. Generate incremental report

### Validation Mode

**Trigger:** Explicit validation request

**Actions:**
1. Verify 100% command coverage
2. Check strategic layer distribution against targets
3. Validate intent documentation completeness
4. Verify domain entity references
5. Detect alignment drift
6. Generate validation report

---

## 5. DDD Reference Architecture

### Bounded Contexts

| Context | Layer | Domain Entities | Pattern Rules |
|---------|-------|-----------------|---------------|
| `activity_ingestion` | CORE | NormalizedEvent | `mcp-snapshot.*`, `work-unit-discovery` |
| `work_unit_synthesis` | CORE | WorkUnit | `spike07-.*-live$`, `assemble$`, `dedup$` |
| `work_classification` | CORE | WorkUnitClassification | `.*phase2.*`, `classify$` |
| `knowledge_labor_metrics` | CORE | MetricSlice | `baseline.*`, `metrics.*` |
| `validation_experimentation` | SUPPORTING | EvaluationResult, ExperimentConfig | `test-.*`, `validate.*` |
| `reporting_analytics` | SUPPORTING | Report, ClientJourney | `.*report.*`, `journey.*` |
| `feedback_labeling` | SUPPORTING | FeedbackLabel, LabeledDataset | `label.*`, `feedback.*` |
| `identity_permissions` | GENERIC | User, Team (external) | (none) |

### Strategic Layer Rules

| Pattern | Layer |
|---------|-------|
| `clean$`, `help$`, `lint$`, `format$`, `docs$` | GENERIC |
| `session-.*`, `backlog-.*`, `artifact.*`, `governance.*` | SUPPORTING |
| All others not matching above | CORE |

---

## 6. Usage Examples

### Example 1: Bootstrap Alignment

**Prompt:**
```
Run DDD alignment in bootstrap mode to map all make commands to bounded contexts.
```

**Expected Output:**

```yaml
ddd_metadata:
  version: 1.0.0
  last_aligned: "2026-01-21T10:30:00Z"
  alignment_mode: bootstrap

  bounded_contexts:
    work_unit_synthesis:
      strategic_layer: CORE
      command_count: 28
      # ...

  strategic_layers:
    CORE:
      actual_coverage: "63%"
      command_count: 89
    SUPPORTING:
      actual_coverage: "32%"
      command_count: 45
    GENERIC:
      actual_coverage: "5%"
      command_count: 8
```

### Example 2: Validation

**Prompt:**
```
Validate DDD alignment and report any drift or missing documentation.
```

**Expected Report:**

```markdown
## Validation Results
- ✅ Coverage Completeness: 142/142 commands mapped
- ✅ Strategic Distribution: All layers within range
- ⚠️  Intent Documentation: 2 CORE commands missing intent
- ⚠️  Drift Detected: baseline-compare may belong in work_classification
```

---

## 7. Integration Points

### Integration with rep-mak-reg

```yaml
# ddd-make-align extends rep-mak-reg output
workflow:
  1. rep-mak-reg creates base MAKE_COMMAND_REGISTRY.yaml
  2. ddd-make-align adds ddd_metadata section
  3. ddd-make-align extends each command with DDD fields
  4. Both prompts preserve each other's fields
```

### Integration with Architecture Docs

```yaml
# DDD alignment updates architecture documentation
workflow:
  1. ddd-make-align maps commands to contexts
  2. Updates docs/ARCHITECTURE_DDD.md with command references
  3. Creates MAKE_COMMANDS_BY_CONTEXT.md cheat sheet
```

---

## 8. Success Criteria

### Validation Rules

| Rule | Description |
|------|-------------|
| Coverage Complete | 100% of commands have bounded_context |
| Distribution Valid | Layer distribution within expected ranges |
| Intent Documented | All CORE/SUPPORTING have intent field |
| Entities Valid | All domain_entity references exist |
| No Orphans | No commands without context (except specific cases) |
| Confidence Transparent | All auto-mapped have ddd_confidence |
| Changelog Present | Every run adds changelog entry |
| Idempotent | Validation mode produces identical results on reruns |

### Quality Metrics

| Metric | Target |
|--------|--------|
| AUTO_MAP_RATE | ≥80% HIGH confidence |
| CORE_COVERAGE | 60-70% |
| SUPPORTING_COVERAGE | 25-35% |
| GENERIC_COVERAGE | 5-10% |
| INTENT_COMPLETENESS | 100% for CORE/SUPPORTING |

---

## 9. Constraints

1. **Additive Only** - Never delete existing functional domain organization
2. **Backlog Preservation** - Preserve all backlog_refs fields
3. **Single Context** - Each command belongs to exactly ONE bounded context
4. **Intent Required** - CORE/SUPPORTING commands MUST have intent
5. **Distribution Targets** - Must be within expected ranges
6. **Valid References** - Domain entities must be defined
7. **Structure Preservation** - Maintain YAML formatting

---

## 10. Error Handling

| Error Condition | Handling |
|-----------------|----------|
| Ambiguous context | Add to manual_review_queue with suggestions |
| Multiple context match | Assign to primary context, document in intent |
| Missing pattern rules | Apply strategic layer rules as fallback |
| Distribution out of range | Flag for review, suggest remapping |
| Invalid entity reference | Report as validation error |

---

## Appendix: Confidence Scoring

### Confidence Levels

| Level | Score Range | Description |
|-------|-------------|-------------|
| HIGH | ≥0.85 | Strong pattern match, auto-assign |
| MEDIUM | 0.70-0.84 | Moderate match, review recommended |
| LOW | <0.70 | Weak match, manual review required |

### Scoring Factors

| Factor | Weight | Description |
|--------|--------|-------------|
| Pattern Match | 40% | Matches context pattern rules |
| Layer Rules | 30% | Matches strategic layer patterns |
| Backlog Context | 20% | Related story context |
| Name Analysis | 10% | Command name semantic analysis |
