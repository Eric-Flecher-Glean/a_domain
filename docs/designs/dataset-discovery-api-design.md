# Dataset Discovery & Registry - API Design

**Document ID**: DES-004
**Status**: Current
**Created**: 2026-02-15
**Last Updated**: 2026-02-18
**Authors**: Requirements Chat (AI-Generated), API Team

## Overview

This document defines the RESTful API design for the Dataset Discovery & Registry service, which enables automated dataset lifecycle management across client journey stages.

### API Principles

- **RESTful**: Resource-oriented URLs with standard HTTP methods
- **Idempotent**: Safe retry semantics for all provisioning operations
- **Event-Driven**: Publishes domain events for all state changes
- **Versioned**: API version in URL path (v1)
- **Async-First**: Long-running operations return 202 Accepted with status tracking

## Base URL

```
https://api.a-domain.com/v1/dataops
```

## Authentication

```yaml
Authentication:
  method: Bearer token (JWT)
  header: Authorization: Bearer <token>
  scopes:
    - dataops:datasets:read
    - dataops:datasets:write
    - dataops:templates:read
    - dataops:quality:read
    - dataops:admin (full access)
```

## Resource Models

### Dataset Resource

```json
{
  "dataset_id": "uuid",
  "name": "ACME-Sandbox-Confluence",
  "dataset_type": "confluence_pages",
  "stage": "sandbox",
  "client_id": "uuid",
  "journey_id": "uuid",
  "status": "ready",
  "created_at": "2026-01-28T10:30:00Z",
  "ready_at": "2026-01-28T11:15:00Z",
  "archived_at": null,
  "data_source": "mock_template",
  "record_count": 500,
  "size_bytes": 15728640,
  "quality_score": 98.5,
  "connector": {
    "connector_id": "uuid",
    "name": "ACME-Sandbox-Confluence",
    "status": "healthy",
    "endpoint_url": "https://glean.acme.com/connectors/conf-001"
  },
  "template": {
    "template_id": "uuid",
    "name": "FinTech Developer Productivity - Confluence"
  },
  "metadata": {
    "industry": "fintech",
    "use_case": "developer_productivity",
    "tags": ["sandbox", "mock", "testing"]
  },
  "quality_checks": [
    {
      "check_id": "uuid",
      "check_type": "schema_validation",
      "status": "passed",
      "score": 100.0,
      "executed_at": "2026-01-28T11:10:00Z"
    }
  ],
  "_links": {
    "self": "/v1/dataops/datasets/{dataset_id}",
    "quality": "/v1/dataops/datasets/{dataset_id}/quality",
    "usage": "/v1/dataops/datasets/{dataset_id}/usage",
    "teardown": "/v1/dataops/datasets/{dataset_id}/teardown"
  }
}
```

### DatasetTemplate Resource

```json
{
  "template_id": "uuid",
  "name": "FinTech Developer Productivity - Confluence",
  "dataset_type": "confluence_pages",
  "industry": "fintech",
  "use_case": "developer_productivity",
  "description": "Mock Confluence pages for FinTech companies focused on developer productivity",
  "source_path": "mock_data/templates/fintech/developer_productivity/confluence_pages.json",
  "schema": {
    "version": "1.0",
    "fields": [
      {"name": "page_id", "type": "string", "required": true},
      {"name": "title", "type": "string", "required": true},
      {"name": "content", "type": "text", "required": true},
      {"name": "author", "type": "string", "required": false},
      {"name": "created_date", "type": "datetime", "required": true}
    ]
  },
  "default_record_count": 500,
  "estimated_size_mb": 15,
  "quality_rules": [
    {"rule": "all_required_fields_present", "threshold": 100},
    {"rule": "content_length_min", "value": 50, "threshold": 95}
  ],
  "_links": {
    "self": "/v1/dataops/templates/{template_id}",
    "datasets": "/v1/dataops/datasets?template_id={template_id}"
  }
}
```

### QualityScore Resource

```json
{
  "dataset_id": "uuid",
  "overall_score": 98.5,
  "meets_threshold": true,
  "threshold": 95.0,
  "calculated_at": "2026-01-28T11:15:00Z",
  "checks": {
    "schema_validation": {
      "score": 100.0,
      "weight": 0.30,
      "status": "passed",
      "details": "All 500 records match schema"
    },
    "data_completeness": {
      "score": 98.0,
      "weight": 0.30,
      "status": "passed",
      "details": "490/500 records fully populated (98%)"
    },
    "connector_health": {
      "score": 100.0,
      "weight": 0.25,
      "status": "passed",
      "details": "Connector healthy, response time 1.2s"
    },
    "sample_query_success": {
      "score": 100.0,
      "weight": 0.15,
      "status": "passed",
      "details": "10/10 test queries successful"
    }
  },
  "_links": {
    "dataset": "/v1/dataops/datasets/{dataset_id}",
    "revalidate": "/v1/dataops/datasets/{dataset_id}/quality/validate"
  }
}
```

## API Endpoints

### Datasets API

#### List Datasets

```http
GET /v1/dataops/datasets
```

**Query Parameters:**
```
?client_id=uuid           # Filter by client
?journey_id=uuid          # Filter by journey
?stage=sandbox            # Filter by stage (sandbox, pilot, production)
?status=ready             # Filter by status
?dataset_type=confluence  # Filter by type
?page=1                   # Pagination
?per_page=20              # Page size (max 100)
```

**Response: 200 OK**
```json
{
  "datasets": [<Dataset>],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total_pages": 5,
    "total_count": 87
  },
  "_links": {
    "self": "/v1/dataops/datasets?page=1",
    "next": "/v1/dataops/datasets?page=2",
    "last": "/v1/dataops/datasets?page=5"
  }
}
```

#### Get Dataset

```http
GET /v1/dataops/datasets/{dataset_id}
```

**Response: 200 OK**
```json
<Dataset>
```

**Error Responses:**
- `404 Not Found`: Dataset does not exist

#### Create Dataset (Provision)

```http
POST /v1/dataops/datasets
```

**Request Body:**
```json
{
  "journey_id": "uuid",
  "client_id": "uuid",
  "stage": "sandbox",
  "dataset_types": ["confluence_pages", "github_repos"],
  "template_selection": "auto",  # or "manual"
  "template_overrides": {
    "confluence_pages": "template-uuid"  # optional manual selection
  },
  "metadata": {
    "requested_by": "user@acme.com",
    "reason": "sandbox_stage_transition"
  }
}
```

**Response: 202 Accepted** (Async operation)
```json
{
  "operation_id": "uuid",
  "status": "provisioning",
  "message": "Dataset provisioning started",
  "datasets": [
    {
      "dataset_id": "uuid",
      "dataset_type": "confluence_pages",
      "status": "provisioning"
    }
  ],
  "estimated_completion": "2026-01-28T12:30:00Z",
  "_links": {
    "status": "/v1/dataops/operations/{operation_id}",
    "datasets": "/v1/dataops/datasets?journey_id={journey_id}"
  }
}
```

**Error Responses:**
- `400 Bad Request`: Invalid request (e.g., missing required fields)
- `409 Conflict`: Dataset already exists for this client/stage/type
- `422 Unprocessable Entity`: Template not found or incompatible

#### Update Dataset Metadata

```http
PATCH /v1/dataops/datasets/{dataset_id}
```

**Request Body:**
```json
{
  "metadata": {
    "tags": ["updated", "tested"],
    "custom_field": "value"
  }
}
```

**Response: 200 OK**
```json
<Dataset>
```

#### Delete Dataset (Teardown)

```http
DELETE /v1/dataops/datasets/{dataset_id}
```

**Query Parameters:**
```
?reason=stage_transition    # Reason for teardown
?archive=true               # Archive before delete (default: true)
```

**Response: 202 Accepted** (Async operation)
```json
{
  "operation_id": "uuid",
  "status": "tearing_down",
  "message": "Dataset teardown initiated",
  "estimated_completion": "2026-01-28T11:00:00Z",
  "_links": {
    "status": "/v1/dataops/operations/{operation_id}"
  }
}
```

### Quality API

#### Get Quality Score

```http
GET /v1/dataops/datasets/{dataset_id}/quality
```

**Response: 200 OK**
```json
<QualityScore>
```

#### Trigger Quality Validation

```http
POST /v1/dataops/datasets/{dataset_id}/quality/validate
```

**Request Body:**
```json
{
  "checks": ["schema_validation", "data_completeness", "connector_health", "sample_query_success"],
  "force_revalidation": false
}
```

**Response: 202 Accepted**
```json
{
  "operation_id": "uuid",
  "status": "validating",
  "message": "Quality validation started",
  "estimated_completion": "2026-01-28T11:20:00Z",
  "_links": {
    "status": "/v1/dataops/operations/{operation_id}",
    "results": "/v1/dataops/datasets/{dataset_id}/quality"
  }
}
```

#### Get Quality History

```http
GET /v1/dataops/datasets/{dataset_id}/quality/history
```

**Query Parameters:**
```
?from=2026-01-01T00:00:00Z
?to=2026-01-28T23:59:59Z
?check_type=schema_validation
```

**Response: 200 OK**
```json
{
  "dataset_id": "uuid",
  "history": [
    {
      "check_id": "uuid",
      "check_type": "schema_validation",
      "score": 100.0,
      "status": "passed",
      "executed_at": "2026-01-28T11:10:00Z"
    }
  ],
  "_links": {
    "dataset": "/v1/dataops/datasets/{dataset_id}"
  }
}
```

### Templates API

#### List Templates

```http
GET /v1/dataops/templates
```

**Query Parameters:**
```
?industry=fintech
?use_case=developer_productivity
?dataset_type=confluence_pages
```

**Response: 200 OK**
```json
{
  "templates": [<DatasetTemplate>],
  "total_count": 15
}
```

#### Get Template

```http
GET /v1/dataops/templates/{template_id}
```

**Response: 200 OK**
```json
<DatasetTemplate>
```

#### Get Template Recommendations

```http
POST /v1/dataops/templates/recommend
```

**Request Body:**
```json
{
  "client_metadata": {
    "industry": "fintech",
    "use_case": "developer_productivity",
    "company_size": "mid_market"
  },
  "dataset_types": ["confluence_pages", "github_repos"],
  "stage": "sandbox"
}
```

**Response: 200 OK**
```json
{
  "recommendations": [
    {
      "dataset_type": "confluence_pages",
      "recommended_template": <DatasetTemplate>,
      "confidence_score": 0.95,
      "reason": "Exact match on industry and use_case"
    }
  ]
}
```

### Connectors API

#### List Connectors

```http
GET /v1/dataops/connectors
```

**Query Parameters:**
```
?client_id=uuid
?stage=sandbox
?status=healthy
```

**Response: 200 OK**
```json
{
  "connectors": [
    {
      "connector_id": "uuid",
      "name": "ACME-Sandbox-Confluence",
      "connector_type": "confluence",
      "status": "healthy",
      "dataset_id": "uuid",
      "health_check": {
        "last_checked": "2026-01-28T11:30:00Z",
        "response_time_ms": 1200,
        "error_rate": 0.0
      }
    }
  ]
}
```

#### Get Connector Health

```http
GET /v1/dataops/connectors/{connector_id}/health
```

**Response: 200 OK**
```json
{
  "connector_id": "uuid",
  "status": "healthy",
  "checks": {
    "connection": {"status": "passed", "message": "Endpoint reachable"},
    "authentication": {"status": "passed", "message": "Credentials valid"},
    "responsiveness": {"status": "passed", "response_time_ms": 1200},
    "error_rate": {"status": "passed", "rate": 0.0, "threshold": 0.01}
  },
  "last_sync": {
    "started_at": "2026-01-28T10:00:00Z",
    "completed_at": "2026-01-28T10:05:00Z",
    "records_synced": 500,
    "status": "success"
  }
}
```

### Operations API (Async Status Tracking)

#### Get Operation Status

```http
GET /v1/dataops/operations/{operation_id}
```

**Response: 200 OK**
```json
{
  "operation_id": "uuid",
  "operation_type": "dataset_provisioning",
  "status": "in_progress",
  "progress": {
    "current_step": 3,
    "total_steps": 6,
    "step_description": "Populating mock data",
    "percent_complete": 50
  },
  "started_at": "2026-01-28T10:30:00Z",
  "estimated_completion": "2026-01-28T11:30:00Z",
  "result": null,
  "_links": {
    "self": "/v1/dataops/operations/{operation_id}"
  }
}
```

**When Complete: 200 OK**
```json
{
  "operation_id": "uuid",
  "operation_type": "dataset_provisioning",
  "status": "completed",
  "progress": {
    "current_step": 6,
    "total_steps": 6,
    "percent_complete": 100
  },
  "started_at": "2026-01-28T10:30:00Z",
  "completed_at": "2026-01-28T11:15:00Z",
  "duration_minutes": 45,
  "result": {
    "datasets": [
      {
        "dataset_id": "uuid",
        "status": "ready",
        "quality_score": 98.5
      }
    ]
  },
  "_links": {
    "datasets": "/v1/dataops/datasets?operation_id={operation_id}"
  }
}
```

**When Failed: 200 OK**
```json
{
  "operation_id": "uuid",
  "status": "failed",
  "error": {
    "code": "QUALITY_VALIDATION_FAILED",
    "message": "Dataset quality score 92.5% below threshold 95%",
    "details": {
      "failed_checks": ["data_completeness"],
      "quality_score": 92.5
    }
  },
  "started_at": "2026-01-28T10:30:00Z",
  "failed_at": "2026-01-28T10:50:00Z"
}
```

## Webhooks (Event Notifications)

### Webhook Registration

Clients can register webhook URLs to receive event notifications:

```http
POST /v1/dataops/webhooks
```

**Request Body:**
```json
{
  "url": "https://client.acme.com/webhooks/dataops",
  "events": [
    "dataset.provisioning.completed",
    "dataset.validation.failed",
    "dataset.ready",
    "dataset.archived"
  ],
  "secret": "webhook_signing_secret"
}
```

### Webhook Payload Example

```json
{
  "event_id": "uuid",
  "event_type": "dataset.ready",
  "timestamp": "2026-01-28T11:15:00Z",
  "data": {
    "dataset_id": "uuid",
    "journey_id": "uuid",
    "quality_score": 98.5,
    "ready_at": "2026-01-28T11:15:00Z"
  },
  "_links": {
    "dataset": "/v1/dataops/datasets/{dataset_id}"
  }
}
```

## Error Responses

### Standard Error Format

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      "field": "Additional context"
    },
    "request_id": "uuid",
    "timestamp": "2026-01-28T11:30:00Z"
  }
}
```

### Error Codes

| Status | Code | Message |
|--------|------|---------|
| 400 | INVALID_REQUEST | Request validation failed |
| 401 | UNAUTHORIZED | Authentication required |
| 403 | FORBIDDEN | Insufficient permissions |
| 404 | NOT_FOUND | Resource does not exist |
| 409 | CONFLICT | Resource already exists |
| 422 | UNPROCESSABLE_ENTITY | Business rule violation |
| 429 | RATE_LIMIT_EXCEEDED | Too many requests |
| 500 | INTERNAL_ERROR | Server error |
| 503 | SERVICE_UNAVAILABLE | Temporary service disruption |

## Rate Limiting

```yaml
RateLimits:
  per_client:
    requests_per_minute: 100
    burst: 20
  per_operation:
    dataset_provisioning: 10 concurrent per client
    quality_validation: 5 concurrent per client
  headers:
    X-RateLimit-Limit: 100
    X-RateLimit-Remaining: 87
    X-RateLimit-Reset: 1706443200 (Unix timestamp)
```

## Idempotency

All write operations support idempotency via `Idempotency-Key` header:

```http
POST /v1/dataops/datasets
Idempotency-Key: {client-generated-uuid}
```

- Same `Idempotency-Key` within 24 hours returns cached response
- Prevents duplicate dataset creation
- Returns `409 Conflict` if operation with same key is in progress

## Pagination

List endpoints use cursor-based pagination:

```http
GET /v1/dataops/datasets?page=2&per_page=20
```

**Response Headers:**
```
Link: </v1/dataops/datasets?page=1>; rel="prev",
      </v1/dataops/datasets?page=3>; rel="next",
      </v1/dataops/datasets?page=5>; rel="last"
```

## Versioning Strategy

- **URL Versioning**: `/v1/dataops/...`
- **Backward Compatibility**: Maintain v1 for 12 months after v2 release
- **Deprecation Notice**: 6 months warning via `Deprecation` header
- **Sunset Date**: `Sunset` header with RFC 7234 date

---

**Related Documents:**
- ARCH-004: Data Architecture - DataOps Lifecycle
- DDD-003: DataOps Lifecycle - Bounded Context
- TECH-004: DataOps Lifecycle - API Reference

**Implements Stories:**
- P0-A2A-F2-001: Dataset Discovery & Registry

**Referenced By:**
- P0-A2A-F2-000: Requirements Chat - DataOps Lifecycle
