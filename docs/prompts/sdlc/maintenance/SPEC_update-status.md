---
title: "Technical Specification: update-status"
version: 1.0
date: 2026-01-22
status: draft
purpose: "Documentation for Technical Specification: update-status"
---

# Technical Specification: update-status

**Prompt Name:** Update Status
**Short Name:** `update-status`
**Version:** 1.0
**Stateful:** No
**SDLC Subdomain:** Maintenance

---

## 1. Purpose & Objectives

### Primary Goal

Produce a comprehensive, actionable project progress report that synthesizes all work completed to date and all work planned, and defines clear next steps.

### Key Objectives

1. **Progress Synthesis** - Combine all status inputs into coherent view
2. **Work Categorization** - Distinguish completed, in-progress, planned work
3. **Risk Identification** - Surface blockers and dependencies
4. **Next Steps Definition** - Provide specific, actionable follow-ups
5. **Gap Identification** - Call out missing information

---

## 2. Input/Output Schemas

### Input Sources

| Source Type | Description | Purpose |
|-------------|-------------|---------|
| Status Updates | Reported progress | Completed work |
| Planned Work | Upcoming tasks/roadmap | Future work |
| Backlog | Story statuses | State tracking |
| Risk Log | Known issues | Risk section |

### Input Format

```yaml
status_input:
  reported_progress:
    - item: "Completed Work Unit Discovery implementation"
      date: "2026-01-20"
      status: completed
      details: "All acceptance criteria met"

    - item: "Baseline Comparison in progress"
      date: "2026-01-21"
      status: in_progress
      details: "70% complete"

  planned_work:
    - item: "GTM Motion Classification"
      priority: P0
      timeline: "Next sprint"

    - item: "Client Journey Tracking"
      priority: P1
      timeline: "Following sprint"

  risks_blockers:
    - risk: "MCP rate limiting not implemented"
      impact: "Medium"
      mitigation: "Add rate limiting in next iteration"

  open_questions:
    - question: "Integration with external calendar API?"
```

### Output Schema

```markdown
# Project Progress Report

**Report Date:** 2026-01-21
**Reporting Period:** [Date range]
**Status:** On Track / At Risk / Off Track

---

## 1. Executive Summary

- **Overall Status:** On Track with 2 of 3 P0 features complete
- **Key Accomplishment:** Work Unit Discovery validated with 89% confidence
- **Current Focus:** Baseline Comparison (70% complete)
- **Next Milestone:** GTM Motion Classification
- **Key Risk:** MCP rate limiting needed before production

---

## 2. Completed Work (Reported Progress)

### P0 Features
| Feature | Status | Completion Date | Notes |
|---------|--------|-----------------|-------|
| Work Unit Discovery | ✅ Complete | 2026-01-20 | All AC met |
| Baseline Validation | ✅ Complete | 2026-01-15 | 51.4 min average |

### Infrastructure
- Test framework established (P0-INFRA-001) ✅
- Environment configuration complete ✅

### Documentation
- IMPLEMENTATION_BACKLOG.yaml at version 13
- 142 make commands cataloged

---

## 3. Current Status & In-Progress Work

### Active Work Items
| Item | Owner | Progress | Status | Target |
|------|-------|----------|--------|--------|
| Baseline Comparison | Team | 70% | On Track | 2026-01-22 |
| Client Extraction | Team | 40% | At Risk | 2026-01-24 |

### Blocked Items
| Item | Blocker | Impact | Mitigation |
|------|---------|--------|------------|
| None currently blocked |

---

## 4. Planned Work (Upcoming Progress)

### Short-term (This Week)
1. Complete Baseline Comparison feature
2. Begin GTM Motion Classification

### Mid-term (Next 2 Weeks)
1. GTM Motion Classification (P0)
2. Client Journey Tracking (P1)
3. Reporting integration (P1)

### Long-term (Next Month)
1. Production deployment preparation
2. Performance optimization
3. Documentation completion

---

## 5. Risks, Blockers, and Dependencies

### Active Risks
| Risk | Probability | Impact | Mitigation | Owner |
|------|-------------|--------|------------|-------|
| MCP rate limiting | Medium | High | Add throttling layer | TBD |
| API changes | Low | Medium | Pin API versions | Team |

### Dependencies
| Dependency | Status | Notes |
|------------|--------|-------|
| Glean MCP access | ✅ Available | Configured |
| Test data | ✅ Available | Sample data ready |

### Blockers
- None currently

---

## 6. Detailed Next Steps

### Immediate (Today/Tomorrow)
1. **Complete Baseline Comparison testing**
   - What: Run validation tests
   - Why: Unblock GTM Motion work
   - Expected: All tests passing
   - Owner: [TBD]

2. **Review GTM Motion design**
   - What: Review classification approach
   - Why: Prepare for implementation
   - Expected: Approved design

### This Week
1. **Implement GTM Motion Classification**
   - Start after Baseline Comparison complete
   - Follow existing pattern from Work Unit Discovery

2. **Update documentation**
   - Update README with progress
   - Generate artifact report

### Decisions Needed
1. Rate limiting strategy for MCP queries
2. Production deployment timeline

---

## 7. Open Questions / Information Gaps

### Clarification Needed
- Integration approach for external calendar API
- Performance targets for production

### Missing Information
- Final production environment details
- User acceptance testing schedule

### Assumptions Made
- Current MCP access will remain available
- No major API changes before release
```

---

## 3. Dependencies

### Required Inputs

| Dependency | Type | Description |
|------------|------|-------------|
| Status Inputs | Context | Progress reports |
| Planned Work | Context | Future tasks |
| Backlog | Optional | State reference |

### Runtime Dependencies

| Dependency | Purpose |
|------------|---------|
| `yml-bck-mgr` | Backlog state |
| `quality-gate` | Validation results |

### Downstream Consumers

| Consumer | Purpose |
|----------|---------|
| Stakeholders | Progress visibility |
| `update-readme` | README updates |
| Project planning | Future work decisions |

---

## 4. Processing Steps

### Step 1: Parse Reported Progress

**Actions:**
- List all reported progress items
- Categorize: completed, in-progress
- Note completion dates and details

### Step 2: Parse Planned Work

**Actions:**
- List all planned/upcoming items
- Categorize: short-term, mid-term, long-term
- Note priorities and timelines

### Step 3: Group into Workstreams

**Actions:**
- Organize by workstream, team, or milestone
- Identify logical groupings
- Create coherent structure

### Step 4: Evaluate Status

**Actions:**
- Assess per-workstream status
- Overall project status: on track / at risk / off track
- Consider timing and scope

### Step 5: Draft Progress Report

**Actions:**
- Executive summary (2-5 bullets)
- Completed work section
- Current status section
- Planned work section

### Step 6: Define Next Steps

**Actions:**
- Create specific, actionable items
- Include: what, why, expected outcome
- Add owner/timeline if available
- Prioritize by urgency

### Step 7: Document Gaps

**Actions:**
- List open questions
- Note missing information
- Document assumptions made
- Identify decisions needed

---

## 5. Usage Examples

### Example 1: Full Status Report

**Prompt:**
```
Produce a comprehensive project progress report with detailed next steps.
```

**Expected Output:**
- Executive summary with 5 key points
- Completed work by workstream
- In-progress items with % complete
- Planned work by timeline
- 3 risks with mitigation
- 10 specific next steps

### Example 2: Stakeholder Update

**Prompt:**
```
Create an executive-ready status update for the weekly meeting.
```

**Expected Behavior:**
- Focus on executive summary
- Highlight major accomplishments
- Call out key risks
- Clear next milestone
- Concise format

### Example 3: Team Sync Report

**Prompt:**
```
Generate a detailed status report for the development team.
```

**Expected Behavior:**
- Technical detail included
- Specific task status
- Detailed next steps
- Technical blockers noted
- Implementation guidance

---

## 6. Integration Points

### Integration with yml-bck-mgr

```yaml
# Status reflects backlog state
workflow:
  1. Read IMPLEMENTATION_BACKLOG.yaml
  2. Extract story statuses
  3. Include in completed/in-progress sections
  4. Reference story IDs
```

### Integration with update-readme

```yaml
# Status informs README updates
workflow:
  1. update-status produces progress report
  2. update-readme uses status summary
  3. README current project status updated
```

---

## 7. Success Criteria

### Validation Rules

| Rule | Description |
|------|-------------|
| Both Directions | Reports both completed and planned work |
| Clear Separation | Completed vs planned clearly distinguished |
| Next Steps Section | Dedicated section for follow-ups |
| Risks Surfaced | Blockers and dependencies identified |
| Gaps Called Out | Assumptions and missing info explicit |
| Consistent | No contradictions with provided updates |

### Quality Metrics

| Metric | Target |
|--------|--------|
| Completeness | All input items reflected |
| Actionability | Next steps are specific |
| Clarity | Self-contained report |
| Stakeholder Ready | Executive summary present |

---

## 8. Constraints

1. **Evidence-Based** - Only conclude from provided info
2. **Self-Contained** - Readable without raw updates
3. **Clear Structure** - Headings and bullets, no long paragraphs
4. **Separated Sections** - Completed vs planned clearly divided
5. **No Jargon** - Explain acronyms on first use

---

## 9. Error Handling

| Error Condition | Handling |
|-----------------|----------|
| Missing status info | Note gap, proceed with available |
| Conflicting updates | Use most recent, note conflict |
| Unclear timeline | Flag as "timeline TBD" |
| No planned work | Note as "planning needed" |

---

## 10. Output Format

### Required Sections

1. **Executive Summary** (2-5 bullets)
   - Overall status
   - Major accomplishments
   - Key upcoming work

2. **Completed Work**
   - By workstream/milestone
   - Key deliverables

3. **Current Status & In-Progress**
   - Active items with progress
   - Status indicators

4. **Planned Work**
   - Short/mid/long term
   - Priorities and timelines

5. **Risks, Blockers, Dependencies**
   - Known issues
   - Impact and mitigation

6. **Detailed Next Steps**
   - Specific, actionable
   - What, why, expected outcome
   - Owner/timeline if available

7. **Open Questions / Information Gaps**
   - Clarification needed
   - Assumptions documented

---

## Appendix: Status Indicators

| Indicator | Meaning | Criteria |
|-----------|---------|----------|
| On Track | Proceeding as planned | No blockers, timeline met |
| At Risk | May miss target | Minor issues, mitigation possible |
| Off Track | Missing target | Major blockers, intervention needed |
| Blocked | Cannot proceed | Requires external resolution |
| Complete | Finished | All acceptance criteria met |
