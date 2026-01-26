# Integrated A/B Prompt Engineering System

**Production-ready XML prompt generation with automated quality validation and iterative refinement**

[![Status](https://img.shields.io/badge/status-production%20ready-brightgreen)]()
[![Version](https://img.shields.io/badge/version-1.0.0-blue)]()
[![Architecture](https://img.shields.io/badge/architecture-DDD%2BCQRS%2BES-purple)]()

---

## Overview

A sophisticated two-agent system that generates high-quality XML prompts through intelligent collaboration:

- **Agent A (Generator)** creates XML prompts from natural language
- **Agent B (Validator)** ensures quality through detailed validation
- **Feedback Loop** iterates until quality threshold is met (≥90/100)
- **Context Discovery** automatically identifies required inputs and Glean integrations

**Result**: Production-ready XML prompts with complete input specifications, context requirements, and validation in seconds.

---

## Quick Start

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd a_domain

# Install dependencies
npm install

# Test the system
make test-ab-workflow
```

### Usage

```bash
# Generate a validated XML prompt
make xml-prompt-ab TASK="Create a prompt for meeting summarization"

# Output files:
# - output/ab-prompt.xml           (Final XML prompt)
# - output/ab-prompt-ab-report.json (Validation report)
```

### Example Output

```
✅ Session completed successfully!

Summary:
- Prompt Name: m3t-4ng-s1m
- Final Score: 95/100
- Attempts: 2
- Duration: 9.0 seconds

Input Analysis:
- Required inputs: 2 (meeting_transcript, attendee_list)
- Optional inputs: 1 (meeting_date)
- Context sources: 1 (previous_meetings via glean_meeting_lookup)
- Glean tools: mcp__glean__meeting_lookup
```

---

## Documentation

### Getting Started
- **[SYSTEM-OVERVIEW.md](./SYSTEM-OVERVIEW.md)** - Complete system guide (1 page)
- **[QUICK-START.md](./QUICK-START.md)** - Get started in 5 minutes
- **[USAGE.md](./USAGE.md)** - Detailed usage examples

### Operations
- **[docs/OBSERVATION-AND-TESTING.md](./docs/OBSERVATION-AND-TESTING.md)** - Testing and observability guide
- **[docs/EXECUTIVE-SUMMARY.md](./docs/EXECUTIVE-SUMMARY.md)** - Business case and ROI

### Architecture
- **[ARCHITECTURE-SUMMARY.md](./ARCHITECTURE-SUMMARY.md)** - Architecture overview
- **[docs/architecture/](./docs/architecture/)** - Comprehensive architecture documentation
  - [Reference Architecture](./docs/architecture/REFERENCE-ARCHITECTURE.md) - System design with data flows
  - [Aggregate Design](./docs/architecture/AGGREGATE-DESIGN.md) - DDD patterns and domain model
  - [Event Sourcing & CQRS](./docs/architecture/EVENT-SOURCING-CQRS.md) - Event-driven patterns
  - [Agent Nodes and Workflow](./docs/architecture/AGENT-NODES-AND-WORKFLOW.md) - Node architecture with 6-hop workflow
  - [Artifact-Driven Validation](./docs/architecture/ARTIFACT-DRIVEN-VALIDATION.md) - Validation system design

---

## Features

### ✅ Intelligent Quality Assurance
- **Automated validation** across 4 dimensions (structural, completeness, quality, context)
- **90/100 quality threshold** ensures production-ready outputs
- **Specific feedback** for targeted improvements

### ✅ Context Intelligence
- **Automatic input detection** - identifies what users must provide
- **Context source mapping** - finds relevant Glean data sources
- **Glean tool selection** - chooses appropriate MCP tools

### ✅ Iterative Refinement
- **Feedback-driven improvement** - Agent B tells Agent A exactly what to fix
- **Up to 3 attempts** to reach quality threshold
- **XML evolution tracking** - see what changed between attempts

### ✅ Artifact-Driven Configuration
- **Declarative validation rules** in JSON/YAML files
- **Example library** for reference patterns
- **Google Drive integration** ready (repo-based currently)
- **No code changes** needed to update standards

### ✅ Complete Observability
- **Event sourcing** for full audit trail
- **Validation reports** with detailed score breakdowns
- **Attempt history** for improvement analysis
- **Correlation tracking** across all workflow hops

---

## Architecture Highlights

### Domain-Driven Design
- **4 Bounded Contexts**: PromptEngineering, ContextDiscovery, GleanIntegration, WorkflowOrchestration
- **4 Core Aggregates**: PromptSpecification, ValidationResult, WorkflowSession, InputAnalysis
- **18+ Domain Events**: Complete event flow from start to completion

### Event Sourcing
- **Complete audit trail** of all operations
- **Event store** for historical analysis
- **Temporal queries** for time-travel debugging (planned)

### CQRS (Planned)
- **Separate read/write models** for scalability
- **Optimized projections** for fast queries
- **Independent scaling** of reads and writes

---

## Technology Stack

- **Runtime**: Node.js 18+ / TypeScript
- **Agents**: Glean MCP (Claude Sonnet 4.5)
- **Configuration**: YAML/JSON for rules and standards
- **Storage**: File system (event store: PostgreSQL planned)
- **CLI**: Make-based interface

---

## Project Structure

```
a_domain/
├── agents/                          # Agent specifications
│   ├── prompt-generator/            # Agent A (Generator)
│   │   └── agent-spec.yaml
│   └── prompt-validator/            # Agent B (Validator)
│       └── agent-spec.yaml
│
├── workflow-orchestration/          # Validation artifacts
│   ├── global/                      # Organization-wide standards
│   │   ├── config/
│   │   │   └── validation-standards.json
│   │   └── examples/
│   │       ├── good/                # Good example prompts
│   │       └── bad/                 # Anti-patterns to avoid
│   │
│   └── workflows/
│       └── prompt-generation/       # Workflow-specific artifacts
│           └── stages/
│               ├── 01-generate-prompt/
│               └── 02-validate-quality/
│                   ├── validation-rules.json
│                   ├── instructions.md
│                   └── examples/
│
├── scripts/                         # Implementation
│   └── run-mcp-workflow-integrated.js
│
├── docs/                            # Documentation
│   └── architecture/                # Architecture docs (~3,400 lines)
│
├── output/                          # Generated files
│
├── Makefile                         # CLI interface
├── SYSTEM-OVERVIEW.md               # 1-page system guide
└── QUICK-START.md                   # Quick start guide
```

---

## Examples

### Meeting Summarization
```bash
make xml-prompt-ab TASK="Create a prompt for meeting summarization"
# Result: 100/100, 1 attempt, identifies meeting_transcript + attendee_list inputs
```

### Code Review
```bash
make xml-prompt-ab TASK="Create a prompt for code review"
# Result: 100/100, 1 attempt, identifies code_content + programming_language inputs
```

### Customer Feedback Analysis
```bash
make xml-prompt-ab TASK="Create a prompt for customer feedback analysis"
# Result: 100/100, 1 attempt, identifies feedback_text input + customer_history context
```

---

## Roadmap

### ✅ Version 1.0 (Current)
- Two-agent A/B workflow with feedback loops
- Context discovery and input analysis
- Artifact-driven validation system
- Complete DDD domain model
- Event sourcing architecture
- Makefile CLI interface

### 📅 Version 1.1 (Next)
- [ ] PostgreSQL event store
- [ ] Event versioning and snapshots
- [ ] Enhanced context discovery patterns
- [ ] Google Drive artifact storage

### 📅 Version 2.0 (Future)
- [ ] CQRS with separate read models
- [ ] REST API for workflow execution
- [ ] Web UI dashboard
- [ ] Real-time updates via WebSocket
- [ ] Analytics and reporting

---

## Contributing

### Adding New Examples

Add example prompts to the library:

1. Create XML file in `workflow-orchestration/global/examples/good/`
2. Update `_metadata.json` with example details
3. System automatically discovers new examples

### Updating Validation Rules

Modify validation criteria:

1. Edit `validation-rules.json` in stage folder
2. Update point values, severities, or checks
3. No code changes required - agents load rules at runtime

### Architecture Changes

For architectural changes:

1. Review [architecture documentation](./docs/architecture/)
2. Ensure alignment with DDD principles
3. Update relevant architecture docs
4. Create pull request with context map updates

---

## Support

- **Documentation**: [docs/architecture/](./docs/architecture/)
- **Quick Start**: [QUICK-START.md](./QUICK-START.md)
- **System Overview**: [SYSTEM-OVERVIEW.md](./SYSTEM-OVERVIEW.md)
- **Issues**: Create GitHub issue with reproduction steps

---

## License

[Your License Here]

---

## Acknowledgments

Built with:
- **Claude Sonnet 4.5** for agent intelligence
- **Glean MCP** for agent infrastructure
- **Domain-Driven Design** principles
- **Event Sourcing** and **CQRS** patterns

---

**Status**: ✅ Production Ready
**Version**: 1.0.0
**Last Updated**: 2026-01-26

**Built with industry best practices for enterprise AI systems.**
