# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Core Principles documentation (CORE-PRINCIPLES.md) establishing LLM compute constraints
- Architecture Review Checklist (ARCHITECTURE-REVIEW-CHECKLIST.md) for pre-merge validation
- GitHub Actions workflow for architecture validation (.github/workflows/architecture-validation.yml)
- Comprehensive test suite (scripts/run-architecture-tests.sh) with 12 validation tests
- Local XML prompt templates directory structure (sdlc/prompts/)
- Three XML prompt templates for requirements analysis
- Exception classes for Glean Agent Registry operations
- Comprehensive error handling in AGENT-REGISTRY-GUIDE.md (37 try/except blocks, 69 logging statements)

### Changed
- Standardized all 16 agent schemas to JSON Schema Draft 7 format
- Updated all prompt repository references from GitHub to local paths (sdlc/prompts)
- Fixed ADR-006 internal link references
- Enhanced Python examples in AGENT-REGISTRY-GUIDE.md with production-ready error handling
- Updated agent metadata in AGENT-REGISTRY.yaml (52 total agents, 16 documented)
- Added example_invocation fields to all 16 agents in AGENT-REGISTRY.yaml

### Fixed
- Validation script bugs in ARCHITECTURE-REVIEW-CHECKLIST.md
- XML syntax error in analyze-requirements.xml template
- Broken GitHub prompt repository references across documentation
- Incorrect ADR-006 anchor references

## [1.0.0] - 2026-02-11

### Added
- Initial release with comprehensive architecture documentation
- Domain-Driven Design specification
- Event Sourcing and CQRS patterns
- Reference architecture
- Agent implementation guides
- Glean MCP integration patterns
- XML prompt agent patterns
- Agent Registry with 16 documented agents across 5 domains

### Documentation Domains
- Sales Enablement (3 agents)
- SDLC/Engineering (4 agents)
- Customer Support (3 agents)
- Knowledge Management (2 agents)
- Journey Orchestration (2 agents)

---

**Note**: This CHANGELOG tracks architectural and documentation changes. For code changes, see git commit history.
