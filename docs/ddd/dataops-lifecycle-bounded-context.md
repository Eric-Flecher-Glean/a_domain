# DataOps Lifecycle - Bounded Context

**Document ID**: DDD-003
**Status**: Current
**Created**: 2026-01-20
**Last Updated**: 2026-01-28
**Authors**: Domain Modeling Team, Requirements Chat (AI-Generated)

## Bounded Context Overview

### Context Name
**DataOps Lifecycle**

### Purpose
Manages the complete lifecycle of datasets from discovery through teardown, ensuring stage-appropriate data quality, automated provisioning, and zero-touch cleanup for client environments across sandbox/pilot/production stages.

### Strategic Classification
**Supporting Domain** - Provides essential infrastructure for client journey orchestration but is not core business differentiator. Automates repetitive dataset management tasks that were previously manual.

## Context Map

### Upstream Dependencies (Consumers)

```
┌─────────────────────────────────────────────────────────┐
│                 DataOps Lifecycle Context                │
│                    (Supporting Domain)                   │
└─────────────────────────────────────────────────────────┘
            ▲                    ▲                    ▲
            │                    │                    │
      [Customer-                │              [Conformist]
       Supplier]                │
            │              [Customer-
    ┌───────┴───────┐      Supplier]         ┌──────────────┐
    │  medtronic_   │           │             │ knowledge_   │
    │  mock_data    │    ┌──────┴──────┐     │ labor_obs... │
    │               │    │    sdlc     │     │              │
    │  Provides:    │    │             │     │  Consumes:   │
    │  • Templates  │    │  Provides:  │     │  • Usage     │
    │  • Mock Data  │    │  • Test     │     │    Metrics   │
    │               │    │    Specs    │     │  • Quality   │
    └───────────────┘    │  • Validators│    │    Data      │
                         └─────────────┘     └──────────────┘
```

### Downstream Dependencies (Providers)

```
┌─────────────────────────────────────────────────────────┐
│                 DataOps Lifecycle Context                │
└─────────────────────────────────────────────────────────┘
                         │
                         │ [Published Language:
                         │  Domain Events]
                         │
            ┌────────────┴────────────┐
            ▼                         ▼
    ┌───────────────┐         ┌──────────────┐
    │   a_domain    │         │   Clients    │
    │  (Journey     │         │              │
    │ Orchestration)│         │  Consumes:   │
    │               │         │  • Datasets  │
    │  Consumes:    │         │  • Glean     │
    │  • Events     │         │    Connectors│
    │  • Dataset    │         └──────────────┘
    │    Status     │
    └───────────────┘
```

### Integration Patterns

| Relationship | Pattern | Direction | Description |
|-------------|---------|-----------|-------------|
| medtronic_mock_data | Customer-Supplier | Upstream | Consumes mock data templates (read-only) |
| sdlc | Customer-Supplier | Upstream | Consumes test specs, provides test data |
| knowledge_labor_obs | Conformist | Upstream | Conforms to metrics schema, publishes events |
| a_domain | Published Language | Downstream | Publishes domain events for orchestration |
| Clients | Published Language | Downstream | Provides datasets via Glean connectors |

## Ubiquitous Language

### Core Terms

| Term | Definition | Usage Context |
|------|------------|---------------|
| **Dataset** | A collection of records of a specific type (e.g., Confluence pages, GitHub repos) provisioned for a client stage | "The sandbox dataset contains 500 mock Confluence pages" |
| **Dataset Lifecycle** | The complete journey from discovery → provisioning → validation → ready → teardown → archived | "Monitor dataset lifecycle dashboards to track active datasets" |
| **Provisioning** | The process of creating a dataset, populating it with data, and configuring connectors | "Dataset provisioning completes in under 60 minutes" |
| **Quality Score** | Calculated metric (0-100%) measuring dataset readiness based on schema, completeness, connector health, and query success | "Dataset requires quality score ≥95% to be marked ready" |
| **Stage** | Client journey phase: sandbox (mock data), pilot (sanitized production), or production (real data) | "Sandbox stage uses 100% synthetic mock data" |
| **Dataset Template** | Predefined schema and sample data for a specific industry/use-case combination | "Use FinTech Developer Productivity template for sandbox" |
| **Connector** | Glean data source connection configured to ingest dataset records | "ACME-Sandbox-Confluence connector syncs 500 pages" |
| **Teardown** | Safe removal of dataset including connector disconnection, data archival, and cleanup | "Teardown triggers on stage transition to pilot" |
| **Mock Data** | Synthetic, realistic data sourced from templates with no real PII | "Mock data ensures reproducible testing scenarios" |
| **Sanitized Production** | Production-like data with PII anonymized for pilot stage | "Sanitized production data maintains usage patterns" |
| **Quality Check** | Automated validation (schema, completeness, connector health, queries) | "4 quality checks must pass before dataset marked ready" |
| **Orphaned Dataset** | Dataset not cleaned up after journey completion or stage transition | "Daily scan detects orphaned datasets for cleanup" |

### Agent-Specific Language

| Term | Agent | Definition |
|------|-------|------------|
| **Dataset Discovery** | DatasetDiscoveryAgent | Scanning existing datasets to catalog schemas and templates |
| **Dataset Catalog** | DatasetDiscoveryAgent | Registry of available dataset types, schemas, and templates |
| **Dataset Provisioning** | DatasetProvisioningAgent | Creating datasets from templates and populating with data |
| **Connector Configuration** | DatasetProvisioningAgent | Automated setup of Glean data source connectors |
| **Data Quality Validation** | DataValidationAgent | Running quality checks to ensure dataset readiness |
| **Sample Query Execution** | DataValidationAgent | Testing dataset searchability with predefined queries |
| **Dataset Archival** | DataTeardownAgent | Safely storing dataset metadata for audit/compliance |
| **Connector Cleanup** | DataTeardownAgent | Disconnecting and deleting Glean connectors |

## Aggregates

### DatasetRegistry Aggregate

**Aggregate Root**: DatasetRegistry

**Entities:**
- Dataset
- DatasetTemplate
- DataQualityRule

**Value Objects:**
- DatasetMetadata
- QualityScore
- ConnectorConfiguration

**Invariants:**
1. All datasets must belong to a valid client and stage
2. Quality score must be ≥95% before dataset status = READY
3. Only one active dataset of each type per client per stage
4. Connector name must be unique across all stages
5. Archived datasets are immutable (cannot transition back to active)

**Business Rules:**
1. **Stage Transition Rule**: When journey transitions to new stage, teardown all previous stage datasets
2. **Quality Threshold Rule**: Dataset cannot be marked READY until all 4 quality checks pass
3. **Connector Health Rule**: Connector must remain healthy or dataset reverts to VALIDATING
4. **Orphan Prevention Rule**: Daily scan archives datasets with no associated active journey
5. **Template Selection Rule**: Dataset type and client industry/use-case determine template

### Domain Events

```yaml
DatasetProvisionRequested:
  event_id: UUID
  journey_id: UUID
  client_id: UUID
  stage: enum [sandbox, pilot, production]
  dataset_types: [string]
  requested_at: timestamp
  requested_by: actor

DatasetProvisioningStarted:
  event_id: UUID
  dataset_id: UUID
  journey_id: UUID
  template_id: UUID
  stage: enum
  started_at: timestamp

DatasetProvisionCompleted:
  event_id: UUID
  dataset_id: UUID
  journey_id: UUID
  quality_score: float
  record_count: integer
  connector_id: UUID
  completed_at: timestamp
  duration_minutes: integer

DatasetValidationFailed:
  event_id: UUID
  dataset_id: UUID
  journey_id: UUID
  failed_checks: [check_type]
  error_message: text
  failed_at: timestamp

DatasetReady:
  event_id: UUID
  dataset_id: UUID
  journey_id: UUID
  quality_score: float
  ready_at: timestamp

DatasetTeardownStarted:
  event_id: UUID
  dataset_id: UUID
  journey_id: UUID
  reason: enum [stage_transition, journey_completed, orphan_cleanup, manual]
  started_at: timestamp

DatasetArchived:
  event_id: UUID
  dataset_id: UUID
  journey_id: UUID
  archive_location: string
  archived_at: timestamp
  original_size_bytes: integer
```

## Domain Services

### DatasetProvisioningService

**Responsibilities:**
- Orchestrate multi-step provisioning workflow
- Select appropriate template based on client metadata
- Coordinate with medtronic_mock_data for mock data retrieval
- Create and configure Glean connectors
- Trigger quality validation

**Operations:**
```
provisionDataset(journey_id, stage, dataset_types) -> Dataset
  1. Load client metadata from journey
  2. Select templates matching client industry/use-case
  3. Create connector with naming convention: {client}-{stage}-{type}
  4. Populate dataset from template (mock or sanitized)
  5. Initiate quality validation
  6. Publish DatasetProvisioningStarted event

selectTemplate(client_metadata, dataset_type) -> DatasetTemplate
  Matches client industry/use-case to appropriate template

populateFromTemplate(dataset, template) -> void
  Uploads records from template to connector
```

### DataValidationService

**Responsibilities:**
- Execute 4 quality checks: schema, completeness, connector health, sample queries
- Calculate overall quality score
- Determine dataset readiness
- Track quality trends over time

**Operations:**
```
validateDataset(dataset_id) -> QualityScore
  1. Run schemaValidation -> score_1
  2. Run dataCompletenessCheck -> score_2
  3. Run connectorHealthCheck -> score_3
  4. Run sampleQueryTests -> score_4
  5. Calculate overall score (weighted average)
  6. Update dataset.quality_score
  7. If score >= 95%, mark dataset READY, else FAILED

runSchemaValidation(dataset_id) -> DataQualityCheck
  Validates all records match expected schema (100% required)

runDataCompletenessCheck(dataset_id) -> DataQualityCheck
  Validates record count and field completeness (>95% required)

runConnectorHealthCheck(connector_id) -> DataQualityCheck
  Tests connection, auth, response time (<5s required)

runSampleQueries(dataset_id) -> DataQualityCheck
  Executes 10 predefined queries (100% success required)
```

### DataTeardownService

**Responsibilities:**
- Safely remove datasets when no longer needed
- Archive dataset metadata for audit/compliance
- Disconnect and delete Glean connectors
- Verify complete cleanup

**Operations:**
```
teardownDataset(dataset_id, reason) -> void
  1. Update dataset.status = TEARDOWN
  2. Pause connector sync
  3. Archive dataset metadata to audit storage
  4. Disconnect connector via Glean API
  5. Delete connector (after 24h grace period)
  6. Update dataset.status = ARCHIVED
  7. Publish DatasetArchived event

archiveDatasetMetadata(dataset_id) -> archive_location
  Saves dataset config, quality history, usage metrics to S3

cleanupOrphanedDatasets() -> [Dataset]
  Daily job: finds datasets with no active journey, initiates teardown
```

## Context Boundaries

### Internal Responsibilities

✅ **Owned by DataOps Lifecycle:**
- Dataset lifecycle state management
- Data quality calculation and validation
- Connector configuration and health monitoring
- Dataset-template matching logic
- Archive and cleanup automation
- Quality check execution
- Mock data integration

### External Responsibilities

❌ **NOT owned by DataOps Lifecycle:**
- Client journey state management (owned by a_domain/Journey Orchestration)
- Mock data template creation (owned by medtronic_mock_data)
- Glean platform infrastructure (external SaaS)
- Test specification definitions (owned by sdlc)
- Business metrics tracking (owned by knowledge_labor_observability_metrics)

### Anti-Corruption Layer

**Glean API Integration:**
```yaml
AntiCorruptionLayer_Glean:
  purpose: Isolate DataOps from Glean API changes
  components:
    - GleanConnectorAdapter: Translates internal connector model to Glean API
    - GleanHealthCheckAdapter: Normalizes health status responses
    - GleanQueryAdapter: Standardizes query interface

  internal_model: Dataset, GleanConnector (domain entities)
  external_model: Glean REST API responses

  translation_examples:
    - internal: connector.status = HEALTHY
      external: Glean API response.connector.state = "active" AND response.last_sync.status = "success"
```

## Bounded Context Responsibilities

### Core Capabilities

1. **Dataset Discovery**: Catalog available dataset types, schemas, templates
2. **Automated Provisioning**: Zero-touch dataset creation in <1 hour
3. **Quality Assurance**: 4-tier validation ensuring 95%+ quality
4. **Connector Management**: Auto-create, configure, monitor, cleanup Glean connectors
5. **Lifecycle Orchestration**: Manage full dataset journey from request to archive
6. **Stage Transition Handling**: Automatic teardown/reprovisioning on stage changes
7. **Orphan Detection**: Daily cleanup of datasets with no active journey

### Business Rules Summary

| Rule | Description | Enforcement |
|------|-------------|-------------|
| Stage Appropriateness | Sandbox=mock, Pilot=sanitized, Prod=real | Template selection logic |
| Quality Threshold | Quality score ≥95% required for READY status | QualityScore invariant |
| Connector Uniqueness | One connector per client/stage/type | DatasetRegistry invariant |
| Automatic Cleanup | Teardown on stage transition | Event handler |
| Orphan Prevention | Archive datasets with no journey (daily scan) | Scheduled job |
| Audit Trail | All lifecycle events logged for 90 days | Event publishing |

## Success Metrics

### Business Metrics
- **Dataset Provisioning Time**: Target <1 hour (baseline 2-3 days)
- **Data Quality Issues**: Target <2% (baseline 15%)
- **Connector Misconfiguration Rate**: Target <1% (baseline 25%)
- **SE Time Saved per Client**: Target 0.5 hours (baseline 8 hours)

### Operational Metrics
- **Quality Score Distribution**: ≥90% of datasets score ≥95%
- **Provisioning Success Rate**: ≥98% first-time success
- **Teardown Completion Rate**: 100% cleanup within 24h
- **Orphaned Dataset Count**: <5 active orphans at any time

### Performance Metrics
- **Provisioning Duration**: p95 <60 minutes
- **Quality Check Duration**: p95 <15 minutes
- **Teardown Duration**: p95 <15 minutes
- **Registry Query Latency**: p95 <100ms

## Context Evolution

### Current State (v1.0)
- Manual template selection
- Fixed quality thresholds
- Single-region deployment
- Snapshot-based archival

### Planned Evolution (v2.0)
- ML-based template recommendation
- Configurable quality rules per client
- Multi-region dataset replication
- Incremental dataset updates
- Cost optimization tracking

---

**Related Documents:**
- ARCH-004: Data Architecture - DataOps Lifecycle
- DES-004: Dataset Discovery & Registry - API Design
- TECH-004: DataOps Lifecycle - API Reference
- ARCH-001: DDD Specification - Agent-to-Agent Platform

**Implemented By Stories:**
- P0-A2A-F2-001: Dataset Discovery & Registry
- P0-A2A-F2-002: Provisioning & Teardown Automation

**Referenced By:**
- P0-A2A-F2-000: Requirements Chat - DataOps Lifecycle
