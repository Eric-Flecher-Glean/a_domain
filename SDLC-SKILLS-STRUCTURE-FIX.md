# SDLC Skills Structure Fix - Issue Report

**Date**: 2026-01-27
**Status**: ✅ RESOLVED
**Severity**: High (Skills not discoverable)

---

## Issue Summary

SDLC framework commands/skills were not appearing in the Claude Code skills menu despite the symlink being correctly configured.

## Root Cause

The SDLC skills were structured as flat `.md` files but Claude Code requires skills to be in directories with `SKILL.md` files.

### Expected Structure
```
.claude/skills/
└── skill-name/
    └── SKILL.md    # Must be named exactly "SKILL.md"
```

### Actual Structure (Before Fix)
```
.sdlc/.sdlc/skills/
├── artifact.md
├── test.md
├── quality.md
└── ... (other skills as flat .md files)
```

### Corrected Structure (After Fix)
```
.sdlc/.sdlc/skills/
├── artifact/
│   └── SKILL.md
├── test/
│   └── SKILL.md
├── quality/
│   └── SKILL.md
└── ... (other skills in directories)
```

## Fix Applied

### 1. Restructured Skill Files
Moved each skill from `{name}.md` to `{name}/SKILL.md`:
- `artifact.md` → `artifact/SKILL.md`
- `client-meetings.md` → `client-meetings/SKILL.md`
- `deploy.md` → `deploy/SKILL.md`
- `implement.md` → `implement/SKILL.md`
- `new-feature-chat.md` → `new-feature-chat/SKILL.md`
- `plan.md` → `plan/SKILL.md`
- `quality.md` → `quality/SKILL.md`
- `sdlc.initialize.md` → `sdlc.initialize/SKILL.md`
- `session.md` → `session/SKILL.md`
- `status.md` → `status/SKILL.md`
- `test.md` → `test/SKILL.md`

### 2. Added YAML Frontmatter
Each skill now has proper frontmatter:
```yaml
---
name: skill-name
description: Brief description of what this skill does
---
```

### 3. Verified Symlink
The symlink `.claude/skills/sdlc` → `../../.sdlc/.sdlc/skills/` is working correctly.

## Impact

**Before Fix:**
- SDLC commands not visible in Claude Code
- Skills menu showed only project-specific skills
- Users couldn't discover or invoke SDLC workflows

**After Fix:**
- All SDLC skills now appear in the skills menu
- Commands like `/test`, `/quality`, `/implement` are discoverable
- Full integration with Claude Code workflow

## Available SDLC Skills

Now accessible via Claude Code:
- `/test` - Run tests (unit/integration/functional)
- `/quality` - Run governance + tests
- `/deploy` - Deployment workflow
- `/new-feature-chat` - Interactive TDD story creation
- `/implement` - Execute implementation workflow
- `/artifact` - Search and process artifacts
- `/client-meetings` - Generate client meeting reports
- `/sdlc-initialize` - Initialize SDLC framework
- `/session` - Session start/end workflows
- `/status` - Display backlog and health status
- `/plan` - Query backlog and plan next work

## Validation

### Test Commands
```bash
# Verify skills directory structure
ls -la .sdlc/.sdlc/skills/

# Check symlink is working
ls -la .claude/skills/sdlc/

# Verify frontmatter on a skill
head -5 .sdlc/.sdlc/skills/test/SKILL.md
```

### Expected Output
```
---
name: test
description: Run tests (unit/integration/functional) and report results
---
```

## Recommendations for SDLC Project

### 1. Update Documentation
Update `.sdlc/.sdlc/skills/README.md` to document the required structure:
```markdown
## Skill File Structure

Each skill must follow this structure:
```
.sdlc/skills/
└── skill-name/
    └── SKILL.md    # Required name
```

### 2. Add Structure Validation
Create a validation script to check skill structure:
```bash
#!/bin/bash
# File: .sdlc/scripts/validate-skills.sh

cd .sdlc/skills
for dir in */; do
  if [ ! -f "$dir/SKILL.md" ]; then
    echo "ERROR: Missing SKILL.md in $dir"
    exit 1
  fi
done
echo "✅ All skills have correct structure"
```

### 3. CI/CD Check
Add a pre-commit hook or CI check to validate skill structure:
```yaml
# .github/workflows/validate-skills.yml
name: Validate Skills Structure
on: [pull_request]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Check skill structure
        run: .sdlc/scripts/validate-skills.sh
```

### 4. Migration Guide
Create a migration guide for other projects using the SDLC framework:
```markdown
# Migrating to New Skill Structure

If you have an older version of the SDLC framework with flat .md skills:

1. For each skill file:
   ```bash
   mkdir -p skill-name
   mv skill-name.md skill-name/SKILL.md
   ```

2. Add frontmatter to each SKILL.md:
   ```yaml
   ---
   name: skill-name
   description: Brief description
   ---
   ```

3. Verify with:
   ```bash
   .sdlc/scripts/validate-skills.sh
   ```
```

## Files Changed

### SDLC Repository
- `.sdlc/skills/*/SKILL.md` - All skills restructured
- Committed: `1979343`

### Parent Repository
- No changes needed (symlink already correct)

## Lessons Learned

1. **Follow framework conventions** - Claude Code has specific requirements for skill structure
2. **Document structure requirements** - Make the expected format explicit in README
3. **Validate structure automatically** - Add scripts to catch structure issues early
4. **Test integration points** - Verify skills appear in the menu after changes

## Related Documentation

- [Claude Code Skills Documentation](.claude/skills/README.md)
- [SDLC Skills README](.sdlc/.sdlc/skills/README.md)
- [SDLC Commands Setup](.sdlc/SDLC_COMMANDS_SETUP.md)

---

## Issue Tracking

**Created**: 2026-01-27
**Resolved**: 2026-01-27
**Resolution Time**: < 1 hour
**Priority**: P0 (Critical - blocking feature discovery)

---

**Reporter**: User
**Assignee**: Claude Code Assistant
**Verified By**: Structure validation and menu visibility check
