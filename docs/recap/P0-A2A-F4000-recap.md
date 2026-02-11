# P0-A2A-F4000: Requirements-to-Design Pipeline - Feature Recap

**Story ID:** P0-A2A-F4000
**Priority:** P0
**Status:** Requirements Complete
**Created:** 2026-02-11
**Requirements Chat:** ✅ Complete

---

## Overview

Comprehensive requirements gathering and design for an automated pipeline that transforms customer conversations (Gong sales calls) and design specifications (Figma files) into structured SDLC implementation stories. Hybrid LLM + rule-based extraction with human review gates ensures quality while dramatically reducing manual work.

---

## Requirements Chat Session Summary

### Session Format
Interactive requirements gathering using `/sdlc.new-feature-chat` command following the established P0-A2A-F* requirements story pattern.

### Key Questions Answered

**Q1: Gong Transcript Extraction Strategy**
- **Answer:** C) Hybrid Approach (LLM + Rules) - RECOMMENDED
- **Rationale:** LLM for nuanced extraction, rules for validation, confidence scoring for quality gates

**Q2: Figma Design Parsing Depth**
- **Answer:** D) Design System Integration - RECOMMENDED
- **Rationale:** Component-level extraction + design tokens + annotations, links to design system

**Q3: SDLC Story Generation Format**
- **Answer:** C) Epic → Stories → Tasks - RECOMMENDED
- **Rationale:** Matches PM mental model, implementable stories, granular tasks

**Q4: Requirement Quality Scoring**
- **Answer:** D) Composite Priority Score - RECOMMENDED
- **Rationale:** Data-driven formula (impact, urgency, confidence, completeness) with executive weighting

**Q5: Pipeline Orchestration & Human-in-Loop**
- **Answer:** B) Review Before Generation - RECOMMENDED
- **Rationale:** Quality gate prevents hallucinated stories, builds trust, enables gradual automation

---

## Problem Statement

**Current Pain:**
- Manual extraction from Gong transcripts: 4-6 hours per call
- Inconsistent requirement quality and prioritization
- Figma designs not linked to implementation stories
- Lost context between customer conversation → design → code
- Slow time-to-implementation (weeks between call → story → dev)

**Impact:**
- Sales deals delayed waiting for product confirmation
- Engineering builds wrong features due to incomplete requirements
- Design rework due to misunderstood requirements
- Product team bottleneck (doesn't scale)

---

## Solution Architecture

### System Overview

**End-to-End Pipeline:**
```
Gong Call → Extract Requirements → Score Quality → Human Review →
Generate Stories → Validate → Commit to Backlog → Notify
```

**Key Components:**
1. **Gong Extraction Service** (LLM + Rules)
2. **Figma Parsing Service** (REST API)
3. **Quality Scoring Engine** (Composite formula)
4. **Story Generation Engine** (Epic → Stories → Tasks)
5. **Human Review Queue** (UI/API)
6. **Pipeline Orchestrator** (Celery)
7. **Notification Service** (Slack/Email)

### Extraction Strategy: Hybrid LLM + Rules

**LLM Component (Claude Sonnet 4.5):**
- Extract requirement text, type, speaker, timestamp
- Identify priority signals (urgency words, timelines, executive mentions)
- Extract entities (systems, features, metrics)
- Calculate initial confidence score

**Rule-Based Component:**
- Validate urgency keywords (critical, urgent, asap → high)
- Regex for timelines ("within 2 weeks" → high urgency)
- Executive role detection (CTO, CEO → 2x weight)
- Confidence scoring (speaker authority × clarity × corroboration)

**Output:** `requirements.yaml` with structured requirements

### Figma Parsing: Design System Aware

**Extraction:**
- Components (buttons, inputs, cards, screens)
- Properties (dimensions, colors, typography, spacing)
- Design tokens (color palette, type scale, spacing system)
- Annotations (accessibility, implementation notes)
- Component hierarchy (parent-child relationships)

**Enhancement:**
- User story hints from component purpose
- Implementation notes from designer annotations
- Complexity estimation from component count/variants

**Output:** `design-spec.yaml` with full component specifications

### Quality Scoring: Composite Priority Formula

```python
priority_score = (
    business_impact * 0.4 +     # Revenue risk, customer tier, strategic value (0-10)
    urgency * 0.3 +              # Timeline, urgency keywords, pain level (0-10)
    confidence * 10 * 0.2 +      # Speaker authority, clarity (0-1.0)
    completeness / 10 * 0.1      # Has AC, timeline, metrics (0-100)
) * executive_multiplier         # 2x if C-level speaker

P0: score >= 8.0
P1: score >= 5.0
P2: score < 5.0
```

**Inputs:**
- Business Impact: Revenue at risk, customer tier, strategic alignment
- Urgency: Timeline pressure, urgency keywords, pain level
- Confidence: Speaker authority, clarity, corroboration, source quality
- Completeness: Has acceptance criteria, timeline, success metrics, dependencies

### Story Generation: Epic → Stories → Tasks

**Epic Generation:**
- Group related requirements by business goal, system, or Figma flow
- Create feature-level Epic story
- Link all child stories

**Story Generation:**
- One story per screen or API endpoint
- Title: "{{action_verb}} {{component_name}}"
- Description: Requirement text + Figma URL + Gong call link
- Tasks: From Figma implementation_notes + component hierarchy
- Acceptance Criteria: From design annotations + requirement text
- Effort: Component count × 2pts + integration/validation penalties

**Task Generation:**
- Set up design tokens (if needed)
- Implement each component
- Add variants
- Integrate with APIs
- Add validation

---

## Key Design Decisions

### 1. Hybrid LLM + Rules Extraction

**Decision:** Combine LLM understanding with rule-based validation

**Pros:**
- LLM: Natural language understanding, context awareness, nuanced extraction
- Rules: Deterministic, fast, transparent, no cost
- Hybrid: Best of both worlds with quality gates

**Cons:**
- More complexity than pure LLM
- Rules require maintenance

**Why chosen:** Risk mitigation (rules catch LLM errors), cost optimization (rules are free), trust building (transparent validation)

### 2. Human Review Before Generation

**Decision:** Mandatory human approval before story generation (Phase 1)

**Pros:**
- Prevents hallucinated requirements from polluting backlog
- Human judgment on priority and scope
- Builds trust in automated extraction
- Feedback loop for model improvement

**Cons:**
- Manual bottleneck
- Slows pipeline

**Why chosen:** Phase 1 focus on quality over speed. Phase 2 will auto-approve high-confidence (>0.9) requirements.

### 3. Event-Driven Pipeline Architecture

**Decision:** Async task queue (Celery) vs synchronous REST API

**Pros:**
- Handles long-running tasks (2+ min extraction)
- Resilience (failed stages can retry)
- Scalability (add workers as needed)
- Natural "wait state" for human review
- Clear observability (state at each stage)

**Cons:**
- More complex than synchronous
- Requires Redis/queue infrastructure

**Why chosen:** Long extraction times make sync APIs impractical. Human review requires async by nature.

### 4. PostgreSQL + File Storage

**Decision:** Database for structured data, YAML files for artifacts

**Pros:**
- PostgreSQL: Rich querying, ACID, JSONB for flexible schemas
- YAML files: Version control friendly, human-readable, Git-trackable

**Cons:**
- Dual storage adds complexity
- Potential sync issues

**Why chosen:** Each storage type optimized for its use case. Database for operational queries, files for artifact versioning.

### 5. Epic → Stories → Tasks Hierarchy

**Decision:** Three-level story structure

**Pros:**
- Epic: Feature-level PM thinking
- Story: Implementable units (one screen/API)
- Task: Granular work items (half-day chunks)
- Matches existing IMPLEMENTATION_BACKLOG.yaml pattern

**Cons:**
- More overhead than flat stories

**Why chosen:** Matches PM mental model, provides feature context, aligns with existing backlog structure.

---

## Functional Requirements Summary

### 10 Core Requirements (P0-P2)

**FR-1: Gong Transcript Extraction (P0)**
- Hybrid LLM + rules
- Extract requirements in < 2 minutes per 30-min call
- Confidence >= 80% accuracy vs manual review

**FR-2: Figma Design Spec Parsing (P0)**
- Extract components, design tokens, annotations
- Parse 50 components in < 30 seconds
- 100% property extraction

**FR-3: Requirement Quality Scoring (P0)**
- Composite formula (impact, urgency, confidence, completeness)
- Priority mapping (P0/P1/P2)
- >= 85% priority accuracy

**FR-4: Epic and Story Generation (P0)**
- Group requirements → Epic
- Generate stories (one per screen/API)
- Tasks from implementation notes
- ACs from annotations

**FR-5: Human Review Queue (P0)**
- UI for reviewing extracted requirements
- Show confidence scores, priority signals
- Edit/approve/reject workflow
- Low-confidence flagging (< 0.7)

**FR-6: Pipeline Orchestration (P0)**
- End-to-end pipeline coordination
- Async task queue (Celery)
- Error handling and retry
- State persistence

**FR-7: Traceability and Audit Trail (P1)**
- Link story → Gong call → timestamp
- Link story → Figma component
- Audit log for all actions
- Review decision tracking

**FR-8: Figma-to-Story Component Linking (P1)**
- Figma URLs with node_id in story tasks
- design-spec.yaml as artifact
- Implementation checklist from annotations

**FR-9: Requirement Deduplication (P2)**
- Semantic similarity detection
- Flag duplicates (>80% similarity)
- Merge workflow

**FR-10: Feedback Loop and Model Improvement (P2)**
- Track approval rates
- Track edit distance
- Generate training data
- Report quality metrics

---

## Success Metrics

**Performance:**
- 80% reduction in time from call → backlog (6 hours → 1 hour)
- < 2 minutes extraction per 30-min call
- < 5 minutes end-to-end pipeline (excluding human review)

**Accuracy:**
- 90%+ requirement extraction accuracy
- 85%+ priority scoring accuracy (P0/P1/P2 correct)
- 95%+ story schema validation pass rate

**Quality:**
- 100% traceability (every story links to Gong/Figma)
- Review approval rate >= 90%
- Confidence scoring accuracy >= 80%

---

## Technical Stack

**Backend:**
- Python 3.11 (FastAPI, Celery)
- Claude Sonnet 4.5 (LLM extraction)
- PostgreSQL 15 (state storage)
- Redis 7 (task queue)

**Frontend:**
- React 18 (review UI)
- FastAPI (review API)

**APIs:**
- Gong API (OAuth 2.0)
- Figma API (Bearer token)
- Glean MCP (mcp__glean__chat tool)

**Infrastructure:**
- Docker containers
- Celery worker pool
- S3/local file storage

---

## Implementation Approach

### Phase 1: MVP (Weeks 1-4)

**Stories:**
- **P0-A2A-F4001:** Gong Extraction Service (Hybrid LLM + Rules)
- **P0-A2A-F4002:** Figma Parsing Service (Design System Aware)
- **P1-A2A-F4003:** Story Generation Engine (Epic → Stories → Tasks)
- **P1-A2A-F4004:** Human Review Queue (CLI MVP)

**Deliverables:**
- End-to-end pipeline (manual review)
- CLI review interface
- Generated stories in backlog
- Basic notifications

### Phase 2: UI & Automation (Weeks 5-8)

**Stories:**
- Web-based review UI
- Auto-approve high-confidence (>0.9)
- Batch review support
- Enhanced notifications

### Phase 3: Optimization (Weeks 9-12)

**Stories:**
- Requirement deduplication
- Feedback loop and metrics
- Performance optimization
- ML model fine-tuning

---

## Deliverables Created

### 1. Requirements Document (`output/requirements/requirements-to-design-requirements.yaml`)
- 10 functional requirements (FR-1 through FR-10)
- 5 non-functional requirements (Performance, Accuracy, Reliability, Scalability, Maintainability)
- 6 user stories with acceptance criteria
- Technical requirements (API integrations)
- Success metrics and risks

### 2. Design Specification (`output/figma/requirements-to-design-design.yaml`)
- System architecture (event-driven pipeline)
- 7 component specifications
  - Gong Extraction Service
  - Figma Parsing Service
  - Quality Scoring Engine
  - Story Generation Engine
  - Human Review Queue
  - Pipeline Orchestrator
  - Notification Service
- API specifications (Gong, Figma, Claude)
- Database schema
- Deployment architecture

### 3. Architecture Document (`docs/architecture/requirements-to-design-architecture.md`)
- System overview and high-level architecture
- Component architecture with detailed diagrams
- Data flow and state transitions
- API integrations (Gong, Figma, Claude)
- Data model (PostgreSQL schema)
- Processing pipeline orchestration
- Quality scoring formulas
- Story generation algorithms
- Design rationale for key decisions

### 4. Feature Recap (`docs/recap/P0-A2A-F4000-recap.md`)
- This document

---

## Dependencies

**External APIs:**
- Gong API access and credentials
- Figma API personal access token
- Glean MCP server configuration (authenticated session)

**Internal:**
- Existing IMPLEMENTATION_BACKLOG.yaml structure
- requirements.yaml schema (existing)
- design-spec.yaml schema (existing)

**Infrastructure:**
- PostgreSQL database
- Redis queue
- S3 or local file storage
- Celery worker environment

---

## Risks & Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| LLM hallucinations creating invalid requirements | High | Medium | Confidence scoring, human review, rule-based validation |
| Gong API changes breaking extraction | High | Low | Version API calls, abstraction layer, monitoring |
| Figma design drift (designs change after story created) | Medium | High | Version design specs, drift detection, re-extraction |
| Poor priority scoring → wrong P0/P1/P2 | High | Medium | Calibration with historical data, PM override |
| Human review bottleneck slowing pipeline | Medium | Medium | Batch review UI, auto-approve high-confidence (Phase 2) |

---

## Out of Scope (Phase 1)

- Automated story implementation (still manual)
- Real-time Gong call extraction during call
- Figma design generation from requirements
- Automated testing of generated stories
- Multi-language support (English only)
- Integration with Jira, Linear, or other PM tools
- Bi-directional sync (update Figma from code)

---

## Future Enhancements

- **Phase 2:** Auto-approve high-confidence requirements (>0.9)
- **Phase 2:** Real-time extraction during Gong call
- **Phase 3:** Bi-directional sync (update Figma from code changes)
- **Phase 3:** ML model fine-tuning on feedback data
- **Phase 4:** Cross-call requirement aggregation
- **Phase 4:** Automated story refinement based on implementation feedback

---

## Next Steps

### Immediate
1. ✅ Review requirements, design, and architecture documents
2. ✅ Get stakeholder approval
3. Generate implementation stories (P0-A2A-F4001 through P1-A2A-F4004)
4. Prioritize implementation (coordinate with A2A platform)

### Implementation Phase
1. Build Gong Extraction Service (hybrid LLM + rules)
2. Build Figma Parsing Service (design system aware)
3. Implement quality scoring engine
4. Build story generation engine
5. Create CLI review interface (MVP)
6. Integrate pipeline orchestration
7. Test end-to-end

### Validation
1. Run functional tests on each component
2. Test with real Gong calls and Figma files
3. Validate generated stories against schema
4. Manual review of extraction accuracy
5. Performance benchmarks

---

## Integration with A2A Platform

**Leverages:**
- ProtocolBrokerAgent: Message routing between services
- DatasetDiscoveryAgent: If data requirements detected in Gong calls
- JourneyCoordinatorAgent: Link generated stories to customer journey stage

**Extends:**
- New agent: RequirementsExtractorAgent
- New agent: DesignParserAgent
- New agent: StoryGeneratorAgent

**Pattern Consistency:**
- Follows A2A agent protocol
- Event-driven architecture matches A2A platform
- TDD approach with functional test plans

---

## Conclusion

P0-A2A-F4000 requirements chat successfully completed. Comprehensive requirements, design, and architecture documents created for automated Requirements-to-Design Pipeline. System ready for implementation story generation and development.

**Key Innovation:**
Hybrid LLM + rule-based extraction with human review gates provides the right balance of automation, quality, and trust-building for transforming customer conversations and designs into implementation-ready stories.

**Status:** ✅ Requirements Complete → Ready for Implementation Planning

---

**Related Artifacts:**
- `output/requirements/requirements-to-design-requirements.yaml` (10 FRs, 5 NFRs, 6 user stories)
- `output/figma/requirements-to-design-design.yaml` (7 component specs, full system design)
- `docs/architecture/requirements-to-design-architecture.md` (Complete architecture)
- `IMPLEMENTATION_BACKLOG.yaml` (Story P0-A2A-F4000 to be updated)
