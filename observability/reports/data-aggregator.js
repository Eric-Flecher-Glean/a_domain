const fs = require('fs').promises;
const path = require('path');
const readline = require('readline');
const { createReadStream } = require('fs');

/**
 * Aggregates observability data from JSONL files
 * Reads traces, events, and logs for a specific session
 */
class DataAggregator {
  constructor(baseDir = 'observability') {
    this.baseDir = baseDir;
  }

  /**
   * Main entry point: aggregates all data for a session
   */
  async aggregateSessionData(sessionId, date = new Date()) {
    const dateStr = this.formatDate(date);

    // Read all data sources in parallel
    const [traces, events, logs] = await Promise.all([
      this.readTraces(sessionId, dateStr),
      this.readEvents(sessionId, dateStr),
      this.readLogs(sessionId, dateStr)
    ]);

    if (traces.length === 0) {
      throw new Error(`No trace data found for session ${sessionId} on ${dateStr}`);
    }

    // Extract metadata from root span and events
    const metadata = this.extractMetadata(traces, events);

    return {
      sessionId,
      traceId: traces[0].traceId,
      spans: traces,
      events: events,
      logs: logs,
      metadata: metadata
    };
  }

  /**
   * Reads trace spans from JSONL file
   */
  async readTraces(sessionId, dateStr) {
    const filePath = path.join(this.baseDir, 'traces', `workflow-${dateStr}.jsonl`);
    return this.readJsonlFile(filePath, (line) => {
      // Filter by session_id in attributes
      return line.attributes?.['session.id'] === sessionId;
    });
  }

  /**
   * Reads events from JSONL file
   */
  async readEvents(sessionId, dateStr) {
    const filePath = path.join(this.baseDir, 'events', `events-${dateStr}.jsonl`);
    return this.readJsonlFile(filePath, (line) => {
      // Events use aggregateId for session correlation
      return line.aggregateId === sessionId;
    });
  }

  /**
   * Reads logs from JSONL file
   */
  async readLogs(sessionId, dateStr) {
    const filePath = path.join(this.baseDir, 'logs', `logs-${dateStr}.jsonl`);
    return this.readJsonlFile(filePath, (line) => {
      // Filter by session_id in attributes
      return line.attributes?.session_id === sessionId;
    });
  }

  /**
   * Generic JSONL file reader with filtering
   */
  async readJsonlFile(filePath, filterFn) {
    const results = [];

    try {
      await fs.access(filePath);
    } catch (err) {
      // File doesn't exist - return empty array
      return results;
    }

    const fileStream = createReadStream(filePath);
    const rl = readline.createInterface({
      input: fileStream,
      crlfDelay: Infinity
    });

    for await (const line of rl) {
      if (!line.trim()) continue;

      try {
        const parsed = JSON.parse(line);
        if (!filterFn || filterFn(parsed)) {
          results.push(parsed);
        }
      } catch (err) {
        console.warn(`Failed to parse line in ${filePath}:`, err.message);
      }
    }

    return results;
  }

  /**
   * Extracts high-level metadata from traces and events
   */
  extractMetadata(traces, events) {
    // Find root span (WorkflowSession or any span without parent)
    const rootSpan = traces.find(s => !s.parentSpanId && s.name === 'WorkflowSession')
                     || traces.find(s => !s.parentSpanId);
    if (!rootSpan) {
      throw new Error('No root span found in trace data');
    }

    // Find session started event
    const sessionStartedEvent = events.find(e => e.eventType === 'WorkflowSessionStarted');

    // Convert OTel timestamps (array format: [seconds, nanoseconds])
    const startTime = this.convertOtelTimestamp(rootSpan.startTime);
    const endTime = this.convertOtelTimestamp(rootSpan.endTime);

    // Calculate total duration from timestamp difference (more accurate than stored duration)
    const totalDuration = endTime - startTime;

    return {
      workflowId: rootSpan.attributes?.['workflow.id']
                  || sessionStartedEvent?.payload?.workflow_id
                  || 'Workflow Execution',
      workflowPattern: rootSpan.attributes?.['workflow.pattern']
                       || sessionStartedEvent?.payload?.workflow_pattern
                       || 'generic',
      task: sessionStartedEvent?.payload?.task || rootSpan.attributes?.['workflow.task'] || 'No task description',
      'workflow.output_path': sessionStartedEvent?.payload?.['workflow.output_path'] || null,
      startTime: startTime,
      endTime: endTime,
      totalDuration: totalDuration,
      status: rootSpan.status?.code === 1 ? 'success' : 'error'
    };
  }

  /**
   * Converts OpenTelemetry timestamp format [seconds, nanoseconds] to Date
   */
  convertOtelTimestamp(otelTime) {
    if (Array.isArray(otelTime)) {
      return new Date(otelTime[0] * 1000 + otelTime[1] / 1000000);
    }
    return new Date(otelTime);
  }

  /**
   * Formats date as YYYY-MM-DD
   */
  formatDate(date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  }

  /**
   * Finds the latest session ID from today's files
   */
  async findLatestSession(date = new Date()) {
    const dateStr = this.formatDate(date);
    const filePath = path.join(this.baseDir, 'traces', `workflow-${dateStr}.jsonl`);

    try {
      await fs.access(filePath);
    } catch (err) {
      throw new Error(`No trace file found for ${dateStr}`);
    }

    // Read all session IDs from the file
    const sessionIds = new Set();
    const fileStream = createReadStream(filePath);
    const rl = readline.createInterface({
      input: fileStream,
      crlfDelay: Infinity
    });

    for await (const line of rl) {
      if (!line.trim()) continue;

      try {
        const parsed = JSON.parse(line);
        const sessionId = parsed.attributes?.['session.id'];
        if (sessionId) {
          sessionIds.add(sessionId);
        }
      } catch (err) {
        // Skip invalid lines
      }
    }

    if (sessionIds.size === 0) {
      throw new Error('No sessions found in trace file');
    }

    // Return the last session ID (assuming chronological order in file)
    return Array.from(sessionIds).pop();
  }
}

module.exports = { DataAggregator };
