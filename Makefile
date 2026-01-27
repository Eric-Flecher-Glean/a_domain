# Makefile - Integration hub for a_domain + SDLC framework
# This file integrates both the a_domain project commands and the SDLC governance framework

.PHONY: help local-help sdlc-help

# Include SDLC framework targets first (lower priority)
-include .sdlc-integration.mk

# Include project-specific targets second (higher priority - will override SDLC targets with same name)
include Makefile.local

# Unified help command
help: local-help show-sdlc-help

# Project-specific help
local-help:
	@echo ""
	@echo "\033[0;34m=== a_domain Project Commands ===\033[0m"
	@echo ""
	@echo "Prompt Engineering MCP Server - Makefile Commands"
	@echo ""
	@echo "\033[0;32mmake xml-prompt TASK=\"your task description\"\033[0m"
	@echo "  Generate and validate an XML prompt from natural language"
	@echo ""
	@echo "\033[0;32mmake xml-prompt-enhanced TASK=\"your task description\"\033[0m"
	@echo "  Generate prompt WITH context analysis (direct, bypasses agents)"
	@echo ""
	@echo "\033[0;32mmake xml-prompt-ab TASK=\"your task description\"\033[0m"
	@echo "  Generate prompt using A/B agent system WITH context analysis (RECOMMENDED)"
	@echo ""
	@echo "\033[0;32mmake validate-prompt FILE=\"path/to/prompt.xml\"\033[0m"
	@echo "  Validate an existing XML prompt"
	@echo ""
	@echo "\033[0;32mmake test-workflow\033[0m"
	@echo "  Run the full generation + validation workflow with test data"
	@echo ""
	@echo "\033[0;32mmake test-context-analysis\033[0m"
	@echo "  Test context analysis and input identification"
	@echo ""
	@echo "\033[0;32mmake test-ab-workflow\033[0m"
	@echo "  Test integrated A/B agent workflow with context analysis"
	@echo ""
	@echo "\033[0;32mmake view-latest-report\033[0m"
	@echo "  View the latest workflow timeline report in browser"
	@echo ""
	@echo "\033[0;32mmake view-report SESSION_ID=\"session-id\"\033[0m"
	@echo "  View a specific workflow timeline report"
	@echo ""
	@echo "\033[0;32mmake generate-report\033[0m"
	@echo "  Manually generate timeline report for latest session"
	@echo ""
	@echo "\033[0;32mmake explorer\033[0m"
	@echo "  Launch the Report Explorer web app to browse all reports"
	@echo ""
	@echo "\033[0;32mmake explorer-install\033[0m"
	@echo "  Install dependencies for the Report Explorer"
	@echo ""
	@echo "\033[0;32mmake ux-review\033[0m"
	@echo "  Run comprehensive UX review of timeline reports (creates user stories)"
	@echo ""
	@echo "\033[0;32mmake clean\033[0m"
	@echo "  Clean generated outputs"
	@echo ""
	@echo "Examples:"
	@echo "  make xml-prompt TASK=\"Create a prompt for meeting summarization\""
	@echo "  make xml-prompt-ab TASK=\"Summarize customer feedback\"  (RECOMMENDED)"
	@echo "  make validate-prompt FILE=\"output/my-prompt.xml\""
	@echo "  make explorer  # Browse all reports in web UI"

# Note: SDLC help is provided by show-sdlc-help target in .sdlc-integration.mk
