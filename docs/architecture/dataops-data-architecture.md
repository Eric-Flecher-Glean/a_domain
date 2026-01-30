# Data Architecture - DataOps Lifecycle

**Document ID**: ARCH-004
**Status**: Current
**Created**: 2026-01-18
**Last Updated**: 2026-01-28
**Authors**: Data Architecture Team, Requirements Chat (AI-Generated)

## Overview

This document defines the data architecture for the DataOps Lifecycle system, which automates the full lifecycle of dataset creation, testing, population, and teardown for client environments across sandbox/pilot/production stages.

### Purpose

Enable zero-touch dataset management that reduces dataset provisioning time from 2-3 days to <1 hour while ensuring data quality >95% and eliminating connector misconfiguration issues.

### Bounded Context

**DataOps Lifecycle** - Manages the complete lifecycle of datasets from discovery through teardown, ensuring stage-appropriate data quality and automated cleanup.

## Data Models

### Core Aggregates

#### DatasetRegistry Aggregate

The central registry tracking all datasets across all client stages.

```yaml
DatasetRegistry:
  aggregate_id: dataset_registry_id (UUID)
  attributes:
    registry_version: semantic_version
    last_updated: timestamp
    total_datasets: integer
  entities:
    - Dataset
    - DatasetTemplate
    - DataQualityRule
  value_objects:
    - DatasetMetadata
    - QualityScore
    - ConnectorConfiguration
```

#### Dataset Entity

```yaml
Dataset:
  entity_id: dataset_id (UUID)
  attributes:
    name: string
    dataset_type: enum [confluence_pages, github_repos, slack_messages, jira_issues, custom]
    stage: enum [sandbox, pilot, production]
    client_id: UUID
    journey_id: UUID
    status: enum [provisioning, ready, validating, failed, archived, teardown]
    created_at: timestamp
    ready_at: timestamp
    archived_at: timestamp
    data_source: enum [mock_template, sanitized_production, custom]
    record_count: integer
    size_bytes: integer
    quality_score: float (0.0-100.0)
    connector_id: UUID
  relationships:
    - template: DatasetTemplate (optional)
    - quality_checks: [DataQualityCheck]
    - usage_metrics: [DatasetUsageMetric]
```

#### DatasetTemplate Entity

```yaml
DatasetTemplate:
  entity_id: template_id (UUID)
  attributes:
    name: string
    dataset_type: enum [confluence_pages, github_repos, slack_messages, jira_issues, custom]
    industry: enum [fintech, healthcare, enterprise, manufacturing, retail]
    use_case: string
    description: text
    source_path: string (path to mock data file)
    schema_definition: json_schema
    default_record_count: integer
    metadata_template: json
    quality_rules: [DataQualityRule]
  relationships:
    - datasets: [Dataset] (instances created from this template)
```

#### DataQualityCheck Entity

```yaml
DataQualityCheck:
  entity_id: check_id (UUID)
  attributes:
    dataset_id: UUID
    check_type: enum [schema_validation, data_completeness, connector_health, sample_query_success]
    status: enum [pending, running, passed, failed]
    executed_at: timestamp
    result: json
    score: float (0.0-100.0)
    threshold: float (0.0-100.0)
    passed: boolean
    error_message: text (optional)
```

#### GleanConnector Entity

```yaml
GleanConnector:
  entity_id: connector_id (UUID)
  attributes:
    name: string (e.g., "ACME-Sandbox-Confluence")
    client_id: UUID
    stage: enum [sandbox, pilot, production]
    connector_type: enum [confluence, github, slack, jira, gdrive, custom]
    status: enum [creating, healthy, unhealthy, disconnected, archived]
    endpoint_url: string
    authentication: json (encrypted)
    health_check_interval: duration
    last_health_check: timestamp
    health_status: json
  relationships:
    - dataset: Dataset
```

### Value Objects

#### DatasetMetadata

```yaml
DatasetMetadata:
  attributes:
    industry: string
    use_case: string
    data_type: enum [mock, sanitized_production, production]
    stage: enum [sandbox, pilot, production]
    tags: [string]
    custom_fields: json
```

#### QualityScore

```yaml
QualityScore:
  attributes:
    overall_score: float (0.0-100.0)
    schema_validation_score: float (0.0-100.0)
    data_completeness_score: float (0.0-100.0)
    connector_health_score: float (0.0-100.0)
    query_success_score: float (0.0-100.0)
    calculated_at: timestamp
    meets_threshold: boolean (>= 95%)
```

#### ConnectorConfiguration

```yaml
ConnectorConfiguration:
  attributes:
    connector_type: string
    endpoint: string
    authentication_method: enum [api_key, oauth2, basic_auth, service_account]
    configuration_json: json
    rate_limits: json
    sync_schedule: cron_expression
```

## Data Lifecycle States

### Dataset State Machine

```
[PROVISIONING] → [VALIDATING] → [READY] → [TEARDOWN] → [ARCHIVED]
       ↓             ↓
   [FAILED]      [FAILED]
```

**State Transitions:**

1. **PROVISIONING**: Dataset creation in progress
   - Selecting template
   - Creating connector
   - Uploading data
   - Initial configuration

2. **VALIDATING**: Quality checks running
   - Schema validation
   - Data completeness check
   - Connector health check
   - Sample queries execution

3. **READY**: Dataset available for use
   - All quality checks passed
   - Connector healthy
   - Quality score >= 95%

4. **FAILED**: Provisioning or validation failed
   - Error captured in dataset entity
   - Manual intervention may be required
   - Can retry or teardown

5. **TEARDOWN**: Dataset being removed
   - Connector disconnection
   - Data archival
   - Cleanup operations

6. **ARCHIVED**: Dataset safely removed
   - Data archived for audit
   - Connector deleted
   - Resources cleaned up

## Data Storage Strategy

### Dataset Storage Locations

```yaml
Storage_Hierarchy:
  mock_data_templates:
    location: medtronic_mock_data repository
    format: JSON files
    access: read-only from DatasetProvisioningAgent

  active_datasets:
    location: Glean data source connectors
    format: connector-specific (API-based)
    access: read/write through Glean API

  archived_datasets:
    location: S3/blob storage (audit trail)
    format: compressed JSON snapshots
    access: read-only for compliance/audit
    retention: 90 days minimum
```

### Registry Storage

```yaml
DatasetRegistry_Storage:
  primary: PostgreSQL database
  schema: dataops_lifecycle
  tables:
    - datasets
    - dataset_templates
    - quality_checks
    - connectors
    - usage_metrics
  indexes:
    - datasets(client_id, stage)
    - datasets(status)
    - datasets(journey_id)
    - quality_checks(dataset_id, check_type)
```

## Data Quality Framework

### Quality Check Definitions

#### 1. Schema Validation (100% required)

```yaml
SchemaValidation:
  check_type: schema_validation
  threshold: 100%
  validation_rules:
    - all_required_fields_present
    - field_types_match_schema
    - no_unexpected_fields (warning only)
    - field_value_constraints_met
  scoring:
    formula: (valid_records / total_records) * 100
    pass_threshold: 100.0
```

#### 2. Data Completeness (>95% required)

```yaml
DataCompleteness:
  check_type: data_completeness
  threshold: 95%
  validation_rules:
    - non_null_required_fields >= 95%
    - record_count >= template.default_record_count * 0.95
    - essential_relationships_populated >= 95%
  scoring:
    formula: (complete_records / expected_records) * 100
    pass_threshold: 95.0
```

#### 3. Connector Health (must be healthy)

```yaml
ConnectorHealth:
  check_type: connector_health
  threshold: healthy
  health_checks:
    - connection_successful: boolean
    - authentication_valid: boolean
    - endpoint_responsive: boolean (response_time < 5s)
    - error_rate < 1%
  scoring:
    formula: all_checks_passed ? 100.0 : 0.0
    pass_threshold: 100.0
```

#### 4. Sample Query Success (100% required)

```yaml
SampleQuerySuccess:
  check_type: sample_query_success
  threshold: 100%
  test_queries: 10 predefined queries per dataset_type
  validation_rules:
    - all_queries_return_results
    - no_query_errors
    - response_time < 10s per query
    - results_match_expected_schema
  scoring:
    formula: (successful_queries / total_queries) * 100
    pass_threshold: 100.0
```

### Overall Quality Score Calculation

```
overall_quality_score = (
  schema_validation_score * 0.30 +
  data_completeness_score * 0.30 +
  connector_health_score * 0.25 +
  query_success_score * 0.15
)

dataset_ready = (overall_quality_score >= 95.0)
```

## Mock Data Integration

### Integration with medtronic_mock_data

```yaml
MockDataIntegration:
  source_repository: medtronic_mock_data
  access_pattern: read-only via DatasetProvisioningAgent

  template_structure:
    path: mock_data/templates/{industry}/{use_case}/{dataset_type}.json
    examples:
      - mock_data/templates/fintech/developer_productivity/confluence_pages.json
      - mock_data/templates/healthcare/clinical_workflows/jira_issues.json
      - mock_data/templates/enterprise/knowledge_mgmt/slack_messages.json

  template_schema:
    metadata:
      industry: string
      use_case: string
      dataset_type: string
      version: string
      default_record_count: integer
    schema:
      fields: [field_definition]
      relationships: [relationship_definition]
    data:
      records: [record_data]
```

### Stage-Appropriate Data Selection

```yaml
DataSelection_ByStage:
  sandbox:
    data_source: mock_template
    data_characteristics:
      - 100% synthetic data
      - industry-specific scenarios
      - realistic but fake content
      - PII-free
      - reproducible for testing
    record_counts:
      confluence_pages: 500
      github_repos: 50
      slack_messages: 2000
      jira_issues: 300

  pilot:
    data_source: sanitized_production
    data_characteristics:
      - production-like volume
      - sanitized PII (anonymized names, emails)
      - real usage patterns
      - production schema compliance
    sanitization_rules:
      - user_names → anonymized
      - email_addresses → fake_but_valid
      - phone_numbers → removed
      - SSN/credentials → removed
      - dates → preserved (relative offsets)

  production:
    data_source: production
    data_characteristics:
      - real production data
      - full volume and complexity
      - strict access controls
      - audit logging required
```

## Connector Configuration Automation

### Connector Lifecycle

```
[CREATE] → [CONFIGURE] → [VALIDATE] → [MONITOR] → [DISCONNECT] → [DELETE]
```

### Auto-Configuration Process

```yaml
ConnectorAutomation:
  creation:
    trigger: dataset provisioning started
    steps:
      1. generate_connector_name: "{client_name}-{stage}-{connector_type}"
      2. create_glean_connector: via Glean API
      3. configure_authentication: using stored credentials
      4. set_endpoint: connector-specific endpoint URL
      5. configure_sync_schedule: default or custom
      6. enable_health_monitoring: 5-minute interval

  validation:
    steps:
      1. test_connection: verify endpoint reachable
      2. validate_authentication: confirm credentials valid
      3. test_data_sync: sync first 10 records
      4. verify_searchability: run test queries
      5. check_metadata: ensure correct tags/labels

  monitoring:
    health_check_interval: 5 minutes
    metrics_tracked:
      - sync_success_rate
      - query_response_time
      - error_count
      - data_freshness
      - connector_uptime

  cleanup:
    trigger: stage_transition or journey_completed
    steps:
      1. pause_sync: stop new data ingestion
      2. archive_metadata: save connector config
      3. disconnect_connector: via Glean API
      4. delete_connector: after 24-hour grace period
      5. verify_cleanup: confirm resources released
```

## Data Governance

### Access Control

```yaml
AccessControl:
  dataset_access:
    sandbox:
      - client SE team: read/write
      - internal testing: read-only
      - production users: no access
    pilot:
      - client pilot users: read-only
      - client SE team: read/write
      - internal support: read-only
    production:
      - client production users: read-only (via Glean)
      - client admins: read/write (via Glean admin)
      - internal support: no direct access (via client request)

  registry_access:
    DatasetProvisioningAgent: read/write all datasets
    DataValidationAgent: read all, write quality_checks
    DataTeardownAgent: read all, write status/archived_at
    Client SEs: read client-specific datasets only
```

### Audit Trail

```yaml
AuditLogging:
  logged_events:
    - dataset_created
    - dataset_status_changed
    - quality_check_executed
    - connector_created
    - connector_health_changed
    - dataset_archived
    - template_modified

  log_retention: 90 days minimum
  log_storage: centralized audit log service

  compliance_reports:
    - datasets_by_stage_by_client (weekly)
    - data_quality_trends (daily)
    - connector_health_summary (daily)
    - orphaned_datasets_check (daily)
```

## Performance Considerations

### Provisioning Performance Targets

```yaml
PerformanceTargets:
  dataset_provisioning:
    target: <1 hour (60 minutes)
    breakdown:
      - template_selection: <1 minute
      - connector_creation: <5 minutes
      - data_upload: <30 minutes (depends on record count)
      - quality_validation: <15 minutes
      - final_verification: <5 minutes
      - buffer: 4 minutes

  quality_checks:
    schema_validation: <5 minutes
    data_completeness: <5 minutes
    connector_health: <2 minutes
    sample_queries: <3 minutes (10 queries * 18s avg)

  teardown:
    target: <15 minutes
    steps:
      - disconnect_connector: <5 minutes
      - archive_dataset: <5 minutes
      - cleanup_resources: <3 minutes
      - verify_completion: <2 minutes
```

### Scalability

```yaml
Scalability:
  concurrent_provisioning:
    max_parallel_datasets: 10 per stage
    max_datasets_per_client: 50 across all stages

  registry_capacity:
    estimated_max_datasets: 10,000 active
    estimated_max_templates: 500
    estimated_growth_rate: 100 datasets/month

  query_performance:
    registry_queries: <100ms p95
    connector_health_checks: <5s p95
    quality_score_calculation: <1s per dataset
```

## Integration Points

### Domain Integration

```yaml
DomainIntegration:
  medtronic_mock_data:
    integration_type: data_source
    access_method: read-only file system access
    data_consumed: template JSON files

  sdlc:
    integration_type: service_collaboration
    provides: test specifications, validation rules
    consumes: test data for integration tests

  knowledge_labor_observability_metrics:
    integration_type: event_emitter
    events_published:
      - DatasetProvisioned
      - DatasetValidated
      - DatasetArchived
    metrics_tracked: provisioning time, quality scores, usage

  a_domain (Journey Orchestration):
    integration_type: orchestration
    events_consumed:
      - JourneyStageChanged
      - DatasetProvisionRequested
      - JourneyCompleted
    events_published:
      - DatasetProvisionCompleted
      - DatasetValidationFailed
```

## Future Enhancements

### Planned Improvements

1. **Incremental Data Updates**: Support updating datasets without full reprovisioning
2. **Multi-Region Support**: Deploy datasets across geographic regions
3. **Dataset Versioning**: Track dataset schema evolution and migrations
4. **Smart Template Selection**: ML-based template recommendation
5. **Cost Optimization**: Track and optimize storage/connector costs per dataset

---

**Referenced By Stories:**
- P0-A2A-F2-000 (Requirements Chat - DataOps Lifecycle)
- P0-A2A-F2-001 (Dataset Discovery & Registry)
- P0-A2A-F2-002 (Provisioning & Teardown Automation)

**Related Documents:**
- DDD-003: DataOps Lifecycle - Bounded Context
- DES-004: Dataset Discovery & Registry - API Design
- TECH-004: DataOps Lifecycle - API Reference
- ARCH-001: DDD Specification - Agent-to-Agent Platform
