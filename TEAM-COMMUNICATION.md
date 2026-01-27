# SDLC Framework Integration - Team Communication

**Date**: January 27, 2026
**Status**: Complete

## TL;DR

The a_domain project now includes the SDLC governance framework. All existing features work unchanged. New development lifecycle tools are available.

## ACTION REQUIRED (First Time)

If you're pulling these changes for the first time:

```bash
git pull origin main
git submodule update --init --recursive
make help
```

That's it! You're ready to go.

## What's New

### New Development Lifecycle Commands

```bash
make help              # Shows both a_domain and SDLC commands
make check-artifacts   # Find unregistered artifacts
make register-artifacts # Register new work products
```

### New Claude Skills

```bash
/sdlc-plan             # Planning assistance
/sdlc-implement        # Implementation tracking
/sdlc-test             # Testing guidance
/sdlc-quality          # Quality gates
```

## What's Unchanged

**Everything else!** All your current workflow remains the same:

```bash
make xml-prompt-ab TASK="..."  # Still works
make explorer                  # Still works
make clean                     # Still works

/project-generate-examples     # Still works
/project-new-workflow          # Still works
```

## Quick Start

### For Prompt Engineering Work (No Changes)

Continue as before:

```bash
make xml-prompt-ab TASK="Summarize customer feedback"
make view-latest-report
make explorer
```

### To Try SDLC Features (Optional)

```bash
# Check artifact registration
make check-artifacts

# Register new artifacts
make register-artifacts

# Use Claude skills
/sdlc-plan
/sdlc-status
```

## Documentation

- **What Changed**: [.sdlc/WHATS-NEW.md](.sdlc/WHATS-NEW.md)
- **Quick Reference**: [.sdlc/QUICK-REFERENCE.md](.sdlc/QUICK-REFERENCE.md)
- **Full Integration Guide**: [docs/SDLC-INTEGRATION.md](docs/SDLC-INTEGRATION.md)
- **Training Guide**: [.sdlc/TRAINING.md](.sdlc/TRAINING.md)

## FAQ

### Do I have to use SDLC?

No! It's completely optional. Use what's helpful, ignore the rest.

### Will this slow me down?

No! Your existing workflow is unchanged. SDLC adds optional tools.

### What if something breaks?

See [docs/ROLLBACK.md](docs/ROLLBACK.md) for removal instructions, or ask for help.

### How do I learn more?

- Read [.sdlc/WHATS-NEW.md](.sdlc/WHATS-NEW.md) (5 min read)
- Try [.sdlc/TRAINING.md](.sdlc/TRAINING.md) (30 min hands-on)
- Check [docs/SDLC-INTEGRATION.md](docs/SDLC-INTEGRATION.md) (complete guide)

## Support

- **Documentation**: See links above
- **Issues**: Create GitHub issue or ask on team channel
- **Questions**: Reach out to project maintainers

## Technical Details

For those interested:

- **Integration Method**: Git submodule at `.sdlc/`
- **Python Version**: 3.13.9 (in `.sdlc/.venv/`)
- **Makefile Pattern**: Coexistence (zero breaking changes)
- **Skills Organization**: Namespace separation (project/ and sdlc/)
- **Rollback**: Full backup created (see docs/ROLLBACK.md)

## Next Steps

1. **Pull changes**: `git pull && git submodule update --init --recursive`
2. **Verify**: `make help`
3. **Learn**: Read [.sdlc/WHATS-NEW.md](.sdlc/WHATS-NEW.md)
4. **Try it**: Use SDLC on your next task
5. **Share feedback**: What works? What doesn't?

---

**Remember**: This is additive only. Nothing breaks, everything still works!
