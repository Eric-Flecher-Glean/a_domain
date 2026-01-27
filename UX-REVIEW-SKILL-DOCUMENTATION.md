# UX Review Skill - Documentation

## Overview

The `/ux-review-timeline` skill provides comprehensive UX analysis of the Workflow Timeline Reports, generating user personas, user journeys, and actionable user stories.

## What It Does

### 1. **Current State Analysis**
- Reads the latest generated HTML report from `observability/reports-output/`
- Analyzes actual rendering vs. design specifications
- Identifies gaps between expected and actual implementation

### 2. **User Research**
Defines **3-5 user personas** such as:
- **Sarah, Backend Engineer** - Debugging failed workflows
- **Mike, Team Lead** - Reviewing team performance
- **Alex, DevOps Engineer** - Monitoring system health
- **Jordan, Product Manager** - Tracking feature rollouts
- **Taylor, New Team Member** - Learning the system

Each persona includes:
- Role and responsibilities
- Goals when using reports
- Pain points and frustrations
- Technical comfort level
- Usage frequency

### 3. **User Journey Mapping**
Maps **2-3 critical user journeys**:

**Example Journey: "Debug a Failed Workflow"**
1. **Trigger**: Alert notification or failed build
2. **Entry**: Opens latest timeline report
3. **Scan**: Quickly identifies red ✗ indicators
4. **Investigate**: Drills into failed stage details
5. **Action**: Fixes code based on bottleneck data
6. **Exit**: Re-runs workflow to verify fix

### 4. **Heuristic Evaluation**
Evaluates against **Nielsen's 10 Usability Heuristics**:
1. Visibility of system status
2. Match between system and real world
3. User control and freedom
4. Consistency and standards
5. Error prevention
6. Recognition rather than recall
7. Flexibility and efficiency
8. Aesthetic and minimalist design
9. Help users recognize/diagnose/recover from errors
10. Help and documentation

Each rated: ✅ Good | ⚠️ Needs Work | ❌ Poor

### 5. **User Story Generation**
Creates **15-20 prioritized user stories** in format:

```
As a [persona],
I want to [action],
So that [benefit].

Acceptance Criteria:
- [ ] Criterion 1
- [ ] Criterion 2

Priority: P0-Critical | P1-High | P2-Medium | P3-Low
Effort: Small | Medium | Large
Impact: High | Medium | Low
```

**Story Categories**:
- Visual Design (layout, colors, spacing)
- Data Visualization (charts, scales, legends)
- Information Architecture (hierarchy, grouping)
- Interaction Design (hover, clicks, navigation)
- Performance (load time, responsiveness)
- Accessibility (screen readers, keyboard nav)
- Content (labels, help text, errors)
- Mobile/Responsive (small screens)

### 6. **Design Recommendations**
Provides specific, actionable recommendations:
- Color palette refinement
- Typography scale improvements
- Spacing/layout system
- Component patterns
- Interaction enhancements

### 7. **Implementation Roadmap**
Three-phase prioritization:

**Phase 1: Quick Wins** (P0-P1, <1 week)
- Critical fixes
- High-impact, low-effort improvements

**Phase 2: Polish** (P1-P2, 1-2 weeks)
- Medium-impact enhancements
- UX refinements

**Phase 3: Delight** (P2-P3, future)
- Nice-to-have features
- Advanced interactions

## Usage

### Command Line
```bash
# Via Makefile (shows instructions)
make ux-review

# Or directly invoke the skill
/ux-review-timeline
```

### In Claude Code
Simply type:
```
/ux-review-timeline
```

The skill will automatically:
1. Find the latest timeline report
2. Read implementation specs
3. Conduct full UX analysis
4. Generate comprehensive review document

## Output

### Generated Document
**Location**: `observability/reports/UX-REVIEW-{date}.md`

**Contains**:
- Executive Summary (ratings, top issues)
- Current State Analysis
- User Personas (3-5 detailed personas)
- User Journeys (2-3 critical paths)
- Heuristic Evaluation (scores & findings)
- User Stories (15-20 prioritized)
- Design System Recommendations
- Implementation Roadmap

**Example Output Structure**:
```markdown
# UX Review: Workflow Timeline Reports
Date: 2026-01-26

## Executive Summary
Overall UX Maturity: ⭐⭐⭐⭐ (4/5)

Top 3 Strengths:
1. Clear visual hierarchy
2. Comprehensive metrics
3. Self-contained HTML

Top 3 Critical Issues:
1. Timeline scales poorly for very short durations
2. Missing interactive drill-down
3. No comparison between sessions

## User Personas

### Persona 1: Sarah, Backend Engineer
**Role**: Senior backend developer
**Goals**: Debug failed workflows quickly
**Pain Points**: Too much manual log diving
**Tech Savvy**: High
**Frequency**: 5-10 times/day

[... continues with detailed analysis ...]
```

## Example User Stories

### Visual Design
```
As a backend engineer,
I want the timeline blocks to have consistent minimum widths,
So that even very short stages are visible and clickable.

Acceptance Criteria:
- [ ] All duration blocks are at least 30px wide
- [ ] Sub-millisecond durations show actual value on hover
- [ ] Visual scale indicates when blocks are compressed

Priority: P1-High
Effort: Small
Impact: High
```

### Data Visualization
```
As a team lead,
I want to compare timelines across multiple sessions side-by-side,
So that I can identify performance regressions.

Acceptance Criteria:
- [ ] Can select 2-5 sessions for comparison
- [ ] Timelines align by stage name
- [ ] Duration differences are highlighted
- [ ] Can export comparison as image

Priority: P2-Medium
Effort: Large
Impact: Medium
```

### Accessibility
```
As a keyboard-only user,
I want to navigate the timeline with arrow keys,
So that I can explore without a mouse.

Acceptance Criteria:
- [ ] Tab moves between timeline rows
- [ ] Arrow keys move between elements
- [ ] Enter opens details panel
- [ ] Focus indicators are visible

Priority: P1-High
Effort: Medium
Impact: High
```

## When to Use

### After Implementation
- New report features added
- Visual changes made
- New metrics added

### Before Major Changes
- Planning UI redesign
- Adding new visualizations
- Changing data structure

### Periodic Reviews
- Quarterly UX audits
- After user feedback sessions
- Sprint retrospectives

### User Testing
- Before user interviews
- After beta testing
- When gathering feedback

## Integration with Development

### Sprint Planning
1. Run `/ux-review-timeline`
2. Review generated user stories
3. Import P0-P1 stories into sprint backlog
4. Assign to team members

### Design Sprints
1. Use personas for design decisions
2. Reference user journeys for flows
3. Validate designs against heuristics
4. Track story completion

### User Acceptance Testing
1. Use acceptance criteria for test cases
2. Validate with actual personas
3. Measure against success metrics
4. Iterate based on findings

## Metrics to Track

After implementing UX improvements, track:

### Quantitative
- Time to insight (how fast users find key info)
- Bounce rate (users leaving without action)
- Feature usage (which metrics are viewed most)
- Error rate (confusion, wrong actions)

### Qualitative
- User satisfaction scores
- Net Promoter Score (NPS)
- Verbatim feedback
- Support ticket reduction

## Customization

### Adding New Personas
Edit `.claude/skills/ux-review-timeline.md`:
- Add persona to "Example Personas to Consider" section
- Include role, goals, pain points

### New Journey Types
Add to "Example Journeys" section:
- Trigger, entry, scan, investigate, action, exit
- Pain points at each step
- Delight opportunities

### Additional Heuristics
Extend beyond Nielsen's 10:
- Mobile-first design
- Performance perception
- Trust and transparency
- Emotional design

## Best Practices

### Before Running Review
1. **Generate latest report**: Ensure fresh data
2. **Document expectations**: Clear design spec
3. **Gather feedback**: User complaints/requests
4. **Set goals**: What questions need answers?

### During Review
1. **Be objective**: Data over opinions
2. **Be specific**: "Button too small" vs "Increase to 44px"
3. **Be actionable**: Every issue has a story
4. **Be realistic**: Prioritize by impact/effort

### After Review
1. **Share findings**: With team, stakeholders
2. **Create tasks**: Import stories to backlog
3. **Assign owners**: Who will implement?
4. **Set timeline**: When to revisit?

## Success Criteria

A successful review delivers:
- ✅ Actionable, not vague recommendations
- ✅ User-centered, not feature-centered
- ✅ Prioritized by impact, not preference
- ✅ Testable acceptance criteria
- ✅ Clear implementation path
- ✅ Realistic effort estimates

## FAQ

**Q: How often should we run this?**
A: Monthly for active development, quarterly for maintenance.

**Q: Can we customize the personas?**
A: Yes! Edit the skill file to add project-specific personas.

**Q: What if we disagree with priorities?**
A: The skill provides recommendations; final prioritization is up to the team based on business context.

**Q: How long does a review take?**
A: The skill runs in 2-3 minutes. Human review of output takes 15-30 minutes.

**Q: Can we use this for other features?**
A: Yes! The skill can be adapted for any UI/UX analysis by modifying the skill prompt.

## Files

- **Skill Definition**: `.claude/skills/ux-review-timeline.md`
- **Skill Documentation**: `.claude/skills/README.md`
- **Output Location**: `observability/reports/UX-REVIEW-{date}.md`
- **Makefile Target**: `make ux-review`

## Support

For questions or issues:
1. Check this documentation
2. Review the skill file: `.claude/skills/ux-review-timeline.md`
3. Examine example output (once generated)
4. Modify skill to fit your needs

---

**Ready to start? Run `/ux-review-timeline` now!**
