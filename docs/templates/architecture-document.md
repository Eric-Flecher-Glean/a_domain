---
title: "{{ story_title }} - Architecture"
story_id: "{{ story_id }}"
doc_type: architecture
status: draft
created_date: "{{ created_date }}"
author: "{{ author }}"
version: 0.1
---

# {{ story_title }} - Architecture Document

**Story ID**: {{ story_id }}
**Status**: Draft
**Version**: 0.1
**Last Updated**: {{ created_date }}

---

## Executive Summary

<!-- High-level overview of the architecture (2-3 paragraphs) -->

{{ description }}

---

## System Context

### Business Context

<!-- Why does this system exist? What business problem does it solve? -->

### Stakeholders

| Stakeholder | Role | Concerns |
|-------------|------|----------|
|             |      |          |

### External Dependencies

<!-- Systems, services, or teams this architecture depends on -->

-

---

## Architecture Overview

### System Landscape

```
┌─────────────────────────────────────────────────┐
│                                                 │
│            [System Context Diagram]             │
│                                                 │
│  [External System] <--> [This System] <--> [DB] │
│                                                 │
└─────────────────────────────────────────────────┘
```

### Key Architectural Decisions

<!-- List ADRs or key architectural decisions -->

1. **Decision**:
   - **Rationale**:
   - **Alternatives Considered**:

2. **Decision**:
   - **Rationale**:
   - **Alternatives Considered**:

---

## Container Architecture

### Container Diagram

```
┌──────────────────────────────────────────────────────┐
│                                                      │
│  [Frontend]  -->  [API Gateway]  -->  [Services]     │
│                                                      │
│                         ↓                            │
│                    [Database]                        │
│                                                      │
└──────────────────────────────────────────────────────┘
```

### Container Descriptions

#### Container 1: [Name]

**Technology**: Python/Node.js/etc.
**Responsibility**:

**Interfaces**:
-

**Data Storage**:
-

#### Container 2: [Name]

**Technology**:
**Responsibility**:

**Interfaces**:
-

**Data Storage**:
-

---

## Component Architecture

### Component Diagram

```
[Component A]
    ├── [Subcomponent A1]
    ├── [Subcomponent A2]
    └── [Subcomponent A3]

[Component B]
    ├── [Subcomponent B1]
    └── [Subcomponent B2]
```

### Component Details

#### Component: [Name]

**Responsibility**:

**Internal Structure**:
-

**Key Classes/Modules**:
```python
class ComponentName:
    """Description"""
    pass
```

---

## Data Architecture

### Domain Model

<!-- DDD bounded context, aggregates, entities, value objects -->

```yaml
bounded_context: {{ story_id }}
aggregates:
  - name: AggregateRoot
    entities:
      - Entity1
      - Entity2
    value_objects:
      - ValueObject1
```

### Database Schema

<!-- If applicable, define database schema -->

```sql
CREATE TABLE example (
    id SERIAL PRIMARY KEY,
    field1 VARCHAR(255),
    created_at TIMESTAMP
);
```

### Data Flow

<!-- How does data move through the system? -->

```
User Input --> Validation --> Processing --> Storage --> Response
```

---

## Integration Architecture

### Integration Points

| System | Protocol | Purpose | SLA |
|--------|----------|---------|-----|
|        |          |         |     |

### Message Formats

<!-- Define message schemas for integration points -->

```json
{
  "event_type": "example.event",
  "payload": {
    "field": "value"
  }
}
```

---

## Quality Attributes

### Performance

**Requirements**:
- Response time: < X ms
- Throughput: Y requests/second

**Strategy**:
-

### Reliability

**Requirements**:
- Uptime: 99.9%
- Recovery time: < X minutes

**Strategy**:
-

### Security

**Requirements**:
- Authentication:
- Authorization:
- Encryption:

**Strategy**:
-

### Scalability

**Requirements**:
- Horizontal scaling:
- Vertical scaling:

**Strategy**:
-

---

## Deployment Architecture

### Infrastructure

```
[Load Balancer]
      |
      v
[App Server 1]  [App Server 2]  [App Server 3]
      |              |              |
      v              v              v
         [Database Cluster]
```

### Configuration Management

<!-- How is configuration managed? -->

### Monitoring & Observability

<!-- How is the system monitored? -->

- Metrics:
- Logs:
- Traces:
- Alerts:

---

## Implementation Roadmap

### Phase 1: Foundation

{% for task in tasks[:3] %}
- {{ task }}
{% endfor %}

### Phase 2: Core Features

<!-- Additional tasks if needed -->

### Phase 3: Optimization

<!-- Additional tasks if needed -->

---

## Risks & Trade-offs

### Technical Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
|      |        |            |

### Architectural Trade-offs

| Decision | Benefits | Drawbacks |
|----------|----------|-----------|
|          |          |           |

---

## Acceptance Criteria

{% for ac in acceptance_criteria %}
- **AC{{ loop.index }}**: {{ ac }}
{% endfor %}

---

## References

- Story: {{ story_id }} in IMPLEMENTATION_BACKLOG.yaml
- Related Architecture:
  -
- Standards:
  -

---

## Changelog

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 0.1 | {{ created_date }} | {{ author }} | Initial draft created via /new-feature-chat |
