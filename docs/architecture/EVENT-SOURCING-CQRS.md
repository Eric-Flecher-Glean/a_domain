# Event Sourcing & CQRS Architecture

## Overview

This document describes how **Event Sourcing** and **CQRS (Command Query Responsibility Segregation)** can be applied to the Prompt Engineering system for enhanced auditability, scalability, and temporal querying.

---

## 1. Event Sourcing Architecture

### 1.1 Event Store Structure

```
┌─────────────────────────────────────────────────────────────────┐
│                         EVENT STORE                             │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  Event Stream: workflow-session-{sessionId}               │ │
│  │                                                           │ │
│  │  Version  Event Type                    Timestamp  Data  │ │
│  │  ───────────────────────────────────────────────────────  │ │
│  │  1        WorkflowSessionStarted        14:30:01   {...} │ │
│  │  2        AttemptInitiated              14:30:02   {...} │ │
│  │  3        TaskAnalyzed                  14:30:03   {...} │ │
│  │  4        PromptGenerated               14:30:05   {...} │ │
│  │  5        PromptValidated               14:30:07   {...} │ │
│  │  6        PromptRejected                14:30:07   {...} │ │
│  │  7        FeedbackGenerated             14:30:07   {...} │ │
│  │  8        AttemptInitiated              14:30:08   {...} │ │
│  │  9        FeedbackApplied               14:30:08   {...} │ │
│  │  10       PromptGenerated               14:30:10   {...} │ │
│  │  11       PromptValidated               14:30:12   {...} │ │
│  │  12       PromptApproved                14:30:12   {...} │ │
│  │  13       WorkflowSessionCompleted      14:30:13   {...} │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  Event Stream: prompt-spec-{promptName}                   │ │
│  │                                                           │ │
│  │  Version  Event Type                    Timestamp  Data  │ │
│  │  ───────────────────────────────────────────────────────  │ │
│  │  1        PromptGenerated               14:30:05   {...} │ │
│  │  2        InputAdded                    14:30:05   {...} │ │
│  │  3        InputAdded                    14:30:05   {...} │ │
│  │  4        ContextSourceAdded            14:30:05   {...} │ │
│  │  5        PromptRefined                 14:30:10   {...} │ │
│  │  6        PromptApproved                14:30:12   {...} │ │
│  └───────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 Event Schema

```typescript
// Base Event Interface
interface DomainEvent {
  eventId: string; // UUID
  eventType: string;
  aggregateId: string;
  aggregateType: string;
  version: number;
  timestamp: Date;
  userId?: string;
  correlationId?: string;
  causationId?: string;
  metadata: Record<string, any>;
  payload: Record<string, any>;
}

// Example: WorkflowSessionStarted Event
interface WorkflowSessionStartedEvent extends DomainEvent {
  eventType: 'WorkflowSessionStarted';
  aggregateType: 'WorkflowSession';
  payload: {
    sessionId: string;
    userRequest: string;
    maxAttempts: number;
    analyzeContext: boolean;
  };
}

// Example: PromptGenerated Event
interface PromptGeneratedEvent extends DomainEvent {
  eventType: 'PromptGenerated';
  aggregateType: 'PromptSpecification';
  payload: {
    promptName: string;
    xmlContent: string;
    inputAnalysis: {
      requiredInputs: any[];
      optionalInputs: any[];
      contextSources: any[];
      gleanIntegrations: string[];
    };
    generationMetadata: {
      attempt: number;
      timestamp: string;
      refinementsApplied: string[];
    };
  };
}

// Example: PromptValidated Event
interface PromptValidatedEvent extends DomainEvent {
  eventType: 'PromptValidated';
  aggregateType: 'ValidationResult';
  payload: {
    validationId: string;
    promptName: string;
    attemptNumber: number;
    isValid: boolean;
    qualityScore: number;
    checks: any[];
    feedback: string[];
    scoreBreakdown: {
      structural: number;
      completeness: number;
      quality: number;
      contextQuality: number;
    };
    contextValidation: {
      inputSpecificationPresent: boolean;
      requiredInputsCount: number;
      contextSourcesCount: number;
      gleanIntegrations: string[];
    };
  };
}
```

### 1.3 Event Store Implementation

```typescript
interface EventStore {
  // Append events to a stream
  append(
    streamId: string,
    events: DomainEvent[],
    expectedVersion: number
  ): Promise<void>;

  // Read events from a stream
  readStream(
    streamId: string,
    fromVersion?: number,
    toVersion?: number
  ): Promise<DomainEvent[]>;

  // Read all events across streams
  readAllEvents(
    fromPosition?: number,
    maxCount?: number
  ): Promise<DomainEvent[]>;

  // Subscribe to new events
  subscribe(
    eventType: string | string[],
    handler: (event: DomainEvent) => Promise<void>
  ): Subscription;

  // Create snapshot
  createSnapshot(
    streamId: string,
    version: number,
    snapshot: any
  ): Promise<void>;

  // Read snapshot
  readSnapshot(streamId: string): Promise<{ version: number; snapshot: any } | null>;
}
```

### 1.4 Aggregate Reconstruction from Events

```typescript
class WorkflowSession {
  private events: DomainEvent[] = [];

  // Reconstruct aggregate from event history
  static fromHistory(events: DomainEvent[]): WorkflowSession {
    const session = new WorkflowSession();
    events.forEach(event => session.apply(event, false));
    return session;
  }

  // Apply event to mutate state
  private apply(event: DomainEvent, isNew: boolean = true) {
    switch (event.eventType) {
      case 'WorkflowSessionStarted':
        this.applyWorkflowSessionStarted(event as WorkflowSessionStartedEvent);
        break;
      case 'AttemptInitiated':
        this.applyAttemptInitiated(event as AttemptInitiatedEvent);
        break;
      case 'AttemptCompleted':
        this.applyAttemptCompleted(event as AttemptCompletedEvent);
        break;
      case 'WorkflowSessionCompleted':
        this.applyWorkflowSessionCompleted(event as WorkflowSessionCompletedEvent);
        break;
      // ... more cases
    }

    if (isNew) {
      this.events.push(event);
    }
  }

  private applyWorkflowSessionStarted(event: WorkflowSessionStartedEvent) {
    this.sessionId = event.payload.sessionId;
    this.userRequest = event.payload.userRequest;
    this.maxAttempts = event.payload.maxAttempts;
    this.status = SessionStatus.IN_PROGRESS;
    this.currentAttempt = 0;
  }

  private applyAttemptInitiated(event: AttemptInitiatedEvent) {
    this.currentAttempt = event.payload.attemptNumber;
    this.attemptHistory.push({
      attemptNumber: event.payload.attemptNumber,
      startedAt: event.timestamp
    });
  }

  // ... more apply methods
}
```

---

## 2. CQRS Architecture

### 2.1 Command/Query Separation

```
┌─────────────────────────────────────────────────────────────────┐
│                         WRITE SIDE (Commands)                   │
│                                                                 │
│  Client                                                         │
│    │                                                            │
│    │ Command: GeneratePrompt                                   │
│    │ {                                                          │
│    │   task: "Create prompt...",                               │
│    │   maxAttempts: 3                                          │
│    │ }                                                          │
│    ▼                                                            │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Command Handler                                        │   │
│  │  - Validate command                                     │   │
│  │  - Load aggregate from event store                      │   │
│  │  - Execute domain logic                                 │   │
│  │  - Persist new events to event store                    │   │
│  │  - Publish events to event bus                          │   │
│  └─────────────────────────────────────────────────────────┘   │
│    │                                                            │
│    │ Events Published                                          │
│    ▼                                                            │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Event Store                                            │   │
│  │  - WorkflowSessionStarted                               │   │
│  │  - AttemptInitiated                                     │   │
│  │  - PromptGenerated                                      │   │
│  │  - ...                                                  │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ Event Bus
                              │
┌─────────────────────────────▼───────────────────────────────────┐
│                         READ SIDE (Queries)                     │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Event Projections (Read Model Updaters)               │   │
│  │                                                         │   │
│  │  ┌───────────────────────────────────────────────────┐ │   │
│  │  │  WorkflowSessionListProjection                    │ │   │
│  │  │  - Subscribe to: WorkflowSessionStarted,          │ │   │
│  │  │                  WorkflowSessionCompleted         │ │   │
│  │  │  - Update: workflow_sessions table                │ │   │
│  │  └───────────────────────────────────────────────────┘ │   │
│  │                                                         │   │
│  │  ┌───────────────────────────────────────────────────┐ │   │
│  │  │  PromptCatalogProjection                          │ │   │
│  │  │  - Subscribe to: PromptGenerated, PromptApproved  │ │   │
│  │  │  - Update: prompt_catalog table                   │ │   │
│  │  └───────────────────────────────────────────────────┘ │   │
│  │                                                         │   │
│  │  ┌───────────────────────────────────────────────────┐ │   │
│  │  │  ValidationHistoryProjection                      │ │   │
│  │  │  - Subscribe to: PromptValidated                  │ │   │
│  │  │  - Update: validation_history table               │ │   │
│  │  └───────────────────────────────────────────────────┘ │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                  │
│                              ▼                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Read Models (Optimized for Queries)                   │   │
│  │                                                         │   │
│  │  ┌─────────────────────────────────────────────────┐   │   │
│  │  │  workflow_sessions (Table)                      │   │   │
│  │  │  - session_id, user_request, status,           │   │   │
│  │  │    current_attempt, final_score, duration       │   │   │
│  │  └─────────────────────────────────────────────────┘   │   │
│  │                                                         │   │
│  │  ┌─────────────────────────────────────────────────┐   │   │
│  │  │  prompt_catalog (Table)                         │   │   │
│  │  │  - prompt_name, task_description, quality_score,│   │   │
│  │  │    glean_integrations, created_at               │   │   │
│  │  └─────────────────────────────────────────────────┘   │   │
│  │                                                         │   │
│  │  ┌─────────────────────────────────────────────────┐   │   │
│  │  │  validation_history (Table)                     │   │   │
│  │  │  - validation_id, prompt_name, attempt_number,  │   │   │
│  │  │    quality_score, feedback_items                │   │   │
│  │  └─────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────┘   │
│    │                                                            │
│    │ Query: GetWorkflowSessions                                │
│    │ Query: GetPromptByName                                    │
│    │ Query: GetValidationHistory                               │
│    ▼                                                            │
│  Client                                                         │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Command Definitions

```typescript
// Base Command
interface Command {
  commandId: string;
  commandType: string;
  timestamp: Date;
  userId?: string;
  correlationId?: string;
}

// Generate Prompt Command
interface GeneratePromptCommand extends Command {
  commandType: 'GeneratePrompt';
  payload: {
    task: string;
    maxAttempts: number;
    analyzeContext: boolean;
  };
}

// Retry Attempt Command
interface RetryAttemptCommand extends Command {
  commandType: 'RetryAttempt';
  payload: {
    sessionId: string;
    feedback: string[];
  };
}

// Approve Prompt Command
interface ApprovePromptCommand extends Command {
  commandType: 'ApprovePrompt';
  payload: {
    validationId: string;
    promptName: string;
  };
}
```

### 2.3 Query Definitions

```typescript
// Base Query
interface Query {
  queryType: string;
}

// Get Workflow Sessions Query
interface GetWorkflowSessionsQuery extends Query {
  queryType: 'GetWorkflowSessions';
  filters?: {
    status?: string;
    fromDate?: Date;
    toDate?: Date;
  };
  pagination?: {
    page: number;
    pageSize: number;
  };
}

// Get Prompt By Name Query
interface GetPromptByNameQuery extends Query {
  queryType: 'GetPromptByName';
  promptName: string;
}

// Get Validation History Query
interface GetValidationHistoryQuery extends Query {
  queryType: 'GetValidationHistory';
  promptName: string;
}

// Search Prompts Query
interface SearchPromptsQuery extends Query {
  queryType: 'SearchPrompts';
  searchTerm: string;
  filters?: {
    minQualityScore?: number;
    gleanTools?: string[];
    taskPattern?: string;
  };
}
```

### 2.4 Read Model Projections

```typescript
// Projection Base Class
abstract class Projection {
  abstract get eventTypes(): string[];
  abstract handle(event: DomainEvent): Promise<void>;
}

// Workflow Session List Projection
class WorkflowSessionListProjection extends Projection {
  get eventTypes() {
    return [
      'WorkflowSessionStarted',
      'AttemptInitiated',
      'AttemptCompleted',
      'WorkflowSessionCompleted',
      'WorkflowSessionFailed'
    ];
  }

  async handle(event: DomainEvent): Promise<void> {
    switch (event.eventType) {
      case 'WorkflowSessionStarted':
        await this.handleSessionStarted(event);
        break;
      case 'AttemptInitiated':
        await this.handleAttemptInitiated(event);
        break;
      case 'WorkflowSessionCompleted':
        await this.handleSessionCompleted(event);
        break;
      // ... more cases
    }
  }

  private async handleSessionStarted(event: DomainEvent) {
    await db.insert('workflow_sessions', {
      session_id: event.aggregateId,
      user_request: event.payload.userRequest,
      status: 'IN_PROGRESS',
      max_attempts: event.payload.maxAttempts,
      current_attempt: 0,
      started_at: event.timestamp
    });
  }

  private async handleAttemptInitiated(event: DomainEvent) {
    await db.update('workflow_sessions')
      .where({ session_id: event.aggregateId })
      .set({
        current_attempt: event.payload.attemptNumber,
        updated_at: event.timestamp
      });
  }

  private async handleSessionCompleted(event: DomainEvent) {
    await db.update('workflow_sessions')
      .where({ session_id: event.aggregateId })
      .set({
        status: 'SUCCESS',
        final_score: event.payload.finalScore,
        completed_at: event.timestamp,
        duration: event.payload.duration
      });
  }
}

// Prompt Catalog Projection
class PromptCatalogProjection extends Projection {
  get eventTypes() {
    return ['PromptGenerated', 'PromptApproved'];
  }

  async handle(event: DomainEvent): Promise<void> {
    switch (event.eventType) {
      case 'PromptGenerated':
        await this.handlePromptGenerated(event);
        break;
      case 'PromptApproved':
        await this.handlePromptApproved(event);
        break;
    }
  }

  private async handlePromptGenerated(event: DomainEvent) {
    await db.insert('prompt_catalog', {
      prompt_name: event.payload.promptName,
      task_description: event.payload.taskDescription,
      xml_content: event.payload.xmlContent,
      input_analysis: JSON.stringify(event.payload.inputAnalysis),
      glean_integrations: event.payload.inputAnalysis.gleanIntegrations,
      created_at: event.timestamp,
      status: 'PENDING_APPROVAL'
    });
  }

  private async handlePromptApproved(event: DomainEvent) {
    await db.update('prompt_catalog')
      .where({ prompt_name: event.payload.promptName })
      .set({
        status: 'APPROVED',
        quality_score: event.payload.qualityScore,
        approved_at: event.timestamp
      });
  }
}
```

---

## 3. Temporal Queries (Time Travel)

### 3.1 Point-in-Time Queries

```typescript
class TemporalQueryService {
  // Get aggregate state at specific point in time
  async getAggregateAtTime<T>(
    aggregateId: string,
    timestamp: Date
  ): Promise<T> {
    const events = await this.eventStore.readStream(
      aggregateId,
      undefined, // from version 1
      undefined  // to latest
    );

    // Filter events up to timestamp
    const eventsUpToTime = events.filter(
      event => event.timestamp <= timestamp
    );

    // Reconstruct aggregate from historical events
    return this.reconstructAggregate<T>(eventsUpToTime);
  }

  // Query how many prompts were approved yesterday
  async getApprovedPromptsYesterday(): Promise<number> {
    const yesterday = new Date();
    yesterday.setDate(yesterday.getDate() - 1);
    yesterday.setHours(0, 0, 0, 0);

    const today = new Date();
    today.setHours(0, 0, 0, 0);

    const events = await this.eventStore.readAllEvents();
    return events.filter(e =>
      e.eventType === 'PromptApproved' &&
      e.timestamp >= yesterday &&
      e.timestamp < today
    ).length;
  }

  // Get quality score trend over time
  async getQualityScoreTrend(
    promptName: string
  ): Promise<{ timestamp: Date; score: number }[]> {
    const events = await this.eventStore.readStream(`prompt-spec-${promptName}`);

    return events
      .filter(e => e.eventType === 'PromptValidated')
      .map(e => ({
        timestamp: e.timestamp,
        score: e.payload.qualityScore
      }));
  }
}
```

### 3.2 Audit Trail

```typescript
class AuditService {
  // Get complete audit trail for a session
  async getSessionAuditTrail(sessionId: string): Promise<AuditEntry[]> {
    const events = await this.eventStore.readStream(`workflow-session-${sessionId}`);

    return events.map(event => ({
      timestamp: event.timestamp,
      eventType: event.eventType,
      user: event.userId,
      changes: this.extractChanges(event),
      metadata: event.metadata
    }));
  }

  // Track who approved/rejected prompts
  async getApprovalHistory(promptName: string): Promise<ApprovalHistory[]> {
    const events = await this.eventStore.readAllEvents();

    return events
      .filter(e =>
        (e.eventType === 'PromptApproved' || e.eventType === 'PromptRejected') &&
        e.payload.promptName === promptName
      )
      .map(e => ({
        timestamp: e.timestamp,
        action: e.eventType === 'PromptApproved' ? 'APPROVED' : 'REJECTED',
        approver: e.userId,
        qualityScore: e.payload.qualityScore,
        feedback: e.payload.feedback
      }));
  }
}
```

---

## 4. Event-Driven Integrations

### 4.1 Event Subscribers

```typescript
// Analytics Subscriber
class AnalyticsSubscriber {
  constructor(private analytics: AnalyticsService) {}

  async handlePromptApproved(event: PromptApprovedEvent) {
    await this.analytics.track('prompt_approved', {
      promptName: event.payload.promptName,
      qualityScore: event.payload.qualityScore,
      attemptNumber: event.payload.attemptNumber,
      gleanTools: event.payload.gleanIntegrations
    });
  }

  async handleWorkflowSessionCompleted(event: WorkflowSessionCompletedEvent) {
    await this.analytics.track('workflow_completed', {
      sessionId: event.aggregateId,
      duration: event.payload.duration,
      attempts: event.payload.attempts,
      success: event.payload.status === 'SUCCESS'
    });
  }
}

// Notification Subscriber
class NotificationSubscriber {
  async handlePromptRejected(event: PromptRejectedEvent) {
    if (event.payload.attemptNumber === 3) {
      await this.sendAlert({
        type: 'MAX_ATTEMPTS_REACHED',
        sessionId: event.aggregateId,
        promptName: event.payload.promptName,
        finalScore: event.payload.qualityScore
      });
    }
  }

  async handleWorkflowSessionFailed(event: WorkflowSessionFailedEvent) {
    await this.sendAlert({
      type: 'WORKFLOW_FAILED',
      sessionId: event.aggregateId,
      reason: event.payload.reason
    });
  }
}

// Cache Invalidation Subscriber
class CacheInvalidationSubscriber {
  async handlePromptGenerated(event: PromptGeneratedEvent) {
    await this.cache.invalidate(`prompt:${event.payload.promptName}`);
  }

  async handlePromptApproved(event: PromptApprovedEvent) {
    await this.cache.invalidate('approved-prompts-list');
    await this.cache.set(
      `prompt:${event.payload.promptName}`,
      event.payload,
      { ttl: 3600 }
    );
  }
}
```

---

## 5. Implementation Roadmap

### Phase 1: Basic Event Sourcing (Current)
- ✅ In-memory event collection
- ✅ Event-driven workflow orchestration
- ✅ Domain events published within process

### Phase 2: Persistent Event Store
- [ ] Implement EventStore interface with PostgreSQL
- [ ] Add event versioning
- [ ] Add snapshots for performance
- [ ] Add event replaying capability

### Phase 3: CQRS Implementation
- [ ] Separate write and read models
- [ ] Implement projection engine
- [ ] Create optimized read models (tables)
- [ ] Add eventual consistency handling

### Phase 4: Advanced Features
- [ ] Temporal queries (time travel)
- [ ] Event replay for debugging
- [ ] Sagas for complex workflows
- [ ] Event-driven integrations with external systems

---

## 6. Benefits Summary

### Event Sourcing Benefits
✅ **Complete Audit Trail** - Every state change is recorded
✅ **Temporal Queries** - Query state at any point in time
✅ **Event Replay** - Rebuild aggregates from events
✅ **Debugging** - See exactly what happened and when
✅ **Compliance** - Immutable audit log

### CQRS Benefits
✅ **Scalability** - Read and write sides scale independently
✅ **Performance** - Optimized read models for queries
✅ **Flexibility** - Multiple read models for different use cases
✅ **Separation of Concerns** - Commands and queries isolated
✅ **Evolution** - Easy to add new projections without changing write side

---

## Summary

The Event Sourcing + CQRS architecture provides:

✅ **Full Auditability** - Complete history of all workflow executions
✅ **Temporal Queries** - Analyze trends and historical data
✅ **Scalability** - Independent scaling of reads and writes
✅ **Flexibility** - Multiple optimized views of the same data
✅ **Debuggability** - Replay events to reproduce issues
✅ **Event-Driven Integration** - Easy integration with analytics, notifications, etc.

This architecture is production-ready and follows industry best practices for event-driven systems.
