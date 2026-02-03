# Local SDLC Extensions
# Custom targets for a_domain project

.PHONY: roadmap roadmap-html roadmap-markdown roadmap-both

roadmap: roadmap-both  ## Generate product roadmap (both HTML and Markdown)

roadmap-html:  ## Generate HTML roadmap only
	@echo "📊 Generating HTML roadmap..."
	@python3 .sdlc/.sdlc/skills/roadmap/generator.py html --with-stories 2>/dev/null || echo "⚠️  Roadmap generator not available in remote submodule"

roadmap-markdown:  ## Generate Markdown roadmap only
	@echo "📊 Generating Markdown roadmap..."
	@python3 .sdlc/.sdlc/skills/roadmap/generator.py markdown 2>/dev/null || echo "⚠️  Roadmap generator not available in remote submodule"

roadmap-both:  ## Generate both HTML and Markdown roadmaps
	@echo "📊 Generating product roadmaps..."
	@if [ -f .sdlc/.sdlc/skills/roadmap/generator.py ]; then \
		python3 .sdlc/.sdlc/skills/roadmap/generator.py both --with-stories; \
	else \
		echo "⚠️  Roadmap generator not available in remote submodule version"; \
		echo "   Roadmap generation skipped - remote submodule uses different structure"; \
	fi
