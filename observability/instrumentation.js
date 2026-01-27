/**
 * Instrumentation Utilities for Workflows
 *
 * High-level helpers for creating spans, emitting events, recording metrics,
 * and structured logging with correlation.
 */

const { SpanStatusCode, context, trace } = require('@opentelemetry/api');
const { getTracer, getMeter, getEventExporter, getLogger } = require('./otel-setup');

/**
 * Generate UUID for session/event IDs
 */
function generateUUID() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    const r = Math.random() * 16 | 0;
    const v = c === 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}

/**
 * Get current trace context (trace_id, span_id)
 */
function getCurrentTraceContext() {
  const activeSpan = trace.getActiveSpan();
  if (activeSpan) {
    const spanContext = activeSpan.spanContext();
    return {
      trace_id: spanContext.traceId,
      span_id: spanContext.spanId
    };
  }
  return { trace_id: null, span_id: null };
}

/**
 * Workflow Session Instrumentation
 */
class WorkflowInstrumentation {
  constructor(workflowId, workflowPattern) {
    this.tracer = getTracer();
    this.meter = getMeter();
    this.eventExporter = getEventExporter();
    this.logger = getLogger();

    this.workflowId = workflowId;
    this.workflowPattern = workflowPattern;
    this.sessionId = generateUUID();

    // Metrics
    this.sessionsCounter = this.meter.createCounter('workflow.sessions.total', {
      description: 'Total number of workflow sessions started'
    });

    this.attemptsCounter = this.meter.createCounter('workflow.attempts.total', {
      description: 'Total number of workflow attempts'
    });

    this.validationCounter = this.meter.createCounter('workflow.validations.total', {
      description: 'Total number of validations',
      unit: 'validations'
    });

    this.durationHistogram = this.meter.createHistogram('workflow.duration_ms', {
      description: 'Workflow session duration',
      unit: 'ms'
    });

    this.qualityScoreHistogram = this.meter.createHistogram('workflow.quality_score', {
      description: 'Quality score of workflow outputs',
      unit: 'score'
    });

    this.attemptDurationHistogram = this.meter.createHistogram('workflow.attempt_duration_ms', {
      description: 'Duration of individual attempts',
      unit: 'ms'
    });
  }

  /**
   * Start workflow session (creates root span) - manually managed
   */
  startSession(task, metadata = {}) {
    // Create span manually (not with callback)
    this.rootSpan = this.tracer.startSpan('WorkflowSession', {
      attributes: {
        'workflow.id': this.workflowId,
        'workflow.pattern': this.workflowPattern,
        'session.id': this.sessionId,
        'workflow.task': task,
        ...metadata
      }
    });

    // Increment session counter
    this.sessionsCounter.add(1, {
      'workflow.id': this.workflowId
    });

    // Emit WorkflowSessionStarted event
    const traceContext = getCurrentTraceContext();
    this.eventExporter.exportEvent({
      eventType: 'WorkflowSessionStarted',
      aggregateId: this.sessionId,
      aggregateType: 'WorkflowSession',
      version: 1,
      correlationId: traceContext.trace_id,
      causationId: traceContext.span_id,
      payload: {
        workflow_id: this.workflowId,
        workflow_pattern: this.workflowPattern,
        task,
        ...metadata
      }
    });

    // Log session start
    this.logger.info('Workflow session started', {
      session_id: this.sessionId,
      workflow_id: this.workflowId,
      task,
      trace_id: traceContext.trace_id,
      span_id: traceContext.span_id
    });
  }

  /**
   * Start an attempt (creates child span) - manually managed
   */
  startAttempt(attemptNumber, maxAttempts) {
    // End previous attempt span if exists
    if (this.currentAttemptSpan) {
      this.currentAttemptSpan.end();
    }

    // Create new attempt span
    this.currentAttemptSpan = this.tracer.startSpan('Attempt', {
      attributes: {
        'attempt.number': attemptNumber,
        'attempt.max': maxAttempts,
        'session.id': this.sessionId
      }
    });

    // Increment attempt counter
    this.attemptsCounter.add(1, {
      'workflow.id': this.workflowId,
      'session.id': this.sessionId
    });

    // Emit AttemptInitiated event
    const traceContext = getCurrentTraceContext();
    this.eventExporter.exportEvent({
      eventType: 'AttemptInitiated',
      aggregateId: this.sessionId,
      aggregateType: 'WorkflowSession',
      version: attemptNumber + 1,
      correlationId: traceContext.trace_id,
      causationId: traceContext.span_id,
      payload: {
        attempt_number: attemptNumber,
        max_attempts: maxAttempts
      }
    });

    // Log attempt start
    this.logger.info('Attempt started', {
      session_id: this.sessionId,
      attempt_number: attemptNumber,
      max_attempts: maxAttempts,
      trace_id: traceContext.trace_id,
      span_id: traceContext.span_id
    });
  }

  /**
   * Instrument a stage execution (creates child span)
   */
  async instrumentStage(stageId, agentId, stageFunction) {
    const startTime = Date.now();
    const stageSpan = this.tracer.startSpan(stageId, {
      attributes: {
        'stage.id': stageId,
        'stage.agent_id': agentId,
        'session.id': this.sessionId
      }
    });

    const traceContext = getCurrentTraceContext();

    try {
      // Log stage start
      this.logger.info(`Stage ${stageId} started`, {
        session_id: this.sessionId,
        stage_id: stageId,
        agent_id: agentId,
        trace_id: traceContext.trace_id,
        span_id: traceContext.span_id
      });

      // Emit AgentInvoked event
      this.eventExporter.exportEvent({
        eventType: 'AgentInvoked',
        aggregateId: this.sessionId,
        aggregateType: 'WorkflowSession',
        correlationId: traceContext.trace_id,
        causationId: traceContext.span_id,
        payload: {
          stage_id: stageId,
          agent_id: agentId
        }
      });

      // Execute stage
      const result = await stageFunction();

      const duration = Date.now() - startTime;

      // Add completion event to span
      stageSpan.addEvent('StageCompleted', {
        'stage.duration_ms': duration,
        'stage.output_size': JSON.stringify(result).length
      });

      // Emit StageCompleted event
      this.eventExporter.exportEvent({
        eventType: 'StageCompleted',
        aggregateId: this.sessionId,
        aggregateType: 'WorkflowSession',
        correlationId: traceContext.trace_id,
        causationId: traceContext.span_id,
        payload: {
          stage_id: stageId,
          agent_id: agentId,
          duration_ms: duration
        }
      });

      // Log stage completion
      this.logger.info(`Stage ${stageId} completed`, {
        session_id: this.sessionId,
        stage_id: stageId,
        agent_id: agentId,
        duration_ms: duration,
        trace_id: traceContext.trace_id,
        span_id: traceContext.span_id
      });

      stageSpan.setStatus({ code: SpanStatusCode.OK });
      stageSpan.end();

      return result;
    } catch (error) {
      const duration = Date.now() - startTime;

      // Add error event to span
      stageSpan.addEvent('StageExecutionFailed', {
        'error.type': error.name,
        'error.message': error.message,
        'stage.duration_ms': duration
      });

      // Log error
      this.logger.error(`Stage ${stageId} failed`, {
        session_id: this.sessionId,
        stage_id: stageId,
        agent_id: agentId,
        error: error.message,
        duration_ms: duration,
        trace_id: traceContext.trace_id,
        span_id: traceContext.span_id
      });

      stageSpan.setStatus({
        code: SpanStatusCode.ERROR,
        message: error.message
      });
      stageSpan.end();

      throw error;
    }
  }

  /**
   * Record validation result
   */
  recordValidation(isValid, qualityScore, feedback = []) {
    const traceContext = getCurrentTraceContext();

    // Increment validation counter
    this.validationCounter.add(1, {
      'workflow.id': this.workflowId,
      'validation.status': isValid ? 'passed' : 'failed'
    });

    // Record quality score
    this.qualityScoreHistogram.record(qualityScore, {
      'workflow.id': this.workflowId,
      'session.id': this.sessionId
    });

    // Emit PromptValidated event
    this.eventExporter.exportEvent({
      eventType: isValid ? 'PromptValidated' : 'PromptRejected',
      aggregateId: this.sessionId,
      aggregateType: 'WorkflowSession',
      correlationId: traceContext.trace_id,
      causationId: traceContext.span_id,
      payload: {
        is_valid: isValid,
        quality_score: qualityScore,
        feedback_count: feedback.length,
        feedback: feedback
      }
    });

    // Log validation
    this.logger.info('Validation completed', {
      session_id: this.sessionId,
      is_valid: isValid,
      quality_score: qualityScore,
      feedback_count: feedback.length,
      trace_id: traceContext.trace_id,
      span_id: traceContext.span_id
    });

    // Add event to active span
    const activeSpan = trace.getActiveSpan();
    if (activeSpan) {
      activeSpan.addEvent(isValid ? 'PromptValidated' : 'PromptRejected', {
        'validation.is_valid': isValid,
        'validation.quality_score': qualityScore,
        'validation.feedback_count': feedback.length
      });
    }
  }

  /**
   * Record feedback cycle
   */
  recordFeedbackCycle(feedback) {
    const traceContext = getCurrentTraceContext();

    // Emit FeedbackGenerated event
    this.eventExporter.exportEvent({
      eventType: 'FeedbackGenerated',
      aggregateId: this.sessionId,
      aggregateType: 'WorkflowSession',
      correlationId: traceContext.trace_id,
      causationId: traceContext.span_id,
      payload: {
        feedback_items_count: feedback.length,
        feedback: feedback
      }
    });

    // Log feedback
    this.logger.info('Feedback cycle started', {
      session_id: this.sessionId,
      feedback_items_count: feedback.length,
      trace_id: traceContext.trace_id,
      span_id: traceContext.span_id
    });

    // Add event to active span
    const activeSpan = trace.getActiveSpan();
    if (activeSpan) {
      activeSpan.addEvent('FeedbackCycleStarted', {
        'feedback.items_count': feedback.length
      });
    }
  }

  /**
   * Complete workflow session
   */
  async completeSession(finalScore, attempts, status = 'success') {
    const traceContext = getCurrentTraceContext();

    // Emit WorkflowSessionCompleted event
    this.eventExporter.exportEvent({
      eventType: 'WorkflowSessionCompleted',
      aggregateId: this.sessionId,
      aggregateType: 'WorkflowSession',
      correlationId: traceContext.trace_id,
      causationId: traceContext.span_id,
      payload: {
        final_score: finalScore,
        attempts: attempts,
        status: status
      }
    });

    // Log session completion
    this.logger.info('Workflow session completed', {
      session_id: this.sessionId,
      final_score: finalScore,
      attempts: attempts,
      status: status,
      trace_id: traceContext.trace_id,
      span_id: traceContext.span_id
    });

    // Add event to root span
    if (this.rootSpan) {
      this.rootSpan.addEvent('WorkflowSessionCompleted', {
        'workflow.final_score': finalScore,
        'workflow.attempts': attempts,
        'workflow.status': status
      });

      this.rootSpan.setStatus({
        code: status === 'success' ? SpanStatusCode.OK : SpanStatusCode.ERROR
      });
      this.rootSpan.end();
    }

    // Generate timeline report asynchronously (don't block workflow completion)
    this.generateTimelineReport().catch(err => {
      this.logger.warn('Failed to generate timeline report', {
        session_id: this.sessionId,
        error: err.message
      });
    });
  }

  /**
   * Generates timeline report for this session
   */
  async generateTimelineReport() {
    try {
      // Small delay to ensure all data is flushed to files
      await new Promise(resolve => setTimeout(resolve, 500));

      const { TimelineReportGenerator } = require('./reports/timeline-generator');
      const generator = new TimelineReportGenerator();

      const reportPath = await generator.generate(this.sessionId, new Date());

      this.logger.info('Timeline report generated', {
        session_id: this.sessionId,
        report_path: reportPath
      });

      console.log(`\n📊 Timeline Report: ${reportPath}`);
    } catch (error) {
      // Don't throw - just log the error
      this.logger.error('Timeline report generation failed', {
        session_id: this.sessionId,
        error: error.message
      });
    }
  }

  /**
   * Record attempt duration
   */
  recordAttemptDuration(attemptNumber, durationMs) {
    this.attemptDurationHistogram.record(durationMs, {
      'workflow.id': this.workflowId,
      'attempt.number': attemptNumber
    });
  }

  /**
   * Record session duration
   */
  recordSessionDuration(durationMs) {
    this.durationHistogram.record(durationMs, {
      'workflow.id': this.workflowId,
      'session.id': this.sessionId
    });
  }
}

module.exports = {
  WorkflowInstrumentation,
  generateUUID,
  getCurrentTraceContext
};
