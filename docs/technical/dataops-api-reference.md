# DataOps Lifecycle - API Reference

**Document ID**: TECH-004
**Status**: Draft
**Created**: 2026-02-18
**Last Updated**: 2026-02-28
**Authors**: DataOps Team, Requirements Chat (AI-Generated)

## Overview

Complete API reference for the DataOps Lifecycle management system. This document provides detailed specifications for all API endpoints, request/response schemas, authentication, and integration patterns.

**Base URL**: `https://api.a-domain.com/v1/dataops`

**API Version**: 1.0

## Quick Start

### Authentication

```bash
# Obtain access token
curl -X POST https://auth.a-domain.com/token \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "your-client-id",
    "client_secret": "your-client-secret",
    "grant_type": "client_credentials",
    "scope": "dataops:datasets:write dataops:datasets:read"
  }'

# Use token in requests
export TOKEN="eyJhbGc..."
curl -H "Authorization: Bearer $TOKEN" \
  https://api.a-domain.com/v1/dataops/datasets
```

### Provision a Dataset

```bash
curl -X POST https://api.a-domain.com/v1/dataops/datasets \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "journey_id": "uuid",
    "client_id": "uuid",
    "stage": "sandbox",
    "dataset_types": ["confluence_pages"]
  }'
```

### Check Quality Score

```bash
curl -H "Authorization: Bearer $TOKEN" \
  https://api.a-domain.com/v1/dataops/datasets/{dataset_id}/quality
```

## Authentication & Authorization

### OAuth 2.0 Client Credentials Flow

**Token Endpoint**: `POST https://auth.a-domain.com/token`

**Request:**
```json
{
  "client_id": "your-client-id",
  "client_secret": "your-client-secret",
  "grant_type": "client_credentials",
  "scope": "dataops:datasets:write dataops:datasets:read dataops:templates:read"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "scope": "dataops:datasets:write dataops:datasets:read"
}
```

### Scopes

| Scope | Description | Required For |
|-------|-------------|--------------|
| `dataops:datasets:read` | Read dataset information | GET /datasets, GET /datasets/{id} |
| `dataops:datasets:write` | Create, update, delete datasets | POST /datasets, PATCH /datasets/{id}, DELETE /datasets/{id} |
| `dataops:templates:read` | Read dataset templates | GET /templates, GET /templates/{id} |
| `dataops:quality:read` | Read quality scores | GET /datasets/{id}/quality |
| `dataops:quality:write` | Trigger quality validation | POST /datasets/{id}/quality/validate |
| `dataops:admin` | Full administrative access | All endpoints |

### Request Headers

```
Authorization: Bearer {access_token}
Content-Type: application/json
Accept: application/json
Idempotency-Key: {uuid} (optional, for POST/DELETE)
X-Request-ID: {uuid} (optional, for tracing)
```

## Datasets API

### List Datasets

**Endpoint**: `GET /v1/dataops/datasets`

**Description**: Retrieve a paginated list of datasets with optional filtering.

**Query Parameters:**

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `client_id` | UUID | No | Filter by client | `?client_id=123e4567-e89b-12d3-a456-426614174000` |
| `journey_id` | UUID | No | Filter by journey | `?journey_id=123e4567-e89b-12d3-a456-426614174001` |
| `stage` | enum | No | Filter by stage | `?stage=sandbox` |
| `status` | enum | No | Filter by status | `?status=ready` |
| `dataset_type` | string | No | Filter by type | `?dataset_type=confluence_pages` |
| `page` | integer | No | Page number (default: 1) | `?page=2` |
| `per_page` | integer | No | Page size (default: 20, max: 100) | `?per_page=50` |

**Enum Values:**
- `stage`: `sandbox`, `pilot`, `production`
- `status`: `provisioning`, `validating`, `ready`, `failed`, `teardown`, `archived`

**Request Example:**
```bash
GET /v1/dataops/datasets?client_id=123e4567-e89b-12d3-a456-426614174000&stage=sandbox&status=ready
```

**Response: 200 OK**
```json
{
  "datasets": [
    {
      "dataset_id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "ACME-Sandbox-Confluence",
      "dataset_type": "confluence_pages",
      "stage": "sandbox",
      "client_id": "123e4567-e89b-12d3-a456-426614174000",
      "journey_id": "123e4567-e89b-12d3-a456-426614174001",
      "status": "ready",
      "created_at": "2026-01-28T10:30:00Z",
      "ready_at": "2026-01-28T11:15:00Z",
      "archived_at": null,
      "data_source": "mock_template",
      "record_count": 500,
      "size_bytes": 15728640,
      "quality_score": 98.5,
      "connector": {
        "connector_id": "660e8400-e29b-41d4-a716-446655440001",
        "name": "ACME-Sandbox-Confluence",
        "status": "healthy",
        "endpoint_url": "https://glean.acme.com/connectors/conf-001"
      },
      "template": {
        "template_id": "770e8400-e29b-41d4-a716-446655440002",
        "name": "FinTech Developer Productivity - Confluence"
      },
      "metadata": {
        "industry": "fintech",
        "use_case": "developer_productivity",
        "tags": ["sandbox", "mock", "testing"]
      },
      "_links": {
        "self": "/v1/dataops/datasets/550e8400-e29b-41d4-a716-446655440000",
        "quality": "/v1/dataops/datasets/550e8400-e29b-41d4-a716-446655440000/quality",
        "usage": "/v1/dataops/datasets/550e8400-e29b-41d4-a716-446655440000/usage",
        "teardown": "/v1/dataops/datasets/550e8400-e29b-41d4-a716-446655440000/teardown"
      }
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total_pages": 1,
    "total_count": 1
  },
  "_links": {
    "self": "/v1/dataops/datasets?client_id=123e4567-e89b-12d3-a456-426614174000&stage=sandbox&status=ready&page=1",
    "first": "/v1/dataops/datasets?client_id=123e4567-e89b-12d3-a456-426614174000&stage=sandbox&status=ready&page=1",
    "last": "/v1/dataops/datasets?client_id=123e4567-e89b-12d3-a456-426614174000&stage=sandbox&status=ready&page=1"
  }
}
```

### Get Dataset by ID

**Endpoint**: `GET /v1/dataops/datasets/{dataset_id}`

**Description**: Retrieve detailed information about a specific dataset.

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `dataset_id` | UUID | Yes | Dataset unique identifier |

**Request Example:**
```bash
GET /v1/dataops/datasets/550e8400-e29b-41d4-a716-446655440000
```

**Response: 200 OK** (same schema as list datasets item)

**Response: 404 Not Found**
```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "Dataset not found",
    "details": {
      "dataset_id": "550e8400-e29b-41d4-a716-446655440000"
    },
    "request_id": "req-123",
    "timestamp": "2026-01-28T12:00:00Z"
  }
}
```

### Create Dataset (Provision)

**Endpoint**: `POST /v1/dataops/datasets`

**Description**: Initiate dataset provisioning for a client journey stage. This is an asynchronous operation that returns immediately with operation tracking details.

**Request Headers:**
```
Authorization: Bearer {token}
Content-Type: application/json
Idempotency-Key: {uuid} (recommended)
```

**Request Body Schema:**
```json
{
  "journey_id": "uuid (required)",
  "client_id": "uuid (required)",
  "stage": "enum (required): sandbox | pilot | production",
  "dataset_types": ["string (required): array of dataset types"],
  "template_selection": "string (optional): auto | manual (default: auto)",
  "template_overrides": {
    "dataset_type": "template_id (optional)"
  },
  "metadata": {
    "requested_by": "string (optional)",
    "reason": "string (optional)",
    "custom_fields": {}
  }
}
```

**Request Example:**
```bash
POST /v1/dataops/datasets
Authorization: Bearer eyJhbGc...
Content-Type: application/json
Idempotency-Key: 880e8400-e29b-41d4-a716-446655440003

{
  "journey_id": "123e4567-e89b-12d3-a456-426614174001",
  "client_id": "123e4567-e89b-12d3-a456-426614174000",
  "stage": "sandbox",
  "dataset_types": ["confluence_pages", "github_repos"],
  "template_selection": "auto",
  "metadata": {
    "requested_by": "john.doe@acme.com",
    "reason": "sandbox_stage_transition"
  }
}
```

**Response: 202 Accepted**
```json
{
  "operation_id": "990e8400-e29b-41d4-a716-446655440004",
  "status": "provisioning",
  "message": "Dataset provisioning started",
  "datasets": [
    {
      "dataset_id": "550e8400-e29b-41d4-a716-446655440005",
      "dataset_type": "confluence_pages",
      "status": "provisioning"
    },
    {
      "dataset_id": "550e8400-e29b-41d4-a716-446655440006",
      "dataset_type": "github_repos",
      "status": "provisioning"
    }
  ],
  "estimated_completion": "2026-01-28T12:30:00Z",
  "_links": {
    "status": "/v1/dataops/operations/990e8400-e29b-41d4-a716-446655440004",
    "datasets": "/v1/dataops/datasets?journey_id=123e4567-e89b-12d3-a456-426614174001"
  }
}
```

**Error Responses:**

**400 Bad Request** - Invalid request
```json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "Request validation failed",
    "details": {
      "dataset_types": "Must provide at least one dataset type"
    }
  }
}
```

**409 Conflict** - Dataset already exists
```json
{
  "error": {
    "code": "CONFLICT",
    "message": "Dataset already exists",
    "details": {
      "existing_dataset_id": "550e8400-e29b-41d4-a716-446655440000",
      "conflict": "Dataset of type 'confluence_pages' already exists for client/stage"
    }
  }
}
```

### Update Dataset Metadata

**Endpoint**: `PATCH /v1/dataops/datasets/{dataset_id}`

**Description**: Update dataset metadata (tags, custom fields). Does not modify core dataset properties.

**Request Body:**
```json
{
  "metadata": {
    "tags": ["updated", "validated"],
    "custom_field": "value"
  }
}
```

**Response: 200 OK** (returns updated dataset)

### Delete Dataset (Teardown)

**Endpoint**: `DELETE /v1/dataops/datasets/{dataset_id}`

**Description**: Initiate dataset teardown, including connector disconnection, data archival, and cleanup.

**Query Parameters:**

| Parameter | Type | Required | Description | Default |
|-----------|------|----------|-------------|---------|
| `reason` | enum | No | Reason for teardown | `manual` |
| `archive` | boolean | No | Archive before delete | `true` |

**Enum Values for `reason`:**
- `stage_transition`: Journey moved to new stage
- `journey_completed`: Journey ended
- `orphan_cleanup`: Automated orphan detection
- `manual`: Manual deletion

**Request Example:**
```bash
DELETE /v1/dataops/datasets/550e8400-e29b-41d4-a716-446655440000?reason=stage_transition&archive=true
```

**Response: 202 Accepted**
```json
{
  "operation_id": "aa0e8400-e29b-41d4-a716-446655440007",
  "status": "tearing_down",
  "message": "Dataset teardown initiated",
  "estimated_completion": "2026-01-28T11:00:00Z",
  "_links": {
    "status": "/v1/dataops/operations/aa0e8400-e29b-41d4-a716-446655440007"
  }
}
```

## Quality API

### Get Quality Score

**Endpoint**: `GET /v1/dataops/datasets/{dataset_id}/quality`

**Description**: Retrieve the current quality score and detailed check results for a dataset.

**Response: 200 OK**
```json
{
  "dataset_id": "550e8400-e29b-41d4-a716-446655440000",
  "overall_score": 98.5,
  "meets_threshold": true,
  "threshold": 95.0,
  "calculated_at": "2026-01-28T11:15:00Z",
  "checks": {
    "schema_validation": {
      "score": 100.0,
      "weight": 0.30,
      "status": "passed",
      "details": "All 500 records match schema",
      "executed_at": "2026-01-28T11:10:00Z"
    },
    "data_completeness": {
      "score": 98.0,
      "weight": 0.30,
      "status": "passed",
      "details": "490/500 records fully populated (98%)",
      "executed_at": "2026-01-28T11:11:00Z"
    },
    "connector_health": {
      "score": 100.0,
      "weight": 0.25,
      "status": "passed",
      "details": "Connector healthy, response time 1.2s",
      "executed_at": "2026-01-28T11:12:00Z"
    },
    "sample_query_success": {
      "score": 100.0,
      "weight": 0.15,
      "status": "passed",
      "details": "10/10 test queries successful",
      "executed_at": "2026-01-28T11:13:00Z"
    }
  },
  "_links": {
    "dataset": "/v1/dataops/datasets/550e8400-e29b-41d4-a716-446655440000",
    "revalidate": "/v1/dataops/datasets/550e8400-e29b-41d4-a716-446655440000/quality/validate"
  }
}
```

### Trigger Quality Validation

**Endpoint**: `POST /v1/dataops/datasets/{dataset_id}/quality/validate`

**Description**: Manually trigger quality validation checks. Use `force_revalidation` to re-run even if recent validation exists.

**Request Body:**
```json
{
  "checks": ["schema_validation", "data_completeness", "connector_health", "sample_query_success"],
  "force_revalidation": false
}
```

**Check Types:**
- `schema_validation`: Validate all records match schema (100% required)
- `data_completeness`: Check record count and field completeness (>95% required)
- `connector_health`: Test connection, auth, response time (<5s required)
- `sample_query_success`: Execute 10 test queries (100% success required)

**Response: 202 Accepted**
```json
{
  "operation_id": "bb0e8400-e29b-41d4-a716-446655440008",
  "status": "validating",
  "message": "Quality validation started",
  "estimated_completion": "2026-01-28T11:20:00Z",
  "_links": {
    "status": "/v1/dataops/operations/bb0e8400-e29b-41d4-a716-446655440008",
    "results": "/v1/dataops/datasets/550e8400-e29b-41d4-a716-446655440000/quality"
  }
}
```

### Get Quality History

**Endpoint**: `GET /v1/dataops/datasets/{dataset_id}/quality/history`

**Description**: Retrieve historical quality check results for trend analysis.

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `from` | ISO 8601 | No | Start date/time |
| `to` | ISO 8601 | No | End date/time |
| `check_type` | enum | No | Filter by check type |

**Response: 200 OK**
```json
{
  "dataset_id": "550e8400-e29b-41d4-a716-446655440000",
  "history": [
    {
      "check_id": "cc0e8400-e29b-41d4-a716-446655440009",
      "check_type": "schema_validation",
      "score": 100.0,
      "status": "passed",
      "executed_at": "2026-01-28T11:10:00Z",
      "duration_ms": 4523
    },
    {
      "check_id": "dd0e8400-e29b-41d4-a716-446655440010",
      "check_type": "data_completeness",
      "score": 98.0,
      "status": "passed",
      "executed_at": "2026-01-28T11:11:00Z",
      "duration_ms": 3821
    }
  ],
  "_links": {
    "dataset": "/v1/dataops/datasets/550e8400-e29b-41d4-a716-446655440000"
  }
}
```

## Templates API

### List Templates

**Endpoint**: `GET /v1/dataops/templates`

**Description**: Retrieve available dataset templates filtered by industry, use case, or dataset type.

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `industry` | enum | No | Filter by industry |
| `use_case` | string | No | Filter by use case |
| `dataset_type` | string | No | Filter by dataset type |

**Industries:** `fintech`, `healthcare`, `enterprise`, `manufacturing`, `retail`

**Response: 200 OK**
```json
{
  "templates": [
    {
      "template_id": "770e8400-e29b-41d4-a716-446655440002",
      "name": "FinTech Developer Productivity - Confluence",
      "dataset_type": "confluence_pages",
      "industry": "fintech",
      "use_case": "developer_productivity",
      "description": "Mock Confluence pages for FinTech companies focused on developer productivity",
      "default_record_count": 500,
      "estimated_size_mb": 15,
      "_links": {
        "self": "/v1/dataops/templates/770e8400-e29b-41d4-a716-446655440002"
      }
    }
  ],
  "total_count": 15
}
```

### Get Template Recommendations

**Endpoint**: `POST /v1/dataops/templates/recommend`

**Description**: Get AI-powered template recommendations based on client metadata.

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
      "recommended_template": {
        "template_id": "770e8400-e29b-41d4-a716-446655440002",
        "name": "FinTech Developer Productivity - Confluence"
      },
      "confidence_score": 0.95,
      "reason": "Exact match on industry and use_case"
    }
  ]
}
```

## Operations API

### Get Operation Status

**Endpoint**: `GET /v1/dataops/operations/{operation_id}`

**Description**: Track the status of asynchronous operations (provisioning, validation, teardown).

**Response: 200 OK (In Progress)**
```json
{
  "operation_id": "990e8400-e29b-41d4-a716-446655440004",
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
    "self": "/v1/dataops/operations/990e8400-e29b-41d4-a716-446655440004"
  }
}
```

**Response: 200 OK (Completed)**
```json
{
  "operation_id": "990e8400-e29b-41d4-a716-446655440004",
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
        "dataset_id": "550e8400-e29b-41d4-a716-446655440005",
        "dataset_type": "confluence_pages",
        "status": "ready",
        "quality_score": 98.5
      }
    ]
  },
  "_links": {
    "datasets": "/v1/dataops/datasets?operation_id=990e8400-e29b-41d4-a716-446655440004"
  }
}
```

## SDK Examples

### Python SDK

```python
from a_domain_sdk import DataOpsClient

# Initialize client
client = DataOpsClient(
    client_id="your-client-id",
    client_secret="your-client-secret"
)

# Provision dataset
operation = client.datasets.create(
    journey_id="123e4567-e89b-12d3-a456-426614174001",
    client_id="123e4567-e89b-12d3-a456-426614174000",
    stage="sandbox",
    dataset_types=["confluence_pages"]
)

# Poll for completion
while not operation.is_complete():
    time.sleep(5)
    operation.refresh()

# Get dataset
dataset = operation.result.datasets[0]
print(f"Dataset ready: {dataset.quality_score}% quality")

# Check quality
quality = client.datasets.get_quality(dataset.dataset_id)
print(f"Schema validation: {quality.checks.schema_validation.score}%")

# Teardown dataset
client.datasets.delete(dataset.dataset_id, reason="stage_transition")
```

### JavaScript SDK

```javascript
const { DataOpsClient } = require('@a-domain/sdk');

const client = new DataOpsClient({
  clientId: 'your-client-id',
  clientSecret: 'your-client-secret'
});

// Provision dataset
const operation = await client.datasets.create({
  journeyId: '123e4567-e89b-12d3-a456-426614174001',
  clientId: '123e4567-e89b-12d3-a456-426614174000',
  stage: 'sandbox',
  datasetTypes: ['confluence_pages']
});

// Wait for completion
await operation.wait();

// Get dataset
const dataset = operation.result.datasets[0];
console.log(`Dataset ready: ${dataset.qualityScore}% quality`);

// Teardown
await client.datasets.delete(dataset.datasetId, { reason: 'stage_transition' });
```

---

**Related Documents:**
- ARCH-004: Data Architecture - DataOps Lifecycle
- DDD-003: DataOps Lifecycle - Bounded Context
- DES-004: Dataset Discovery & Registry - API Design

**Implements Stories:**
- P0-A2A-F2-001: Dataset Discovery & Registry
- P0-A2A-F2-002: Provisioning & Teardown Automation

**Referenced By:**
- P0-A2A-F2-000: Requirements Chat - DataOps Lifecycle
