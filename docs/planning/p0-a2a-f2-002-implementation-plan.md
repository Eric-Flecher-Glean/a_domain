# Implementation Plan: P0-A2A-F2-002 - Dataset Provisioning & Teardown Automation

**Story ID**: P0-A2A-F2-002
**Priority**: P0
**Type**: Feature
**Estimated Effort**: 40 points (80 hours)
**Status**: Ready for Implementation
**Created**: 2026-01-30

## Overview

Implement automated dataset provisioning and teardown for the DataOps Lifecycle platform. This provides the execution layer that creates datasets from templates, populates them with mock data, configures Glean connectors, and safely tears down datasets when stages complete.

### Purpose

Enable zero-touch dataset management that reduces provisioning time from 2-3 days to <1 hour and eliminates manual connector configuration errors.

### Prerequisites

**Dependencies (All Met ✅)**:
- P0-A2A-F2-001: Dataset Discovery & Registry (Completed)
- P0-A2A-F2-000: Requirements Chat - DataOps Lifecycle (Completed)

**Required Documentation**:
- ✅ ARCH-004: Data Architecture - DataOps Lifecycle
- ✅ DDD-003: DataOps Lifecycle - Bounded Context
- ✅ DES-004: Dataset Discovery & Registry - API Design
- ✅ TECH-004: DataOps Lifecycle - API Reference

**Required Infrastructure**:
- ✅ Dataset Registry (from P0-A2A-F2-001)
- ✅ medtronic_mock_data repository with templates
- ✅ Glean API access for connector management

## Implementation Tasks

### Task 1: Implement DatasetProvisioningAgent

**Status**: Not Started
**Estimated Time**: 24 hours
**Dependencies**: None (leverages P0-A2A-F2-001 registry)
**Acceptance Criteria**: AC1, AC2

**Description**:
Create the DatasetProvisioningAgent that automates the complete dataset provisioning workflow: template selection, data population, connector configuration, and quality validation.

**Implementation Steps**:

1. **Create agent infrastructure**:
   ```
   sdlc_framework/dataops/agents/
   ├── __init__.py
   ├── dataset_provisioning_agent.py
   ├── connector_manager.py
   └── data_populator.py
   ```

2. **Implement DatasetProvisioningAgent**:
   ```python
   class DatasetProvisioningAgent:
       """
       Orchestrates dataset provisioning workflow.

       Responsibilities:
       - Select appropriate template based on client metadata
       - Coordinate data population from mock sources
       - Configure Glean connector
       - Trigger quality validation
       - Emit domain events
       """

       async def provision_dataset(
           self,
           client_id: UUID,
           journey_id: UUID,
           stage: Stage,
           dataset_type: DatasetType,
           template_id: Optional[UUID] = None
       ) -> Dataset:
           # 1. Load or select template
           template = await self._select_template(dataset_type, client_id)

           # 2. Create dataset entity (status=PROVISIONING)
           dataset = await self._create_dataset_entity(
               client_id, journey_id, stage, template
           )

           # 3. Populate data from mock source
           await self._populate_data(dataset, template)

           # 4. Configure Glean connector
           connector = await self._configure_connector(dataset)

           # 5. Update dataset with connector reference
           dataset.connector_id = connector.connector_id
           dataset.status = DatasetStatus.VALIDATING

           # 6. Trigger quality validation (async)
           await self._trigger_quality_checks(dataset)

           # 7. Emit DatasetProvisionCompleted event
           await self._emit_event(DatasetProvisionCompleted(dataset))

           return dataset
   ```

3. **Implement ConnectorManager**:
   ```python
   class ConnectorManager:
       """
       Manages Glean data connector lifecycle.

       Uses Glean Admin API to:
       - Create connectors
       - Configure authentication
       - Set sync schedules
       - Monitor health
       """

       async def create_connector(
           self,
           dataset: Dataset,
           connector_type: str,
           config: ConnectorConfiguration
       ) -> GleanConnector:
           # 1. Generate unique connector name
           name = f"{dataset.client_id}-{dataset.stage}-{connector_type}"

           # 2. Call Glean Admin API
           response = await self.glean_api.create_datasource(
               name=name,
               type=connector_type,
               config=config.to_glean_format()
           )

           # 3. Create GleanConnector entity
           connector = GleanConnector(
               connector_id=response.id,
               name=name,
               client_id=dataset.client_id,
               stage=dataset.stage,
               connector_type=connector_type,
               status=ConnectorStatus.CREATING
           )

           # 4. Store in repository
           await self.connector_repo.save(connector)

           # 5. Start health monitoring
           await self._start_health_monitoring(connector)

           return connector
   ```

4. **Implement DataPopulator**:
   ```python
   class DataPopulator:
       """
       Populates datasets with mock data from templates.

       Sources:
       - medtronic_mock_data repository (JSON/CSV files)
       - In-memory generated data (for large datasets)
       - Sanitized production data (pilot stage only)
       """

       async def populate_from_template(
           self,
           dataset: Dataset,
           template: DatasetTemplate
       ) -> PopulationResult:
           # 1. Load mock data file
           source_path = Path(template.source_path)
           mock_data = await self._load_mock_data(source_path)

           # 2. Transform to dataset schema
           records = await self._transform_records(
               mock_data, template.schema_definition
           )

           # 3. Write to staging location
           staging_path = self._get_staging_path(dataset)
           await self._write_records(staging_path, records)

           # 4. Update dataset metadata
           dataset.record_count = len(records)
           dataset.size_bytes = await self._calculate_size(staging_path)
           dataset.data_source = DataSource.MOCK_TEMPLATE

           return PopulationResult(
               records_written=len(records),
               size_bytes=dataset.size_bytes,
               staging_path=str(staging_path)
           )
   ```

5. **Template selection logic**:
   ```python
   async def _select_template(
       self,
       dataset_type: DatasetType,
       client_id: UUID
   ) -> DatasetTemplate:
       # 1. Load client metadata
       client = await self.client_repo.find_by_id(client_id)

       # 2. Query registry for matching templates
       templates = await self.registry.find_templates(
           dataset_type=dataset_type,
           industry=client.industry,
           use_case=client.use_case
       )

       # 3. Rank by relevance (exact match > industry match > default)
       template = self._rank_templates(templates, client)

       # 4. Return best match
       return template
   ```

6. **Error handling and retry logic**:
   - Connector creation failures: Retry up to 3 times with exponential backoff
   - Data population errors: Rollback partial writes, mark dataset as FAILED
   - Quality check failures: Move to VALIDATING state, log issues
   - Emit DatasetProvisionFailed event on terminal failures

**Tests**:
```python
# Unit tests
pytest tests/unit/dataops/agents/test_provisioning_agent.py
pytest tests/unit/dataops/agents/test_connector_manager.py
pytest tests/unit/dataops/agents/test_data_populator.py

# Test cases:
# - Select correct template based on client metadata
# - Provision dataset end-to-end (happy path)
# - Handle connector creation failure with retry
# - Rollback on data population error
# - Emit correct domain events
```

**Success Criteria**:
- Agent provisions complete dataset from template in <1 hour
- Connector configured correctly with no manual intervention
- Quality validation triggered automatically
- All error scenarios handled gracefully with proper rollback

---

### Task 2: Integrate with medtronic_mock_data Repository

**Status**: Not Started
**Estimated Time**: 12 hours
**Dependencies**: Task 1
**Acceptance Criteria**: AC2

**Description**:
Build integration layer with the medtronic_mock_data repository to load mock data templates and transform them into Glean-compatible format.

**Implementation Steps**:

1. **Create mock data adapter**:
   ```
   sdlc_framework/dataops/adapters/
   ├── __init__.py
   ├── mock_data_adapter.py
   └── glean_data_transformer.py
   ```

2. **Implement MockDataAdapter**:
   ```python
   class MockDataAdapter:
       """
       Adapter for medtronic_mock_data repository.

       Responsibilities:
       - Locate template files by industry/use-case/type
       - Load JSON/CSV files
       - Parse metadata sections
       - Validate data integrity
       """

       def __init__(self, repo_path: Path):
           self.repo_path = repo_path
           self.templates_path = repo_path / "mock_data" / "templates"

       async def load_template_data(
           self,
           industry: str,
           use_case: str,
           dataset_type: str
       ) -> Dict[str, Any]:
           # 1. Construct file path
           file_path = (
               self.templates_path /
               industry /
               use_case /
               f"{dataset_type}.json"
           )

           # 2. Load JSON file
           with open(file_path) as f:
               data = json.load(f)

           # 3. Validate structure
           self._validate_template_structure(data)

           return data
   ```

3. **Implement GleanDataTransformer**:
   ```python
   class GleanDataTransformer:
       """
       Transforms mock data into Glean-ingestible format.

       Each data source type has specific format requirements:
       - Confluence: Page ID, title, body, space, author
       - GitHub: Repo name, description, language, stars, issues
       - Slack: Message ID, text, channel, author, timestamp
       - Jira: Issue key, summary, description, status, assignee
       """

       async def transform_to_glean_format(
           self,
           records: List[Dict],
           dataset_type: DatasetType
       ) -> List[Dict]:
           transformer = self._get_transformer(dataset_type)
           return [transformer(record) for record in records]

       def _transform_confluence_page(self, record: Dict) -> Dict:
           return {
               "objectType": "CONFLUENCE_PAGE",
               "documentId": record["page_id"],
               "title": record["title"],
               "body": {
                   "mimeType": "text/html",
                   "textContent": record["body"]
               },
               "container": record["space_key"],
               "author": {"email": record["author_email"]},
               "updatedAt": record["last_modified"]
           }
   ```

4. **Repository path configuration**:
   ```python
   # sdlc_config.yaml
   dataops:
     mock_data_repo:
       path: ${MOCK_DATA_REPO_PATH:-../medtronic_mock_data}
       templates_subdir: mock_data/templates

   # Environment variable fallback
   MOCK_DATA_REPO_PATH=/path/to/medtronic_mock_data
   ```

5. **Template metadata extraction**:
   ```python
   async def extract_template_metadata(
       self,
       template_data: Dict
   ) -> DatasetMetadata:
       # Parse metadata section from template
       meta = template_data.get("metadata", {})

       return DatasetMetadata(
           industry=meta.get("industry"),
           use_case=meta.get("use_case"),
           data_type=meta.get("data_type", "mock"),
           stage=meta.get("stage", "sandbox"),
           tags=meta.get("tags", []),
           custom_fields=meta.get("custom_fields", {})
       )
   ```

**Tests**:
```python
# Integration tests
pytest tests/integration/dataops/test_mock_data_integration.py

# Test cases:
# - Load template from medtronic_mock_data repository
# - Transform Confluence pages to Glean format
# - Transform GitHub repos to Glean format
# - Transform Slack messages to Glean format
# - Handle missing template files gracefully
# - Validate transformed data schema
```

**Success Criteria**:
- All template types (Confluence, GitHub, Slack, Jira) load successfully
- Transformed data validates against Glean schemas
- Metadata extracted correctly from template files
- Integration works with both local and Git submodule paths

---

### Task 3: Implement Glean Connector Configuration

**Status**: Not Started
**Estimated Time**: 20 hours
**Dependencies**: Task 1, Task 2
**Acceptance Criteria**: AC3

**Description**:
Build automated Glean connector configuration using the Glean Admin API, including authentication setup, sync schedules, and health monitoring.

**Implementation Steps**:

1. **Create Glean API client**:
   ```
   sdlc_framework/dataops/infrastructure/
   ├── __init__.py
   ├── glean_client.py
   └── connector_config_builder.py
   ```

2. **Implement GleanAPIClient**:
   ```python
   class GleanAPIClient:
       """
       Client for Glean Admin API.

       Provides methods for:
       - Creating data sources
       - Configuring authentication
       - Starting/stopping sync jobs
       - Querying connector health
       """

       def __init__(self, api_key: str, base_url: str):
           self.api_key = api_key
           self.base_url = base_url
           self.session = aiohttp.ClientSession(
               headers={"Authorization": f"Bearer {api_key}"}
           )

       async def create_datasource(
           self,
           name: str,
           datasource_type: str,
           config: Dict
       ) -> CreateDatasourceResponse:
           """Create new Glean data source."""
           payload = {
               "name": name,
               "connector": datasource_type,
               "config": config
           }

           async with self.session.post(
               f"{self.base_url}/api/v1/datasources",
               json=payload
           ) as response:
               response.raise_for_status()
               data = await response.json()
               return CreateDatasourceResponse(**data)

       async def configure_authentication(
           self,
           datasource_id: str,
           auth_config: Dict
       ) -> None:
           """Configure OAuth or API token authentication."""
           payload = {"authConfig": auth_config}

           async with self.session.put(
               f"{self.base_url}/api/v1/datasources/{datasource_id}/auth",
               json=payload
           ) as response:
               response.raise_for_status()

       async def start_sync(
           self,
           datasource_id: str,
           incremental: bool = False
       ) -> SyncJobResponse:
           """Start data sync job."""
           payload = {"incremental": incremental}

           async with self.session.post(
               f"{self.base_url}/api/v1/datasources/{datasource_id}/sync",
               json=payload
           ) as response:
               response.raise_for_status()
               data = await response.json()
               return SyncJobResponse(**data)
   ```

3. **Implement ConnectorConfigBuilder**:
   ```python
   class ConnectorConfigBuilder:
       """
       Builds connector-specific configuration.

       Each connector type requires different config:
       - Confluence: Base URL, space keys, auth token
       - GitHub: Org name, repos, PAT token
       - Slack: Workspace ID, channels, OAuth token
       """

       def build_confluence_config(
           self,
           dataset: Dataset,
           template: DatasetTemplate
       ) -> Dict:
           return {
               "baseUrl": "https://mock-confluence.example.com",
               "spaceKeys": self._get_space_keys(template),
               "authentication": {
                   "type": "API_TOKEN",
                   "token": self._get_mock_token()
               },
               "syncSettings": {
                   "fullSyncSchedule": "0 2 * * *",  # Daily at 2 AM
                   "incrementalSyncSchedule": "0 */4 * * *"  # Every 4 hours
               }
           }

       def build_github_config(
           self,
           dataset: Dataset,
           template: DatasetTemplate
       ) -> Dict:
           return {
               "organization": "mock-org",
               "repositories": self._get_repo_list(template),
               "authentication": {
                   "type": "PAT",
                   "token": self._get_mock_token()
               },
               "syncSettings": {
                   "includeIssues": True,
                   "includePullRequests": True,
                   "includeWiki": False
               }
           }
   ```

4. **Mock authentication token generation** (for sandbox):
   ```python
   def _get_mock_token(self) -> str:
       """
       Generate mock authentication token for sandbox.

       Sandbox connectors don't connect to real systems,
       so we use placeholder tokens that Glean accepts
       but don't grant actual access.
       """
       # Use deterministic token based on dataset ID
       token_seed = f"{self.dataset.dataset_id}-mock-token"
       return hashlib.sha256(token_seed.encode()).hexdigest()
   ```

5. **Connector health monitoring**:
   ```python
   async def monitor_connector_health(
       self,
       connector: GleanConnector
   ) -> ConnectorHealth:
       """
       Poll Glean API for connector health status.

       Health checks:
       - Connector status (healthy, unhealthy, disconnected)
       - Last successful sync timestamp
       - Error count in last 24 hours
       - Data freshness (time since last update)
       """
       health = await self.glean_client.get_connector_health(
           connector.connector_id
       )

       # Update connector entity
       connector.status = health.status
       connector.last_health_check = datetime.utcnow()
       connector.health_status = health.to_dict()

       await self.connector_repo.save(connector)

       # Trigger quality re-validation if unhealthy
       if health.status != ConnectorStatus.HEALTHY:
           await self._trigger_quality_recheck(connector.dataset_id)

       return health
   ```

6. **Error handling**:
   - API rate limiting: Exponential backoff with jitter
   - Authentication failures: Log error, mark connector as failed
   - Network timeouts: Retry up to 3 times
   - Invalid configuration: Validate before API call, provide clear error

**Tests**:
```python
# Integration tests
pytest tests/integration/dataops/test_glean_connector.py

# Test cases:
# - Create Confluence connector successfully
# - Create GitHub connector successfully
# - Handle API rate limiting gracefully
# - Detect connector health issues
# - Retry on transient failures
# - Validate configuration before creation
```

**Success Criteria**:
- Connectors created via Glean Admin API with no manual steps
- Authentication configured correctly (mock tokens for sandbox)
- Health monitoring detects issues within 5 minutes
- API errors handled gracefully with clear error messages

---

### Task 4: Implement DataTeardownAgent with Archival

**Status**: Not Started
**Estimated Time**: 24 hours
**Dependencies**: Task 1, Task 3
**Acceptance Criteria**: AC4

**Description**:
Create the DataTeardownAgent that safely removes datasets when stages complete, including connector disconnection, data archival, and cleanup verification.

**Implementation Steps**:

1. **Create teardown infrastructure**:
   ```
   sdlc_framework/dataops/agents/
   ├── data_teardown_agent.py
   └── archival_service.py
   ```

2. **Implement DataTeardownAgent**:
   ```python
   class DataTeardownAgent:
       """
       Orchestrates safe dataset teardown.

       Responsibilities:
       - Archive dataset metadata and sample data
       - Disconnect Glean connector
       - Delete staging data
       - Verify complete cleanup
       - Emit domain events
       """

       async def teardown_dataset(
           self,
           dataset_id: UUID,
           reason: TeardownReason
       ) -> TeardownResult:
           # 1. Load dataset
           dataset = await self.dataset_repo.find_by_id(dataset_id)

           # 2. Validate teardown is safe
           await self._validate_teardown_safety(dataset)

           # 3. Update status to TEARDOWN
           dataset.status = DatasetStatus.TEARDOWN
           await self.dataset_repo.save(dataset)

           # 4. Archive dataset (metadata + sample data)
           archive_path = await self._archive_dataset(dataset)

           # 5. Disconnect connector
           await self._disconnect_connector(dataset.connector_id)

           # 6. Delete staging data
           await self._delete_staging_data(dataset)

           # 7. Update status to ARCHIVED
           dataset.status = DatasetStatus.ARCHIVED
           dataset.archived_at = datetime.utcnow()
           await self.dataset_repo.save(dataset)

           # 8. Emit DatasetTeardownCompleted event
           await self._emit_event(
               DatasetTeardownCompleted(dataset, reason, archive_path)
           )

           return TeardownResult(
               dataset_id=dataset_id,
               archived_path=archive_path,
               cleanup_verified=True
           )
   ```

3. **Implement ArchivalService**:
   ```python
   class ArchivalService:
       """
       Archives dataset metadata and sample data.

       Archive structure:
       archives/
       ├── {client_id}/
       │   └── {stage}/
       │       └── {dataset_type}/
       │           ├── metadata.json
       │           ├── sample_data.json
       │           └── quality_reports.json
       """

       async def archive_dataset(
           self,
           dataset: Dataset
       ) -> Path:
           # 1. Create archive directory
           archive_path = self._get_archive_path(dataset)
           archive_path.mkdir(parents=True, exist_ok=True)

           # 2. Archive metadata
           metadata = {
               "dataset_id": str(dataset.dataset_id),
               "name": dataset.name,
               "dataset_type": dataset.dataset_type.value,
               "stage": dataset.stage.value,
               "client_id": str(dataset.client_id),
               "journey_id": str(dataset.journey_id),
               "created_at": dataset.created_at.isoformat(),
               "archived_at": datetime.utcnow().isoformat(),
               "record_count": dataset.record_count,
               "size_bytes": dataset.size_bytes,
               "quality_score": dataset.quality_score
           }

           await self._write_json(
               archive_path / "metadata.json",
               metadata
           )

           # 3. Archive sample data (first 100 records)
           sample_data = await self._extract_sample_data(dataset)
           await self._write_json(
               archive_path / "sample_data.json",
               sample_data
           )

           # 4. Archive quality reports
           quality_checks = await self.quality_repo.find_by_dataset(
               dataset.dataset_id
           )
           await self._write_json(
               archive_path / "quality_reports.json",
               [check.to_dict() for check in quality_checks]
           )

           return archive_path
   ```

4. **Connector disconnection**:
   ```python
   async def _disconnect_connector(
       self,
       connector_id: UUID
   ) -> None:
       """
       Safely disconnect and delete Glean connector.

       Steps:
       1. Stop any running sync jobs
       2. Wait for jobs to complete
       3. Delete connector via API
       4. Update connector status to DISCONNECTED
       """
       connector = await self.connector_repo.find_by_id(connector_id)

       # 1. Stop sync jobs
       await self.glean_client.stop_sync(str(connector_id))

       # 2. Wait for sync completion (max 5 minutes)
       await self._wait_for_sync_completion(connector, timeout=300)

       # 3. Delete connector
       await self.glean_client.delete_datasource(str(connector_id))

       # 4. Update status
       connector.status = ConnectorStatus.DISCONNECTED
       await self.connector_repo.save(connector)
   ```

5. **Staging data cleanup**:
   ```python
   async def _delete_staging_data(
       self,
       dataset: Dataset
   ) -> None:
       """
       Delete staging data files.

       Verifies deletion completed successfully.
       """
       staging_path = self._get_staging_path(dataset)

       if staging_path.exists():
           # Delete directory tree
           shutil.rmtree(staging_path)

           # Verify deletion
           if staging_path.exists():
               raise TeardownError(
                   f"Failed to delete staging data: {staging_path}"
               )
   ```

6. **Teardown safety validation**:
   ```python
   async def _validate_teardown_safety(
       self,
       dataset: Dataset
   ) -> None:
       """
       Validate it's safe to tear down dataset.

       Checks:
       - Dataset not in use by active journey
       - No pending quality checks
       - Connector not syncing
       """
       # Check journey status
       journey = await self.journey_repo.find_by_id(dataset.journey_id)
       if journey.status == JourneyStatus.ACTIVE:
           raise TeardownError(
               f"Cannot teardown dataset for active journey {journey.journey_id}"
           )

       # Check for pending quality checks
       pending_checks = await self.quality_repo.find_pending_by_dataset(
           dataset.dataset_id
       )
       if pending_checks:
           raise TeardownError(
               f"Cannot teardown dataset with {len(pending_checks)} pending quality checks"
           )

       # Check connector sync status
       connector = await self.connector_repo.find_by_id(dataset.connector_id)
       if connector.status == ConnectorStatus.SYNCING:
           raise TeardownError(
               f"Cannot teardown dataset while connector syncing"
           )
   ```

7. **Orphaned dataset detection**:
   ```python
   async def detect_orphaned_datasets(self) -> List[Dataset]:
       """
       Find datasets with no associated active journey.

       Runs daily as scheduled task.
       Triggers automatic teardown after 7 days.
       """
       # Find datasets older than 7 days
       cutoff_date = datetime.utcnow() - timedelta(days=7)
       old_datasets = await self.dataset_repo.find_older_than(cutoff_date)

       orphaned = []
       for dataset in old_datasets:
           # Check if journey still active
           journey = await self.journey_repo.find_by_id(dataset.journey_id)
           if journey.status != JourneyStatus.ACTIVE:
               orphaned.append(dataset)

       return orphaned
   ```

**Tests**:
```python
# Integration tests
pytest tests/integration/dataops/test_teardown_agent.py

# Test cases:
# - Teardown dataset successfully (happy path)
# - Archive metadata and sample data correctly
# - Disconnect connector before deletion
# - Handle teardown failures gracefully
# - Prevent teardown of active journey datasets
# - Detect orphaned datasets
# - Verify complete cleanup
```

**Success Criteria**:
- Teardown completes safely with all data archived
- Connector disconnected and deleted via API
- Staging data removed completely
- Orphaned datasets detected and cleaned up automatically
- No data loss (metadata and samples preserved in archive)

---

## Testing Plan

### Unit Tests

**Scope**: Agent logic, business rules, data transformations

**Test Files**:
- `tests/unit/dataops/agents/test_provisioning_agent.py`
- `tests/unit/dataops/agents/test_teardown_agent.py`
- `tests/unit/dataops/agents/test_connector_manager.py`
- `tests/unit/dataops/agents/test_data_populator.py`
- `tests/unit/dataops/adapters/test_mock_data_adapter.py`
- `tests/unit/dataops/adapters/test_glean_transformer.py`

**Key Test Cases**:
1. Template selection logic (industry/use-case matching)
2. Data population from mock templates
3. Connector configuration building
4. Teardown safety validation
5. Archival service operations
6. Error handling and rollback logic

**Coverage Target**: >95%

### Integration Tests

**Scope**: End-to-end workflows, external integrations

**Test Files**:
- `tests/integration/dataops/test_dataset_provisioning.py`
- `tests/integration/dataops/test_mock_data_integration.py`
- `tests/integration/dataops/test_glean_connector.py`
- `tests/integration/dataops/test_dataset_teardown.py`

**Key Test Cases**:
1. Provision dataset from template end-to-end
2. Load data from medtronic_mock_data repository
3. Create Glean connector via API
4. Teardown dataset with archival
5. Orphaned dataset detection
6. Multi-stage dataset lifecycle

**Coverage Target**: >85%

### Functional Tests

**From Acceptance Criteria**:

**AC1: Datasets provisioned in <1 hour**
```bash
# Test command
time uv run tests/integration/test_dataset_provisioning.py::test_provision_speed

# Expected output
real    0m45.234s  # <1 hour (3600 seconds)
user    0m5.123s
sys     0m1.456s

# Success criteria
- Provisioning completes in <60 minutes
- Dataset status changes to READY
- Quality score ≥95%
```

**AC2: Mock data populated from medtronic_mock_data**
```bash
# Test command
uv run tests/integration/test_mock_data_integration.py::test_data_population

# Expected output
✅ Loaded template: FinTech Developer Productivity - Confluence
✅ Populated 500 records
✅ Transformed to Glean format
✅ Sample data validated

# Success criteria
- All template types load successfully
- Record count matches template default
- Data validates against schema
```

**AC3: Connectors auto-configured**
```bash
# Test command
uv run tests/integration/test_glean_connector.py::test_auto_configuration

# Expected output
✅ Connector created: ACME-Sandbox-Confluence
✅ Authentication configured
✅ Sync schedule set
✅ Health monitoring started

# Success criteria
- Connector created via API (no manual steps)
- Status shows as HEALTHY
- Configuration matches dataset requirements
```

**AC4: Teardown archives data and cleans up**
```bash
# Test command
uv run tests/integration/test_dataset_teardown.py::test_teardown_workflow

# Expected output
✅ Dataset archived: archives/client-123/sandbox/confluence/
✅ Connector disconnected and deleted
✅ Staging data removed
✅ Dataset status: ARCHIVED

# Success criteria
- Archive contains metadata, sample data, quality reports
- Connector no longer exists in Glean
- Staging directory deleted
- Dataset marked as ARCHIVED
```

---

## Risk Management

### Risk 1: Glean API Rate Limiting

**Probability**: MEDIUM
**Impact**: HIGH
**Description**: Provisioning multiple datasets concurrently may hit Glean API rate limits, causing failures

**Mitigation**:
- Implement exponential backoff with jitter
- Queue connector creation requests
- Monitor API usage and throttle proactively
- Cache API responses where possible
- Alert on rate limit errors

### Risk 2: Mock Data Repository Structure Changes

**Probability**: LOW
**Impact**: MEDIUM
**Description**: Changes to medtronic_mock_data repository structure could break data loading

**Mitigation**:
- Version detection in mock data adapter
- Support multiple template formats (v1, v2)
- Graceful degradation if format unknown
- Integration tests validate against actual repository
- Document expected repository structure

### Risk 3: Connector Configuration Complexity

**Probability**: MEDIUM
**Impact**: MEDIUM
**Description**: Each connector type (Confluence, GitHub, Slack, etc.) has unique configuration requirements

**Mitigation**:
- Comprehensive configuration builders per connector type
- Validation before API submission
- Detailed error messages for misconfigurations
- Template library for common configurations
- Integration tests for each connector type

### Risk 4: Archival Storage Growth

**Probability**: HIGH
**Impact**: LOW
**Description**: Archival storage will grow unbounded as datasets are torn down

**Mitigation**:
- Implement archive retention policy (90 days default)
- Compress archived data
- Periodic cleanup of old archives
- Monitor storage usage
- Configure storage location (local, S3, GCS)

### Risk 5: Teardown Safety

**Probability**: LOW
**Impact**: HIGH
**Description**: Accidental teardown of active dataset could disrupt client journey

**Mitigation**:
- Multi-step safety validation before teardown
- Require explicit confirmation for manual teardown
- Prevent teardown of datasets with active journeys
- Archive before deletion (reversible)
- Audit log all teardown operations

---

## Timeline

**Total Effort**: 40 points = 80 hours (assumes 2 hours per point)

**Week 1** (40 hours):
- Task 1: DatasetProvisioningAgent (24h) - START
- Task 2: medtronic_mock_data Integration (12h)
- Task 1: DatasetProvisioningAgent (24h) - CONTINUE

**Week 2** (40 hours):
- Task 1: DatasetProvisioningAgent (24h) - FINISH (4h remaining)
- Task 3: Glean Connector Configuration (20h)
- Task 4: DataTeardownAgent (24h) - START (16h)

**Week 3** (Optional buffer - if needed):
- Task 4: DataTeardownAgent (24h) - FINISH (8h remaining)
- Integration testing
- Documentation updates
- Performance tuning

**Milestones**:
- ✅ Week 1 End: Provisioning agent functional, mock data loading
- ✅ Week 2 Mid: Connector configuration working
- ✅ Week 2 End: Teardown agent implemented, all tests passing

---

## Deliverables

### Code Artifacts

1. **Provisioning Layer**:
   - `sdlc_framework/dataops/agents/dataset_provisioning_agent.py`
   - `sdlc_framework/dataops/agents/connector_manager.py`
   - `sdlc_framework/dataops/agents/data_populator.py`

2. **Mock Data Integration**:
   - `sdlc_framework/dataops/adapters/mock_data_adapter.py`
   - `sdlc_framework/dataops/adapters/glean_data_transformer.py`

3. **Glean Integration**:
   - `sdlc_framework/dataops/infrastructure/glean_client.py`
   - `sdlc_framework/dataops/infrastructure/connector_config_builder.py`

4. **Teardown Layer**:
   - `sdlc_framework/dataops/agents/data_teardown_agent.py`
   - `sdlc_framework/dataops/agents/archival_service.py`

### Documentation

1. **User Guide**:
   - How to provision datasets
   - How to trigger teardown
   - Troubleshooting common issues

2. **API Documentation**:
   - Provisioning API endpoints
   - Teardown API endpoints
   - Event schemas

3. **Configuration Guide**:
   - Mock data repository setup
   - Glean API credentials
   - Archive storage configuration

### Configuration

1. **Environment Configuration**:
   ```yaml
   # sdlc_config.yaml
   dataops:
     mock_data_repo:
       path: ${MOCK_DATA_REPO_PATH:-../medtronic_mock_data}
     glean:
       api_key: ${GLEAN_API_KEY}
       base_url: ${GLEAN_BASE_URL:-https://api.glean.com}
     archival:
       storage_path: ${ARCHIVAL_PATH:-./archives}
       retention_days: 90
       compression: true
   ```

2. **Connector Templates**:
   - Confluence connector template
   - GitHub connector template
   - Slack connector template
   - Jira connector template

---

## Validation & Rollout

### Pre-Deployment Checklist

- [ ] All unit tests pass (>95% coverage)
- [ ] All integration tests pass (>85% coverage)
- [ ] Functional tests validate acceptance criteria
- [ ] Provisioning completes in <1 hour (AC1)
- [ ] Mock data integration working (AC2)
- [ ] Connectors auto-configured (AC3)
- [ ] Teardown with archival working (AC4)
- [ ] Glean API access verified
- [ ] medtronic_mock_data repository accessible
- [ ] Archive storage configured
- [ ] Error handling tested (rollback, retry)
- [ ] Code review approved

### Deployment Steps

1. **Infrastructure Setup**:
   ```bash
   # Set environment variables
   export MOCK_DATA_REPO_PATH=/path/to/medtronic_mock_data
   export GLEAN_API_KEY=your_api_key
   export GLEAN_BASE_URL=https://api.glean.com
   export ARCHIVAL_PATH=./archives

   # Create archive directory
   mkdir -p ./archives
   ```

2. **Service Deployment**:
   ```bash
   # Install dependencies
   uv sync

   # Run database migrations (if any)
   alembic upgrade head
   ```

3. **Verification**:
   ```bash
   # Test provisioning agent
   uv run python -m sdlc_framework.dataops.agents.dataset_provisioning_agent \
     --client-id test-client-123 \
     --stage sandbox \
     --dataset-type confluence_pages

   # Verify connector created
   curl -H "Authorization: Bearer $GLEAN_API_KEY" \
     https://api.glean.com/api/v1/datasources

   # Test teardown agent
   uv run python -m sdlc_framework.dataops.agents.data_teardown_agent \
     --dataset-id <dataset_id>

   # Verify archive created
   ls -la ./archives/
   ```

### Rollback Plan

**If critical issues discovered**:

1. Disable provisioning agent (prevent new dataset creation)
2. Complete in-flight provisioning operations
3. Archive current state
4. Revert code changes
5. Investigate issue in staging environment
6. Fix and redeploy

**Rollback triggers**:
- Provisioning failure rate >10%
- Glean API errors >5%
- Teardown failures causing data loss
- Connector misconfiguration >5%

---

## Dependencies on Other Stories

**Blocks**:
- P1-A2A-F2-003: DataOps - Quality Validation Pipeline (requires provisioned datasets to validate)

**Blocked By** (All Complete ✅):
- ✅ P0-A2A-F2-001: Dataset Discovery & Registry
- ✅ P0-A2A-F2-000: Requirements Chat - DataOps Lifecycle

**Related**:
- P0-A2A-F1-002: Journey Orchestration - Unit of Work Executor (triggers provisioning on journey start)
- P1-A2A-F2-003: Quality Validation Pipeline (validates provisioned datasets)

---

## Success Metrics

**Development Metrics**:
- All acceptance criteria met: AC1, AC2, AC3, AC4
- Test coverage: Unit >95%, Integration >85%
- Code review: 0 critical issues, <5 minor issues
- Documentation: 100% public API documented

**Performance Metrics**:
- Provisioning time: <1 hour p95
- Connector creation: <5 minutes p95
- Teardown time: <15 minutes p95
- Archive operation: <2 minutes p95
- API error rate: <1%

**Operational Metrics**:
- Provisioning success rate: >95%
- Teardown success rate: >98%
- Connector health: >99% uptime
- Orphaned dataset detection: 100% (daily scan)

---

**Implementation Start Date**: TBD (upon plan approval)
**Target Completion Date**: TBD (2 weeks from start)
**Plan Version**: 1.0
**Last Updated**: 2026-01-30
