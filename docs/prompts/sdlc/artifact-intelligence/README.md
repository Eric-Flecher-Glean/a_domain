---
title: "Artifact Intelligence Domain"
version: 1.0
date: 2026-01-22
status: draft
purpose: "Documentation for Artifact Intelligence Domain"
---

# Artifact Intelligence Domain

**SDLC Subdomain**: Artifact Intelligence
**Bounded Context**: artifact-intelligence
**Status**: NEW - Active Development

---

## Overview

The Artifact Intelligence domain provides automated discovery, processing, and requirements extraction from Glean-indexed artifacts such as PRDs, wireframes, API specifications, and design documents.

This domain bridges the gap between unstructured knowledge artifacts and structured backlog items by:

1. **Searching** Glean for user-specified artifact types
2. **Processing** artifacts to extract requirements and dependencies
3. **Refining** requirements through cross-artifact analysis
4. **Maintaining** open questions for user clarification
5. **Incorporating** user feedback into requirements
6. **Creating** implementation stories with acceptance criteria
7. **Prioritizing** stories and integrating with the backlog

---

## Prompts

| Prompt | Purpose | Make Target | Execution Mode |
|--------|---------|-------------|----------------|
| artifact-search | Discover artifacts in Glean | `make artifact-search` | Interactive |
| artifact-process | Extract requirements | `make artifact-process` | Autonomous |
| artifact-refine | Cross-artifact analysis | `make artifact-refine` | Hybrid |
| question-maintain | Track open questions | `make question-maintain` | Interactive |
| feedback-incorporate | Integrate user feedback | `make feedback-incorporate` | Autonomous |
| story-refine | Create implementation stories | `make story-refine` | Autonomous |
| backlog-prioritize | Prioritize and add to backlog | `make backlog-prioritize` | Hybrid |

---

## Workflow

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                     ARTIFACT INTELLIGENCE WORKFLOW                            │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│   USER INPUT                                                                  │
│       │                                                                       │
│       ▼                                                                       │
│   ┌─────────────────┐    Search Glean for PRDs,                              │
│   │ artifact-search │    wireframes, API specs, etc.                          │
│   └────────┬────────┘                                                         │
│            │                                                                  │
│            ▼                                                                  │
│   ┌─────────────────┐    Extract functional requirements,                     │
│   │ artifact-process│    NFRs, dependencies, questions                        │
│   └────────┬────────┘                                                         │
│            │                                                                  │
│            ├───────────────────┐                                              │
│            ▼                   ▼                                              │
│   ┌─────────────────┐  ┌─────────────────┐                                   │
│   │ artifact-refine │  │question-maintain│  Manage open                       │
│   │ Cross-analysis  │  │  Track answers  │  questions                         │
│   └────────┬────────┘  └────────┬────────┘                                   │
│            │                    │                                             │
│            │                    ▼                                             │
│            │           ┌─────────────────┐                                   │
│            │           │feedback-        │  Apply user answers                │
│            │           │incorporate      │  to requirements                   │
│            │           └────────┬────────┘                                   │
│            │                    │                                             │
│            ▼◄───────────────────┘                                             │
│   ┌─────────────────┐    Create user stories with                             │
│   │  story-refine   │    acceptance criteria                                  │
│   └────────┬────────┘                                                         │
│            │                                                                  │
│            ▼                                                                  │
│   ┌─────────────────┐    Apply WSJF prioritization,                           │
│   │backlog-prioritize│   add to backlog                                       │
│   └────────┬────────┘                                                         │
│            │                                                                  │
│            ▼                                                                  │
│   IMPLEMENTATION_BACKLOG.yaml                                                 │
│                                                                               │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## Glean MCP Integration

This domain relies on Glean MCP tools for artifact discovery and analysis:

### Primary Tools

| Tool | Used By | Purpose |
|------|---------|---------|
| `mcp__glean_default__search` | artifact-search | Primary document discovery |
| `mcp__glean_default__read_document` | artifact-process | Full content retrieval |
| `mcp__glean_default__chat` | artifact-refine | AI-powered synthesis |
| `mcp__glean_default__user_activity` | artifact-search | Activity-based discovery |

### Artifact Type Patterns

| Type | Search Pattern | Typical Sources |
|------|---------------|-----------------|
| `prd` | PRD, product requirements | Google Docs, Confluence |
| `wireframe` | wireframe, mockup, figma | Figma, Google Drive |
| `api-spec` | API spec, swagger, openapi | GitHub, Confluence |
| `design-doc` | design doc, architecture | Google Docs, Confluence |
| `tech-spec` | tech spec, RFC | Google Docs, Confluence |
| `user-story` | user story, acceptance criteria | Jira, Confluence |

---

## State Files

| File | Purpose | Schema |
|------|---------|--------|
| `artifacts/discovered_index.yaml` | Catalog of discovered artifacts | artifact-index-schema |
| `artifacts/extracted_requirements.yaml` | Raw extracted requirements | requirements-schema |
| `artifacts/refined_requirements.yaml` | Consolidated requirements | requirements-schema |
| `artifacts/open_questions.yaml` | Question tracking | questions-schema |
| `artifacts/draft_stories.yaml` | Story drafts | stories-schema |
| `artifacts/workflow_state.yaml` | Workflow progress | workflow-schema |

---

## Usage Examples

### Complete Workflow

```bash
# 1. Search for PRDs from the last month
make artifact-search ARTIFACT_TYPE=prd OWNER=me DATE_RANGE=past_month

# 2. Process discovered artifacts
make artifact-process

# 3. Refine with cross-artifact analysis
make artifact-refine

# 4. Review open questions
make question-maintain ACTION=list

# 5. Answer blocking questions
make question-maintain ACTION=answer QUESTION_ID=Q-001 ANSWER="200ms p95 response time"

# 6. Incorporate feedback
make feedback-incorporate FEEDBACK_SOURCE=question-answer QUESTION_ID=Q-001

# 7. Create implementation stories
make story-refine

# 8. Prioritize and add to backlog
make backlog-prioritize ALGORITHM=wsjf
```

### Claude Code Integration

Using Claude Code commands for interactive workflow:

```
User: /artifact-search prd OWNER=me

Claude: Searching Glean for PRD artifacts...
        [Executes: make artifact-search ARTIFACT_TYPE=prd OWNER=me]

        Discovered 12 PRD artifacts from the past 30 days.

        Would you like me to:
        1. Process these artifacts to extract requirements
        2. Refine the search with additional filters
        3. View the artifact details

User: 1

Claude: Processing artifacts...
        [Executes: make artifact-process]

        Extracted:
        - 34 functional requirements
        - 8 non-functional requirements
        - 5 system dependencies

        Found 7 open questions requiring clarification.

        Run /questions to review them.
```

---

## Exit Codes

| Code | Category | Meaning | Recovery Action |
|------|----------|---------|-----------------|
| 0 | Success | Operation completed | Continue workflow |
| 1 | Validation | Invalid parameters | Fix input and retry |
| 2 | Dependency | Missing prerequisite | Run previous step |
| 3 | Runtime | Execution error | Check logs, retry |
| 10 | Domain | No artifacts found | Refine search |
| 11 | Domain | Blocking questions | Answer questions first |

---

## Observability

### Key Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `artifact_search_count` | counter | Number of searches executed |
| `artifacts_discovered` | counter | Artifacts found |
| `requirements_extracted` | counter | Requirements extracted |
| `questions_open` | gauge | Current open questions |
| `stories_created` | counter | Stories generated |
| `search_latency` | histogram | Search response time |

### SLOs

| Target | Threshold | Window |
|--------|-----------|--------|
| Search latency | p95 < 60s | 1 hour |
| Question resolution | 80% < 48h | 7 days |
| Blocking questions | < 3 | continuous |

---

## Related Documentation

- [SDLC Prompt Domain Index](../SDLC_PROMPT_DOMAIN_INDEX.md)
- [Claude Orchestration Architecture](../../architecture/CLAUDE_ORCHESTRATION_ARCHITECTURE.md)
- [XSD Schema](../../../schema/aflac-prompt-schema.xsd)
- [Integration Guide](../../architecture/INTEGRATION_GUIDE.md)

---

*Created: 2026-01-21 | Domain: artifact-intelligence | Version: 1.0*
