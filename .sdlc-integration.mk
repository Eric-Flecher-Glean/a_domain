# SDLC Framework Integration
# This file provides SDLC targets with correct path resolution

# Define SDLC base directory
SDLC_DIR := .sdlc/.sdlc

# Check if .sdlc submodule is initialized
SDLC_INITIALIZED := $(shell test -f $(SDLC_DIR)/make/governance.mk && echo yes || echo no)

ifeq ($(SDLC_INITIALIZED),no)
$(error ❌ .sdlc submodule not initialized. Run: git submodule update --init --recursive)
endif

# Auto-start all web services for observability and UX
.PHONY: ensure-services
ensure-services:
	@bash scripts/ensure-all-services.sh

# Legacy aliases (stop-services defined in Makefile.local)
.PHONY: ensure-explorer stop-explorer
ensure-explorer: ensure-services
stop-explorer: stop-services

# Include all SDLC modules with correct paths
include $(SDLC_DIR)/make/governance.mk
include $(SDLC_DIR)/make/testing.mk
include $(SDLC_DIR)/make/demos.mk
include $(SDLC_DIR)/make/backlog.mk
include $(SDLC_DIR)/make/artifacts.mk
include $(SDLC_DIR)/make/logging.mk
-include $(SDLC_DIR)/make/skills.mk  # Optional - may not exist in remote version

# Helper target to initialize .sdlc submodule
.PHONY: sdlc-init
sdlc-init:
	@echo "🔄 Initializing .sdlc submodule..."
	@git submodule update --init --recursive
	@echo "✅ .sdlc submodule initialized"
	@echo ""
	@echo "You can now use:"
	@echo "  make validate-governance"
	@echo "  make test-all"
	@echo "  make backlog-status"

# Override key SDLC targets to ensure all services are running
backlog-next: ensure-services
backlog-status: ensure-services
backlog-in-progress: ensure-services
backlog-blocked: ensure-services
session-start: ensure-services
governance: ensure-services
test-gate: ensure-services
register-artifacts: ensure-services

# SDLC framework help (custom version)
.PHONY: show-sdlc-help
show-sdlc-help:
	@echo ""
	@echo "\033[0;34m=== SDLC Framework Commands ===\033[0m"
	@echo ""
	@echo "Development lifecycle commands for governance and quality:"
	@echo ""
	@echo "Governance:"
	@grep -E '^[a-z-]+:.*##' $(SDLC_DIR)/make/governance.mk | sed 's/:.*##/  /' || true
	@echo ""
	@echo "Testing:"
	@grep -E '^[a-z-]+:.*##' $(SDLC_DIR)/make/testing.mk | sed 's/:.*##/  /' || true
	@echo ""
	@echo "Backlog:"
	@grep -E '^[a-z-]+:.*##' $(SDLC_DIR)/make/backlog.mk | sed 's/:.*##/  /' || true
	@echo ""
	@echo "Artifacts:"
	@grep -E '^[a-z-]+:.*##' $(SDLC_DIR)/make/artifacts.mk | sed 's/:.*##/  /' || true
	@echo ""
	@echo "Logging:"
	@grep -E '^[a-z-]+:.*##' $(SDLC_DIR)/make/logging.mk | sed 's/:.*##/  /' || true
	@echo ""
	@echo "Skills:"
	@grep -E '^[a-z-]+:.*##' $(SDLC_DIR)/make/skills.mk | sed 's/:.*##/  /' || true
	@echo ""
	@echo "Web Services:"
	@echo "  ensure-services  Auto-start all web services (Portal, Explorer, API)"
	@echo "  stop-services    Stop all background web services"
	@echo ""
	@echo "Note: All web services auto-start with SDLC commands"
	@echo "      • Developer Portal:  http://localhost:3001"
	@echo "      • Report Explorer:   http://localhost:3000"
	@echo "      • DataOps API:       http://localhost:8000/docs"
	@echo "Note: Use '/plan', '/implement', '/test', '/deploy' Claude skills for full SDLC workflow"
	@echo "See .sdlc/README.md for complete documentation"
