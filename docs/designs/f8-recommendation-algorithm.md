# F8 Smart Recommendation Algorithm

**Story**: P0-A2A-F8-000 - SDLC Control Plane & Interactive Roadmap
**Task**: Task 2 - Smart Recommendation Engine Design
**Author**: Claude Code
**Date**: 2026-01-30
**Status**: Draft

## Executive Summary

This document specifies the algorithm for analyzing backlog state and generating smart SDLC action recommendations for the Textual button bar. The recommendation engine reads backlog YAML, applies decision tree logic, and outputs ranked actions (e.g., `/implement P0-A2A-F1-001`, `/test functional P0-DOCS-001`) that guide users toward optimal workflow progression.

**Key Features**:
- Context-aware recommendations based on story status, priority, dependencies
- Test-driven workflow enforcement (tests before implementation complete)
- Blocked story detection and alternative suggestions
- Cycle time optimization (reduce context switching)

## Input Schema

### Backlog State Input

```yaml
# Input consumed by recommendation engine
backlog_state:
  stories:
    - story_id: string            # e.g., "P0-A2A-F1-001"
      priority: enum              # P0, P1, P2, P3
      status: enum                # not_started, in_progress, completed, blocked
      type: enum                  # Feature, Infrastructure, Documentation, Bug
      dependencies: list[string]  # Story IDs this story depends on
      tasks: list[string]         # Task descriptions
      acceptance_criteria: list[string]
      functional_test_plan: list[test]  # Test definitions
      estimated_effort: int       # Story points
      started_date: date | null
      completed_date: date | null

  # Derived metrics
  summary:
    total_stories: int
    by_status:
      not_started: int
      in_progress: int
      completed: int
      blocked: int
    by_priority:
      P0: int
      P1: int
      P2: int

  # Current session context (from roadmap HTML view)
  user_context:
    viewing_story: string | null       # Story ID user is viewing in roadmap
    viewing_phase: string | null       # Phase user is viewing
    last_action: string | null         # Last SDLC command executed
    session_start_time: timestamp
```

### Test Execution History (Optional Enhancement)

```yaml
# Historical test results inform recommendations
test_history:
  - story_id: string
    test_type: enum  # functional, unit, integration, governance
    last_run: timestamp
    status: enum     # passed, failed, not_run
    failure_count: int
```

## Output Schema

### Ranked Recommendations

```yaml
# Output: List of recommended actions, ranked by priority
recommendations:
  - rank: int                    # 1 = highest priority
    action_type: enum            # implement, test, quality, commit, review
    command: string              # Exact command to execute (e.g., "/implement P0-A2A-F1-001")
    story_id: string | null      # Associated story (if applicable)
    rationale: string            # Human-readable explanation
    priority_score: float        # 0.0-1.0 (used for ranking)
    urgency: enum                # critical, high, medium, low
    button_label: string         # Display text for button (e.g., "Implement F1-001")
    button_color: enum           # success, warning, danger, info
    estimated_duration: string   # e.g., "2-4 hours", "15 min"

# Example output
recommendations:
  - rank: 1
    action_type: test
    command: "/test functional P0-DOCS-001"
    story_id: "P0-DOCS-001"
    rationale: "Story marked in_progress but tests not run. TDD workflow requires tests before completion."
    priority_score: 0.95
    urgency: critical
    button_label: "🧪 Test P0-DOCS-001"
    button_color: warning
    estimated_duration: "5-10 min"

  - rank: 2
    action_type: implement
    command: "/implement P0-A2A-F8-000"
    story_id: "P0-A2A-F8-000"
    rationale: "Highest priority (P0) story in_progress with incomplete tasks."
    priority_score: 0.90
    urgency: high
    button_label: "⚙️ Continue F8-000"
    button_color: success
    estimated_duration: "2-4 hours"

  - rank: 3
    action_type: implement
    command: "/implement P0-A2A-F1-001"
    story_id: "P0-A2A-F1-001"
    rationale: "Next P0 story with no blockers. Foundation phase work."
    priority_score: 0.85
    urgency: high
    button_label: "▶️ Start F1-001"
    button_color: info
    estimated_duration: "4-6 hours"
```

## Algorithm Pseudocode

### Main Recommendation Flow

```python
def generate_recommendations(backlog_state: BacklogState, user_context: UserContext) -> list[Recommendation]:
    """
    Generate ranked list of SDLC action recommendations.

    Returns:
        List of recommendations sorted by priority_score (desc)
    """
    recommendations = []

    # STEP 1: Analyze in-progress stories (highest priority)
    in_progress_stories = get_stories_by_status(backlog_state, "in_progress")
    for story in in_progress_stories:
        # Check if tests need to run (TDD enforcement)
        if needs_testing(story):
            recommendations.append(create_test_recommendation(story, urgency="critical"))

        # Check if governance validation needed
        if needs_quality_check(story):
            recommendations.append(create_quality_recommendation(story, urgency="high"))

        # Suggest continue implementation if tasks remain
        if has_incomplete_tasks(story):
            recommendations.append(create_implement_recommendation(story, urgency="high"))

    # STEP 2: Find next available work (not started, no blockers)
    available_stories = get_available_stories(backlog_state)
    available_stories = sort_by_priority_and_effort(available_stories)

    for story in available_stories[:3]:  # Top 3 candidates
        recommendations.append(create_implement_recommendation(story, urgency="medium"))

    # STEP 3: Detect blocked stories and suggest unblocking actions
    blocked_stories = get_stories_by_status(backlog_state, "blocked")
    for story in blocked_stories:
        blocking_story = find_blocking_dependency(story, backlog_state)
        if blocking_story:
            recommendations.append(create_unblock_recommendation(story, blocking_story))

    # STEP 4: Context-aware suggestions (based on user's current view)
    if user_context.viewing_story:
        viewed_story = get_story_by_id(backlog_state, user_context.viewing_story)
        if viewed_story and viewed_story.status != "completed":
            # Boost priority of story user is viewing
            boost_recommendation_for_story(recommendations, viewed_story.story_id, boost=0.1)

    # STEP 5: Rank and filter recommendations
    recommendations = calculate_priority_scores(recommendations, backlog_state)
    recommendations = sort_by_score(recommendations)
    recommendations = assign_ranks(recommendations)
    recommendations = limit_to_top_n(recommendations, n=5)  # Max 5 buttons in UI

    return recommendations


def needs_testing(story: Story) -> bool:
    """Check if story needs tests run (TDD enforcement)."""
    if story.status != "in_progress":
        return False

    if not story.functional_test_plan:
        return False  # No tests defined

    # Check if all tasks complete but tests not run
    if all_tasks_complete(story) and not tests_recently_run(story):
        return True

    return False


def get_available_stories(backlog_state: BacklogState) -> list[Story]:
    """Get stories that are ready to start (no blocking dependencies)."""
    available = []

    for story in backlog_state.stories:
        if story.status != "not_started":
            continue

        # Check dependencies are satisfied
        if has_unmet_dependencies(story, backlog_state):
            continue

        available.append(story)

    return available


def has_unmet_dependencies(story: Story, backlog_state: BacklogState) -> bool:
    """Check if story has incomplete dependencies."""
    for dep_id in story.dependencies:
        dep_story = get_story_by_id(backlog_state, dep_id)
        if not dep_story or dep_story.status != "completed":
            return True
    return False


def calculate_priority_scores(recommendations: list[Recommendation], backlog_state: BacklogState) -> list[Recommendation]:
    """Calculate priority scores for ranking recommendations."""
    for rec in recommendations:
        score = 0.5  # Base score

        # Factor 1: Urgency
        urgency_weights = {"critical": 0.3, "high": 0.2, "medium": 0.1, "low": 0.0}
        score += urgency_weights.get(rec.urgency, 0.0)

        # Factor 2: Story priority
        if rec.story_id:
            story = get_story_by_id(backlog_state, rec.story_id)
            priority_weights = {"P0": 0.2, "P1": 0.1, "P2": 0.05, "P3": 0.0}
            score += priority_weights.get(story.priority, 0.0)

        # Factor 3: Action type preference
        # Prefer completing in-progress work over starting new work
        action_weights = {
            "test": 0.15,      # TDD enforcement - always test first
            "quality": 0.10,   # Validate before moving on
            "implement": 0.05, # Continue implementation
            "review": 0.02     # Lower priority
        }
        score += action_weights.get(rec.action_type, 0.0)

        rec.priority_score = min(score, 1.0)  # Cap at 1.0

    return recommendations
```

## Decision Tree

### Recommendation Decision Tree

```
START: Analyze Backlog State
│
├─ Are there stories in_progress?
│  │
│  YES ─► For each in_progress story:
│  │      │
│  │      ├─ All tasks complete AND tests not run?
│  │      │  └─ YES ─► RECOMMEND: /test functional {story_id} [CRITICAL]
│  │      │
│  │      ├─ Tests passed AND governance not validated?
│  │      │  └─ YES ─► RECOMMEND: /quality {story_id} [HIGH]
│  │      │
│  │      └─ Tasks incomplete?
│  │         └─ YES ─► RECOMMEND: /implement {story_id} [HIGH]
│  │
│  NO ──┐
│       │
├───────┴─ Are there not_started stories with no blockers?
│          │
│          YES ─► Sort by priority (P0 > P1 > P2 > P3)
│          │      │
│          │      └─► For top 3:
│          │          └─► RECOMMEND: /implement {story_id} [MEDIUM]
│          │
│          NO ──┐
│                │
├────────────────┴─ Are there blocked stories?
│                   │
│                   YES ─► For each blocked story:
│                   │      │
│                   │      └─► Find blocking dependency
│                   │          └─► RECOMMEND: /implement {blocking_story_id} [MEDIUM]
│                   │              Rationale: "Unblock {blocked_story_id}"
│                   │
│                   NO ──┐
│                         │
└─────────────────────────┴─ All stories complete?
                            │
                            YES ─► RECOMMEND: Review roadmap, plan next phase
                            NO ─► RECOMMEND: Investigate blockers
```

### Test-Driven Workflow Enforcement

```
Story Status: in_progress
│
├─ Check: All tasks complete?
│  │
│  NO ─► RECOMMEND: Continue implementation
│  │
│  YES ─► Check: Tests defined in functional_test_plan?
│           │
│           NO ─► WARN: No tests defined (skip TDD check)
│           │
│           YES ─► Check: Tests run recently? (within last hour)
│                    │
│                    NO ─► RECOMMEND: /test functional {story_id} [CRITICAL]
│                    │     Rationale: "TDD: Verify implementation before marking complete"
│                    │
│                    YES ─► Check: Tests passed?
│                             │
│                             NO ─► RECOMMEND: Fix failing tests [CRITICAL]
│                             │
│                             YES ─► Check: Governance validated?
│                                      │
│                                      NO ─► RECOMMEND: /quality {story_id} [HIGH]
│                                      │
│                                      YES ─► Ready to mark complete!
│                                             RECOMMEND: Review and commit
```

## Input Schema

(Documented above in "Input Schema" section)

## Output Schema

(Documented above in "Output Schema" section)

## Decision Tree

(Documented above in "Decision Tree" section)

## Implementation Considerations

### Performance

- **Target**: Generate recommendations in <50ms for typical backlog (50-100 stories)
- **Optimization**: Cache backlog parse results, only re-analyze on YAML changes
- **Incremental Updates**: When story status changes, only recalculate affected recommendations

### Context Preservation

Recommendation engine maintains awareness of:
1. **User's current view** (which story/phase in roadmap HTML)
2. **Last executed action** (recently ran /implement? Suggest /test next)
3. **Session duration** (long session? Suggest break or switch context)

### Button Bar UI Mapping

Recommendations map to Textual button bar:

```
┌─────────────────────────────────────────────────────────┐
│  Recommended Actions (Context: P0-A2A-F8-000)          │
├─────────────────────────────────────────────────────────┤
│  [🧪 Test P0-DOCS-001]  [⚙️ Continue F8-000]  [▶️ Start F1-001]  │
│  [🔍 Quality Check]     [📊 View Roadmap]                    │
└─────────────────────────────────────────────────────────┘
```

- **Top 5 recommendations** become buttons
- **Button color** reflects urgency (red=critical, yellow=high, blue=medium)
- **Icons** provide visual cues for action type
- **Click** injects command into Claude Code terminal

### Error Handling

- **Invalid backlog YAML**: Return fallback recommendation ("/help")
- **Circular dependencies**: Detect and warn user
- **No available work**: Suggest roadmap review or backlog refinement

## Future Enhancements

### Machine Learning Integration

- **Learn from user behavior**: Track which recommendations users follow
- **Personalization**: Adapt to individual work patterns
- **Velocity prediction**: Estimate completion times based on historical data

### Glean Integration

- **Meeting context**: Incorporate recent discussions about stories
- **Document changes**: Detect when design docs are updated
- **Team activity**: Show which stories colleagues are working on

### Advanced Features

- **Pair programming suggestions**: "Story X would benefit from collaboration with [teammate]"
- **Break reminders**: Detect long sessions, suggest breaks
- **Sprint planning**: Recommend stories for next sprint based on capacity

## Testing Strategy

### Unit Tests

```python
def test_needs_testing_enforcement():
    """Verify TDD workflow enforces tests before marking complete."""
    story = Story(
        story_id="TEST-001",
        status="in_progress",
        tasks=["Task 1: Complete"],
        functional_test_plan=[Test(command="/test functional TEST-001")],
        test_history=[]  # No tests run
    )

    assert needs_testing(story) == True


def test_priority_sorting():
    """Verify P0 stories rank higher than P1."""
    p0_story = Story(priority="P0", status="not_started", dependencies=[])
    p1_story = Story(priority="P1", status="not_started", dependencies=[])

    recommendations = generate_recommendations(
        BacklogState(stories=[p0_story, p1_story]),
        UserContext()
    )

    # P0 story should be first recommendation
    assert recommendations[0].story_id == p0_story.story_id
```

### Integration Tests

- Load real IMPLEMENTATION_BACKLOG.yaml
- Generate recommendations
- Verify top recommendation matches expected next action

## References

- `.sdlc/IMPLEMENTATION_BACKLOG.yaml` - Source data structure
- `docs/designs/f8-terminal-widget-evaluation.md` - Terminal integration approach
- `/implement` SDLC command documentation

---

**Deliverable Status**: ✅ Complete
**Acceptance Criterion**: AC2 - Smart recommendation algorithm fully specified with pseudocode, input schema, output schema, and decision tree logic
