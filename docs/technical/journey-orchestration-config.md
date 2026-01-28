# Journey Orchestration - Configuration Guide

**Document ID**: TECH-003
**Version**: 1.0
**Status**: Draft
**Created**: 2026-01-27
**Author**: Requirements Chat (P0-A2A-F1-000)

---

## 1. Overview

This guide provides configuration instructions for deploying and operating the Client Journey Orchestration Engine.

**Target Audience**: DevOps Engineers, Platform Operators

---

## 2. Environment Variables

### 2.1 Core Configuration

```bash
# Journey Orchestrator Settings
JOURNEY_ORCHESTRATOR_ENABLED=true
JOURNEY_MAX_CONCURRENT=100
JOURNEY_STAGE_TRANSITION_TIMEOUT=300  # seconds (5 minutes)
JOURNEY_UOW_TASK_TIMEOUT=120          # seconds (2 minutes)

# State Persistence
JOURNEY_STATE_STORE=postgresql
JOURNEY_STATE_DB_HOST=postgres.a-domain.svc.cluster.local
JOURNEY_STATE_DB_PORT=5432
JOURNEY_STATE_DB_NAME=journey_state
JOURNEY_STATE_DB_USER=journey_orchestrator
JOURNEY_STATE_DB_PASSWORD=${SECRET_JOURNEY_DB_PASSWORD}

# Event Store
JOURNEY_EVENT_STORE=eventstoredb
JOURNEY_EVENT_STORE_HOST=eventstore.a-domain.svc.cluster.local
JOURNEY_EVENT_STORE_PORT=2113
JOURNEY_EVENT_STORE_USER=admin
JOURNEY_EVENT_STORE_PASSWORD=${SECRET_EVENTSTORE_PASSWORD}

# Agent Protocol Integration
PROTOCOL_BROKER_HOST=protocol-broker.a-domain.svc.cluster.local
PROTOCOL_BROKER_PORT=8080
CAPABILITY_DISCOVERY_HOST=capability-discovery.a-domain.svc.cluster.local
CAPABILITY_DISCOVERY_PORT=8081
```

### 2.2 Stage Configuration

```bash
# Sandbox Stage
SANDBOX_DURATION_TARGET_DAYS=15
SANDBOX_EXIT_SEARCH_QUALITY_MIN=0.80
SANDBOX_EXIT_SECURITY_CRITICAL_MAX=0
SANDBOX_EXIT_DEMO_APPROVAL_REQUIRED=true

# Pilot Stage
PILOT_DURATION_TARGET_DAYS=15
PILOT_EXIT_SEARCH_QUALITY_MIN=0.85
PILOT_EXIT_USER_SATISFACTION_MIN=4.0
PILOT_EXIT_BUG_WINDOW_DAYS=7
PILOT_EXIT_P95_LATENCY_MAX_MS=500

# Production Stage
PRODUCTION_ADOPTION_TARGET=0.70
PRODUCTION_SATISFACTION_TARGET=4.5
PRODUCTION_GROWTH_TARGET=0.20
```

### 2.3 External Integrations

```bash
# Glean Platform
GLEAN_API_ENDPOINT=https://api.glean.com/v1
GLEAN_SERVICE_ACCOUNT=${SECRET_GLEAN_SERVICE_ACCOUNT}
GLEAN_DASHBOARD_ENABLED=true
GLEAN_METRICS_PUBLISH_INTERVAL=60  # seconds

# Customer CRM Webhooks
CRM_WEBHOOK_ENABLED=true
CRM_WEBHOOK_URL=https://crm.example.com/webhooks/journey
CRM_WEBHOOK_SECRET=${SECRET_CRM_WEBHOOK_SECRET}

# Notification Service
NOTIFICATION_SERVICE_URL=http://notification-service.a-domain.svc.cluster.local
NOTIFICATION_EMAIL_ENABLED=true
NOTIFICATION_SLACK_ENABLED=true
```

---

## 3. YAML Configuration Files

### 3.1 Journey Orchestrator Config

**File**: `config/journey-orchestrator.yaml`

```yaml
orchestrator:
  name: "journey-orchestrator"
  version: "1.0.0"

  # Concurrency Settings
  max_concurrent_journeys: 100
  worker_pool_size: 10

  # Timeout Settings
  timeouts:
    stage_transition_seconds: 300
    task_execution_seconds: 120
    exit_criteria_validation_seconds: 30
    rollback_initiation_seconds: 600

  # Retry Settings
  retry:
    max_task_retries: 3
    backoff_strategy: "exponential"
    initial_backoff_seconds: 2
    max_backoff_seconds: 60

  # Circuit Breaker
  circuit_breaker:
    enabled: true
    failure_threshold: 5
    timeout_seconds: 60
    half_open_max_requests: 3

  # Feature Flags
  features:
    auto_promotion_enabled: true
    auto_rollback_enabled: true
    glean_dashboard_enabled: true
    metrics_publishing_enabled: true
```

### 3.2 Stage Definitions

**File**: `config/stages.yaml`

```yaml
stages:
  - stage_id: "sandbox"
    name: "Sandbox"
    order: 1
    duration_target_days: 15

    exit_criteria:
      - check_id: "connectors_syncing"
        name: "All Connectors Syncing"
        validator: "ConnectorStatusValidator"
        parameters:
          min_sync_status: "syncing"
          required_connectors: "all"

      - check_id: "search_quality"
        name: "Search Quality Threshold"
        validator: "SearchQualityValidator"
        parameters:
          min_precision: 0.80
          sample_queries: 100

      - check_id: "security_scan"
        name: "Security Scan Passed"
        validator: "SecurityScanValidator"
        parameters:
          max_critical: 0
          max_high: 5

      - check_id: "demo_approval"
        name: "Client Demo Approved"
        validator: "DemoApprovalValidator"
        parameters:
          required: true

  - stage_id: "pilot"
    name: "Pilot"
    order: 2
    duration_target_days: 15

    exit_criteria:
      - check_id: "search_quality"
        name: "Search Quality Threshold"
        validator: "SearchQualityValidator"
        parameters:
          min_precision: 0.85
          sample_queries: 200

      - check_id: "user_satisfaction"
        name: "User Satisfaction Score"
        validator: "UserSatisfactionValidator"
        parameters:
          min_score: 4.0
          min_responses: 10

      - check_id: "bug_window"
        name: "No Critical Bugs"
        validator: "BugWindowValidator"
        parameters:
          window_days: 7
          max_critical: 0
          max_high: 2

      - check_id: "performance_sla"
        name: "Performance SLA Met"
        validator: "PerformanceSLAValidator"
        parameters:
          p95_latency_max_ms: 500
          error_rate_max: 0.01

  - stage_id: "production"
    name: "Production"
    order: 3
    duration_target_days: null  # Ongoing

    success_metrics:
      - metric: "user_adoption"
        target: 0.70
        window_days: 30

      - metric: "search_satisfaction"
        target: 4.5

      - metric: "query_volume_growth"
        target: 0.20
        window_days: 30
```

### 3.3 Unit of Work Templates

**File**: `config/unit-of-work-templates.yaml`

```yaml
templates:
  - template_id: "sandbox_setup"
    name: "Sandbox Environment Setup"
    stage: "sandbox"

    tasks:
      - task_id: "provision_infra"
        name: "Provision Infrastructure"
        agent_intent: "provision_sandbox_environment"
        input_schema:
          client_id: { type: "string", required: true }
          data_sources: { type: "array", required: true }
        output_schema:
          environment_id: { type: "string" }
          status: { type: "string" }
        depends_on: []
        retry_policy:
          max_retries: 3
          backoff: "exponential"

      - task_id: "install_connectors"
        name: "Install Glean Connectors"
        agent_intent: "install_connectors"
        input_schema:
          environment_id: { type: "string", required: true }
          connectors: { type: "array", required: true }
        output_schema:
          installed_connectors: { type: "array" }
        depends_on: ["provision_infra"]
        retry_policy:
          max_retries: 3
          backoff: "exponential"

      - task_id: "provision_test_data"
        name: "Provision Test Dataset"
        agent_intent: "provision_test_dataset"
        input_schema:
          environment_id: { type: "string", required: true }
          data_sources: { type: "array", required: true }
        output_schema:
          dataset_id: { type: "string" }
          record_count: { type: "number" }
        depends_on: ["install_connectors"]
        retry_policy:
          max_retries: 2
          backoff: "linear"

      - task_id: "run_security_scan"
        name: "Security Audit"
        agent_intent: "run_security_scan"
        input_schema:
          environment_id: { type: "string", required: true }
        output_schema:
          scan_result: { type: "object" }
          vulnerabilities: { type: "array" }
        depends_on: ["provision_test_data"]
        retry_policy:
          max_retries: 1
          backoff: "none"

  - template_id: "pilot_setup"
    name: "Pilot Deployment"
    stage: "pilot"

    tasks:
      - task_id: "deploy_to_production"
        name: "Deploy to Production Environment"
        agent_intent: "deploy_production_environment"
        input_schema:
          client_id: { type: "string", required: true }
          pilot_cohort_size: { type: "number", required: true }
        output_schema:
          deployment_id: { type: "string" }
          status: { type: "string" }
        depends_on: []

      - task_id: "configure_user_access"
        name: "Configure Pilot User Access"
        agent_intent: "configure_user_access"
        input_schema:
          deployment_id: { type: "string", required: true }
          users: { type: "array", required: true }
        output_schema:
          configured_users: { type: "array" }
        depends_on: ["deploy_to_production"]

      - task_id: "setup_monitoring"
        name: "Configure Monitoring & Alerts"
        agent_intent: "setup_monitoring"
        input_schema:
          deployment_id: { type: "string", required: true }
        output_schema:
          dashboard_url: { type: "string" }
        depends_on: ["deploy_to_production"]
```

---

## 4. Database Schema

### 4.1 PostgreSQL Schema (State Store)

```sql
-- Journey State Table
CREATE TABLE journey_states (
    client_id VARCHAR(255) PRIMARY KEY,
    current_stage VARCHAR(50) NOT NULL,
    previous_stage VARCHAR(50),
    started_at TIMESTAMP NOT NULL,
    stage_started_at TIMESTAMP NOT NULL,
    completed_stages TEXT[], -- Array of completed stage IDs
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_journey_current_stage ON journey_states(current_stage);
CREATE INDEX idx_journey_started_at ON journey_states(started_at);

-- Unit of Work Table
CREATE TABLE unit_of_works (
    work_id VARCHAR(255) PRIMARY KEY,
    client_id VARCHAR(255) NOT NULL REFERENCES journey_states(client_id),
    stage VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL, -- pending, in_progress, completed, failed
    tasks JSONB NOT NULL, -- Array of task definitions
    results JSONB, -- Task execution results
    created_at TIMESTAMP DEFAULT NOW(),
    started_at TIMESTAMP,
    completed_at TIMESTAMP
);

CREATE INDEX idx_uow_client_id ON unit_of_works(client_id);
CREATE INDEX idx_uow_status ON unit_of_works(status);

-- Stage Transitions Table
CREATE TABLE stage_transitions (
    transition_id VARCHAR(255) PRIMARY KEY,
    client_id VARCHAR(255) NOT NULL REFERENCES journey_states(client_id),
    from_stage VARCHAR(50),
    to_stage VARCHAR(50) NOT NULL,
    transitioned_at TIMESTAMP NOT NULL,
    reason TEXT,
    exit_criteria_results JSONB,
    initiated_by VARCHAR(255) -- "system" or user ID
);

CREATE INDEX idx_transitions_client_id ON stage_transitions(client_id);
CREATE INDEX idx_transitions_timestamp ON stage_transitions(transitioned_at DESC);
```

---

## 5. Kubernetes Deployment

### 5.1 Deployment Manifest

**File**: `k8s/journey-orchestrator-deployment.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: journey-orchestrator
  namespace: a-domain
spec:
  replicas: 3
  selector:
    matchLabels:
      app: journey-orchestrator
  template:
    metadata:
      labels:
        app: journey-orchestrator
    spec:
      containers:
      - name: orchestrator
        image: a-domain/journey-orchestrator:1.0.0
        ports:
        - containerPort: 8080
          name: http
        env:
        - name: JOURNEY_STATE_DB_HOST
          value: "postgres.a-domain.svc.cluster.local"
        - name: JOURNEY_STATE_DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: journey-db-credentials
              key: password
        - name: PROTOCOL_BROKER_HOST
          value: "protocol-broker.a-domain.svc.cluster.local"
        resources:
          requests:
            cpu: "500m"
            memory: "512Mi"
          limits:
            cpu: "2000m"
            memory: "2Gi"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 10
          periodSeconds: 5
        volumeMounts:
        - name: config
          mountPath: /app/config
      volumes:
      - name: config
        configMap:
          name: journey-orchestrator-config
```

### 5.2 Service Manifest

```yaml
apiVersion: v1
kind: Service
metadata:
  name: journey-orchestrator
  namespace: a-domain
spec:
  selector:
    app: journey-orchestrator
  ports:
  - port: 8080
    targetPort: 8080
    name: http
  type: ClusterIP
```

### 5.3 ConfigMap

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: journey-orchestrator-config
  namespace: a-domain
data:
  journey-orchestrator.yaml: |
    # Full config from section 3.1
    ...

  stages.yaml: |
    # Full config from section 3.2
    ...

  unit-of-work-templates.yaml: |
    # Full config from section 3.3
    ...
```

---

## 6. Monitoring & Alerting

### 6.1 Prometheus Metrics

```yaml
# Prometheus scrape config
scrape_configs:
  - job_name: 'journey-orchestrator'
    kubernetes_sd_configs:
      - role: pod
        namespaces:
          names:
            - a-domain
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_label_app]
        action: keep
        regex: journey-orchestrator
```

**Metrics Exposed**:
- `journey_active_count{stage}` - Active journeys by stage
- `journey_stage_duration_seconds{stage}` - Stage duration histogram
- `journey_transition_total{from_stage,to_stage,result}` - Transition counts
- `journey_rollback_total{reason}` - Rollback counts
- `journey_uow_execution_duration_seconds` - UoW execution time
- `journey_task_execution_total{status}` - Task execution counts
- `journey_exit_criteria_pass_rate{stage}` - Exit criteria pass rate

### 6.2 Grafana Dashboard

**Dashboard JSON** (`grafana/journey-orchestrator-dashboard.json`):

```json
{
  "dashboard": {
    "title": "Journey Orchestration",
    "panels": [
      {
        "title": "Active Journeys by Stage",
        "targets": [
          {
            "expr": "journey_active_count"
          }
        ],
        "type": "graph"
      },
      {
        "title": "Stage Duration (P50, P95)",
        "targets": [
          {
            "expr": "histogram_quantile(0.50, rate(journey_stage_duration_seconds_bucket[5m]))"
          },
          {
            "expr": "histogram_quantile(0.95, rate(journey_stage_duration_seconds_bucket[5m]))"
          }
        ],
        "type": "graph"
      },
      {
        "title": "Rollback Rate (24h)",
        "targets": [
          {
            "expr": "rate(journey_rollback_total[24h])"
          }
        ],
        "type": "singlestat"
      }
    ]
  }
}
```

---

## 7. Operational Procedures

### 7.1 Starting a New Journey

```bash
# Using CLI
journey-cli start --client-id="client-123" --data-sources="salesforce,jira,confluence"

# Using API
curl -X POST http://journey-orchestrator.a-domain:8080/api/v1/journeys \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "client-123",
    "data_sources": ["salesforce", "jira", "confluence"]
  }'
```

### 7.2 Checking Journey Status

```bash
# Get current state
journey-cli status --client-id="client-123"

# Get detailed history
journey-cli history --client-id="client-123" --format=json
```

### 7.3 Initiating Manual Rollback

```bash
# Rollback to previous stage
journey-cli rollback --client-id="client-123" --reason="Critical bug detected"

# Rollback to specific stage
journey-cli rollback --client-id="client-123" --to-stage="sandbox" --reason="Re-testing required"
```

---

## 8. Troubleshooting

### 8.1 Common Issues

#### Journey Stuck in Stage

**Symptom**: Journey not progressing despite tasks completed

**Debug Steps**:
```bash
# Check exit criteria validation
journey-cli validate-exit --client-id="client-123"

# Check UoW status
journey-cli uow-status --client-id="client-123" --stage="sandbox"

# View logs
kubectl logs -n a-domain -l app=journey-orchestrator --tail=100
```

#### Task Execution Failures

**Symptom**: Tasks repeatedly failing

**Debug Steps**:
```bash
# Check agent availability
journey-cli check-agents --intent="provision_test_dataset"

# Retry failed tasks
journey-cli retry-tasks --work-id="uow-123"

# View task logs
kubectl logs -n a-domain -l app=journey-orchestrator -c task-executor
```

---

## References

- **State Machine Design**: docs/designs/journey-state-machine-design.md (DES-002)
- **Integration Architecture**: docs/architecture/journey-orchestration-integration.md (ARCH-003)
- **DDD Context**: docs/ddd/journey-orchestration-bounded-context.md (DDD-002)

---

**Last Updated**: 2026-01-27
**Next Review**: After production deployment
