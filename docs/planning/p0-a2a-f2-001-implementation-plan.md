# Implementation Plan: P0-A2A-F2-001 - Dataset Discovery & Registry

**Story ID**: P0-A2A-F2-001
**Priority**: P0
**Type**: Feature
**Estimated Effort**: 30 points (60 hours)
**Status**: Ready for Implementation
**Created**: 2026-01-28

## Overview

Implement the Dataset Discovery & Registry subsystem for the DataOps Lifecycle platform. This provides the foundational infrastructure for cataloging available datasets, schemas, and templates, enabling automated dataset provisioning.

### Purpose

Enable dataset visibility, reusability, and schema cataloging to support zero-touch dataset management that reduces provisioning time from 2-3 days to <1 hour.

### Prerequisites

**Dependencies (All Met ✅)**:
- P0-A2A-F1-002: Journey Orchestration - Unit of Work Executor
- P0-A2A-F2-000: Requirements Chat - DataOps Lifecycle

**Required Documentation**:
- ✅ ARCH-004: Data Architecture - DataOps Lifecycle
- ✅ DDD-003: DataOps Lifecycle - Bounded Context
- ✅ DES-004: Dataset Discovery & Registry - API Design
- ✅ TECH-004: DataOps Lifecycle - API Reference

## Implementation Tasks

### Task 1: Create DatasetRegistry Domain Model

**Status**: Not Started
**Estimated Time**: 12 hours
**Dependencies**: None
**Acceptance Criteria**: AC1, AC2

**Description**:
Implement the core domain model for the DatasetRegistry aggregate, including entities (Dataset, DatasetTemplate, DataQualityRule) and value objects (DatasetMetadata, QualityScore, ConnectorConfiguration).

**Implementation Steps**:

1. **Create directory structure**:
   ```
   sdlc_framework/dataops/
   ├── __init__.py
   ├── domain/
   │   ├── __init__.py
   │   ├── aggregates/
   │   │   ├── __init__.py
   │   │   └── dataset_registry.py
   │   ├── entities/
   │   │   ├── __init__.py
   │   │   ├── dataset.py
   │   │   ├── dataset_template.py
   │   │   └── data_quality_check.py
   │   ├── value_objects/
   │   │   ├── __init__.py
   │   │   ├── dataset_metadata.py
   │   │   ├── quality_score.py
   │   │   └── connector_configuration.py
   │   └── events/
   │       ├── __init__.py
   │       └── dataset_events.py
   ```

2. **Implement Dataset entity** (`dataset.py`):
   - UUID-based entity_id
   - Attributes: name, dataset_type, stage, client_id, journey_id, status, timestamps
   - Enums: DatasetType, Stage, DatasetStatus, DataSource
   - Methods: can_mark_ready(), update_quality_score(), validate_invariants()

3. **Implement DatasetTemplate entity** (`dataset_template.py`):
   - Template metadata (industry, use_case, dataset_type)
   - JSON schema definition
   - Default configuration (record_count, size_mb)
   - Quality rules association

4. **Implement DataQualityCheck entity** (`data_quality_check.py`):
   - Check types: schema_validation, data_completeness, connector_health, sample_query_success
   - Scoring (0-100.0)
   - Thresholds and pass/fail logic

5. **Implement Value Objects**:
   - `DatasetMetadata`: Industry, use_case, tags, custom_fields
   - `QualityScore`: Weighted calculation from 4 check types, meets_threshold logic
   - `ConnectorConfiguration`: Connector type, endpoint, auth method, config JSON

6. **Implement DatasetRegistry Aggregate** (`dataset_registry.py`):
   - Aggregate root with registry_version, last_updated, total_datasets
   - Invariants enforcement:
     - Only one active dataset per client/stage/type
     - Quality score ≥95% required for READY status
     - Connector name uniqueness
   - Business rules implementation

**Tests**:
```python
# Unit tests
pytest tests/unit/dataops/domain/test_dataset.py
pytest tests/unit/dataops/domain/test_dataset_template.py
pytest tests/unit/dataops/domain/test_quality_score.py

# Test cases:
# - Dataset state transitions (provisioning → validating → ready)
# - Quality score calculation (weighted average of 4 checks)
# - Invariant enforcement (quality threshold, uniqueness)
# - Dataset template schema validation
```

**Success Criteria**:
- All domain entities implement DDD patterns (Entity, ValueObject, Aggregate)
- Invariants prevent invalid states (quality <95% cannot be READY)
- All unit tests pass (>95% code coverage)

---

### Task 2: Implement DatasetDiscoveryAgent

**Status**: Not Started
**Estimated Time**: 16 hours
**Dependencies**: Task 1
**Acceptance Criteria**: AC1, AC4

**Description**:
Create the DatasetDiscoveryAgent that scans existing datasets, extracts schema information, and registers datasets in the catalog. Uses code_writer capabilities to analyze dataset structures.

**Implementation Steps**:

1. **Create agent infrastructure**:
   ```
   sdlc_framework/dataops/agents/
   ├── __init__.py
   ├── base_agent.py
   ├── dataset_discovery_agent.py
   ```

2. **Implement DatasetDiscoveryAgent**:
   - Agent trigger: Manual invocation or scheduled scan
   - Capabilities: File system access, schema inference, metadata extraction
   - Scan sources:
     - `medtronic_mock_data` repository templates
     - Existing Glean connector data (via API)
     - Custom dataset definitions

3. **Schema scanning logic**:
   ```python
   async def scan_dataset_schemas(source_path: Path) -> List[DatasetSchema]:
       # 1. Discover JSON/CSV files
       # 2. Infer schema from sample records
       # 3. Extract field types, required fields, relationships
       # 4. Generate JSON Schema definition
       # 5. Calculate default record count and size estimates
   ```

4. **Template registration**:
   ```python
   async def register_template(schema: DatasetSchema, metadata: dict) -> DatasetTemplate:
       # 1. Create DatasetTemplate entity
       # 2. Validate schema completeness
       # 3. Set quality rules based on template type
       # 4. Store in registry
       # 5. Emit DatasetTemplateRegistered event
   ```

5. **Sample data cataloging**:
   - Extract first N records from each dataset as sample
   - Store sample data with template for preview
   - Calculate statistics (avg field lengths, value distributions)

6. **Integration with medtronic_mock_data**:
   - Read templates from `mock_data/templates/{industry}/{use_case}/{dataset_type}.json`
   - Parse metadata section for industry/use_case mapping
   - Register each template with discovered schema

**Tests**:
```python
# Integration tests
pytest tests/integration/dataops/test_dataset_discovery.py

# Test cases:
# - Scan mock data templates directory
# - Infer schema from sample JSON files
# - Register template with correct metadata
# - Handle malformed/invalid templates gracefully
# - Emit correct domain events
```

**Success Criteria**:
- Agent successfully scans medtronic_mock_data templates
- Schema inference accuracy >90% (manual validation of sample)
- All templates registered with valid JSON schemas
- Sample data cataloged for each template

---

### Task 3: Build Dataset Registry Storage & Repository

**Status**: Not Started
**Estimated Time**: 14 hours
**Dependencies**: Task 1
**Acceptance Criteria**: AC2, AC3

**Description**:
Implement persistence layer for DatasetRegistry using SQLAlchemy ORM with PostgreSQL backend. Create repository pattern for aggregate access.

**Implementation Steps**:

1. **Create database schema**:
   ```
   sdlc_framework/dataops/infrastructure/
   ├── __init__.py
   ├── persistence/
   │   ├── __init__.py
   │   ├── models.py (SQLAlchemy models)
   │   ├── repositories/
   │   │   ├── __init__.py
   │   │   ├── dataset_repository.py
   │   │   └── template_repository.py
   │   └── migrations/
   │       └── versions/
   │           └── 001_create_dataset_tables.py
   ```

2. **Define SQLAlchemy models** (`models.py`):
   ```python
   class DatasetModel(Base):
       __tablename__ = 'datasets'
       id = Column(UUID, primary_key=True)
       name = Column(String(255), nullable=False)
       dataset_type = Column(Enum(DatasetType), nullable=False)
       stage = Column(Enum(Stage), nullable=False)
       client_id = Column(UUID, nullable=False)
       journey_id = Column(UUID, nullable=False)
       status = Column(Enum(DatasetStatus), nullable=False)
       quality_score = Column(Float)
       # ... additional fields

       __table_args__ = (
           UniqueConstraint('client_id', 'stage', 'dataset_type', name='uq_dataset_per_client_stage'),
           Index('idx_client_stage', 'client_id', 'stage'),
           Index('idx_journey', 'journey_id'),
       )
   ```

3. **Implement Repository pattern**:
   ```python
   class DatasetRepository:
       async def save(self, dataset: Dataset) -> None
       async def find_by_id(self, dataset_id: UUID) -> Optional[Dataset]
       async def find_by_client_and_stage(self, client_id: UUID, stage: Stage) -> List[Dataset]
       async def find_active_by_type(self, client_id: UUID, stage: Stage, dataset_type: DatasetType) -> Optional[Dataset]
       async def list_all(self, filters: DatasetFilters, pagination: Pagination) -> Page[Dataset]
   ```

4. **Create Alembic migration**:
   - Tables: datasets, dataset_templates, data_quality_checks, glean_connectors
   - Indexes for performance (client_id+stage, journey_id, status)
   - Foreign key constraints
   - Unique constraints for invariants

5. **Connection management**:
   - Database URL from environment config
   - Connection pooling (SQLAlchemy async engine)
   - Transaction management for aggregate consistency
   - Retry logic for transient failures

**Tests**:
```python
# Repository tests (with test database)
pytest tests/integration/dataops/persistence/test_dataset_repository.py

# Test cases:
# - Save and retrieve dataset
# - Enforce unique constraint (client/stage/type)
# - Pagination and filtering
# - Transaction rollback on error
# - Concurrent access handling
```

**Success Criteria**:
- All database tables created via migration
- Repository enforces aggregate invariants
- Query performance <100ms p95 for typical queries
- All persistence tests pass

---

### Task 4: Implement Dataset Registry REST API

**Status**: Not Started
**Estimated Time**: 18 hours
**Dependencies**: Task 2, Task 3
**Acceptance Criteria**: AC3

**Description**:
Build the RESTful API for dataset registry operations following the design in DES-004. Implements endpoints for listing datasets, retrieving templates, and querying the catalog.

**Implementation Steps**:

1. **Create FastAPI application structure**:
   ```
   sdlc_framework/dataops/api/
   ├── __init__.py
   ├── app.py (FastAPI app)
   ├── routes/
   │   ├── __init__.py
   │   ├── datasets.py
   │   ├── templates.py
   │   └── health.py
   ├── schemas/
   │   ├── __init__.py
   │   ├── dataset_schemas.py
   │   └── template_schemas.py
   ├── dependencies/
   │   ├── __init__.py
   │   ├── auth.py
   │   └── database.py
   └── middleware/
       ├── __init__.py
       └── error_handling.py
   ```

2. **Implement Datasets API** (`routes/datasets.py`):
   ```python
   # GET /v1/dataops/datasets
   @router.get("/datasets", response_model=DatasetListResponse)
   async def list_datasets(
       client_id: Optional[UUID],
       journey_id: Optional[UUID],
       stage: Optional[Stage],
       status: Optional[DatasetStatus],
       page: int = 1,
       per_page: int = 20,
       repo: DatasetRepository = Depends(get_dataset_repo)
   ):
       # Apply filters, pagination
       # Return paginated results with _links

   # GET /v1/dataops/datasets/{dataset_id}
   @router.get("/datasets/{dataset_id}", response_model=DatasetResponse)
   async def get_dataset(dataset_id: UUID, repo: DatasetRepository = Depends()):
       # Retrieve by ID
       # Return 404 if not found
   ```

3. **Implement Templates API** (`routes/templates.py`):
   ```python
   # GET /v1/dataops/templates
   @router.get("/templates", response_model=TemplateListResponse)
   async def list_templates(
       industry: Optional[str],
       use_case: Optional[str],
       dataset_type: Optional[str],
       repo: TemplateRepository = Depends()
   ):
       # Filter templates by criteria
       # Return list with metadata

   # GET /v1/dataops/templates/{template_id}
   @router.get("/templates/{template_id}", response_model=TemplateResponse)

   # POST /v1/dataops/templates/recommend
   @router.post("/templates/recommend", response_model=TemplateRecommendationsResponse)
   async def recommend_templates(request: RecommendationRequest):
       # Match client metadata to templates
       # Return ranked recommendations with confidence scores
   ```

4. **Pydantic schemas** (`schemas/dataset_schemas.py`):
   - Request/response models for all endpoints
   - Validation rules (field constraints, enum values)
   - HATEOAS links (_links field)
   - OpenAPI documentation annotations

5. **Authentication & Authorization** (`dependencies/auth.py`):
   - OAuth 2.0 Bearer token validation
   - Scope-based authorization (dataops:datasets:read, dataops:datasets:write)
   - Client ID extraction from token
   - Dependency injection for protected routes

6. **Error handling middleware**:
   - Standard error response format (RFC 7807 Problem Details)
   - HTTP status code mapping
   - Request ID tracking
   - Structured logging

7. **API documentation**:
   - Auto-generated OpenAPI schema (Swagger UI)
   - Endpoint descriptions and examples
   - Response schemas with field descriptions

**Tests**:
```python
# API tests (with TestClient)
pytest tests/api/dataops/test_datasets_api.py
pytest tests/api/dataops/test_templates_api.py

# Test cases:
# - List datasets with filters and pagination
# - Get dataset by ID (success and 404)
# - Get template recommendations
# - Authentication required for all endpoints
# - Proper error responses (400, 401, 404)
```

**Success Criteria**:
- All endpoints from DES-004 implemented
- OpenAPI spec matches design document
- Authentication enforced on all routes
- API tests achieve >90% coverage
- Response time <200ms p95

---

## Testing Plan

### Unit Tests

**Scope**: Domain model logic, business rules, value object calculations

**Test Files**:
- `tests/unit/dataops/domain/test_dataset.py`
- `tests/unit/dataops/domain/test_dataset_template.py`
- `tests/unit/dataops/domain/test_quality_score.py`
- `tests/unit/dataops/domain/test_dataset_registry.py`

**Key Test Cases**:
1. Dataset state machine transitions
2. Quality score calculation (weighted average)
3. Invariant enforcement (quality threshold, uniqueness)
4. Template schema validation
5. Business rule validation

**Coverage Target**: >95%

### Integration Tests

**Scope**: Agent behavior, repository persistence, external integration

**Test Files**:
- `tests/integration/dataops/test_dataset_discovery.py`
- `tests/integration/dataops/persistence/test_dataset_repository.py`
- `tests/integration/dataops/persistence/test_template_repository.py`

**Key Test Cases**:
1. Discovery agent scans mock data templates
2. Repository save/retrieve with database
3. Unique constraint enforcement
4. Transaction rollback behavior
5. Query performance under load

**Coverage Target**: >85%

### API Tests

**Scope**: REST API endpoints, request/response validation, auth

**Test Files**:
- `tests/api/dataops/test_datasets_api.py`
- `tests/api/dataops/test_templates_api.py`

**Key Test Cases**:
1. List datasets with filters (happy path)
2. Get dataset by ID (success and 404)
3. Template recommendations
4. Pagination edge cases
5. Authentication failures (401, 403)
6. Validation errors (400)

**Coverage Target**: >90%

### Functional Tests

**From Acceptance Criteria**:

**AC1: Discovery agent scans and catalogs datasets**
```bash
# Test command
python -m sdlc_framework.dataops.agents.dataset_discovery_agent scan \
  --source mock_data/templates

# Expected output
✅ Scanned 15 dataset templates
✅ Registered 15 templates in catalog
✅ Sample data extracted for all templates

# Success criteria
- All mock data templates discovered
- Schema inference successful for each
- Templates registered with correct metadata
```

**AC2: Schema registry contains all available datasets**
```bash
# Test command
curl http://localhost:8000/v1/dataops/templates \
  -H "Authorization: Bearer $TOKEN"

# Expected output (JSON)
{
  "templates": [
    {
      "template_id": "uuid",
      "name": "FinTech Developer Productivity - Confluence",
      "dataset_type": "confluence_pages",
      "industry": "fintech",
      "schema": { /* JSON Schema */ }
    }
    /* ... more templates */
  ],
  "total_count": 15
}

# Success criteria
- All 15 templates returned
- Each has valid JSON schema
- Metadata fields populated correctly
```

**AC3: API supports dataset queries**
```bash
# Test command
curl "http://localhost:8000/v1/dataops/datasets?client_id=$CLIENT_ID&stage=sandbox" \
  -H "Authorization: Bearer $TOKEN"

# Expected output (JSON)
{
  "datasets": [ /* filtered results */ ],
  "pagination": { "page": 1, "total_count": 5 }
}

# Success criteria
- Filtering works correctly
- Pagination functional
- Response time <200ms
```

**AC4: Sample data cataloged per dataset**
```bash
# Test command
curl http://localhost:8000/v1/dataops/templates/$TEMPLATE_ID \
  -H "Authorization: Bearer $TOKEN"

# Expected output (JSON)
{
  "template_id": "uuid",
  "name": "FinTech Developer Productivity - Confluence",
  "sample_data": [
    { "page_id": "1", "title": "Sample Page", /* ... */ }
  ],
  "default_record_count": 500
}

# Success criteria
- Sample data present for all templates
- Sample represents actual structure
- Statistics calculated (avg sizes, etc.)
```

---

## Risk Management

### Risk 1: Schema Inference Accuracy

**Probability**: MEDIUM
**Impact**: MEDIUM
**Description**: Automatic schema inference from JSON files may produce incorrect or incomplete schemas

**Mitigation**:
- Validate inferred schemas against known good examples
- Manual review of schemas for critical templates
- Schema refinement workflow for corrections
- Fallback to manual schema definition if inference fails

### Risk 2: Performance Degradation Under Load

**Probability**: LOW
**Impact**: MEDIUM
**Description**: Registry queries may slow down with large dataset counts (>1000 datasets)

**Mitigation**:
- Database indexes on common query patterns
- Connection pooling configured correctly
- Load testing before production deployment
- Query optimization based on EXPLAIN ANALYZE
- Caching layer for frequently accessed templates

### Risk 3: medtronic_mock_data Repository Structure Changes

**Probability**: LOW
**Impact**: LOW
**Description**: If mock data repository changes structure, discovery agent breaks

**Mitigation**:
- Version detection in discovery agent
- Support multiple template formats
- Graceful degradation if format unknown
- Integration tests validate against actual repository

### Risk 4: Concurrent Access to Registry

**Probability**: MEDIUM
**Impact**: MEDIUM
**Description**: Multiple agents/API calls updating registry simultaneously may cause conflicts

**Mitigation**:
- Optimistic locking with version field
- Database transaction isolation (READ COMMITTED)
- Retry logic for conflict errors
- Idempotency keys for write operations

---

## Timeline

**Total Effort**: 30 points = 60 hours (assumes 2 hours per point)

**Week 1** (32 hours):
- Task 1: Create DatasetRegistry Domain Model (12h)
- Task 2: Implement DatasetDiscoveryAgent (16h) - START
- Daily standup: Review progress, unblock issues

**Week 2** (28 hours):
- Task 2: Implement DatasetDiscoveryAgent (FINISH)
- Task 3: Build Registry Storage & Repository (14h)
- Task 4: Implement Dataset Registry REST API (18h) - START
- Mid-week review: Validate domain model with stakeholders

**Week 3** (Optional buffer - 4h):
- Task 4: Implement Dataset Registry REST API (FINISH)
- Integration testing
- Documentation updates
- Performance tuning

**Milestones**:
- ✅ Week 1 End: Domain model complete, discovery agent functional
- ✅ Week 2 Mid: Repository persistence working
- ✅ Week 2 End: API endpoints implemented, all tests passing

---

## Deliverables

### Code Artifacts

1. **Domain Model**:
   - `sdlc_framework/dataops/domain/` (entities, value objects, aggregates)
   - Full DDD implementation with invariants

2. **Agent Implementation**:
   - `sdlc_framework/dataops/agents/dataset_discovery_agent.py`
   - Schema inference and template registration logic

3. **Persistence Layer**:
   - `sdlc_framework/dataops/infrastructure/persistence/`
   - SQLAlchemy models, repositories, migrations

4. **REST API**:
   - `sdlc_framework/dataops/api/`
   - FastAPI routes, schemas, middleware

### Documentation

1. **API Documentation**:
   - Auto-generated OpenAPI spec (Swagger UI)
   - Matches DES-004 design

2. **Code Documentation**:
   - Docstrings for all public classes/methods
   - Type hints throughout

3. **Development Guide**:
   - README for dataops module
   - Setup instructions (database, dependencies)
   - Running tests locally

### Configuration

1. **Database Migration**:
   - Alembic migration script for schema creation
   - Seed data for test templates

2. **Environment Configuration**:
   - `.env.example` with required variables
   - Database connection settings
   - API authentication config

---

## Validation & Rollout

### Pre-Deployment Checklist

- [ ] All unit tests pass (>95% coverage)
- [ ] All integration tests pass (>85% coverage)
- [ ] All API tests pass (>90% coverage)
- [ ] Functional tests validate acceptance criteria
- [ ] Database migration tested on staging
- [ ] API performance <200ms p95
- [ ] OpenAPI spec matches design document
- [ ] Security review complete (auth, input validation)
- [ ] Code review approved

### Deployment Steps

1. **Database Setup**:
   ```bash
   alembic upgrade head  # Run migrations
   python scripts/seed_templates.py  # Load initial templates
   ```

2. **Service Deployment**:
   ```bash
   # Start API service
   uvicorn sdlc_framework.dataops.api.app:app --host 0.0.0.0 --port 8000
   ```

3. **Discovery Agent Initial Run**:
   ```bash
   # Scan and register mock data templates
   python -m sdlc_framework.dataops.agents.dataset_discovery_agent scan \
     --source /path/to/medtronic_mock_data/mock_data/templates
   ```

4. **Verification**:
   ```bash
   # Health check
   curl http://localhost:8000/health

   # Verify templates registered
   curl http://localhost:8000/v1/dataops/templates \
     -H "Authorization: Bearer $TOKEN"
   ```

### Rollback Plan

**If critical issues discovered**:

1. Stop API service
2. Rollback database migration: `alembic downgrade -1`
3. Remove registered templates: `python scripts/cleanup_registry.py`
4. Investigate issue in staging environment
5. Fix and redeploy

**Rollback triggers**:
- API error rate >5%
- Database corruption detected
- Authentication bypass discovered
- Performance degradation >2x baseline

---

## Dependencies on Other Stories

**Blocks**:
- P0-A2A-F2-002: Provisioning & Teardown Automation (requires registry to query templates)

**Blocked By** (All Complete ✅):
- ✅ P0-A2A-F1-002: Journey Orchestration - Unit of Work Executor
- ✅ P0-A2A-F2-000: Requirements Chat - DataOps Lifecycle

**Related**:
- P0-A2A-F7-001: Agent Protocol Bridge (will use registry for agent discovery)

---

## Success Metrics

**Development Metrics**:
- All acceptance criteria met: AC1, AC2, AC3, AC4
- Test coverage: Unit >95%, Integration >85%, API >90%
- Code review: 0 critical issues, <5 minor issues
- Documentation: 100% public API documented

**Performance Metrics**:
- Registry query latency: <100ms p95
- API response time: <200ms p95
- Template discovery: <30 seconds for 15 templates
- Database query efficiency: All queries use indexes

**Operational Metrics**:
- Discovery agent success rate: 100% (all templates scanned)
- API uptime: >99.9% (during development/testing)
- Error rate: <1% (API and agent operations)

---

**Implementation Start Date**: TBD (upon plan approval)
**Target Completion Date**: TBD (2-3 weeks from start)
**Plan Version**: 1.0
**Last Updated**: 2026-01-28
