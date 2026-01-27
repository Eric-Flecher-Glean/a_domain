/**
 * OpenTelemetry Setup and Initialization
 *
 * Configures OTel providers (traces, metrics) with file-based exporters
 */

const { NodeSDK } = require('@opentelemetry/sdk-node');
const { PeriodicExportingMetricReader } = require('@opentelemetry/sdk-metrics');
const { resourceFromAttributes } = require('@opentelemetry/resources');
const { ATTR_SERVICE_NAME, ATTR_SERVICE_VERSION, ATTR_DEPLOYMENT_ENVIRONMENT } = require('@opentelemetry/semantic-conventions');
const { SimpleSpanProcessor } = require('@opentelemetry/sdk-trace-node');
const { trace, metrics } = require('@opentelemetry/api');
const fs = require('fs');
const path = require('path');

const {
  TraceFileExporter,
  MetricFileExporter,
  EventFileExporter,
  LogFileExporter
} = require('./file-exporter');

// Load configuration
const configPath = path.join(__dirname, 'otel-config.json');
const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));

// Singleton instances
let sdk = null;
let eventExporter = null;
let logExporter = null;
let isInitialized = false;

/**
 * Initialize OpenTelemetry
 */
function initializeOTel() {
  if (isInitialized) {
    return {
      sdk,
      eventExporter,
      logExporter
    };
  }

  // Create resource with service information
  const resource = resourceFromAttributes({
    [ATTR_SERVICE_NAME]: config.service.name,
    [ATTR_SERVICE_VERSION]: config.service.version,
    [ATTR_DEPLOYMENT_ENVIRONMENT]: config.service.environment,
    ...config.resource.attributes
  });

  // Create file exporters
  const traceExporter = new TraceFileExporter(config.exporters.traces);
  const metricExporter = new MetricFileExporter(config.exporters.metrics);
  const metricReader = new PeriodicExportingMetricReader({
    exporter: metricExporter,
    exportIntervalMillis: config.exporters.metrics.export_interval_ms || 60000
  });

  // Initialize NodeSDK with file-based exporters
  sdk = new NodeSDK({
    resource,
    traceExporter,
    spanProcessor: new SimpleSpanProcessor(traceExporter),
    metricReader
  });

  // Start SDK
  sdk.start();

  // Initialize Event Exporter
  eventExporter = new EventFileExporter(config.exporters.events);

  // Initialize Log Exporter
  logExporter = new LogFileExporter(config.exporters.logs);

  isInitialized = true;

  console.log('OpenTelemetry initialized with file-based exporters');
  console.log(`  Traces: ${config.exporters.traces.path}`);
  console.log(`  Metrics: ${config.exporters.metrics.path}`);
  console.log(`  Events: ${config.exporters.events.path}`);
  console.log(`  Logs: ${config.exporters.logs.path}`);

  return {
    sdk,
    eventExporter,
    logExporter
  };
}

/**
 * Get tracer for instrumentation
 */
function getTracer(name = 'workflow-orchestration') {
  if (!isInitialized) {
    initializeOTel();
  }
  return trace.getTracer(name);
}

/**
 * Get meter for metrics
 */
function getMeter(name = 'workflow-orchestration') {
  if (!isInitialized) {
    initializeOTel();
  }
  return metrics.getMeter(name);
}

/**
 * Get event exporter
 */
function getEventExporter() {
  if (!isInitialized) {
    initializeOTel();
  }
  return eventExporter;
}

/**
 * Get log exporter
 */
function getLogger() {
  if (!isInitialized) {
    initializeOTel();
  }
  return logExporter;
}

/**
 * Shutdown OTel (cleanup)
 */
async function shutdown() {
  if (!isInitialized) {
    return;
  }

  console.log('Shutting down OpenTelemetry...');

  await Promise.all([
    sdk?.shutdown(),
    eventExporter?.shutdown(),
    logExporter?.shutdown()
  ]);

  isInitialized = false;
  console.log('OpenTelemetry shutdown complete');
}

/**
 * Get current configuration
 */
function getConfig() {
  return config;
}

module.exports = {
  initializeOTel,
  getTracer,
  getMeter,
  getEventExporter,
  getLogger,
  shutdown,
  getConfig
};
