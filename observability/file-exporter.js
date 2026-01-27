/**
 * Custom JSONL File Exporter for OpenTelemetry
 *
 * Exports traces, metrics, events, and logs to local JSONL files
 * with daily rotation and configurable retention.
 */

const fs = require('fs');
const path = require('path');
const { ExportResultCode } = require('@opentelemetry/core');

/**
 * Base class for file-based exporters
 */
class FileExporter {
  constructor(options = {}) {
    this.outputDir = options.path || 'observability';
    this.prefix = options.prefix || 'data';
    this.rotation = options.rotation || 'daily';
    this.retentionDays = options.retention_days || 30;

    // Ensure directory exists
    if (!fs.existsSync(this.outputDir)) {
      fs.mkdirSync(this.outputDir, { recursive: true });
    }

    this.currentFile = null;
    this.currentDate = null;
  }

  /**
   * Get filename for current date
   */
  getFilename() {
    const now = new Date();
    const dateStr = now.toISOString().split('T')[0]; // YYYY-MM-DD

    if (this.rotation === 'daily') {
      return path.join(this.outputDir, `${this.prefix}-${dateStr}.jsonl`);
    }

    return path.join(this.outputDir, `${this.prefix}.jsonl`);
  }

  /**
   * Check if file rotation is needed
   */
  shouldRotate() {
    const now = new Date();
    const currentDate = now.toISOString().split('T')[0];

    if (this.currentDate !== currentDate) {
      this.currentDate = currentDate;
      this.currentFile = this.getFilename();
      return true;
    }

    return false;
  }

  /**
   * Write a line to the JSONL file
   */
  writeLine(data) {
    this.shouldRotate(); // Check rotation

    const line = JSON.stringify(data) + '\n';

    try {
      fs.appendFileSync(this.currentFile || this.getFilename(), line, 'utf8');
      return { code: ExportResultCode.SUCCESS };
    } catch (error) {
      console.error('Failed to write to file:', error);
      return { code: ExportResultCode.FAILED, error };
    }
  }

  /**
   * Cleanup old files based on retention policy
   */
  cleanup() {
    try {
      const files = fs.readdirSync(this.outputDir);
      const now = Date.now();
      const retentionMs = this.retentionDays * 24 * 60 * 60 * 1000;

      files.forEach(file => {
        if (file.startsWith(this.prefix) && file.endsWith('.jsonl')) {
          const filePath = path.join(this.outputDir, file);
          const stats = fs.statSync(filePath);
          const age = now - stats.mtime.getTime();

          if (age > retentionMs) {
            fs.unlinkSync(filePath);
            console.log(`Deleted old file: ${file} (age: ${Math.floor(age / (24 * 60 * 60 * 1000))} days)`);
          }
        }
      });
    } catch (error) {
      console.error('Cleanup failed:', error);
    }
  }
}

/**
 * Trace (Span) Exporter - exports spans to JSONL
 */
class TraceFileExporter extends FileExporter {
  constructor(options = {}) {
    super({
      ...options,
      prefix: 'workflow',
      path: options.path || 'observability/traces'
    });
  }

  /**
   * Export spans (required by OTel interface)
   */
  export(spans, resultCallback) {
    try {
      spans.forEach(span => {
        const spanData = {
          traceId: span.spanContext().traceId,
          spanId: span.spanContext().spanId,
          parentSpanId: span.parentSpanId,
          name: span.name,
          kind: span.kind,
          startTime: span.startTime,
          endTime: span.endTime,
          duration: span.endTime ? span.endTime[0] - span.startTime[0] : null,
          attributes: span.attributes,
          events: span.events.map(event => ({
            name: event.name,
            time: event.time,
            attributes: event.attributes
          })),
          status: span.status,
          resource: span.resource?.attributes || {}
        };

        this.writeLine(spanData);
      });

      resultCallback({ code: ExportResultCode.SUCCESS });
    } catch (error) {
      console.error('Trace export failed:', error);
      resultCallback({ code: ExportResultCode.FAILED, error });
    }
  }

  /**
   * Shutdown exporter
   */
  async shutdown() {
    this.cleanup();
    return Promise.resolve();
  }

  /**
   * Force flush (no-op for file exporter)
   */
  async forceFlush() {
    return Promise.resolve();
  }
}

/**
 * Metric Exporter - exports metrics to JSONL
 */
class MetricFileExporter extends FileExporter {
  constructor(options = {}) {
    super({
      ...options,
      prefix: 'metrics',
      path: options.path || 'observability/metrics'
    });
  }

  /**
   * Export metrics (required by OTel interface)
   */
  export(metrics, resultCallback) {
    try {
      const timestamp = new Date().toISOString();

      // Handle different metric export formats
      if (!metrics || !metrics.resourceMetrics) {
        // Empty metrics, just return success
        resultCallback({ code: ExportResultCode.SUCCESS });
        return;
      }

      metrics.resourceMetrics.forEach(resourceMetric => {
        if (!resourceMetric.scopeMetrics) return;

        resourceMetric.scopeMetrics.forEach(scopeMetric => {
          if (!scopeMetric.metrics) return;

          scopeMetric.metrics.forEach(metric => {
            const metricData = {
              timestamp,
              metric: metric.descriptor?.name || metric.name || 'unknown',
              type: metric.descriptor?.type || metric.type || 'unknown',
              unit: metric.descriptor?.unit || metric.unit || '',
              description: metric.descriptor?.description || metric.description || '',
              dataPoints: this.extractDataPoints(metric),
              resource: resourceMetric.resource?.attributes || {}
            };

            this.writeLine(metricData);
          });
        });
      });

      resultCallback({ code: ExportResultCode.SUCCESS });
    } catch (error) {
      console.error('Metric export failed:', error);
      resultCallback({ code: ExportResultCode.FAILED, error });
    }
  }

  /**
   * Extract data points from metric
   */
  extractDataPoints(metric) {
    const points = [];

    if (metric.dataPoints) {
      metric.dataPoints.forEach(point => {
        points.push({
          value: point.value,
          attributes: point.attributes,
          startTime: point.startTime,
          endTime: point.endTime
        });
      });
    } else if (metric.aggregator) {
      // Handle different aggregator types
      const point = metric.aggregator.toPoint();
      points.push({
        value: point.value,
        attributes: metric.attributes || {}
      });
    }

    return points;
  }

  /**
   * Shutdown exporter
   */
  async shutdown() {
    this.cleanup();
    return Promise.resolve();
  }

  /**
   * Force flush
   */
  async forceFlush() {
    return Promise.resolve();
  }
}

/**
 * Event Exporter - exports domain events to JSONL
 */
class EventFileExporter extends FileExporter {
  constructor(options = {}) {
    super({
      ...options,
      prefix: 'events',
      path: options.path || 'observability/events'
    });
  }

  /**
   * Export a domain event
   */
  exportEvent(event) {
    const eventData = {
      eventId: event.eventId || this.generateUUID(),
      eventType: event.eventType,
      aggregateId: event.aggregateId,
      aggregateType: event.aggregateType || 'WorkflowSession',
      version: event.version || 1,
      timestamp: event.timestamp || new Date().toISOString(),
      correlationId: event.correlationId, // trace_id
      causationId: event.causationId, // span_id or parent event_id
      metadata: event.metadata || {},
      payload: event.payload || {}
    };

    return this.writeLine(eventData);
  }

  /**
   * Generate UUID for event ID
   */
  generateUUID() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
      const r = Math.random() * 16 | 0;
      const v = c === 'x' ? r : (r & 0x3 | 0x8);
      return v.toString(16);
    });
  }

  /**
   * Shutdown exporter
   */
  async shutdown() {
    this.cleanup();
    return Promise.resolve();
  }
}

/**
 * Structured Log Exporter - exports logs to JSONL
 */
class LogFileExporter extends FileExporter {
  constructor(options = {}) {
    super({
      ...options,
      prefix: 'logs',
      path: options.path || 'observability/logs',
      retention_days: options.retention_days || 7 // Shorter retention for logs
    });
  }

  /**
   * Export a log entry
   */
  log(level, message, context = {}) {
    const logEntry = {
      timestamp: new Date().toISOString(),
      level: level.toUpperCase(),
      message,
      ...context
    };

    return this.writeLine(logEntry);
  }

  /**
   * Convenience methods for log levels
   */
  error(message, context) { return this.log('error', message, context); }
  warn(message, context) { return this.log('warn', message, context); }
  info(message, context) { return this.log('info', message, context); }
  debug(message, context) { return this.log('debug', message, context); }

  /**
   * Shutdown exporter
   */
  async shutdown() {
    this.cleanup();
    return Promise.resolve();
  }
}

module.exports = {
  TraceFileExporter,
  MetricFileExporter,
  EventFileExporter,
  LogFileExporter
};
