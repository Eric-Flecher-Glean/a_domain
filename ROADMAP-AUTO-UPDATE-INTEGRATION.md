# Roadmap Auto-Update Integration

**Date**: February 3, 2026
**Status**: ✅ COMPLETE

---

## Summary

The product roadmap now automatically regenerates when stories are completed or quality gates pass, ensuring the web portal always reflects the current backlog state.

---

## Integration Points

### 1. `/implement` Command (Story Completion)

**File**: `.sdlc/.sdlc/skills/implement/SKILL.md`

**When**: After all story tasks are completed and acceptance criteria met

**Actions** (lines 193-199):
```bash
# 3. Regenerate roadmap
make roadmap-both

# Updates:
# - docs/roadmaps/roadmap.html (visual timeline)
# - docs/roadmaps/ROADMAP.md (markdown version)
# - docs/roadmaps/stories/*.html (63 individual story pages)
```

**Triggers**:
- Story status changes from `in_progress` → `completed`
- Backlog version incremented
- Roadmap reflects newly completed work

---

### 2. `/quality` Command (Quality Gates Pass)

**File**: `.sdlc/.sdlc/skills/quality/SKILL.md`

**When**: After all quality gates pass (governance + documentation + tests)

**Actions** (lines 104-128):
```bash
# If all quality gates pass:
make roadmap-both
python3 .sdlc/scripts/link_stories_to_docs.py

# Updates:
# - Roadmap with latest validated state
# - Story-to-document links refreshed
# - Documentation portal synchronized
# - Progress metrics updated
```

**Quality Gate Criteria**:
- ✅ Governance validation passing (HIGH priority checks)
- ✅ P0 stories have design/architecture docs
- ✅ All tests passing (unit, integration, functional)

---

## Make Target Configuration

### Updated Target

**File**: `.sdlc/.sdlc/make/skills.mk`

**Changes**:
```makefile
# BEFORE:
roadmap-both:  ## Generate both HTML and Markdown roadmaps
	@echo "📊 Generating product roadmaps..."
	@python3 .sdlc/.sdlc/skills/roadmap/generator.py both

# AFTER:
roadmap-both:  ## Generate both HTML and Markdown roadmaps
	@echo "📊 Generating product roadmaps..."
	@python3 .sdlc/.sdlc/skills/roadmap/generator.py both --with-stories
```

**Benefit**: Now generates all 63 individual story detail pages automatically

---

## Generated Artifacts

When `make roadmap-both` runs, it creates:

### 1. HTML Roadmap
- **Path**: `docs/roadmaps/roadmap.html`
- **Content**: Visual timeline with SVG progress bars
- **Features**:
  - 4 phases over 16 weeks
  - 47 stories on timeline (those with `roadmap_extensions`)
  - Progress percentages per phase
  - Business impact metrics
  - Milestone tracking

### 2. Markdown Roadmap
- **Path**: `docs/roadmaps/ROADMAP.md`
- **Content**: Text version for CLI/documentation
- **Features**:
  - Executive summary with metrics
  - Phase breakdowns with deliverables
  - Story tables with status
  - Velocity tracking
  - Business impact summary

### 3. Story Detail Pages
- **Path**: `docs/roadmaps/stories/*.html`
- **Count**: 63 pages (one per story)
- **Content**: Full story details including:
  - Title, description, priority
  - Tasks list with checkboxes
  - Acceptance criteria
  - Functional test plan
  - Dependencies and timeline
  - Business impact

---

## Workflow Integration

### Automatic Updates Occur During:

1. **Story Implementation** (`/implement`)
   ```
   User runs: /implement P0-AB-001
   → Tasks executed
   → Story completed
   → Backlog updated to 'completed'
   → make roadmap-both automatically runs
   → Roadmap reflects completion
   ```

2. **Quality Validation** (`/quality`)
   ```
   User runs: /quality
   → Governance checks pass
   → Documentation validated
   → Tests pass
   → make roadmap-both automatically runs
   → Documentation links refreshed
   → Portal synchronized
   ```

3. **Manual Generation** (always available)
   ```
   make roadmap-both        # Full regeneration
   make roadmap-html        # HTML only
   make roadmap-markdown    # Markdown only
   make roadmap-with-stories # Explicit story pages
   ```

---

## Backlog Synchronization

### Current State (After A/B Agent Recast)

**Backlog**: `.sdlc/IMPLEMENTATION_BACKLOG.yaml`
- **Version**: 24
- **Total Stories**: 63
- **Completed**: 30 (48%)
- **In Progress**: 1
- **Next Priority**: P0-AB-001 (A/B Agent Demo POC)

**Roadmap**: `docs/roadmaps/roadmap.html`
- **Generated**: 2026-02-03
- **Timeline Stories**: 47 (with `roadmap_extensions`)
- **Story Detail Pages**: 63 (100% coverage)
- **Synchronized**: ✅ YES

---

## Verification

### Test Roadmap Auto-Update:

```bash
# 1. Make any change to backlog
# (e.g., mark a story completed)

# 2. Run quality check
make quality

# 3. Verify roadmap updated
ls -lh docs/roadmaps/roadmap.html
# Should show recent timestamp

# 4. View in browser
open http://localhost:3001/docs/roadmaps/roadmap.html
```

### Verify Story Pages:

```bash
# Count story pages
ls docs/roadmaps/stories/ | wc -l
# Should show: 63

# Check recent generation
ls -lt docs/roadmaps/stories/ | head -5
# Should show recent timestamps
```

---

## Documentation Portal Integration

The Developer Portal (http://localhost:3001) provides access to:

1. **Interactive Roadmap**
   - Link: http://localhost:3001/docs/roadmaps/roadmap.html
   - Auto-updated with `/implement` and `/quality` commands

2. **Story Detail Pages**
   - Direct URLs: http://localhost:3001/docs/roadmaps/stories/[STORY-ID].html
   - Example: http://localhost:3001/docs/roadmaps/stories/P0-AB-001.html

3. **Markdown Version**
   - Link: http://localhost:3001/docs/roadmaps/ROADMAP.md
   - CLI-friendly format

---

## Benefits

### 1. Always Current
- No manual roadmap updates needed
- Web portal always reflects latest backlog state
- Story pages regenerated automatically

### 2. Integrated Workflow
- Roadmap updates are part of normal SDLC commands
- No separate "publish roadmap" step
- Quality gates ensure accuracy before update

### 3. Multiple Formats
- HTML for visual timeline
- Markdown for documentation
- Individual story pages for deep linking

### 4. Single Source of Truth
- IMPLEMENTATION_BACKLOG.yaml is authoritative
- Roadmap is generated artifact
- No synchronization drift

---

## Next Steps

### For Users:

1. **Work from the web portal**: http://localhost:3001
2. **Use `/implement` to complete stories** - roadmap auto-updates
3. **Run `/quality` before commits** - ensures roadmap synchronized

### For Implementation:

1. ✅ COMPLETE: Backlog recast for A/B agent priorities
2. ✅ COMPLETE: Roadmap auto-update integration
3. **NEXT**: Start P0-AB-001 (A/B Agent Demo POC)

---

## Technical Details

### Roadmap Generator Script

**Path**: `.sdlc/.sdlc/skills/roadmap/generator.py`

**Capabilities**:
- Reads from `.sdlc/IMPLEMENTATION_BACKLOG.yaml`
- Generates HTML with Jinja2 templates
- Creates Markdown with formatted tables
- Builds individual story pages
- Supports filtering by phase/priority

**Usage**:
```bash
python3 .sdlc/.sdlc/skills/roadmap/generator.py both --with-stories
```

### Story-Document Linking

**Script**: `.sdlc/scripts/link_stories_to_docs.py`

**Purpose**: Maintains bidirectional traceability between stories and documentation

**Triggered by**: `/quality` command after quality gates pass

---

## Status

✅ **Roadmap auto-update is fully integrated into SDLC commands**

- `/implement` → Auto-regenerates roadmap on story completion
- `/quality` → Auto-regenerates roadmap when quality gates pass
- `make roadmap-both` → Now includes `--with-stories` flag
- All 63 story pages generated automatically
- Developer Portal synchronized with backlog

**User can now work from the web app - everything stays in sync!**
