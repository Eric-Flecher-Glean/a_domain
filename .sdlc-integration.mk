# SDLC Framework Integration
# This file provides SDLC targets with correct path resolution

# Define SDLC base directory
SDLC_DIR := .sdlc/.sdlc

# Include all SDLC modules with correct paths
include $(SDLC_DIR)/make/governance.mk
include $(SDLC_DIR)/make/testing.mk
include $(SDLC_DIR)/make/backlog.mk
include $(SDLC_DIR)/make/artifacts.mk
include $(SDLC_DIR)/make/logging.mk
include $(SDLC_DIR)/make/skills.mk

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
	@echo "Note: Use '/plan', '/implement', '/test', '/deploy' Claude skills for full SDLC workflow"
	@echo "See .sdlc/README.md for complete documentation"
