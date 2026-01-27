# SDLC Framework Rollback Guide

Complete instructions for removing the SDLC framework integration and restoring the project to its pre-integration state.

## Table of Contents

- [Quick Rollback](#quick-rollback)
- [Selective Rollback](#selective-rollback)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)

## Quick Rollback

Complete removal of SDLC framework in one step.

### Step 1: Find Backup Information

```bash
cat .sdlc-init-backup.txt
```

Output will show:
```
Backup: backup/pre-sdlc-YYYYMMDD-HHMMSS
```

### Step 2: Reset to Backup

```bash
# Reset to pre-SDLC state
git reset --hard backup/pre-sdlc-YYYYMMDD-HHMMSS

# Or use the tag
git reset --hard pre-sdlc-init-YYYYMMDD-HHMMSS
```

### Step 3: Clean Up Submodule

```bash
# Deinitialize submodule
git submodule deinit -f .sdlc

# Remove submodule git data
rm -rf .git/modules/.sdlc

# Remove submodule reference
git rm -f .sdlc

# Remove submodules file
rm -f .gitmodules
```

### Step 4: Verify

```bash
# Check status
git status

# Should show clean working directory with no .sdlc/

# Test existing commands
make help
make clean
```

Done! The project is restored to its pre-SDLC state.

## Selective Rollback

Remove specific components while keeping others.

### Remove SDLC Submodule Only

Keep Makefile integration, skills organization, etc., but remove the framework code:

```bash
# Remove submodule
git submodule deinit -f .sdlc
rm -rf .git/modules/.sdlc .sdlc
git rm -f .sdlc
rm -f .gitmodules

# Commit
git add -A
git commit -m "Remove SDLC submodule"
```

**Note**: Makefile will have warnings, but project commands still work.

### Restore Original Makefile

Keep SDLC submodule, but restore original Makefile:

```bash
# Restore from backup
cp Makefile.backup Makefile

# Or copy from Makefile.local
cp Makefile.local Makefile

# Remove integration files
rm -f .sdlc-integration.mk Makefile.local

# Commit
git add Makefile
git rm .sdlc-integration.mk Makefile.local
git commit -m "Restore original Makefile"
```

### Restore Original Skills Organization

Keep SDLC submodule and Makefile, but restore original skills layout:

```bash
# Move skills back to root
mv .claude/skills/project/* .claude/skills/
rmdir .claude/skills/project

# Remove SDLC symlink
rm .claude/skills/sdlc

# Restore original README
cp .sdlc-init-pre-snapshot.txt .claude/skills/README.md.backup
# (manually restore from backup)

# Commit
git add .claude/skills/
git commit -m "Restore original skills organization"
```

### Restore Original .gitignore

```bash
# Restore from backup
cp .gitignore.backup .gitignore

# Commit
git add .gitignore
git commit -m "Restore original .gitignore"
```

## Verification

After rollback, verify the project is working:

### Check Files Restored

```bash
# Should NOT exist
ls .sdlc/                    # Should fail or be empty
ls .sdlc-integration.mk      # Should fail
ls .claude/skills/sdlc       # Should fail

# Should exist
ls Makefile                  # Should exist
ls .claude/skills/generate-examples  # Should exist
```

### Test Commands

```bash
# Original commands should work
make help
make xml-prompt TASK="test"
make clean
```

### Check Git Status

```bash
# Should be clean or show only expected changes
git status

# Check no orphaned files
git clean -n -d
```

## Troubleshooting

### Submodule Won't Remove

**Symptom**: `git rm .sdlc` fails with "fatal: pathspec '.sdlc' did not match any files"

**Solution**:
```bash
# Force remove
rm -rf .sdlc
git rm --cached -r .sdlc
rm -rf .git/modules/.sdlc
```

### Backup Branch Not Found

**Symptom**: `git reset --hard backup/pre-sdlc-*` fails

**Solution**:
```bash
# List all branches
git branch -a

# List all tags
git tag

# Reset to most recent tag
git reset --hard $(git tag | grep pre-sdlc | tail -1)
```

### Makefile Has Errors

**Symptom**: `make help` shows errors about missing targets

**Solution**:
```bash
# Use backed up Makefile
cp Makefile.backup Makefile

# Or restore from git
git checkout HEAD~1 -- Makefile
```

### Skills Not Working

**Symptom**: `/generate-examples` not found

**Solution**:
```bash
# Check skills location
ls -la .claude/skills/

# If in project/ subdirectory, move back
mv .claude/skills/project/* .claude/skills/
rmdir .claude/skills/project
```

### Git Submodule State Corrupt

**Symptom**: Git commands hang or fail with submodule errors

**Solution**:
```bash
# Nuclear option - remove all submodule data
rm -rf .git/modules/
rm -rf .sdlc
rm -f .gitmodules

# Clean git cache
git rm --cached -r .

# Re-add files
git add .
git commit -m "Clean submodule state"
```

## Partial Rollback Scenarios

### Keep SDLC, Remove Integration

**Scenario**: Want SDLC available but not integrated

```bash
# Remove integration
cp Makefile.local Makefile
rm .sdlc-integration.mk

# SDLC still accessible directly
cd .sdlc
make help
```

### Keep Integration, Remove Skills

**Scenario**: Want Makefile commands but not Claude skills

```bash
# Remove skills symlink
rm .claude/skills/sdlc

# Skills organization back to flat
mv .claude/skills/project/* .claude/skills/
rmdir .claude/skills/project
```

### Keep Everything, Freeze SDLC Version

**Scenario**: Don't want SDLC to update

```bash
# Detach submodule from tracking
cd .sdlc
git checkout <specific-commit>
cd ..

# Don't update submodule
# (skip git submodule update commands)
```

## Recovery from Failed Rollback

If rollback goes wrong:

### Use Git Reflog

```bash
# Show recent commits
git reflog

# Reset to before rollback
git reset --hard HEAD@{N}
```

### Restore from Snapshot

```bash
# Check snapshot file
cat .sdlc-init-pre-snapshot.txt

# Manually restore any missing files
```

### Start Over

```bash
# Clone fresh copy
git clone <repo-url> a_domain-fresh
cd a_domain-fresh

# Checkout state before SDLC
git checkout <commit-before-sdlc>
```

## Post-Rollback Cleanup

After successful rollback:

### Remove Temporary Files

```bash
rm -f .sdlc-init-backup.txt
rm -f .sdlc-init-pre-snapshot.txt
rm -f Makefile.backup
rm -f .gitignore.backup
rm -f .sdlcrc
```

### Delete Backup Branch

```bash
# Once confident rollback worked
git branch -d backup/pre-sdlc-YYYYMMDD-HHMMSS
git tag -d pre-sdlc-init-YYYYMMDD-HHMMSS
```

### Update Documentation

```bash
# Remove SDLC sections from README
vim README.md

# Remove SDLC docs
rm -rf docs/SDLC-INTEGRATION.md docs/ROLLBACK.md
```

### Commit Clean State

```bash
git add -A
git commit -m "Complete SDLC framework rollback

Removed:
- .sdlc/ Git submodule
- SDLC Makefile integration
- SDLC skills organization
- SDLC documentation

Restored:
- Original Makefile
- Original skills layout
- Original .gitignore

All original functionality verified working.
"
```

## Getting Help

If rollback fails or you need assistance:

1. **Check backup exists**:
   ```bash
   cat .sdlc-init-backup.txt
   git branch | grep backup
   ```

2. **Review git log**:
   ```bash
   git log --oneline -20
   ```

3. **Create GitHub issue** with:
   - Output of `git status`
   - Output of `ls -la`
   - Error messages
   - What you tried

---

**Remember**: The backup branch `backup/pre-sdlc-*` contains the complete state before SDLC integration. You can always reset to it with `git reset --hard`.
