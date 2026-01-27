const {
  getAgentInfo,
  formatAgentName,
  extractAgentId,
  getQualityScoreClass,
  getQualityScoreEmoji
} = require('./agent-identity');

/**
 * Builds timeline structure from aggregated observability data
 */
class TimelineBuilder {
  /**
   * Builds complete timeline structure
   */
  buildTimeline(aggregatedData) {
    const { spans, events, metadata } = aggregatedData;

    // Build hierarchical rows from spans
    const rows = this.buildRows(spans, events, metadata);

    // Calculate time scale for rendering
    const timeScale = this.calculateTimeScale(metadata.totalDuration);

    // Extract milestone events
    const milestones = this.extractMilestones(events, metadata.startTime);

    return {
      metadata,
      rows,
      timeScale,
      milestones
    };
  }

  /**
   * Builds timeline rows from spans and events
   */
  buildRows(spans, events, metadata) {
    const rows = [];

    // First pass: build basic rows
    const basicRows = this.buildBasicRows(spans, events, metadata);

    // Second pass: enrich with quality scores and agent info
    const enrichedRows = this.enrichWithQualityScores(basicRows, events);

    return enrichedRows;
  }

  /**
   * Builds basic timeline rows from spans
   */
  buildBasicRows(spans, events, metadata) {
    const rows = [];

    // Find root WorkflowSession span
    const rootSpan = spans.find(s => !s.parentSpanId && s.name === 'WorkflowSession');
    if (!rootSpan) {
      // No proper root span - use first span as reference
      if (spans.length === 0) return rows;
      const referenceSpan = spans[0];

      // Show all spans as top-level rows
      const allSpans = spans
        .filter(s => s.name !== 'WorkflowSession')
        .sort((a, b) => {
          const aTime = Array.isArray(a.startTime) ? a.startTime[0] : a.startTime;
          const bTime = Array.isArray(b.startTime) ? b.startTime[0] : b.startTime;
          return aTime - bTime;
        });

      allSpans.forEach(span => {
        const startOffset = this.calculateOffset(span.startTime, referenceSpan.startTime);
        const duration = this.calculateDuration(span.startTime, span.endTime);

        // Extract agent information
        const agentId = extractAgentId(span);
        const agentInfo = getAgentInfo(agentId);

        const row = {
          type: this.getRowType(span.name),
          name: this.formatSpanName(span.name, span.attributes),
          displayName: agentInfo.displayName,
          fullDisplayName: formatAgentName(agentId),
          role: agentInfo.role,
          emoji: agentInfo.emoji,
          agentColor: agentInfo.color,
          agentId: agentId,
          spanId: span.spanId,
          startOffset: startOffset,
          duration: duration,
          status: this.determineStatus(span, events),
          statusIcon: this.getStatusIcon(span, events),
          attributes: span.attributes || {},
          error: this.extractError(span, events),
          events: this.getRowEvents(span, events, referenceSpan.startTime),
          indentLevel: 0,
          attemptNumber: span.attributes?.['attempt.number'] || null,
          hasQualityData: false,
          qualityScore: null,
          isValid: null,
          feedback: []
        };

        rows.push(row);
      });

      return rows;
    }

    // Get child spans and sort by start time
    const childSpans = spans
      .filter(s => s.parentSpanId)
      .sort((a, b) => {
        const aTime = Array.isArray(a.startTime) ? a.startTime[0] : a.startTime;
        const bTime = Array.isArray(b.startTime) ? b.startTime[0] : b.startTime;
        return aTime - bTime;
      });

    // If no child spans, show root-level spans (excluding WorkflowSession)
    if (childSpans.length === 0) {
      const topLevelSpans = spans
        .filter(s => s.name !== 'WorkflowSession')
        .sort((a, b) => {
          const aTime = Array.isArray(a.startTime) ? a.startTime[0] : a.startTime;
          const bTime = Array.isArray(b.startTime) ? b.startTime[0] : b.startTime;
          return aTime - bTime;
        });

      topLevelSpans.forEach(span => {
        const startOffset = this.calculateOffset(span.startTime, rootSpan.startTime);
        const duration = this.calculateDuration(span.startTime, span.endTime);

        // Extract agent information
        const agentId = extractAgentId(span);
        const agentInfo = getAgentInfo(agentId);

        const row = {
          type: this.getRowType(span.name),
          name: this.formatSpanName(span.name, span.attributes),
          displayName: agentInfo.displayName,
          fullDisplayName: formatAgentName(agentId),
          role: agentInfo.role,
          emoji: agentInfo.emoji,
          agentColor: agentInfo.color,
          agentId: agentId,
          spanId: span.spanId,
          startOffset: startOffset,
          duration: duration,
          status: this.determineStatus(span, events),
          statusIcon: this.getStatusIcon(span, events),
          attributes: span.attributes || {},
          error: this.extractError(span, events),
          events: this.getRowEvents(span, events, rootSpan.startTime),
          indentLevel: 0,
          attemptNumber: span.attributes?.['attempt.number'] || null,
          hasQualityData: false,
          qualityScore: null,
          isValid: null,
          feedback: []
        };

        rows.push(row);
      });

      return rows;
    }

    // Build rows for each child span
    childSpans.forEach(span => {
      const startOffset = this.calculateOffset(span.startTime, rootSpan.startTime);
      const duration = this.calculateDuration(span.startTime, span.endTime);

      // Extract agent information
      const agentId = extractAgentId(span);
      const agentInfo = getAgentInfo(agentId);

      const row = {
        type: this.getRowType(span.name),
        name: this.formatSpanName(span.name, span.attributes),
        displayName: agentInfo.displayName,
        fullDisplayName: formatAgentName(agentId),
        role: agentInfo.role,
        emoji: agentInfo.emoji,
        agentColor: agentInfo.color,
        agentId: agentId,
        spanId: span.spanId,
        startOffset: startOffset,
        duration: duration,
        status: this.determineStatus(span, events),
        statusIcon: this.getStatusIcon(span, events),
        attributes: span.attributes || {},
        error: this.extractError(span, events),
        events: this.getRowEvents(span, events, metadata.startTime),
        indentLevel: this.calculateIndent(span.name, span.attributes),
        attemptNumber: span.attributes?.['attempt.number'] || null,
        hasQualityData: false,
        qualityScore: null,
        isValid: null,
        feedback: []
      };

      rows.push(row);
    });

    return rows;
  }

  /**
   * Enriches rows with quality scores from validation events
   */
  enrichWithQualityScores(rows, events) {
    // Find PromptValidated events
    const validationEvents = events.filter(e => e.eventType === 'PromptValidated');

    validationEvents.forEach(event => {
      const spanId = event.causationId;
      const row = rows.find(r => r.spanId === spanId);

      if (row) {
        row.qualityScore = event.payload?.quality_score;
        row.isValid = event.payload?.is_valid;
        row.feedback = event.payload?.feedback || [];
        row.hasQualityData = true;

        // Update status icon based on quality score
        if (row.qualityScore !== null && row.qualityScore !== undefined) {
          row.qualityScoreClass = getQualityScoreClass(row.qualityScore);
          row.qualityScoreEmoji = getQualityScoreEmoji(row.qualityScore);
        }
      }
    });

    return rows;
  }

  /**
   * Extracts error information from span and events
   */
  extractError(span, events) {
    // Check span status for error
    if (span.status?.code === 2) {
      return {
        message: span.status.message || 'Unknown error',
        type: 'span_error',
        stack: span.attributes?.['exception.stacktrace'] || null,
        details: span.attributes?.['error.details'] || null
      };
    }

    // Check validation failures
    if (span.name.includes('Validation')) {
      const validationEvent = events.find(e =>
        e.eventType === 'PromptValidated' &&
        e.causationId === span.spanId
      );

      if (validationEvent && validationEvent.payload?.quality_score < 70) {
        return {
          message: `Validation failed with score ${validationEvent.payload.quality_score}/100`,
          type: 'validation_failure',
          score: validationEvent.payload.quality_score,
          feedback: validationEvent.payload.feedback || []
        };
      }
    }

    return null;
  }

  /**
   * Calculates time offset in milliseconds between two OTel timestamps
   */
  calculateOffset(spanTime, rootTime) {
    const spanMs = Array.isArray(spanTime)
      ? spanTime[0] * 1000 + spanTime[1] / 1000000
      : spanTime;

    const rootMs = Array.isArray(rootTime)
      ? rootTime[0] * 1000 + rootTime[1] / 1000000
      : rootTime;

    return Math.max(0, spanMs - rootMs);
  }

  /**
   * Calculates duration in milliseconds between start and end OTel timestamps
   */
  calculateDuration(startTime, endTime) {
    const startMs = Array.isArray(startTime)
      ? startTime[0] * 1000 + startTime[1] / 1000000
      : startTime;

    const endMs = Array.isArray(endTime)
      ? endTime[0] * 1000 + endTime[1] / 1000000
      : endTime;

    return Math.max(0, endMs - startMs);
  }

  /**
   * Determines row type based on span name
   */
  getRowType(spanName) {
    if (spanName.includes('Generation')) return 'generation';
    if (spanName.includes('Validation')) return 'validation';
    if (spanName.includes('Feedback')) return 'feedback';
    if (spanName.includes('Analysis')) return 'analysis';
    if (spanName.includes('Attempt')) return 'attempt';
    return 'stage';
  }

  /**
   * Formats span name for display
   */
  formatSpanName(spanName, attributes) {
    // Check for attempt number
    const attemptNum = attributes?.['attempt.number'];
    if (attemptNum) {
      return `Attempt #${attemptNum} - ${spanName}`;
    }

    // Clean up technical names
    return spanName
      .replace(/([A-Z])/g, ' $1')  // Add space before capitals
      .trim()
      .replace(/\s+/g, ' ');        // Normalize whitespace
  }

  /**
   * Determines status based on span and related events
   */
  determineStatus(span, events) {
    // Check span status code (OTel: 0=unset, 1=ok, 2=error)
    if (span.status?.code === 2) return 'error';

    // For validation spans, check quality score
    if (span.name.includes('Validation')) {
      const validationEvent = events.find(e =>
        e.eventType === 'PromptValidated' &&
        e.causationId === span.spanId
      );

      if (validationEvent) {
        const score = validationEvent.payload?.quality_score;
        if (score >= 90) return 'success';
        if (score >= 70) return 'warning';
        return 'error';
      }
    }

    // Default to success if span completed without errors
    return span.status?.code === 1 ? 'success' : 'info';
  }

  /**
   * Gets status icon based on status
   */
  getStatusIcon(span, events) {
    const status = this.determineStatus(span, events);

    const icons = {
      success: '✓',
      warning: '⚠',
      error: '✗',
      info: 'ℹ'
    };

    return icons[status] || '•';
  }

  /**
   * Gets events associated with a specific span
   */
  getRowEvents(span, events, startTime) {
    return events
      .filter(e => e.causationId === span.spanId)
      .map(e => ({
        type: e.eventType,
        offset: this.calculateEventOffset(e.timestamp, startTime),
        payload: e.payload
      }));
  }

  /**
   * Calculates event offset from workflow start
   */
  calculateEventOffset(eventTime, startTime) {
    const eventDate = new Date(eventTime);
    const startDate = startTime instanceof Date ? startTime : new Date(startTime);
    return Math.max(0, eventDate - startDate);
  }

  /**
   * Calculates indentation level based on span hierarchy
   */
  calculateIndent(spanName, attributes) {
    // Attempts at level 1
    if (attributes?.['attempt.number']) return 1;

    // Generator/Validator within attempts at level 2
    if (spanName.includes('Generation') || spanName.includes('Validation')) return 2;

    // Feedback at level 1
    if (spanName.includes('Feedback')) return 1;

    // Default no indent
    return 0;
  }

  /**
   * Calculates time scale markers for the timeline
   */
  calculateTimeScale(totalDuration) {
    // Determine appropriate interval based on duration
    const intervals = [
      { threshold: 1000, interval: 100, unit: 'ms' },      // <1s: 100ms intervals
      { threshold: 10000, interval: 1000, unit: 's' },     // <10s: 1s intervals
      { threshold: 60000, interval: 5000, unit: 's' },     // <1m: 5s intervals
      { threshold: 300000, interval: 30000, unit: 's' },   // <5m: 30s intervals
      { threshold: Infinity, interval: 60000, unit: 'm' }  // >=5m: 1m intervals
    ];

    const config = intervals.find(i => totalDuration < i.threshold);
    const numMarkers = Math.ceil(totalDuration / config.interval);

    const markers = [];
    for (let i = 0; i <= numMarkers; i++) {
      const value = i * config.interval;
      markers.push({
        offset: value,
        label: this.formatTimeMarker(value, config.unit)
      });
    }

    return {
      markers,
      interval: config.interval,
      unit: config.unit,
      totalDuration
    };
  }

  /**
   * Formats time marker label
   */
  formatTimeMarker(ms, unit) {
    if (unit === 'ms') {
      return `${ms}ms`;
    } else if (unit === 's') {
      return `${(ms / 1000).toFixed(1)}s`;
    } else if (unit === 'm') {
      return `${(ms / 60000).toFixed(1)}m`;
    }
    return `${ms}ms`;
  }

  /**
   * Extracts milestone events for timeline
   */
  extractMilestones(events, startTime) {
    const milestoneTypes = [
      'WorkflowSessionStarted',
      'WorkflowSessionCompleted',
      'PromptGenerated',
      'PromptValidated',
      'FeedbackGenerated'
    ];

    return events
      .filter(e => milestoneTypes.includes(e.eventType))
      .map(e => ({
        type: e.eventType,
        offset: this.calculateEventOffset(e.timestamp, startTime),
        label: this.formatMilestoneLabel(e),
        payload: e.payload
      }))
      .sort((a, b) => a.offset - b.offset);
  }

  /**
   * Formats milestone label for display
   */
  formatMilestoneLabel(event) {
    const labels = {
      'WorkflowSessionStarted': 'Started',
      'WorkflowSessionCompleted': 'Completed',
      'PromptGenerated': 'Prompt Generated',
      'PromptValidated': 'Validated',
      'FeedbackGenerated': 'Feedback Generated'
    };

    return labels[event.eventType] || event.eventType;
  }
}

module.exports = { TimelineBuilder };
