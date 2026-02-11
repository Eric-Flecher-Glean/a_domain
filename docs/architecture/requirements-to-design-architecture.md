# Requirements-to-Design Pipeline Architecture

**Feature ID:** P0-A2A-F4000
**Version:** 1.0.0
**Status:** Architecture Complete
**Last Updated:** 2026-02-11

---

## Executive Summary

This document defines the architecture for an automated pipeline that transforms customer conversations (Gong sales calls) and design specifications (Figma files) into structured SDLC implementation stories. The system uses a hybrid LLM + rule-based extraction approach with human review gates to ensure quality while maintaining efficiency.

### Key Architectural Decisions

- **Pattern:** Event-driven pipeline with async task orchestration
- **Extraction:** Hybrid LLM (Claude Sonnet 4.5) + rule-based validation
- **Review:** Human-in-the-loop before story generation (Phase 1)
- **Storage:** PostgreSQL for state, S3/filesystem for artifacts
- **Deployment:** Containerized microservices

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture Pattern](#architecture-pattern)
3. [Component Architecture](#component-architecture)
4. [Data Flow](#data-flow)
5. [API Integrations](#api-integrations)
6. [Data Model](#data-model)
7. [Processing Pipeline](#processing-pipeline)
8. [Quality Scoring](#quality-scoring)
9. [Story Generation](#story-generation)
10. [Deployment Architecture](#deployment-architecture)
11. [Design Rationale](#design-rationale)

---

## 1. System Overview

### 1.1 Purpose

Automate the requirements-to-implementation flow:
- Extract requirements from Gong sales call transcripts
- Parse Figma design specifications
- Generate SDLC stories with tasks, acceptance criteria, test plans
- Maintain traceability from customer conversation → design → code

### 1.2 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     External Systems                            │
├─────────────────────────────────────────────────────────────────┤
│  Glean MCP                           Figma API                  │
│  (Meetings, Docs, Search, AI)        (Component Detail)         │
└──────┬───────────────────────────────────────┬──────────────────┘
       │                                       │
       ▼                                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Ingestion Layer                             │
├─────────────────────────────────────────────────────────────────┤
│  Glean MCP Client                    Figma Client (Fallback)    │
│  (Primary for all data)                                         │
└──────┬───────────────────────────────────────┬──────────────────┘
       │                                       │
       ▼                                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Processing Layer                             │
├─────────────────────────────────────────────────────────────────┤
│  Requirement       Design Parser    Quality Scorer              │
│  Extractor                                                      │
│  (LLM + Rules)                                                  │
└──────┬─────────────────┬────────────────────┬────────────────────┘
       │                 │                    │
       ▼                 ▼                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Review Layer                               │
├─────────────────────────────────────────────────────────────────┤
│  Review Queue API   Review UI          Approval Engine          │
│  (Human-in-the-Loop)                                            │
└──────┬─────────────────┬────────────────────┬────────────────────┘
       │                 │                    │
       ▼                 ▼                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Generation Layer                              │
├─────────────────────────────────────────────────────────────────┤
│  Story Generator    Epic Builder       Task Creator             │
└──────┬─────────────────┬────────────────────┬────────────────────┘
       │                 │                    │
       ▼                 ▼                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Persistence Layer                             │
├─────────────────────────────────────────────────────────────────┤
│  PostgreSQL         S3/File Storage    IMPLEMENTATION_BACKLOG   │
└─────────────────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Orchestration Layer                            │
├─────────────────────────────────────────────────────────────────┤
│  Pipeline Coordinator   Event Bus      Notification Service     │
└─────────────────────────────────────────────────────────────────┘
```

### 1.3 Key Components

| Component | Responsibility | Technology |
|-----------|---------------|------------|
| **Meeting Extraction Service** | Extract requirements from calls via Glean MCP | Python, Glean MCP |
| **Design Parsing Service** | Parse design specifications via Glean MCP + Figma API | Python, Glean MCP, Figma API |
| **Quality Scoring Engine** | Calculate priority scores | Python |
| **Story Generation Engine** | Generate SDLC stories | Python |
| **Review Queue** | Human approval workflow | FastAPI + React |
| **Pipeline Orchestrator** | Coordinate workflow | Celery |
| **Notification Service** | Alerts and updates | Slack/Email |

---

## 2. Architecture Pattern

### 2.1 Event-Driven Pipeline

**Pattern:** Asynchronous event-driven architecture with task queues

**Characteristics:**
- Loosely coupled services
- Async communication via event bus (Redis/Celery)
- State persistence at each stage
- Retry and error handling built-in

**Benefits:**
- Scalability: Add workers as needed
- Resilience: Failed stages can retry
- Observability: Clear state transitions
- Flexibility: Easy to add new stages

### 2.2 Pipeline Stages

```
[Start] → Extract → Score → Review → Generate → Validate → Commit → Notify → [End]
          ↓         ↓        ↓         ↓         ↓          ↓        ↓
         DB        DB      WAIT       DB        DB         Git      Slack
```

Each stage:
1. Receives input from previous stage
2. Processes data
3. Persists output to database
4. Emits event for next stage
5. Handles errors with retry logic

### 2.3 Human-in-the-Loop Architecture

**Review Gate:** Mandatory human approval before story generation

```
Extract → Score → [QUEUE FOR REVIEW]
                        ↓
                  Human Reviews
                        ↓
                  Approve/Reject
                        ↓
                  Generate → Commit
```

**Implementation:**
- Review items stored in database (`pending_review` state)
- UI polls for pending items
- Reviewer edits/approves/rejects
- Approval triggers next pipeline stage

---

## 3. Component Architecture

### 3.1 Meeting Extraction Service

**Type:** Microservice
**Input:** Meeting query (participants, date, topic)
**Output:** requirements.yaml

#### Architecture

```
┌─────────────────────────────────────────┐
│   Meeting Extraction Service            │
├─────────────────────────────────────────┤
│                                         │
│  ┌─────────────────────────────────┐   │
│  │   Glean MCP Client              │   │
│  │   - meeting_lookup tool         │   │
│  │   - Fetch transcript            │   │
│  └────────┬────────────────────────┘   │
│           │                             │
│           ▼                             │
│  ┌─────────────────────────────────┐   │
│  │   Glean MCP Chat Extractor      │   │
│  │   - AI-powered extraction       │   │
│  │   - Enterprise context aware    │   │
│  │   - Extract: text, type,        │   │
│  │     speaker, signals            │   │
│  └────────┬────────────────────────┘   │
│           │                             │
│           ▼                             │
│  ┌─────────────────────────────────┐   │
│  │   Rule-Based Validator          │   │
│  │   - Urgency keywords            │   │
│  │   - Timeline regex              │   │
│  │   - Executive role detection    │   │
│  └────────┬────────────────────────┘   │
│           │                             │
│           ▼                             │
│  ┌─────────────────────────────────┐   │
│  │   Confidence Scorer             │   │
│  │   - Speaker authority           │   │
│  │   - Clarity score               │   │
│  │   - Corroboration               │   │
│  └────────┬────────────────────────┘   │
│           │                             │
│           ▼                             │
│  ┌─────────────────────────────────┐   │
│  │   Output Formatter              │   │
│  │   - YAML generation             │   │
│  │   - Schema validation           │   │
│  └─────────────────────────────────┘   │
│                                         │
└─────────────────────────────────────────┘
```

#### LLM Prompt Strategy

**Approach:** Structured extraction with explicit schema

```yaml
prompt_template:
  system: |
    You are a requirements analyst. Extract requirements from
    sales call transcripts with high precision.

  user: |
    Extract all requirements from this transcript:

    {{transcript}}

    For each requirement, output JSON:
    {
      "id": "REQ-001",
      "text": "verbatim quote",
      "type": "integration|feature_request|pain_point|constraint",
      "speaker": {"name": "...", "role": "..."},
      "timestamp": "00:15:42",
      "priority_signals": [...],
      "entities": {"systems": [...], "features": [...]}
    }

  temperature: 0.3  # Low for consistency
  max_tokens: 4096
```

### 3.2 Figma Parsing Service

**Type:** Microservice
**Input:** Figma file_id
**Output:** design-spec.yaml

#### Architecture

```
┌─────────────────────────────────────────┐
│     Figma Parsing Service               │
├─────────────────────────────────────────┤
│                                         │
│  ┌─────────────────────────────────┐   │
│  │   Figma API Client              │   │
│  │   - Bearer token auth           │   │
│  │   - Fetch file metadata         │   │
│  │   - Fetch nodes                 │   │
│  └────────┬────────────────────────┘   │
│           │                             │
│           ▼                             │
│  ┌─────────────────────────────────┐   │
│  │   Node Tree Traverser           │   │
│  │   - DFS traversal               │   │
│  │   - Filter by component type    │   │
│  │   - Build hierarchy             │   │
│  └────────┬────────────────────────┘   │
│           │                             │
│           ▼                             │
│  ┌─────────────────────────────────┐   │
│  │   Property Extractor            │   │
│  │   - Dimensions, colors          │   │
│  │   - Typography, spacing         │   │
│  │   - Effects (shadow, radius)    │   │
│  └────────┬────────────────────────┘   │
│           │                             │
│           ▼                             │
│  ┌─────────────────────────────────┐   │
│  │   Annotation Parser             │   │
│  │   - Component descriptions      │   │
│  │   - Implementation notes        │   │
│  │   - User story hints            │   │
│  └────────┬────────────────────────┘   │
│           │                             │
│           ▼                             │
│  ┌─────────────────────────────────┐   │
│  │   Design Token Generator        │   │
│  │   - Color palette               │   │
│  │   - Type scale                  │   │
│  │   - Spacing system              │   │
│  └─────────────────────────────────┘   │
│                                         │
└─────────────────────────────────────────┘
```

### 3.3 Story Generation Engine

**Type:** Service
**Input:** approved_requirements.json + design-spec.yaml
**Output:** generated_stories.yaml

#### Generation Logic

```
┌─────────────────────────────────────────┐
│     Story Generation Engine             │
├─────────────────────────────────────────┤
│                                         │
│  Step 1: Group Requirements → Epic     │
│  ┌─────────────────────────────────┐   │
│  │   Epic Builder                  │   │
│  │   - Group by business goal      │   │
│  │   - Group by Figma flow         │   │
│  │   - Create epic story           │   │
│  └─────────────────────────────────┘   │
│           │                             │
│           ▼                             │
│  Step 2: Epic → Stories                │
│  ┌─────────────────────────────────┐   │
│  │   Story Generator               │   │
│  │   - One story per screen/API    │   │
│  │   - Link Figma components       │   │
│  │   - Generate title/description  │   │
│  └─────────────────────────────────┘   │
│           │                             │
│           ▼                             │
│  Step 3: Stories → Tasks               │
│  ┌─────────────────────────────────┐   │
│  │   Task Creator                  │   │
│  │   - From implementation_notes   │   │
│  │   - From component hierarchy    │   │
│  │   - From design tokens          │   │
│  └─────────────────────────────────┘   │
│           │                             │
│           ▼                             │
│  Step 4: Generate ACs                  │
│  ┌─────────────────────────────────┐   │
│  │   AC Generator                  │   │
│  │   - From Figma annotations      │   │
│  │   - From requirement text       │   │
│  │   - Design spec matching        │   │
│  └─────────────────────────────────┘   │
│           │                             │
│           ▼                             │
│  Step 5: Estimate Effort               │
│  ┌─────────────────────────────────┐   │
│  │   Effort Estimator              │   │
│  │   - Component count × 2pts      │   │
│  │   - Integration penalty +5pts   │   │
│  │   - Range: 3-21 points          │   │
│  └─────────────────────────────────┘   │
│                                         │
└─────────────────────────────────────────┘
```

---

## 4. Data Flow

### 4.1 End-to-End Flow

```
User Input
    │
    ├─ Gong call_id
    │       │
    │       ▼
    │  [Gong API] ──────┐
    │                   │
    ├─ Figma file_id    │
    │       │           │
    │       ▼           │
    │  [Figma API] ─────┤
    │                   │
    │                   ▼
    │       ┌─────────────────────┐
    │       │  Extract & Parse    │
    │       │  - Requirements     │
    │       │  - Design Spec      │
    │       └──────────┬──────────┘
    │                  │
    │                  ▼
    │       ┌─────────────────────┐
    │       │  Quality Scoring    │
    │       │  - Completeness     │
    │       │  - Impact/Urgency   │
    │       │  - Priority (P0-P2) │
    │       └──────────┬──────────┘
    │                  │
    │                  ▼
    │       ┌─────────────────────┐
    │       │  Review Queue       │
    │       │  [HUMAN APPROVAL]   │
    │       └──────────┬──────────┘
    │                  │
    │                  ▼
    │       ┌─────────────────────┐
    │       │  Story Generation   │
    │       │  - Epic             │
    │       │  - Stories          │
    │       │  - Tasks            │
    │       └──────────┬──────────┘
    │                  │
    │                  ▼
    │       ┌─────────────────────┐
    │       │  Validation         │
    │       │  - Schema check     │
    │       │  - Dependency check │
    │       └──────────┬──────────┘
    │                  │
    │                  ▼
    │       ┌─────────────────────┐
    │       │  Commit to Backlog  │
    │       │  - Append stories   │
    │       │  - Git commit       │
    │       └──────────┬──────────┘
    │                  │
    │                  ▼
    └────────> [Notification] ────> User
               (Slack/Email)
```

### 4.2 State Transitions

```
Requirements States:
  pending_extraction → extracting → extracted →
  pending_review → in_review → approved/rejected →
  generating → generated → committed

Pipeline States:
  initiated → extracting → scoring → waiting_review →
  approved → generating → validating → committing →
  completed/failed
```

---

## 5. API Integrations

### 5.1 Glean MCP (Primary)

**Description:** Primary integration for all search, context, and data retrieval
**Auth:** Glean MCP server authentication

#### Key Tools

```yaml
meeting_lookup:
  description: Search and retrieve meeting transcripts from Gong
  params:
    query: 'after:2026-01-01 participants:"John Smith" topic:"product"'
    extract_transcript: true
  response:
    meetings:
      - meeting_id: abc123
        title: Discovery Call
        transcript: "Full transcript..."
        participants: [...]

chat:
  description: AI-powered extraction with enterprise context
  params:
    message: "Extract requirements from this transcript..."
    context: [previous messages]
  response:
    AI analysis with structured extraction

search:
  description: Find documents, designs, related content
  params:
    query: 'Figma design product'
    app: figma
  response:
    documents: [{url, title, metadata}]

read_document:
  description: Access full document content
  params:
    urls: ['https://figma.com/file/...']
  response:
    Document content and structure
```

**Benefits:**
- Unified API for all enterprise data
- Enterprise context automatically included
- No separate Gong/Confluence/etc. credentials needed
- Glean handles permissions and access control

### 5.2 Figma API (Supplemental)

**Base URL:** `https://api.figma.com/v1`
**Auth:** Bearer token

#### Key Endpoints

```yaml
get_file:
  method: GET
  path: /files/{file_id}
  response:
    document:
      id: file_id
      name: File Name
      children: [node tree]

get_file_nodes:
  method: GET
  path: /files/{file_id}/nodes
  params:
    ids: '1:2,1:3,1:4'
  response:
    nodes:
      '1:2': {node data}
      '1:3': {node data}
```

**Rate Limits:** 1000 calls/hour
**Error Handling:** Retry with exponential backoff
**Use When:** Glean MCP doesn't provide sufficient Figma component detail

**Note:** Glean MCP search should be tried first to locate Figma files via enterprise search before falling back to direct Figma API calls.

---

## 6. Data Model

### 6.1 Database Schema

#### Requirements Table

```sql
CREATE TABLE requirements (
  id UUID PRIMARY KEY,
  call_id VARCHAR(255) NOT NULL,
  requirement_text TEXT NOT NULL,
  requirement_type VARCHAR(50),  -- integration, feature_request, pain_point
  speaker_name VARCHAR(255),
  speaker_role VARCHAR(100),
  timestamp VARCHAR(20),
  confidence_score FLOAT,
  completeness_score FLOAT,
  business_impact_score FLOAT,
  urgency_score FLOAT,
  composite_priority_score FLOAT,
  suggested_priority VARCHAR(10),  -- P0, P1, P2
  status VARCHAR(50),  -- pending, approved, rejected
  reviewed_by VARCHAR(255),
  reviewed_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_requirements_call_id ON requirements(call_id);
CREATE INDEX idx_requirements_status ON requirements(status);
CREATE INDEX idx_requirements_priority ON requirements(suggested_priority);
```

#### Design Components Table

```sql
CREATE TABLE design_components (
  id UUID PRIMARY KEY,
  figma_file_id VARCHAR(255) NOT NULL,
  figma_node_id VARCHAR(255) NOT NULL,
  component_type VARCHAR(100),
  component_name VARCHAR(255),
  properties JSONB,  -- dimensions, colors, typography, etc.
  annotations JSONB,  -- user story hints, implementation notes
  user_story_hints TEXT[],
  implementation_notes TEXT[],
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_components_file_id ON design_components(figma_file_id);
CREATE INDEX idx_components_type ON design_components(component_type);
```

#### Pipeline Runs Table

```sql
CREATE TABLE pipeline_runs (
  id UUID PRIMARY KEY,
  call_id VARCHAR(255),
  figma_file_id VARCHAR(255),
  status VARCHAR(50),  -- running, waiting_review, completed, failed
  current_step VARCHAR(100),
  error_message TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

### 6.2 File Artifacts

```
output/
├── requirements/
│   ├── requirements-{call_id}.yaml
│   └── requirements.yaml (all aggregated)
├── figma/
│   ├── design-spec-{file_id}.yaml
│   └── design-spec.yaml (all aggregated)
└── stories/
    └── generated-stories-{timestamp}.yaml
```

---

## 7. Processing Pipeline

### 7.1 Pipeline Orchestration

**Technology:** Celery (Python task queue)

```python
from celery import chain

pipeline = chain(
    extract_gong.s(call_id),
    score_requirements.s(),
    queue_for_review.s(),
    # Wait for human approval...
    generate_stories.s(figma_file_id),
    validate_stories.s(),
    commit_to_backlog.s(),
    send_notification.s()
)

result = pipeline.apply_async()
```

### 7.2 Error Handling

**Retry Strategy:**
```python
@celery_app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,  # 1 minute
    autoretry_for=(APIError, TimeoutError)
)
def extract_gong(self, call_id):
    try:
        return extractor.extract(call_id)
    except Exception as exc:
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)
```

**Failure Handling:**
- Log error to database
- Preserve pipeline state
- Send alert notification
- Allow manual retry/resume

---

## 8. Quality Scoring

### 8.1 Scoring Formula

```python
def calculate_priority_score(requirement):
    # Business Impact (0-10)
    impact = (
        requirement.revenue_at_risk * 0.4 +
        requirement.customer_tier_value * 0.3 +
        requirement.strategic_value * 0.3
    )

    # Urgency (0-10)
    urgency = (
        timeline_score(requirement.timeline) * 0.5 +
        keyword_score(requirement.urgency_words) * 0.3 +
        pain_level_score(requirement.pain_level) * 0.2
    )

    # Composite Score
    score = (
        impact * 0.4 +
        urgency * 0.3 +
        requirement.confidence * 10 * 0.2 +
        requirement.completeness / 10 * 0.1
    )

    # Executive Multiplier
    if requirement.speaker.is_executive:
        score *= 2.0

    # Clamp to 0-10
    return min(max(score, 0), 10)

def map_to_priority(score):
    if score >= 8.0:
        return 'P0'
    elif score >= 5.0:
        return 'P1'
    else:
        return 'P2'
```

### 8.2 Confidence Scoring

```python
def calculate_confidence(requirement):
    # Speaker Authority (0-1)
    authority = {
        'executive': 0.9,
        'director': 0.8,
        'manager': 0.7,
        'ic': 0.5,
        'unknown': 0.3
    }[requirement.speaker.level]

    # Clarity Score (0-1)
    clarity = assess_clarity(requirement.text)

    # Corroboration (0-1)
    corroboration = (
        1.0 if requirement.mentioned_by_multiple_speakers
        else 0.5
    )

    # Source Quality (0-1)
    source = 1.0 if requirement.from_live_call else 0.7

    # Weighted Average
    confidence = (
        authority * 0.4 +
        clarity * 0.3 +
        corroboration * 0.2 +
        source * 0.1
    )

    return confidence
```

---

## 9. Story Generation

### 9.1 Epic Generation

**Grouping Logic:**
```python
def group_requirements_into_epics(requirements):
    groups = []

    for req in requirements:
        # Find existing group or create new
        group = find_matching_group(req, groups) or create_new_group(req)
        group.add(req)

    epics = []
    for group in groups:
        epic = {
            'story_id': generate_epic_id(group),
            'title': f"{group.feature_name} Epic",
            'description': summarize_requirements(group.requirements),
            'priority': max_priority(group.requirements),
            'stories': []
        }
        epics.append(epic)

    return epics

def find_matching_group(req, groups):
    for group in groups:
        if (same_business_goal(req, group) or
            same_system_integration(req, group) or
            same_figma_flow(req, group)):
            return group
    return None
```

### 9.2 Story Generation

```python
def generate_story(requirement, figma_components):
    story = {
        'story_id': generate_story_id(requirement),
        'priority': requirement.suggested_priority,
        'title': generate_title(requirement, figma_components),
        'description': generate_description(requirement, figma_components),
        'tasks': generate_tasks(figma_components),
        'acceptance_criteria': generate_acs(requirement, figma_components),
        'source_metadata': {
            'gong_calls': [requirement.call_id],
            'figma_files': [c.figma_file_id for c in figma_components]
        },
        'artifact_registry': [
            {'path': f'output/figma/design-spec-{file_id}.yaml', 'type': 'design_spec'}
        ]
    }
    return story

def generate_title(requirement, components):
    # Extract action verb from requirement
    action = extract_action_verb(requirement.text)  # "Integrate", "Add", "Implement"

    # Identify primary component or system
    primary = components[0].name if components else requirement.entities.systems[0]

    return f"{action} {primary}"

def generate_tasks(figma_components):
    tasks = []

    # Task 1: Design tokens (if needed)
    if has_design_tokens(figma_components):
        tasks.append("Set up design tokens (colors, typography, spacing)")

    # Task 2-N: Implement each component
    for comp in figma_components:
        tasks.append(f"Implement {comp.name} component")

        # Add variant tasks
        if comp.variants:
            tasks.append(f"Add {', '.join(comp.variants)} variants")

    # Task N+1: Integration (if API mentioned)
    if has_api_integration(requirement):
        tasks.append(f"Integrate with {requirement.entities.systems[0]} API")

    return tasks
```

---

## 10. Deployment Architecture

### 10.1 Container Deployment

```yaml
services:
  gong-extraction:
    image: requirements-pipeline/gong-extraction:latest
    env:
      - GONG_API_KEY=${GONG_API_KEY}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    resources:
      limits:
        cpu: 1
        memory: 2Gi

  figma-parsing:
    image: requirements-pipeline/figma-parsing:latest
    env:
      - FIGMA_TOKEN=${FIGMA_TOKEN}
    resources:
      limits:
        cpu: 0.5
        memory: 1Gi

  pipeline-orchestrator:
    image: requirements-pipeline/orchestrator:latest
    env:
      - DATABASE_URL=postgresql://...
      - REDIS_URL=redis://...
    resources:
      limits:
        cpu: 1
        memory: 2Gi

  review-api:
    image: requirements-pipeline/review-api:latest
    ports:
      - "8001:8000"
    resources:
      limits:
        cpu: 0.5
        memory: 1Gi

  review-ui:
    image: requirements-pipeline/review-ui:latest
    ports:
      - "3002:3000"
    resources:
      limits:
        cpu: 0.5
        memory: 512Mi

  postgres:
    image: postgres:15
    volumes:
      - postgres-data:/var/lib/postgresql/data

  redis:
    image: redis:7
    volumes:
      - redis-data:/data
```

### 10.2 Infrastructure

```
┌──────────────────────────────────────────────┐
│              Load Balancer                   │
└────────────┬─────────────────────────────────┘
             │
     ┌───────┴────────┐
     │                │
     ▼                ▼
┌─────────┐    ┌──────────┐
│ Review  │    │ Review   │
│ API     │    │ UI       │
│ (8001)  │    │ (3002)   │
└────┬────┘    └──────────┘
     │
     ▼
┌──────────────────────────────────────────────┐
│         Celery Worker Pool                   │
│  ┌────────┐  ┌────────┐  ┌────────┐         │
│  │Worker 1│  │Worker 2│  │Worker 3│  ...    │
│  └────────┘  └────────┘  └────────┘         │
└──────────────┬───────────────────────────────┘
               │
     ┌─────────┴─────────┐
     │                   │
     ▼                   ▼
┌──────────┐      ┌───────────┐
│PostgreSQL│      │  Redis    │
│  (State) │      │  (Queue)  │
└──────────┘      └───────────┘
```

---

## 11. Design Rationale

### 11.1 Why Glean MCP as Primary Integration?

**Decision:** Use Glean MCP for all search, context, and data retrieval

**Rationale:**
- **Unified access:** Single API for Gong, Figma, docs, code, etc.
- **Enterprise context:** Glean enriches data with company knowledge graph
- **Simplified auth:** No need to manage multiple API credentials
- **Permission-aware:** Glean handles access control automatically
- **AI-powered:** Built-in chat tool for extraction with context
- **Scalability:** Glean handles rate limiting and optimization

**Hybrid approach:**
1. Glean MCP meeting_lookup retrieves Gong transcripts
2. Glean MCP chat extracts requirements (with enterprise context)
3. Rules validate urgency keywords (deterministic checks)
4. Rules detect timelines (regex pattern matching)
5. Confidence scoring combines all signals

**Fallback:** Direct Figma API if Glean doesn't provide component detail

**Result:** Simplified architecture, richer context, fewer integrations

### 11.2 Why Human-in-the-Loop?

**Decision:** Mandatory human review before story generation (Phase 1)

**Rationale:**
- **Risk mitigation:** Prevent hallucinated requirements from polluting backlog
- **Quality control:** Human judgment on priority and scope
- **Trust building:** Teams must trust automated extraction before full automation
- **Learning:** Human feedback improves model over time

**Future:** Auto-approve high-confidence (>0.9) requirements in Phase 2

### 11.3 Why Event-Driven Pipeline?

**Decision:** Async task queue (Celery) instead of synchronous API

**Rationale:**
- **Long-running tasks:** Extraction can take 2+ minutes
- **Resilience:** Failures at one stage don't break entire pipeline
- **Scalability:** Add workers to handle load
- **Human review:** Natural "wait state" in pipeline
- **Observability:** Clear state at each stage

**Alternative considered:** Synchronous REST API → Rejected (timeouts, poor UX)

### 11.4 Why PostgreSQL + File Storage?

**Decision:** PostgreSQL for structured data, files for YAML artifacts

**Rationale:**
- **PostgreSQL:** Rich querying, ACID transactions, JSONB for flexible schemas
- **File storage:** Version control friendly (YAML in Git), human-readable
- **Hybrid approach:** Database for operational queries, files for artifact storage

**Alternative considered:** Document DB (MongoDB) → Rejected (prefer relational for this use case)

### 11.5 Why Epic → Stories → Tasks?

**Decision:** Three-level hierarchy for story generation

**Rationale:**
- **Epic:** Matches PM mental model (feature-level thinking)
- **Story:** Implementable units (one screen or API endpoint)
- **Task:** Granular work items (half-day chunks)
- **Existing pattern:** Matches IMPLEMENTATION_BACKLOG.yaml structure

**Alternative considered:** Flat stories → Rejected (loses feature context)

---

## Appendix A: API Reference

### Glean MCP Tools (Primary)

```yaml
meeting_lookup:
  description: Search meetings by filters
  query_examples:
    - "after:2026-01-01 before:2026-02-01"
    - "participants:\"John Smith\" topic:\"integration\""
    - "extract_transcript:\"true\""
  response:
    meetings: array with transcripts

chat:
  description: AI-powered analysis
  message_example: "Extract requirements from this meeting transcript: {transcript}"
  response: Structured extraction with enterprise context

search:
  description: Find documents across all apps
  query_examples:
    - "Figma product design"
    - "app:figma updated:past_week"
  response:
    documents: array with URLs and metadata

read_document:
  description: Get full document content
  urls: ["https://figma.com/file/abc123"]
  response: Document structure and content
```

### Figma API Endpoints (Supplemental)

```yaml
GET /v1/files/{file_id}:
  description: Get file metadata
  response:
    document: node tree

GET /v1/files/{file_id}/nodes:
  description: Get specific nodes
  params:
    ids: comma-separated
  response:
    nodes: object
```

---

## Appendix B: Configuration Examples

### Pipeline Configuration

```yaml
# config/pipeline.yaml

extraction:
  gong:
    api_url: https://api.gong.io/v2
    timeout_seconds: 300
    retry_attempts: 3

  llm:
    model: claude-sonnet-4-5
    temperature: 0.3
    max_tokens: 4096

  rules:
    urgency_keywords:
      high: [critical, urgent, asap, immediately]
      medium: [need, must, should, important]
      low: [want, would like, nice to have]

scoring:
  weights:
    business_impact: 0.4
    urgency: 0.3
    confidence: 0.2
    completeness: 0.1

  priority_thresholds:
    P0: 8.0
    P1: 5.0

generation:
  effort_estimation:
    points_per_component: 2
    integration_penalty: 5
    min_effort: 3
    max_effort: 21
```

---

**Document Metadata:**
- **Authors:** Requirements Chat Session (P0-A2A-F4000)
- **Reviewers:** TBD
- **Approval Status:** Pending
- **Related Documents:**
  - `output/requirements/requirements-to-design-requirements.yaml`
  - `output/figma/requirements-to-design-design.yaml`

**Change History:**
- 2026-02-11: Initial architecture document created
