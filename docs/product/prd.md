<!--
<metadata>
  <bounded_context>Product.Requirements</bounded_context>
  <intent>ProductDefinition</intent>
  <purpose>Comprehensive product requirements document for DDD Domain Registry platform</purpose>
  <version>1.0.0</version>
  <last_updated>2026-01-23</last_updated>
  <status>Draft - Pending Stakeholder Review</status>
  <owner>Product Management & Engineering Platform Team</owner>
</metadata>
-->

# Product Requirements Document (PRD)
## DDD Domain Registry & Unified Agent Interface Platform

**Version:** 1.0
**Status:** In Development
**Owner:** Engineering Platform Team
**Last Updated:** 2026-01-23

---

## Executive Summary

### Vision
Create a domain-driven design (DDD) foundation for the Glean agent ecosystem that enables engineers to discover, compose, and orchestrate AI agents through domain concepts rather than technical implementation details.

### Problem Statement
Current Glean agent development faces critical challenges:

1. **Discovery Problem:** No systematic way to find agents with specific capabilities (avg 20 min manual search)
2. **Consistency Problem:** Agent contracts are inconsistent and lack validation (15 schema errors/month reach production)
3. **Composition Problem:** Building multi-agent workflows requires deep technical knowledge and brittle point-to-point integrations
4. **Scalability Problem:** As agent count grows (100+ templates), maintaining coherence becomes impossible without domain structure

![DDD Registry Value Proposition](../images/executive/ddd-registry-value-proposition-executives-v1.png)
*Visual overview: Current state challenges vs. DDD Registry solution approach*

### Solution Overview
A DDD Domain Registry and Unified Agent Interface Layer that provides:

- **Domain Registry:** Central repository of bounded contexts, aggregates, and agent capabilities
- **Unified Interface:** Standardized contracts (intents) for agent discovery and invocation
- **Value Chain Orchestration:** Composition patterns for multi-agent workflows
- **SDLC Meta-Agents:** Self-improving agents that accelerate system development

### Success Metrics

| Metric | Baseline | Target | Timeline |
|--------|----------|--------|----------|
| Agent discovery time | 20 min | 2 min | 3 months |
| Schema errors in production | 15/month | 3/month | 3 months |
| Story writing time | 45 min | 5 min | 6 months |
| Agent development velocity | 1x | 6-8x | 12 months |
| Value chain reliability | N/A | 99% | 9 months |

### Strategic Value
- **Self-bootstrapping:** SDLC agents improve the platform's own development velocity (compounding gains)
- **Network effects:** Each new agent increases the value of the entire ecosystem
- **Knowledge capture:** Domain models become living documentation
- **Future-proof:** Extensible architecture supports 1000+ agents

![Self-Bootstrapping System Concept](../images/executive/ddd-registry-self-bootstrapping-executives-v1.png)
*Strategic advantage: Each agent accelerates development of subsequent agents, creating compounding velocity gains*

---

## Goals and Non-Goals

### Goals
1. **Enable Domain-Driven Agent Discovery:** Developers find agents by domain intent, not technical implementation
2. **Ensure Contract Consistency:** Automated validation prevents schema errors before deployment
3. **Accelerate SDLC Processes:** Meta-agents automate schema validation, story generation, code scaffolding, testing, and deployment
4. **Support Value Chain Composition:** Developers compose complex workflows from reusable agent components
5. **Maintain Enterprise Security:** Permission enforcement at bounded context level integrated with Glean security

### Non-Goals
1. **Replace Glean Agent Builder:** This is an enhancement layer, not a replacement for Glean's UI
2. **Support Non-Glean Agents:** Initial focus is exclusively on Glean platform agents
3. **General-Purpose Workflow Engine:** Scope limited to agent orchestration, not arbitrary business processes
4. **AI Model Training:** Registry manages agent metadata, not underlying AI models

---

## User Personas

### Primary: Agent Developer (Alex)
- **Role:** Solutions Engineer or Platform Engineer
- **Goals:** Build robust agents quickly, reuse existing patterns, compose agents into workflows
- **Pain Points:** Can't find existing agents, schema errors discovered late, manual story writing is tedious
- **Technical Level:** Intermediate (understands JSON, basic coding, may not know DDD)
- **Success Criteria:** Can build and deploy agent in < 1 day (vs. 3-5 days currently)

### Secondary: Platform Architect (Pat)
- **Role:** Engineering Platform Lead
- **Goals:** Maintain consistency, ensure quality, enable self-service, reduce toil
- **Pain Points:** Schema violations, inconsistent patterns, lack of discoverability, scaling challenges
- **Technical Level:** Expert (deep understanding of systems architecture and DDD)
- **Success Criteria:** 80% reduction in schema bugs, agents self-documenting, clear bounded context boundaries

### Tertiary: Product Manager (Morgan)
- **Role:** Product Manager for internal tools
- **Goals:** Understand agent ecosystem, plan roadmap, measure ROI
- **Pain Points:** Limited visibility into agent usage, unclear dependencies, difficulty estimating effort
- **Technical Level:** Basic (understands concepts, not implementation details)
- **Success Criteria:** Dashboard showing agent usage, value chain metrics, ROI tracking

---

## Functional Requirements

### 1. Domain Registry

#### FR-1.1: Bounded Context Management
**Description:** Manage bounded contexts with ubiquitous language, aggregates, and integration points.

**User Story:**
> As a Platform Architect
> I want to define bounded contexts with clear boundaries
> So that agents align with domain concepts and avoid context bleeding

**Acceptance Criteria:**
- ✓ CRUD operations for bounded contexts via REST API
- ✓ Bounded contexts include: name, description, ubiquitous language terms, aggregates, domain events
- ✓ Validation ensures unique context names and valid aggregate references
- ✓ Bounded contexts searchable in Glean Search
- ✓ Context relationships (Customer-Supplier, Conformist, Shared Kernel) are explicit

**Priority:** P0 (Must Have)

---

#### FR-1.2: Agent Capability Registration
**Description:** Register agents with their supported domain intents and contracts.

**User Story:**
> As an Agent Developer
> I want to register my agent's capabilities in the registry
> So that other developers can discover and use my agent

**Acceptance Criteria:**
- ✓ Agents register with: agent_id, name, bounded_context, supported_intents, dependencies
- ✓ Intent contracts validated against JSON Schema before registration
- ✓ Agent dependencies explicitly declared (required intents, contexts)
- ✓ Registration is transactional (all-or-nothing)
- ✓ Agent versioning supported with rollback capability

**Priority:** P0 (Must Have)

---

#### FR-1.3: Intent Contract Specification
**Description:** Define and validate domain intent contracts.

**User Story:**
> As an Agent Developer
> I want to specify my agent's input/output contracts
> So that consumers know exactly what to expect

**Acceptance Criteria:**
- ✓ Intent contracts follow standard schema: intent_id, intent_type (Query/Command/Event), input_contract, output_contract
- ✓ Contracts validated using JSON Schema Draft 7+
- ✓ Preconditions and postconditions expressible
- ✓ Contract versioning with backward compatibility checks
- ✓ Breaking changes require major version bump

**Priority:** P0 (Must Have)

---

### 2. Unified Agent Interface

#### FR-2.1: Agent Discovery
**Description:** Discover agents capable of handling specific domain intents.

**User Story:**
> As an Agent Developer
> I want to find agents that can handle a specific domain intent
> So that I can reuse existing capabilities

**Acceptance Criteria:**
- ✓ Search by intent type (Query/Command/Event)
- ✓ Search by bounded context
- ✓ Search by operation name or keywords
- ✓ Results ranked by relevance and confidence score
- ✓ Results filtered by user permissions
- ✓ Discovery time < 500ms (p95)

**Priority:** P0 (Must Have)

---

#### FR-2.2: Intent Execution
**Description:** Execute domain intents through discovered agents.

**User Story:**
> As an Agent Developer
> I want to execute intents without knowing agent implementation details
> So that I can focus on domain logic

**Acceptance Criteria:**
- ✓ Execute intent by intent_id with input payload
- ✓ Input validated against intent contract before execution
- ✓ Output validated against intent contract after execution
- ✓ Execution context preserves user identity and permissions
- ✓ Execution failures are retryable with idempotency
- ✓ Timeout and circuit breaker protection

**Priority:** P0 (Must Have)

---

#### FR-2.3: Value Chain Composition
**Description:** Compose multiple agents into orchestrated workflows.

**User Story:**
> As an Agent Developer
> I want to compose multiple agents into a workflow
> So that I can solve complex problems spanning multiple domains

![Journey Orchestration Value Chain Example](../images/executive/ddd-registry-journey-use-case-business-v1.png)
*Example value chain: Customer support journey orchestration showing multi-system coordination and automatic breadcrumb tracking*

**Acceptance Criteria:**
- ✓ Define value chains with sequential and parallel steps
- ✓ Specify step dependencies (this step requires these prior steps)
- ✓ Support both orchestration (central coordinator) and choreography (event-driven)
- ✓ Validate entire chain before execution (contract compatibility, permissions, circular dependencies)
- ✓ Execute chains with saga pattern (compensation handlers for rollback)
- ✓ Chain execution status queryable in real-time

**Priority:** P1 (Should Have)

---

### 3. Event Infrastructure

#### FR-3.1: Domain Event Publishing
**Description:** Publish domain events when significant state changes occur.

**User Story:**
> As an Agent
> I want to publish domain events when I complete operations
> So that other agents can react to my actions

**Acceptance Criteria:**
- ✓ Events include: event_type, aggregate_id, bounded_context, correlation_id, payload
- ✓ Events stored in append-only event log
- ✓ Events published to event bus (Redis Streams/Kafka)
- ✓ Event schema validated before publishing
- ✓ Events immutable once published
- ✓ Event propagation < 1 second (p95)

**Priority:** P1 (Should Have)

---

#### FR-3.2: Event Subscription
**Description:** Subscribe to domain events from other agents/contexts.

**User Story:**
> As an Agent
> I want to subscribe to domain events
> So that I can react to changes in other bounded contexts

**Acceptance Criteria:**
- ✓ Subscribe by event_type and/or bounded_context
- ✓ Filter events by payload attributes
- ✓ At-least-once delivery guarantee
- ✓ Dead letter queue for failed event processing
- ✓ Subscription health monitoring
- ✓ Event ordering preserved within aggregate

**Priority:** P1 (Should Have)

---

### 4. SDLC Meta-Agents

#### FR-4.1: Schema Validation Agent
**Description:** Automated validation of intent contracts against JSON Schema.

**User Story:**
> As an Agent Developer
> I want my schemas validated automatically
> So that I catch errors before deployment

**Acceptance Criteria:**
- ✓ Validates intent contracts against JSON Schema
- ✓ Provides actionable error messages with suggestions
- ✓ Suggests schema improvements (clarity, consistency, security)
- ✓ Generates test data from schemas
- ✓ Registers validated schemas in registry
- ✓ Validation time < 2 minutes

**Priority:** P0 (Must Have - Release 1)

**Detailed Spec:** See `/docs/releases/release-1/schema-validation-agent.md`

---

#### FR-4.2: Story Generator Agent
**Description:** Generate user stories from domain intent definitions.

**User Story:**
> As an Agent Developer
> I want user stories generated from my intents
> So that I don't spend time writing requirements

**Acceptance Criteria:**
- ✓ Generates complete user stories (As a/I want/So that)
- ✓ Creates acceptance criteria (happy path + error cases)
- ✓ Produces Gherkin scenarios
- ✓ Includes Definition of Done checklist
- ✓ Estimates effort based on complexity
- ✓ Story completeness score > 90%
- ✓ Generation time < 5 minutes

**Priority:** P0 (Must Have - Release 2)

**Detailed Spec:** See `/docs/releases/release-2/story-generator-agent.md`

---

#### FR-4.3: Code Generator Agent
**Description:** Generate boilerplate code from intent definitions.

**Priority:** P1 (Should Have - Release 3)

---

#### FR-4.4: PR Review Agent
**Description:** Automated code review for agent implementations.

**Priority:** P1 (Should Have - Release 4)

---

#### FR-4.5: Deployment Agent
**Description:** Automated deployment of agents to Glean platform.

**Priority:** P2 (Nice to Have - Release 5)

---

### 5. Glean Integration

#### FR-5.1: Glean Search Integration
**Description:** Make registry searchable through Glean Search API.

**Acceptance Criteria:**
- ✓ Bounded contexts indexed in Glean
- ✓ Agent capabilities indexed in Glean
- ✓ Search supports filtering by context, intent type, keywords
- ✓ Search results respect user permissions
- ✓ Search latency < 200ms (p95)

**Priority:** P0 (Must Have)

---

#### FR-5.2: Glean Agent Builder Integration
**Description:** Generate Glean agents from domain intent definitions.

**Acceptance Criteria:**
- ✓ Convert domain intents to Glean agent steps
- ✓ Support all Glean step types (search, action, think, respond, branch, loop)
- ✓ Map domain search queries to Glean search syntax
- ✓ Configure Glean actions from domain commands
- ✓ Generated agents deployable directly to Glean

**Priority:** P0 (Must Have)

---

#### FR-5.3: MCP Server
**Description:** Expose registry as MCP server for Claude and other clients.

**Acceptance Criteria:**
- ✓ MCP tools for agent discovery
- ✓ MCP tools for intent execution
- ✓ MCP resources for bounded context documentation
- ✓ Authentication via Glean tokens
- ✓ Connection lifecycle handling

**Priority:** P2 (Nice to Have)

---

## Non-Functional Requirements

### Performance
- **NFR-P1:** Intent validation < 2 seconds (p95)
- **NFR-P2:** Agent discovery < 500ms (p95)
- **NFR-P3:** Value chain execution < 5 minutes for 5-step chains
- **NFR-P4:** Event propagation < 1 second end-to-end
- **NFR-P5:** Registry search < 200ms (p95)
- **NFR-P6:** Support 100+ concurrent value chain executions

### Reliability
- **NFR-R1:** System availability 99.5% (excluding planned maintenance)
- **NFR-R2:** Value chain execution reliability 99%
- **NFR-R3:** Event delivery guarantee: at-least-once
- **NFR-R4:** Data durability 99.999% (5-nines)
- **NFR-R5:** Automatic failover for all services

### Security
- **NFR-S1:** All API calls authenticated via Glean tokens
- **NFR-S2:** Bounded context access control enforced
- **NFR-S3:** Cross-context calls permission-validated
- **NFR-S4:** Audit log for all agent executions
- **NFR-S5:** Secrets encrypted at rest and in transit
- **NFR-S6:** PII detection and redaction in logs

### Scalability
- **NFR-SC1:** Support 1000+ registered agents
- **NFR-SC2:** Support 100+ bounded contexts
- **NFR-SC3:** Handle 10,000+ intent executions/day
- **NFR-SC4:** Store 1M+ domain events
- **NFR-SC5:** Horizontal scaling for all services

### Observability
- **NFR-O1:** Distributed tracing for all value chains
- **NFR-O2:** Metrics dashboard for agent performance
- **NFR-O3:** Alerting for failures above threshold
- **NFR-O4:** Log retention: 90 days hot, 1 year cold
- **NFR-O5:** Real-time execution monitoring

### Usability
- **NFR-U1:** API documentation auto-generated from schemas
- **NFR-U2:** Visual bounded context map
- **NFR-U3:** Interactive value chain builder
- **NFR-U4:** CLI for common operations
- **NFR-U5:** Developer onboarding < 30 minutes

---

## Technical Considerations

### Technology Stack
- **Language:** TypeScript/Node.js for services, Python for ML-heavy agents
- **Database:** PostgreSQL for registry, EventStoreDB or PostgreSQL for events
- **Cache/Queue:** Redis (Streams for pub/sub, Cache for discovery)
- **Search:** Glean Search API
- **Observability:** OpenTelemetry, Prometheus, Grafana
- **Infrastructure:** Kubernetes for orchestration, Docker for containers

### Glean Platform Constraints
- Must integrate with Glean Agent Builder workflow
- Must respect Glean permission model
- Must use Glean Search API for discovery
- Must leverage Glean Actions where applicable
- Agent execution happens within Glean runtime

### Data Migration
- Existing agents must be backwards compatible
- Auto-classification tool to migrate existing agents to bounded contexts
- Gradual migration: new agents use registry, old agents continue working

### Backwards Compatibility
- Existing Glean agents work without modification
- Registry is opt-in for new development
- SDLC agents enhance but don't replace manual processes

---

## Dependencies and Risks

### Dependencies
1. **Glean Platform APIs:** Search, Agent, Actions APIs must be stable and performant
2. **Glean Permissions:** Must integrate with Glean's permission model
3. **Infrastructure:** Requires Kubernetes cluster and PostgreSQL database
4. **SDLC Tools:** Jira, GitHub, Confluence integrations

### Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|-----------|
| Glean API changes break integration | High | Medium | Versioned API contracts, integration tests, regular sync with Glean team |
| Schema validation too slow | Medium | Low | Performance benchmarking in staging, caching, optimized validation logic |
| Developers resist DDD adoption | High | Medium | Strong SDLC agent value prop, excellent documentation, training sessions |
| Event infrastructure doesn't scale | High | Low | Load testing early, horizontal scaling design, circuit breakers |
| Value chains too complex to debug | Medium | Medium | Excellent observability, step-by-step replay, clear error messages |

---

## Success Criteria

### Launch Readiness (Release 1)
- [ ] Domain Registry API functional
- [ ] Schema Validation Agent deployed
- [ ] 5 bounded contexts registered
- [ ] Integration with Glean Search working
- [ ] 100% of new agents validated
- [ ] Documentation complete
- [ ] Team trained

### Post-Launch (3 Months)
- [ ] 50+ agents registered
- [ ] Schema errors reduced 80%
- [ ] Discovery time reduced 90%
- [ ] Developer satisfaction > 4/5
- [ ] System availability 99.5%+

### Long-Term (12 Months)
- [ ] 500+ agents registered
- [ ] 20+ bounded contexts
- [ ] 6-8x velocity improvement for new agents
- [ ] 99% value chain reliability
- [ ] Full SDLC automation (Release 5)

---

## Open Questions

1. **Event Store Selection:** EventStoreDB vs. PostgreSQL for event storage? (Need benchmarking)
2. **MCP Priority:** How critical is MCP server for initial release? (User research needed)
3. **Agent Versioning:** Semantic versioning or date-based? (Team decision)
4. **Cross-Org Usage:** Should registry support multi-org deployments? (Product decision)
5. **AI Model Selection:** Which LLM for SDLC agents? (Experimentation needed)

---

## Appendices

### Appendix A: Bounded Context Examples
- ConfigurationManagement
- JourneyOrchestration
- KnowledgeManagement
- SalesEnablement
- SDLC.SchemaManagement
- SDLC.RequirementsManagement
- SDLC.CodeGeneration
- SDLC.Testing
- SDLC.Deployment

### Appendix B: Intent Type Definitions
- **Query:** Read-only operation, no side effects
- **Command:** State-changing operation, creates/updates/deletes
- **Event:** Notification of state change, publish/subscribe pattern

### Appendix C: Value Chain Patterns
- **Sequential:** Steps execute in order, each depends on previous
- **Parallel:** Steps execute concurrently, no dependencies
- **Conditional:** Steps execute based on conditions/branching
- **Saga:** Long-running transaction with compensation handlers

### Appendix D: Related Documentation
- [Implementation Specification](./implementation-specification.md)
- [Roadmap](./roadmap.md)
- [Headlines from the Future](../marketing/headlines-from-future.md)
- [Release 1 Detailed Spec](../releases/release-1/)
- [Release 2 Detailed Spec](../releases/release-2/)
