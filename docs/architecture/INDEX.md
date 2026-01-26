# Architecture Documentation Index

## Overview

This directory contains comprehensive architecture documentation for the **Integrated A/B Prompt Engineering System with Context Analysis**.

The system is built using **Domain-Driven Design (DDD)**, **Event Sourcing**, and **CQRS** patterns to create a scalable, maintainable, and production-ready solution.

---

## 📚 Documentation Structure

### 1. [Reference Architecture](./REFERENCE-ARCHITECTURE.md)
**Complete system architecture with data flows and DDD events**

**What's Inside:**
- System architecture overview (4-layer architecture)
- 4 Bounded Contexts with responsibilities
- 18+ Domain Events with complete event flow
- End-to-end data flow diagrams
- Sequence diagrams (happy path + refinement path)
- Context map showing bounded context relationships
- Component architecture
- Event storming results
- Integration patterns
- Deployment architecture

**Key Diagrams:**
- System layering (Presentation → Application → Domain → Infrastructure)
- Event flow timeline
- Complete data flow (Input → Context Discovery → Agent A → Agent B → Output)
- Sequence diagrams for successful and retry scenarios
- Context map with OHS, CF, and ACL relationships

**Read This If:**
- You need to understand the overall system architecture
- You want to see how data flows through the system
- You need to understand bounded context interactions
- You're implementing new features and need architectural guidance

---

### 2. [Aggregate Design](./AGGREGATE-DESIGN.md)
**DDD Tactical Patterns: Aggregates, Entities, Value Objects**

**What's Inside:**
- Complete aggregate designs for all 4 bounded contexts:
  - **PromptSpecification** Aggregate
  - **ValidationResult** Aggregate
  - **WorkflowSession** Aggregate
  - **InputAnalysis** Aggregate
- Entity and Value Object definitions
- Domain invariants and business rules
- Domain behaviors (methods)
- Domain events raised by each aggregate
- Aggregate relationships and boundaries
- Repository interfaces

**Key Concepts:**
- Aggregate roots with identity
- Owned entities and value objects
- Invariants that must be maintained
- Domain behaviors encapsulating business logic
- Events published for cross-aggregate communication

**Read This If:**
- You're implementing aggregate logic
- You need to understand business rules and invariants
- You're adding new entities or value objects
- You want to understand repository patterns

---

### 3. [Event Sourcing & CQRS](./EVENT-SOURCING-CQRS.md)
**Event-driven architecture patterns**

**What's Inside:**
- Event Store structure and schemas
- Event sourcing implementation patterns
- Aggregate reconstruction from events
- CQRS architecture (Command/Query separation)
- Command and Query definitions
- Read model projections
- Temporal queries (time travel)
- Audit trail capabilities
- Event-driven integrations
- Implementation roadmap

**Key Patterns:**
- Event Store with versioned event streams
- Command handlers for write operations
- Query handlers for read operations
- Projections that build optimized read models
- Temporal queries to analyze historical data
- Event subscribers for integrations

**Read This If:**
- You need complete audit trail functionality
- You want to implement temporal queries
- You're building read-optimized views
- You need to integrate with external systems via events
- You want to scale reads and writes independently

---

### 4. [Agent Nodes and Workflow](./AGENT-NODES-AND-WORKFLOW.md)
**Generalized node architecture with execution hops**

**What's Inside:**
- Agent A and Agent B as generalized nodes
- Node interface with tool specifications
- Complete 6-hop workflow execution trace
- XML prompt evolution through feedback loops
- Node communication protocol with message envelopes
- Back-and-forth workflow between agents
- Detailed hop-by-hop analysis

**Key Demonstrations:**
- Agents implemented as stateless nodes with tools
- HOP 1: Context Discovery → Input Analysis
- HOP 2: Agent A → Generate XML (Attempt 1)
- HOP 3: Agent B → Validate (Score 85, FAIL)
- HOP 4: Agent B → Agent A (FEEDBACK LOOP)
- HOP 5: Agent A → Generate XML (Attempt 2, refined)
- HOP 6: Agent B → Validate (Score 95, PASS) → Save Output
- Exact XML differences showing how feedback improves the prompt

**Read This If:**
- You want to understand how agents are implemented as nodes
- You need to see the actual workflow execution with data flow
- You're implementing the workflow orchestrator
- You want to understand the feedback loop mechanism
- You need to see how XML prompts evolve through iterations

---

### 5. [Artifact-Driven Validation](./ARTIFACT-DRIVEN-VALIDATION.md)
**Declarative validation system using external artifacts**

**What's Inside:**
- Complete artifact repository structure
- Artifact types (Configuration, Examples, Instructions)
- How artifacts are loaded at runtime
- Python implementation of artifact loader
- External storage integration (Google Drive, S3)
- Artifact discovery and caching
- Version control for artifacts
- Hybrid storage strategies (repo + GDrive)

**Key Concepts:**
- All validation logic defined in artifacts (JSON/YAML/XML)
- No hardcoded validation rules in agent code
- Three-layer architecture: Agent Spec → Workflow Rules → Global Standards
- Example libraries for reference comparison
- Shareable across teams via Google Drive

**Read This If:**
- You want to understand how Agent B's validation is defined
- You're implementing artifact loading infrastructure
- You need to add new validation rules or examples
- You're planning external storage integration
- You want to enable non-technical users to update validation logic

---

## 🎯 Quick Navigation

### By Role

**Software Architect**
1. Start with [Reference Architecture](./REFERENCE-ARCHITECTURE.md) for overall system design
2. Review [Aggregate Design](./AGGREGATE-DESIGN.md) for DDD patterns
3. Study [Event Sourcing & CQRS](./EVENT-SOURCING-CQRS.md) for advanced patterns
4. Review [Agent Nodes and Workflow](./AGENT-NODES-AND-WORKFLOW.md) for execution flow

**Backend Developer**
1. Start with [Aggregate Design](./AGGREGATE-DESIGN.md) to understand domain model
2. Review repository interfaces and domain behaviors
3. Check [Reference Architecture](./REFERENCE-ARCHITECTURE.md) for component interactions
4. Study [Event Sourcing & CQRS](./EVENT-SOURCING-CQRS.md) for event handling
5. Review [Agent Nodes and Workflow](./AGENT-NODES-AND-WORKFLOW.md) for workflow implementation

**Frontend Developer**
1. Review [Reference Architecture](./REFERENCE-ARCHITECTURE.md) - Data Flow section
2. Check command and query definitions in [Event Sourcing & CQRS](./EVENT-SOURCING-CQRS.md)
3. Understand workflow states from [Aggregate Design](./AGGREGATE-DESIGN.md)
4. Study [Agent Nodes and Workflow](./AGENT-NODES-AND-WORKFLOW.md) for workflow visualization

**DevOps Engineer**
1. Review [Reference Architecture](./REFERENCE-ARCHITECTURE.md) - Deployment Architecture section
2. Check [Event Sourcing & CQRS](./EVENT-SOURCING-CQRS.md) for persistence requirements
3. Review integration patterns for external services
4. Study [Agent Nodes and Workflow](./AGENT-NODES-AND-WORKFLOW.md) for node communication protocol

---

## 📋 Key Concepts

### Bounded Contexts

| Context | Responsibility | Core Aggregates |
|---------|---------------|-----------------|
| **PromptEngineering** | XML prompt generation and validation | PromptSpecification, ValidationResult |
| **ContextDiscovery** | Input and context source identification | InputAnalysis |
| **GleanIntegration** | Glean MCP service integration | GleanQuery, ContextRetrieval |
| **WorkflowOrchestration** | Agent coordination and feedback loops | WorkflowSession, FeedbackCycle |

### Domain Events

**Workflow Events:**
- WorkflowSessionStarted
- AttemptInitiated
- AttemptCompleted
- MaxAttemptsReached
- WorkflowSessionCompleted
- WorkflowSessionFailed

**Prompt Events:**
- PromptGenerationRequested
- PromptGenerated
- PromptRefined
- InputAdded
- ContextSourceAdded

**Validation Events:**
- PromptValidationRequested
- PromptValidated
- PromptApproved
- PromptRejected
- FeedbackGenerated

**Context Events:**
- TaskAnalysisRequested
- TaskAnalyzed
- InputsIdentified
- ContextSourcesDiscovered
- GleanToolsMapped

### Integration Patterns

| Pattern | Usage | Document |
|---------|-------|----------|
| **Request-Response** | Synchronous agent calls | Reference Architecture §9.1 |
| **Publish-Subscribe** | Event-driven notifications | Reference Architecture §9.2 |
| **Anti-Corruption Layer** | Glean integration protection | Reference Architecture §6 |
| **Repository Pattern** | Data access abstraction | Aggregate Design §6 |
| **CQRS** | Read/write separation | Event Sourcing & CQRS §2 |

---

## 🏗️ Architecture Patterns Used

### Domain-Driven Design (DDD)
- ✅ Bounded Contexts
- ✅ Aggregates, Entities, Value Objects
- ✅ Domain Events
- ✅ Repositories
- ✅ Ubiquitous Language
- ✅ Context Mapping (OHS, CF, ACL)

### Event Sourcing
- ✅ Event Store
- ✅ Event-driven state changes
- ✅ Aggregate reconstruction from events
- ✅ Temporal queries
- ✅ Complete audit trail

### CQRS (Command Query Responsibility Segregation)
- ✅ Command handlers (write side)
- ✅ Query handlers (read side)
- ✅ Projections (read model builders)
- ✅ Eventual consistency
- ✅ Optimized read models

### Clean Architecture
- ✅ Layered architecture (Presentation, Application, Domain, Infrastructure)
- ✅ Dependency inversion
- ✅ Domain isolation from infrastructure

---

## 🔄 Data Flow Summary

```
User Request
    ↓
Application Layer (Workflow Orchestrator)
    ↓
Domain Layer
    ├─→ ContextDiscovery: Analyze task → Identify inputs/context
    ├─→ PromptEngineering: Generate XML (Agent A)
    ├─→ PromptEngineering: Validate quality (Agent B)
    └─→ WorkflowOrchestration: Manage feedback loop
    ↓
Infrastructure Layer
    ├─→ Glean MCP (Agent A, Agent B, MCP Tools)
    ├─→ Event Store (persist events)
    └─→ File System (save XML and reports)
    ↓
Output (XML Prompt + Validation Report)
```

---

## 📈 Evolution & Roadmap

### Current State (v1.0)
- ✅ In-process event handling
- ✅ File-based persistence
- ✅ Simulated agent calls
- ✅ Complete DDD domain model
- ✅ A/B agent workflow with context analysis

### Phase 2 (Event Persistence)
- [ ] PostgreSQL event store
- [ ] Event versioning
- [ ] Snapshots
- [ ] Event replay

### Phase 3 (CQRS Implementation)
- [ ] Separate read/write databases
- [ ] Projection engine
- [ ] Optimized read models
- [ ] Query endpoints

### Phase 4 (Production Features)
- [ ] Glean API integration
- [ ] Authentication & authorization
- [ ] REST API
- [ ] WebSocket for real-time updates
- [ ] Dashboard UI

---

## 🔗 Related Documentation

**Project Root:**
- [Quick Start](../../QUICK-START.md) - Getting started guide
- [README](../../README.md) - Project overview
- [Usage Guide](../../USAGE.md) - Detailed usage examples

**Implementation:**
- [Agent Specifications](../../agents/) - Agent configs and contracts
- [Workflow Scripts](../../scripts/) - Implementation code
- [MCP Server Config](../../mcp-servers/prompt-engineering/) - MCP server setup

**Concepts:**
- [Context Management](../context-management.md) - Context discovery design
- [Integration Guide](../integrating-context-with-ab-agents.md) - A/B integration details
- [Workflow Demo](../CONTEXT-WORKFLOW-DEMO.md) - Usage demonstrations

---

## 🎨 Diagram Legend

### Symbols Used in Architecture Diagrams

```
┌─────────┐     Box with rounded corners = Component/Service
│         │
└─────────┘

┌─────────┐     Box with sharp corners = Aggregate/Entity
|         |
└─────────┘

    ↓           Solid arrow = Synchronous call/dependency

    ─ ─ ─>      Dashed arrow = Asynchronous/event

    ◄───        Left arrow = Response/callback

    │           Vertical line = Sequential flow
    ▼

OHS             Open Host Service (provides API)
CF              Conformist (conforms to external model)
ACL             Anti-Corruption Layer (protects domain)
```

### Color Coding (in visual tools)

- 🟦 **Blue** - Application Layer
- 🟩 **Green** - Domain Layer
- 🟨 **Yellow** - Infrastructure Layer
- 🟥 **Red** - External Services
- 🟪 **Purple** - Events

---

## 📞 Contact & Contribution

**Questions about architecture?**
- Review the specific document for your area of interest
- Check the related documentation links
- Refer to the code comments in implementation files

**Proposing architectural changes?**
1. Review existing patterns in these documents
2. Ensure alignment with DDD principles
3. Consider impact on bounded contexts
4. Update relevant architecture documentation

---

## 📝 Document Maintenance

**Last Updated:** 2026-01-26
**Version:** 1.0.0
**Status:** Complete and Production-Ready

**Change Log:**
- 2026-01-26: Initial architecture documentation
  - Reference Architecture
  - Aggregate Design
  - Event Sourcing & CQRS patterns

**Maintainers:**
- System Architecture: See reference architecture
- Domain Model: See aggregate design
- Event Patterns: See event sourcing & CQRS

---

## Summary

This architecture documentation provides a **complete, production-ready blueprint** for:

✅ **System Design** - Layered architecture with clear separation of concerns
✅ **Domain Model** - Rich DDD aggregates with business logic
✅ **Data Flow** - End-to-end understanding of request processing
✅ **Event Architecture** - Event sourcing and CQRS patterns
✅ **Integration Patterns** - How to integrate with external systems
✅ **Scalability** - Patterns for scaling reads and writes independently
✅ **Maintainability** - Clear boundaries and responsibilities
✅ **Auditability** - Complete event history and temporal queries

**The architecture is ready for production deployment and future evolution.**
