# OpenTelemetry File-Based Observability

This directory contains the file-based observability infrastructure using OpenTelemetry, implemented without requiring any backend services.

## Overview

The observability system captures:
- **Traces**: Distributed traces of workflow executions (spans, events)
- **Metrics**: Quantitative measurements (counters, histograms, gauges)
- **Events**: Domain events following event sourcing patterns
- **Logs**: Structured logs with correlation IDs

All data is exported to local JSONL files with daily rotation and configurable retention.

## Directory Structure

```
observability/
├── traces/              # Workflow execution traces
│   └── traces-YYYY-MM-DD.jsonl
├── metrics/             # Performance and quality metrics
│   └── metrics-YYYY-MM-DD.jsonl
├── events/              # Domain events (event sourcing)
│   └── events-YYYY-MM-DD.jsonl
├── logs/                # Structured application logs
│   └── logs-YYYY-MM-DD.jsonl
├── reports/             # Timeline report generator
│   ├── timeline-generator.js
│   ├── data-aggregator.js
│   ├── timeline-builder.js
│   ├── html-renderer.js
│   ├── svg-timeline.js
│   ├── metrics-calculator.js
│   ├── generate-report.js
│   ├── templates/
│   └── README.md
├── reports-output/      # Generated HTML timeline reports
│   └── {session-id}-timeline.html
├── otel-setup.js        # OTel initialization
├── otel-config.json     # Configuration
├── file-exporter.js     # Custom JSONL exporters
├── instrumentation.js   # Instrumentation utilities
├── rotation.js          # File rotation and retention
└── README.md            # This file
```

## Configuration

Edit `otel-config.json` to customize:

```json
{
  "service": {
    "name": "workflow-orchestration",
    "version": "1.0.0",
    "environment": "development"
  },
  "exporters": {
    "traces": {
      "retention_days": 30  // How long to keep trace files
    },
    "metrics": {
      "retention_days": 30,
      "export_interval_ms": 60000  // Export metrics every 60s
    },
    "events": {
      "retention_days": 30
    },
    "logs": {
      "retention_days": 7  // Shorter retention for logs
    }
  }
}
```

## Usage

### Automatic Instrumentation

The workflow script is automatically instrumented. Simply run:

```bash
node scripts/run-mcp-workflow-integrated.js --mode generate --task "Create a sentiment analysis prompt"
```

Observability data will be written to:
- `observability/traces/traces-2026-01-26.jsonl`
- `observability/metrics/metrics-2026-01-26.jsonl`
- `observability/events/events-2026-01-26.jsonl`
- `observability/logs/logs-2026-01-26.jsonl`

**NEW**: A beautiful HTML timeline report is automatically generated after each workflow execution!

### Timeline Reports

After running a workflow, an interactive HTML timeline report is automatically created showing:
- Horizontal timeline with execution steps
- Visual duration blocks color-coded by status
- Metrics panel with bottleneck identification
- Quality progression across attempts
- Status indicators (✓ success, ⚠ warning, ✗ error)

**View the latest report:**
```bash
make view-latest-report
```

**View a specific report:**
```bash
make view-report SESSION_ID="your-session-id"
```

**Manually generate a report:**
```bash
# For latest session
make generate-report

# For specific session
node observability/reports/generate-report.js --session-id abc123-def456

# For all sessions today
node observability/reports/generate-report.js --all
```

See [reports/README.md](reports/README.md) for detailed documentation on timeline reports.

### Viewing Traces

```bash
# View all traces from today
cat observability/traces/workflow-$(date +%Y-%m-%d).jsonl | jq '.'

# Find a specific trace by ID
cat observability/traces/workflow-*.jsonl | jq 'select(.traceId == "abc123")'

# View span hierarchy
cat observability/traces/workflow-*.jsonl | jq '.name, .spanId, .parentSpanId'
```

### Analyzing Metrics

```bash
# Average quality score
cat observability/metrics/metrics-*.jsonl | \
  jq -r 'select(.metric=="workflow.quality_score") | .dataPoints[].value' | \
  awk '{sum+=$1; count++} END {print "Average:", sum/count}'

# Count sessions by status
cat observability/events/events-*.jsonl | \
  jq -r 'select(.eventType=="WorkflowSessionCompleted") | .payload.status' | \
  sort | uniq -c
```

### Viewing Events

```bash
# Event stream for a session
SESSION_ID="your-session-id"
cat observability/events/events-*.jsonl | jq "select(.aggregateId == \"$SESSION_ID\")"

# All events by type
cat observability/events/events-*.jsonl | jq '.eventType' | sort | uniq -c

# Failed validations
cat observability/events/events-*.jsonl | \
  jq 'select(.eventType=="PromptRejected") | [.timestamp, .payload.quality_score] | @csv'
```

### Viewing Logs

```bash
# Logs with errors
cat observability/logs/logs-*.jsonl | jq 'select(.level=="ERROR")'

# Logs for a specific session
cat observability/logs/logs-*.jsonl | jq 'select(.session_id=="your-session-id")'

# Logs correlated with a trace
TRACE_ID="abc123"
cat observability/logs/logs-*.jsonl | jq "select(.trace_id == \"$TRACE_ID\")"
```

## File Rotation and Retention

### View Statistics

```bash
node observability/rotation.js stats
```

Output:
```
Observability File Statistics:
===============================

Traces:
  Files: 5
  Total Size: 2.45 MB
  Oldest: 2026-01-21T10:30:00.000Z
  Newest: 2026-01-26T15:45:00.000Z
```

### Run Cleanup

```bash
node observability/rotation.js cleanup
```

This will:
- Delete files older than retention period
- Compress files older than 7 days (gzip)

### Automated Cleanup (Cron)

Add to crontab for daily cleanup at 2am:

```bash
0 2 * * * cd /path/to/a_domain && node observability/rotation.js cleanup
```

## Signal Types

### 1. Traces

Traces capture the execution flow:

```json
{
  "traceId": "abc123...",
  "spanId": "def456...",
  "parentSpanId": "root-span",
  "name": "PromptGeneration",
  "kind": 1,
  "startTime": [1706270445, 0],
  "endTime": [1706270446, 500000000],
  "duration": 1500000000,
  "attributes": {
    "stage.id": "PromptGeneration",
    "stage.agent_id": "prompt-generator-001",
    "session.id": "session-uuid"
  },
  "events": [
    {
      "name": "StageCompleted",
      "time": [1706270446, 0],
      "attributes": {
        "stage.duration_ms": 1500,
        "stage.output_size": 1024
      }
    }
  ],
  "status": { "code": 1 }
}
```

### 2. Metrics

Metrics capture measurements:

```json
{
  "timestamp": "2026-01-26T10:30:45.123Z",
  "metric": "workflow.quality_score",
  "type": "histogram",
  "unit": "score",
  "dataPoints": [
    {
      "value": 95,
      "attributes": {
        "workflow.id": "prompt-generation",
        "session.id": "session-uuid"
      }
    }
  ]
}
```

### 3. Events

Domain events for event sourcing:

```json
{
  "eventId": "evt-001",
  "eventType": "PromptGenerated",
  "aggregateId": "session-uuid",
  "aggregateType": "WorkflowSession",
  "version": 2,
  "timestamp": "2026-01-26T10:30:45.500Z",
  "correlationId": "trace-abc123",
  "causationId": "evt-001",
  "payload": {
    "prompt_name": "mtg-sum-wkl",
    "xml_length": 1024,
    "attempt": 1
  }
}
```

### 4. Logs

Structured logs with correlation:

```json
{
  "timestamp": "2026-01-26T10:30:45.123Z",
  "level": "INFO",
  "message": "Prompt validation passed",
  "session_id": "session-uuid",
  "attempt": 1,
  "quality_score": 95,
  "trace_id": "abc123",
  "span_id": "def456"
}
```

## Correlation

All signals are correlated via `trace_id`:

```bash
# Given a trace_id, find all related data
TRACE_ID="abc123"

echo "=== Traces ==="
cat observability/traces/*.jsonl | jq "select(.traceId == \"$TRACE_ID\")"

echo "=== Events ==="
cat observability/events/*.jsonl | jq "select(.correlationId == \"$TRACE_ID\")"

echo "=== Logs ==="
cat observability/logs/*.jsonl | jq "select(.trace_id == \"$TRACE_ID\")"

echo "=== Metrics ==="
# Metrics don't have trace_id, but have session_id which can be found in events
SESSION_ID=$(cat observability/events/*.jsonl | jq -r "select(.correlationId == \"$TRACE_ID\") | .aggregateId" | head -1)
cat observability/metrics/*.jsonl | jq "select(.dataPoints[].attributes.\"session.id\" == \"$SESSION_ID\")"
```

## Migration to Production Backends

When ready to migrate to production backends (Jaeger, Prometheus, Loki):

1. **Install backend exporters**:
   ```bash
   npm install @opentelemetry/exporter-trace-otlp-http
   npm install @opentelemetry/exporter-prometheus
   ```

2. **Update `otel-setup.js`**:
   ```javascript
   // Change from:
   const traceExporter = new TraceFileExporter(config.exporters.traces);

   // To:
   const { OTLPTraceExporter } = require('@opentelemetry/exporter-trace-otlp-http');
   const traceExporter = new OTLPTraceExporter({
     url: 'http://jaeger:4318/v1/traces'
   });
   ```

3. **Zero instrumentation changes required** - all span creation, event emission, and metric recording stays the same.

## Troubleshooting

### No files created

Check that OTel is initialized:
```bash
# Should see "OpenTelemetry initialized" message
node scripts/run-mcp-workflow-integrated.js --mode generate --task "test"
```

### Files empty

Ensure `shutdown()` is called to flush buffers:
```javascript
await shutdownOTel();
```

### Large file sizes

Adjust retention:
```json
{
  "exporters": {
    "logs": {
      "retention_days": 3  // Shorter retention for logs
    }
  }
}
```

Run cleanup:
```bash
node observability/rotation.js cleanup
```

## Benefits

1. **Zero infrastructure** - No servers, databases, or services required
2. **Immediate implementation** - Works locally without setup
3. **Event sourcing foundation** - Files become event stream for Phase 2
4. **Easy analysis** - JSONL is grep-able, jq-able, human-readable
5. **Future migration** - Switch exporters without changing instrumentation
6. **Compliance/audit** - Persistent record of all workflow executions

## Next Steps

1. **Phase 2**: Import events into PostgreSQL for event sourcing
2. **Phase 3**: Build CQRS read models from event stream
3. **Phase 4**: Migrate to production backends (Jaeger, Prometheus, Loki)
4. **Phase 5**: Add analytics and ML on event/metric data
