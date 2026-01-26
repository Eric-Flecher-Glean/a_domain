.PHONY: help xml-prompt xml-prompt-enhanced xml-prompt-ab validate-prompt test-workflow test-context-analysis test-ab-workflow clean

# Colors for output
GREEN := \033[0;32m
YELLOW := \033[0;33m
BLUE := \033[0;34m
NC := \033[0m # No Color

help:
	@echo "$(BLUE)Prompt Engineering MCP Server - Makefile Commands$(NC)"
	@echo ""
	@echo "$(GREEN)make xml-prompt TASK=\"your task description\"$(NC)"
	@echo "  Generate and validate an XML prompt from natural language"
	@echo ""
	@echo "$(GREEN)make xml-prompt-enhanced TASK=\"your task description\"$(NC)"
	@echo "  Generate prompt WITH context analysis (direct, bypasses agents)"
	@echo ""
	@echo "$(GREEN)make xml-prompt-ab TASK=\"your task description\"$(NC)"
	@echo "  Generate prompt using A/B agent system WITH context analysis (RECOMMENDED)"
	@echo ""
	@echo "$(GREEN)make validate-prompt FILE=\"path/to/prompt.xml\"$(NC)"
	@echo "  Validate an existing XML prompt"
	@echo ""
	@echo "$(GREEN)make test-workflow$(NC)"
	@echo "  Run the full generation + validation workflow with test data"
	@echo ""
	@echo "$(GREEN)make test-context-analysis$(NC)"
	@echo "  Test context analysis and input identification"
	@echo ""
	@echo "$(GREEN)make test-ab-workflow$(NC)"
	@echo "  Test integrated A/B agent workflow with context analysis"
	@echo ""
	@echo "Examples:"
	@echo "  make xml-prompt TASK=\"Create a prompt for meeting summarization\""
	@echo "  make xml-prompt-ab TASK=\"Summarize customer feedback\"  (RECOMMENDED)"
	@echo "  make validate-prompt FILE=\"output/my-prompt.xml\""

# Generate XML prompt from natural language task description
xml-prompt:
ifndef TASK
	@echo "$(YELLOW)Error: TASK parameter required$(NC)"
	@echo "Usage: make xml-prompt TASK=\"your task description\""
	@exit 1
endif
	@echo "$(BLUE)Generating XML prompt for:$(NC) $(TASK)"
	@mkdir -p output
	@node scripts/run-mcp-workflow.js \
		--mode generate \
		--task "$(TASK)" \
		--output output/generated-prompt.xml \
		--max-attempts 3

# Validate an existing XML prompt
validate-prompt:
ifndef FILE
	@echo "$(YELLOW)Error: FILE parameter required$(NC)"
	@echo "Usage: make validate-prompt FILE=\"path/to/prompt.xml\""
	@exit 1
endif
	@echo "$(BLUE)Validating XML prompt:$(NC) $(FILE)"
	@node scripts/run-mcp-workflow.js \
		--mode validate \
		--file "$(FILE)"

# Test the full workflow with example tasks
test-workflow:
	@echo "$(BLUE)Testing prompt generation workflow...$(NC)"
	@echo ""
	@echo "$(GREEN)Test 1: Meeting Summarization$(NC)"
	@make xml-prompt TASK="Create a prompt for meeting summarization"
	@echo ""
	@echo "$(GREEN)Test 2: Code Review$(NC)"
	@make xml-prompt TASK="Generate a prompt for code review"
	@echo ""
	@echo "$(GREEN)Test 3: Email Draft$(NC)"
	@make xml-prompt TASK="Create a prompt for drafting professional emails"

# Generate XML prompt with context analysis (ENHANCED)
xml-prompt-enhanced:
ifndef TASK
	@echo "$(YELLOW)Error: TASK parameter required$(NC)"
	@echo "Usage: make xml-prompt-enhanced TASK=\"your task description\""
	@exit 1
endif
	@echo "$(BLUE)Generating XML prompt WITH context analysis:$(NC) $(TASK)"
	@mkdir -p output
	@chmod +x scripts/run-mcp-workflow-enhanced.js
	@node scripts/run-mcp-workflow-enhanced.js \
		--mode generate \
		--task "$(TASK)" \
		--output output/enhanced-prompt.xml \
		--max-attempts 3

# Generate XML prompt using A/B agents WITH context analysis (INTEGRATED - RECOMMENDED)
xml-prompt-ab:
ifndef TASK
	@echo "$(YELLOW)Error: TASK parameter required$(NC)"
	@echo "Usage: make xml-prompt-ab TASK=\"your task description\""
	@exit 1
endif
	@echo "$(BLUE)Generating XML prompt using A/B Agent System + Context Analysis:$(NC) $(TASK)"
	@mkdir -p output
	@chmod +x scripts/run-mcp-workflow-integrated.js
	@node scripts/run-mcp-workflow-integrated.js \
		--mode generate \
		--task "$(TASK)" \
		--output output/ab-prompt.xml \
		--max-attempts 3

# Test context analysis with different prompt types
test-context-analysis:
	@echo "$(BLUE)Testing Context Analysis & Input Identification...$(NC)"
	@echo ""
	@echo "$(GREEN)Test 1: Meeting Summarization$(NC)"
	@make xml-prompt-enhanced TASK="Create a prompt for summarizing meeting transcripts"
	@echo ""
	@echo "$(GREEN)Test 2: Code Review$(NC)"
	@make xml-prompt-enhanced TASK="Generate a prompt for code review with security focus"
	@echo ""
	@echo "$(GREEN)Test 3: Customer Feedback Analysis$(NC)"
	@make xml-prompt-enhanced TASK="Create a prompt for sentiment analysis of customer reviews"

# Test integrated A/B workflow with context analysis
test-ab-workflow:
	@echo "$(BLUE)Testing Integrated A/B Agent Workflow + Context Analysis...$(NC)"
	@echo ""
	@echo "$(GREEN)Test 1: Meeting Summarization (A/B Agents)$(NC)"
	@make xml-prompt-ab TASK="Create a prompt for summarizing meeting transcripts"
	@echo ""
	@echo "$(GREEN)Test 2: Code Review (A/B Agents)$(NC)"
	@make xml-prompt-ab TASK="Generate a prompt for code review with security focus"
	@echo ""
	@echo "$(GREEN)Test 3: Customer Feedback (A/B Agents)$(NC)"
	@make xml-prompt-ab TASK="Create a prompt for sentiment analysis of customer reviews"

# Clean generated outputs
clean:
	@echo "$(YELLOW)Cleaning output directory...$(NC)"
	@rm -rf output/
	@echo "$(GREEN)Done!$(NC)"
