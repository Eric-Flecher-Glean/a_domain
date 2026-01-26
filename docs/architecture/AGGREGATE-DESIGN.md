# Aggregate Design (DDD)

## 1. PromptSpecification Aggregate

### Aggregate Root: PromptSpecification

```
┌─────────────────────────────────────────────────────────────────┐
│  PromptSpecification (Aggregate Root)                           │
│                                                                 │
│  Identity: PromptName (Value Object)                           │
│  - value: string (pattern: "^[a-z0-9]{3}-[a-z0-9]{3}-[a-z0-9]{3}$") │
│                                                                 │
│  Attributes:                                                    │
│  - xmlContent: XmlContent (Value Object)                       │
│  - metadata: Metadata (Value Object)                           │
│  - version: Version (Value Object)                             │
│  - createdAt: Timestamp                                        │
│  - generatedBy: AgentId                                        │
│                                                                 │
│  Entities (owned):                                              │
│  ├─ InputSpecification (Entity)                                │
│  │  ├─ inputs: Collection<Input>                              │
│  │  │  ├─ name: string                                        │
│  │  │  ├─ type: InputType (enum)                              │
│  │  │  ├─ required: boolean                                   │
│  │  │  ├─ source: InputSource (enum)                          │
│  │  │  ├─ description: string                                 │
│  │  │  └─ validationRules: ValidationRules (VO)              │
│  │  └─ isComplete(): boolean                                  │
│  │                                                             │
│  └─ ContextRequirements (Entity)                               │
│     ├─ contextSources: Collection<ContextSource>              │
│     │  ├─ name: string                                        │
│     │  ├─ source: SourceType (enum)                           │
│     │  ├─ query: QueryTemplate (VO)                           │
│     │  ├─ required: boolean                                   │
│     │  └─ gleanTool: GleanToolId (VO)                         │
│     └─ getGleanIntegrations(): GleanToolId[]                  │
│                                                                 │
│  Domain Invariants:                                             │
│  - Prompt name must be unique and follow pattern               │
│  - XML content must be well-formed                             │
│  - If InputSpecification exists, must have ≥1 required input   │
│  - Each ContextSource must map to valid Glean tool             │
│  - Metadata version must follow semver                         │
│                                                                 │
│  Domain Behaviors:                                              │
│  + addInput(input: Input): void                               │
│  + addContextSource(source: ContextSource): void              │
│  + updateWithFeedback(feedback: Feedback[]): PromptSpecification │
│  + toXml(): string                                             │
│  + validate(): ValidationResult                                │
│                                                                 │
│  Domain Events Raised:                                          │
│  - PromptGenerated (when first created)                        │
│  - PromptRefined (when updated with feedback)                  │
│  - InputAdded (when input added to specification)              │
│  - ContextSourceAdded (when context source added)              │
└─────────────────────────────────────────────────────────────────┘
```

### Value Objects

```
┌──────────────────────────────────────────┐
│  XmlContent (Value Object)               │
│  - value: string                         │
│  - parsedDocument: XmlDocument           │
│  + isWellFormed(): boolean              │
│  + hasSection(name: string): boolean    │
│  + getSection(name: string): XmlElement │
│  + equals(other: XmlContent): boolean   │
└──────────────────────────────────────────┘

┌──────────────────────────────────────────┐
│  Metadata (Value Object)                 │
│  - name: PromptName                      │
│  - version: Version                      │
│  - description: string                   │
│  - createdAt: Timestamp                  │
│  + bumpVersion(): Metadata              │
└──────────────────────────────────────────┘

┌──────────────────────────────────────────┐
│  QueryTemplate (Value Object)            │
│  - template: string                      │
│  - variables: string[]                   │
│  + interpolate(values: Map): string     │
│  + validate(): boolean                   │
└──────────────────────────────────────────┘
```

### Enumerations

```
enum InputType {
  STRING,
  NUMBER,
  BOOLEAN,
  ARRAY,
  OBJECT
}

enum InputSource {
  USER_PROVIDED,
  GLEAN_SEARCH,
  GLEAN_MEETING_LOOKUP,
  GLEAN_CODE_SEARCH,
  GLEAN_DOCUMENT,
  SYSTEM_GENERATED
}

enum SourceType {
  GLEAN_SEARCH,
  GLEAN_MEETING_LOOKUP,
  GLEAN_CODE_SEARCH,
  GLEAN_DOCUMENT,
  GLEAN_EMPLOYEE_SEARCH,
  EXTERNAL_API
}
```

---

## 2. ValidationResult Aggregate

### Aggregate Root: ValidationResult

```
┌─────────────────────────────────────────────────────────────────┐
│  ValidationResult (Aggregate Root)                              │
│                                                                 │
│  Identity: ValidationId (Value Object)                         │
│  - value: UUID                                                 │
│                                                                 │
│  Attributes:                                                    │
│  - promptName: PromptName (FK to PromptSpecification)         │
│  - attemptNumber: AttemptNumber (Value Object)                │
│  - qualityScore: QualityScore (Value Object)                  │
│  - isValid: boolean                                            │
│  - validatedAt: Timestamp                                      │
│  - validatedBy: AgentId                                        │
│                                                                 │
│  Entities (owned):                                              │
│  ├─ ValidationChecks (Entity Collection)                       │
│  │  ├─ ruleId: string                                         │
│  │  ├─ status: CheckStatus (enum: PASS, FAIL)                │
│  │  ├─ message: string                                        │
│  │  ├─ severity: Severity (enum: ERROR, WARNING, INFO)       │
│  │  ├─ section: ValidationSection (enum)                     │
│  │  └─ scoreImpact: number                                   │
│  │                                                             │
│  ├─ ScoreBreakdown (Value Object)                             │
│  │  ├─ structural: number (max 35)                           │
│  │  ├─ completeness: number (max 30)                         │
│  │  ├─ quality: number (max 25)                              │
│  │  ├─ contextQuality: number (max 10)                       │
│  │  ├─ bonuses: number                                       │
│  │  └─ penalties: number                                     │
│  │                                                             │
│  ├─ ContextValidation (Value Object)                          │
│  │  ├─ inputSpecificationPresent: boolean                    │
│  │  ├─ contextRequirementsPresent: boolean                   │
│  │  ├─ requiredInputsCount: number                           │
│  │  ├─ contextSourcesCount: number                           │
│  │  ├─ gleanIntegrations: GleanToolId[]                      │
│  │  └─ validationIssues: string[]                            │
│  │                                                             │
│  └─ Feedback (Entity Collection)                               │
│     ├─ priority: number                                       │
│     ├─ category: FeedbackCategory (enum)                     │
│     ├─ message: string                                       │
│     └─ actionable: boolean                                   │
│                                                                 │
│  Domain Invariants:                                             │
│  - Quality score must be 0-100                                 │
│  - isValid = (score >= 90 AND no ERROR severity checks)       │
│  - Score breakdown components must sum to qualityScore         │
│  - Feedback is generated only when isValid = false             │
│  - attemptNumber must be 1-3                                   │
│                                                                 │
│  Domain Behaviors:                                              │
│  + addCheck(check: ValidationCheck): void                     │
│  + calculateScore(): QualityScore                             │
│  + generateFeedback(): Feedback[]                             │
│  + approve(): void // sets isValid = true                     │
│  + reject(): void // sets isValid = false                     │
│  + getPrioritizedFeedback(): Feedback[]                       │
│                                                                 │
│  Domain Events Raised:                                          │
│  - PromptValidated (when validation completes)                 │
│  - PromptApproved (when isValid = true)                        │
│  - PromptRejected (when isValid = false)                       │
│  - FeedbackGenerated (when feedback is created)                │
└─────────────────────────────────────────────────────────────────┘
```

### Value Objects

```
┌──────────────────────────────────────────┐
│  QualityScore (Value Object)             │
│  - value: number (0-100)                 │
│  + isAboveThreshold(threshold: number): boolean │
│  + trendFrom(previous: QualityScore): Trend │
└──────────────────────────────────────────┘

┌──────────────────────────────────────────┐
│  AttemptNumber (Value Object)            │
│  - value: number (1-3)                   │
│  + increment(): AttemptNumber           │
│  + isLast(): boolean                    │
└──────────────────────────────────────────┘
```

### Enumerations

```
enum CheckStatus {
  PASS,
  FAIL
}

enum Severity {
  ERROR,
  WARNING,
  INFO
}

enum ValidationSection {
  STRUCTURAL,
  COMPLETENESS,
  QUALITY,
  CONTEXT_QUALITY
}

enum FeedbackCategory {
  MISSING_CONTENT,
  INVALID_FORMAT,
  CONTEXT_ISSUE,
  QUALITY_ISSUE,
  STRUCTURAL_ISSUE
}
```

---

## 3. WorkflowSession Aggregate

### Aggregate Root: WorkflowSession

```
┌─────────────────────────────────────────────────────────────────┐
│  WorkflowSession (Aggregate Root)                               │
│                                                                 │
│  Identity: SessionId (Value Object)                            │
│  - value: UUID                                                 │
│                                                                 │
│  Attributes:                                                    │
│  - userRequest: string                                         │
│  - status: SessionStatus (Value Object)                        │
│  - currentAttempt: AttemptNumber                               │
│  - maxAttempts: number                                         │
│  - startedAt: Timestamp                                        │
│  - completedAt: Timestamp?                                     │
│  - duration: Duration?                                         │
│                                                                 │
│  Entities (owned):                                              │
│  ├─ AttemptHistory (Entity Collection)                         │
│  │  ├─ attemptNumber: number                                  │
│  │  ├─ promptGenerated: PromptName                            │
│  │  ├─ validationResult: ValidationId                         │
│  │  ├─ qualityScore: number                                   │
│  │  ├─ feedbackReceived: Feedback[]                           │
│  │  ├─ startedAt: Timestamp                                   │
│  │  └─ completedAt: Timestamp                                 │
│  │                                                             │
│  └─ FeedbackCycles (Entity Collection)                         │
│     ├─ cycleNumber: number                                    │
│     ├─ sourceAgent: AgentId                                   │
│     ├─ targetAgent: AgentId                                   │
│     ├─ feedbackItems: Feedback[]                              │
│     ├─ appliedAt: Timestamp                                   │
│     └─ resultingAttempt: number                               │
│                                                                 │
│  Domain Invariants:                                             │
│  - Session can only be started once                            │
│  - Current attempt cannot exceed max attempts                  │
│  - Status transitions: PENDING → IN_PROGRESS → (SUCCESS|FAILED) │
│  - Feedback cycle can only exist if attempt failed             │
│  - Duration is calculated when status = SUCCESS or FAILED      │
│                                                                 │
│  Domain Behaviors:                                              │
│  + start(): void                                               │
│  + initiateAttempt(number: number): Attempt                   │
│  + recordAttempt(attempt: Attempt): void                      │
│  + initiateFeedbackCycle(feedback: Feedback[]): FeedbackCycle │
│  + complete(finalPrompt: PromptName): void                    │
│  + fail(reason: string): void                                 │
│  + shouldRetry(): boolean                                      │
│  + getAttemptHistory(): Attempt[]                             │
│                                                                 │
│  Domain Events Raised:                                          │
│  - WorkflowSessionStarted                                      │
│  - AttemptInitiated                                            │
│  - AttemptCompleted                                            │
│  - FeedbackCycleStarted                                        │
│  - FeedbackApplied                                             │
│  - MaxAttemptsReached                                          │
│  - WorkflowSessionCompleted                                    │
│  - WorkflowSessionFailed                                       │
└─────────────────────────────────────────────────────────────────┘
```

### Value Objects

```
┌──────────────────────────────────────────┐
│  SessionStatus (Value Object)            │
│  - value: enum (PENDING, IN_PROGRESS,    │
│           SUCCESS, FAILED, CANCELLED)    │
│  + canTransitionTo(status): boolean     │
│  + isFinal(): boolean                   │
└──────────────────────────────────────────┘

┌──────────────────────────────────────────┐
│  Duration (Value Object)                 │
│  - milliseconds: number                  │
│  + toSeconds(): number                  │
│  + toHumanReadable(): string            │
└──────────────────────────────────────────┘
```

---

## 4. InputAnalysis Aggregate

### Aggregate Root: InputAnalysis

```
┌─────────────────────────────────────────────────────────────────┐
│  InputAnalysis (Aggregate Root)                                 │
│                                                                 │
│  Identity: AnalysisId (Value Object)                           │
│  - value: UUID                                                 │
│                                                                 │
│  Attributes:                                                    │
│  - taskRequest: string                                         │
│  - analyzedAt: Timestamp                                       │
│  - pattern: TaskPattern (Value Object)                        │
│                                                                 │
│  Entities (owned):                                              │
│  ├─ RequiredInputs (Entity Collection)                         │
│  │  ├─ name: string                                           │
│  │  ├─ type: InputType                                        │
│  │  ├─ source: InputSource                                    │
│  │  ├─ description: string                                    │
│  │  └─ validationRules: ValidationRules                       │
│  │                                                             │
│  ├─ OptionalInputs (Entity Collection)                         │
│  │  ├─ name: string                                           │
│  │  ├─ type: InputType                                        │
│  │  ├─ source: InputSource                                    │
│  │  ├─ description: string                                    │
│  │  ├─ default: any                                           │
│  │  └─ validationRules: ValidationRules                       │
│  │                                                             │
│  ├─ ContextSources (Entity Collection)                         │
│  │  ├─ name: string                                           │
│  │  ├─ source: SourceType                                     │
│  │  ├─ query: QueryTemplate                                   │
│  │  ├─ required: boolean                                      │
│  │  └─ cacheDuration: Duration?                               │
│  │                                                             │
│  └─ GleanIntegrations (Value Object Collection)                │
│     └─ toolIds: GleanToolId[]                                 │
│                                                                 │
│  Domain Invariants:                                             │
│  - Must have at least 1 required input OR 1 context source     │
│  - User-provided inputs cannot have Glean source               │
│  - Glean-retrieved contexts must map to valid tool             │
│  - QueryTemplate variables must match input names              │
│                                                                 │
│  Domain Behaviors:                                              │
│  + addRequiredInput(input: Input): void                       │
│  + addOptionalInput(input: Input): void                       │
│  + addContextSource(source: ContextSource): void              │
│  + getGleanTools(): GleanToolId[]                             │
│  + toInputSpecification(): InputSpecification                 │
│  + toContextRequirements(): ContextRequirements               │
│                                                                 │
│  Domain Events Raised:                                          │
│  - TaskAnalyzed                                                │
│  - InputsIdentified                                            │
│  - ContextSourcesDiscovered                                    │
│  - GleanToolsMapped                                            │
└─────────────────────────────────────────────────────────────────┘
```

### Value Objects

```
┌──────────────────────────────────────────┐
│  TaskPattern (Value Object)              │
│  - patternType: enum (MEETING, CODE,     │
│                 CUSTOMER_FEEDBACK, ...)  │
│  - keywords: string[]                    │
│  - confidence: number (0-1)              │
│  + matches(task: string): boolean       │
└──────────────────────────────────────────┘

┌──────────────────────────────────────────┐
│  ValidationRules (Value Object)          │
│  - minLength: number?                    │
│  - maxLength: number?                    │
│  - pattern: RegExp?                      │
│  - minItems: number? (for arrays)        │
│  - maxItems: number? (for arrays)        │
│  + validate(value: any): boolean        │
└──────────────────────────────────────────┘
```

---

## 5. Aggregate Relationships

```
┌────────────────────────────────────────────────────────────────┐
│                    AGGREGATE RELATIONSHIPS                     │
│                                                                │
│  InputAnalysis                                                 │
│       │                                                        │
│       │ (produces)                                             │
│       ▼                                                        │
│  PromptSpecification ◄───────┐                                │
│       │                      │                                │
│       │ (validates)          │ (references)                   │
│       ▼                      │                                │
│  ValidationResult ────────────┘                                │
│       │                                                        │
│       │ (tracked by)                                           │
│       ▼                                                        │
│  WorkflowSession                                               │
│       │                                                        │
│       │ (contains)                                             │
│       └─► AttemptHistory (value object collection)            │
│           ├─ attemptNumber                                    │
│           ├─ promptGenerated (PromptName)                     │
│           └─ validationResult (ValidationId)                  │
│                                                                │
│  Notes:                                                        │
│  - Aggregates only reference each other by ID                 │
│  - No direct object references across aggregate boundaries    │
│  - Communication via domain events                            │
│  - Each aggregate has its own repository                      │
└────────────────────────────────────────────────────────────────┘
```

---

## 6. Repository Interfaces

```typescript
interface PromptSpecificationRepository {
  save(spec: PromptSpecification): Promise<void>;
  findByName(name: PromptName): Promise<PromptSpecification | null>;
  findBySession(sessionId: SessionId): Promise<PromptSpecification[]>;
  delete(name: PromptName): Promise<void>;
}

interface ValidationResultRepository {
  save(result: ValidationResult): Promise<void>;
  findById(id: ValidationId): Promise<ValidationResult | null>;
  findByPromptName(name: PromptName): Promise<ValidationResult[]>;
  findBySession(sessionId: SessionId): Promise<ValidationResult[]>;
}

interface WorkflowSessionRepository {
  save(session: WorkflowSession): Promise<void>;
  findById(id: SessionId): Promise<WorkflowSession | null>;
  findActive(): Promise<WorkflowSession[]>;
  findCompleted(limit: number): Promise<WorkflowSession[]>;
}

interface InputAnalysisRepository {
  save(analysis: InputAnalysis): Promise<void>;
  findById(id: AnalysisId): Promise<InputAnalysis | null>;
  findByTaskPattern(pattern: TaskPattern): Promise<InputAnalysis | null>;
  cache(task: string, analysis: InputAnalysis): Promise<void>;
}
```

---

## Summary

This aggregate design provides:

✅ **Clear Boundaries** - Each aggregate is independent with its own lifecycle
✅ **Strong Invariants** - Business rules enforced at aggregate level
✅ **Rich Behaviors** - Domain logic encapsulated in aggregate methods
✅ **Event-Driven** - Aggregates publish events for cross-aggregate communication
✅ **Persistence Ignorance** - Repository pattern abstracts data access
✅ **Consistency** - Transactional boundaries align with aggregate boundaries

The design follows DDD tactical patterns with:
- Aggregate Roots
- Entities
- Value Objects
- Domain Events
- Repositories
- Ubiquitous Language
