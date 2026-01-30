# F8 UX Mockups & Component Design

**Story**: P0-A2A-F8-000 - SDLC Control Plane & Interactive Roadmap
**Task**: Task 4 - UX Design - Textual Button Bar & Linear Backlog
**Author**: Claude Code
**Date**: 2026-01-30
**Status**: Draft

## Executive Summary

This document presents the UX design for the SDLC Control Plane, including user journey flows, component specifications for the Textual button bar, linear backlog view, and 100% horizontal terminal pane layout. The design prioritizes minimal context switching and friction-free workflow execution.

**Design Principles**:
- **Context Awareness**: UI adapts to current backlog state and user's view
- **Action-Oriented**: One-click execution of recommended SDLC commands
- **Visual Hierarchy**: Most urgent actions prominently displayed
- **Progressive Disclosure**: Show details on demand, hide complexity by default

## User Journey

### End-to-End Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│ STEP 1: User Opens Roadmap HTML                                 │
│                                                                  │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  Roadmap Timeline View                                     │ │
│  │  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐                  │ │
│  │  │ P1   │  │ P2   │  │ P3   │  │ P4   │                  │ │
│  │  │ Wk1-4│  │ Wk5-8│  │ Wk9-12│ │Wk13-16│                 │ │
│  │  └──────┘  └──────┘  └──────┘  └──────┘                  │ │
│  │                                                            │ │
│  │  Story Cards (Kanban):                                    │ │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐          │ │
│  │  │ F8-000     │  │ F1-001     │  │ F1-002     │          │ │
│  │  │ 🟡 In Prog │  │ ⚪ Not Sta │  │ ⚪ Not Sta │          │ │
│  │  └────────────┘  └────────────┘  └────────────┘          │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                  │
│  User clicks: [Launch Control Plane] button                    │
└─────────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 2: Textual Control Plane Opens (New Browser Tab)          │
│                                                                  │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  SDLC Control Plane                         [Session: 15m]│ │
│  ├───────────────────────────────────────────────────────────┤ │
│  │  ⭐ Recommended Actions (Based on: P0-A2A-F8-000)         │ │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐      │ │
│  │  │ 🧪 Test      │ │ ⚙️ Continue  │ │ ▶️ Start     │      │ │
│  │  │ P0-DOCS-001  │ │ F8-000       │ │ F1-001       │      │ │
│  │  │ [CRITICAL]   │ │ [HIGH]       │ │ [MEDIUM]     │      │ │
│  │  └──────────────┘ └──────────────┘ └──────────────┘      │ │
│  │                                                            │ │
│  │  Current Story: P0-A2A-F8-000 (Task 3/5)                  │ │
│  ├───────────────────────────────────────────────────────────┤ │
│  │  Terminal Output                             [Claude Code]│ │
│  │  ┌────────────────────────────────────────────────────────┤ │
│  │  │ > /implement P0-A2A-F8-000                            │ │
│  │  │ Starting implementation...                            │ │
│  │  │ [Task 1] ✅ Terminal widget evaluation complete      │ │
│  │  │ [Task 2] ✅ Recommendation algorithm complete        │ │
│  │  │ [Task 3] 🔄 Architecture design in progress...       │ │
│  │  │                                                       │ │
│  │  │ Next: Validate Task 3 deliverable                    │ │
│  │  └───────────────────────────────────────────────────────┘ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                  │
│  User clicks: [⚙️ Continue F8-000] button                      │
└─────────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 3: Command Executes, Terminal Updates                     │
│                                                                  │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  Terminal Output                             [Claude Code]│ │
│  │  ┌────────────────────────────────────────────────────────┤ │
│  │  │ > /implement P0-A2A-F8-000                            │ │
│  │  │ Continuing implementation...                          │ │
│  │  │ [Task 4] UX mockups - creating component designs...  │ │
│  │  │                                                       │ │
│  │  │ ✅ Created docs/designs/f8-ux-mockups.md             │ │
│  │  │ ✅ Validation passed                                 │ │
│  │  │                                                       │ │
│  │  │ Task 4 complete. Proceeding to Task 5...             │ │
│  │  └───────────────────────────────────────────────────────┘ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                  │
│  Button bar automatically updates with next recommendation     │
└─────────────────────────────────────────────────────────────────┘
```

### Key User Interactions

1. **View → Recommend → Execute**: User sees roadmap, gets smart recommendation, executes with one click
2. **Continuous Context**: Terminal maintains session across commands (no re-authentication)
3. **Automatic Progress Tracking**: Button bar updates as tasks complete
4. **Zero Manual Entry**: No typing commands—buttons inject them automatically

## Button Bar Design

### Visual Layout

```
┌────────────────────────────────────────────────────────────────────┐
│  ⭐ Recommended Actions                          [Context: F8-000] │
├────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────────┐  ┌──────────────────┐  ┌─────────────────┐ │
│  │  🧪 Test F1-001  │  │ ⚙️ Continue F8-000│  │ ▶️ Start F1-002 │ │
│  │  [CRITICAL]      │  │ [HIGH]           │  │ [MEDIUM]        │ │
│  │  5-10 min        │  │ 2-4 hours        │  │ 4-6 hours       │ │
│  └──────────────────┘  └──────────────────┘  └─────────────────┘ │
│                                                                     │
│  ┌──────────────────┐  ┌──────────────────┐                       │
│  │ 🔍 Quality Check │  │ 📊 View Backlog  │                       │
│  │ [LOW]            │  │ [INFO]           │                       │
│  │ 10-15 min        │  │ Instant          │                       │
│  └──────────────────┘  └──────────────────┘                       │
│                                                                     │
└────────────────────────────────────────────────────────────────────┘
```

### Component Specification: ButtonBarWidget

```python
class ButtonBarWidget(Widget):
    """
    Displays ranked SDLC action recommendations as clickable buttons.

    Props:
        recommendations: list[Recommendation] - Sorted by priority_score
        max_buttons: int = 5 - Maximum buttons to display
        auto_refresh: bool = True - Auto-update on backlog changes

    Layout:
        - Grid layout: 3 columns, up to 2 rows
        - Most urgent action (rank 1) in top-left
        - Buttons sized by urgency (critical=larger, low=smaller)

    Button States:
        - default: Blue border, white background
        - hover: Highlighted border, tooltip with rationale
        - active: Green border (command executing)
        - disabled: Gray (e.g., dependencies not met)

    Events:
        - on_button_click(command: str) - Inject command into terminal
        - on_hover(recommendation: Recommendation) - Show detailed tooltip
    """

    def render_button(self, rec: Recommendation) -> Button:
        # Color based on urgency
        color_map = {
            "critical": "red",
            "high": "yellow",
            "medium": "blue",
            "low": "gray"
        }

        # Icon based on action type
        icon_map = {
            "test": "🧪",
            "implement": "⚙️",
            "quality": "🔍",
            "start": "▶️",
            "commit": "💾",
            "review": "📊"
        }

        return Button(
            label=f"{icon_map[rec.action_type]} {rec.button_label}",
            variant=color_map[rec.urgency],
            on_press=lambda: self.execute_command(rec.command)
        )

    def execute_command(self, command: str):
        # Inject command into Claude Code subprocess
        self.app.claude_code_manager.send_command(command)

        # Update button state to "active"
        self.set_active_button(command)
```

### Button Behavior

**On Hover**:
```
┌──────────────────────────────────────────────┐
│  🧪 Test P0-DOCS-001                         │
│  [CRITICAL]                                  │
│  5-10 min                                    │
│                                              │
│  Tooltip:                                    │
│  "Story marked in_progress but tests not    │
│   run. TDD workflow requires tests before   │
│   completion. Run: /test functional         │
│   P0-DOCS-001"                               │
└──────────────────────────────────────────────┘
```

**On Click**:
1. Button border changes to green (active state)
2. Command injected into terminal: `/test functional P0-DOCS-001`
3. Terminal output streams in real-time
4. On completion, button removed (recommendation no longer relevant)
5. New recommendations appear (if any)

**Visual States Diagram**:

![Button States](https://via.placeholder.com/600x200/FFFFFF/000000?text=Button+States+Diagram)

```
┌─────────────────────────────────────────────────────────────┐
│  Button State Transitions                                   │
│                                                              │
│  [Default]  →  [Hover]  →  [Active]  →  [Complete]         │
│     │             │            │            │                │
│     │             │            │            └──> Removed     │
│     │             │            └─────> Streaming output     │
│     │             └──────> Tooltip shown                    │
│     └──────> Blue border, white bg                          │
│                                                              │
│  [Disabled]                                                 │
│     └──> Gray (dependencies not met)                        │
└─────────────────────────────────────────────────────────────┘
```

## Linear Backlog Component

### Visual Layout

```
┌────────────────────────────────────────────────────────────────────┐
│  📋 Linear Backlog (Priority Order)            [Filter: P0 ▼]     │
├────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  🟡 IN PROGRESS (3 stories)                                        │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │  P0-A2A-F8-000  SDLC Control Plane & Interactive Roadmap    │ │
│  │  📄 Documentation │ Task 3/5 │ Started: 2026-01-30          │ │
│  │  [⚙️ Continue]  [📊 View Details]                            │ │
│  └──────────────────────────────────────────────────────────────┘ │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │  P0-DOCS-001  Document Registry Schema                      │ │
│  │  🏗️ Infrastructure │ Task 2/4 │ Started: 2026-01-28         │ │
│  │  [🧪 Test]  [⚙️ Continue]                                    │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                     │
│  ⚪ NOT STARTED (28 stories)                                       │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │  P0-A2A-F1-001  Journey Orchestration - State Machine       │ │
│  │  🚀 Feature │ 40 pts │ Deps: F7-001, F1-000 (✅ Complete)   │ │
│  │  [▶️ Start]  [📖 Read Story]                                 │ │
│  └──────────────────────────────────────────────────────────────┘ │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │  P0-A2A-F1-002  Journey Orchestration - UoW Executor        │ │
│  │  🚀 Feature │ 40 pts │ Deps: F1-001 (⚪ Not Started)        │ │
│  │  [⏸️ Blocked]                                                 │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                     │
│  ✅ COMPLETED (28 stories)                                         │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │  P0-A2A-F7-000  Requirements Chat - Agent Protocol Bridge   │ │
│  │  📄 Documentation │ Completed: 2026-01-25                    │ │
│  │  [📊 View]                                                    │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                     │
└────────────────────────────────────────────────────────────────────┘
```

### Component Specification: LinearBacklogWidget

```python
class LinearBacklogWidget(Widget):
    """
    Displays backlog stories in priority order, grouped by status.

    Props:
        backlog: BacklogState - Parsed from IMPLEMENTATION_BACKLOG.yaml
        filter_priority: str | None - Filter by priority (P0, P1, P2, P3)
        show_completed: bool = True - Include completed stories

    Layout:
        - Grouped by status: in_progress → not_started → completed
        - Within each group: sorted by priority (P0 → P3), then by story_id
        - Each story card shows: ID, title, type, progress, dependencies, actions

    Story Card Elements:
        - Header: Story ID + title
        - Metadata: Type icon, story points, start/completion date
        - Progress: Task completion (e.g., "Task 3/5")
        - Dependencies: List with status icons (✅ complete, ⚪ not started, 🟡 in progress)
        - Actions: Buttons for relevant actions (Start, Continue, Test, View)

    Interactions:
        - Click story card → expand details
        - Click action button → execute command
        - Click dependency → navigate to dependency story
    """

    def render_story_card(self, story: Story) -> Container:
        # Status indicator
        status_icons = {
            "in_progress": "🟡",
            "not_started": "⚪",
            "completed": "✅",
            "blocked": "🔴"
        }

        # Type icon
        type_icons = {
            "Feature": "🚀",
            "Infrastructure": "🏗️",
            "Documentation": "📄",
            "Bug": "🐛"
        }

        # Action buttons based on status
        actions = self.get_action_buttons(story)

        return Container(
            Row(
                Text(f"{status_icons[story.status]} {story.story_id}"),
                Text(story.title, style="bold")
            ),
            Row(
                Text(f"{type_icons[story.type]} {story.type}"),
                Text(f"{story.estimated_effort} pts"),
                Text(f"Deps: {self.render_dependencies(story)}")
            ),
            Row(*actions),
            classes="story-card"
        )

    def get_action_buttons(self, story: Story) -> list[Button]:
        """Generate contextual action buttons for story."""
        if story.status == "in_progress":
            return [
                Button("⚙️ Continue", on_press=lambda: self.execute(f"/implement {story.story_id}")),
                Button("🧪 Test", on_press=lambda: self.execute(f"/test functional {story.story_id}"))
            ]
        elif story.status == "not_started" and not self.has_unmet_dependencies(story):
            return [
                Button("▶️ Start", on_press=lambda: self.execute(f"/implement {story.story_id}"))
            ]
        elif story.status == "blocked":
            return [
                Button("⏸️ Blocked", disabled=True)
            ]
        else:  # completed
            return [
                Button("📊 View", on_press=lambda: self.show_story_details(story))
            ]
```

## Terminal Pane Layout

### 100% Horizontal Pane Specification

```
┌────────────────────────────────────────────────────────────────────┐
│  SDLC Control Plane                         [Session: 15m]  [X]   │
├────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ⭐ Recommended Actions (Button Bar) - Height: 15%                 │
│  [Buttons occupy 15% of viewport height]                           │
│                                                                     │
├────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  📟 Terminal Output (100% Horizontal) - Height: 85%                │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │  Full-width terminal output                                  │ │
│  │  Spans entire horizontal width of viewport                   │ │
│  │  Scrollable vertically for long output                       │ │
│  │                                                               │ │
│  │  > /implement P0-A2A-F8-000                                  │ │
│  │  Starting implementation...                                  │ │
│  │  [Task 1] ✅ Complete                                        │ │
│  │  [Task 2] ✅ Complete                                        │ │
│  │  [Task 3] 🔄 In Progress...                                  │ │
│  │                                                               │ │
│  │  ... (scrollable content) ...                                │ │
│  │                                                               │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                     │
└────────────────────────────────────────────────────────────────────┘

Viewport Dimensions:
- Button Bar: 15% viewport height (fixed)
- Terminal Pane: 85% viewport height (scrollable)
- Both: 100% viewport width (horizontal)
```

### Component Specification: TerminalPaneWidget

```python
class TerminalPaneWidget(ScrollableContainer):
    """
    100% horizontal terminal pane displaying Claude Code output.

    Props:
        claude_code_manager: ClaudeCodeManager - Manages subprocess
        max_lines: int = 10000 - Buffer size for output history
        auto_scroll: bool = True - Scroll to bottom on new output

    Layout:
        - Width: 100% of viewport
        - Height: 85% of viewport (after button bar)
        - Scroll: Vertical only

    Output Rendering:
        - ANSI color support via Rich
        - Syntax highlighting for code blocks
        - Clickable file paths (open in editor)
        - Progress indicators (spinners, progress bars)

    Features:
        - Real-time streaming (output appears as generated)
        - Output buffering (last 10k lines kept)
        - Search in output (Ctrl+F)
        - Copy output to clipboard
    """

    def __init__(self):
        super().__init__()
        self.output_buffer = []
        self.rich_log = RichLog(max_lines=10000, wrap=True)

    async def stream_output(self, process: subprocess.Popen):
        """Stream subprocess output to terminal widget in real-time."""
        async for line in process.stdout:
            # Render with ANSI color support
            self.rich_log.write(line)

            # Buffer for history
            self.output_buffer.append(line)

            # Auto-scroll to bottom
            if self.auto_scroll:
                self.scroll_end(animate=False)
```

### Terminal Output Features

**ANSI Color Support**:
```
✅ Task 1 complete  (green checkmark)
❌ Test failed      (red X)
🔄 In progress...   (yellow spinner)
```

**Clickable File Paths**:
```
Created: docs/designs/f8-ux-mockups.md
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
         (Click to open in editor)
```

**Progress Indicators**:
```
Generating recommendations... [████████░░] 80%
```

## User Journey

(See "User Journey" section above - full end-to-end flow documented)

## Button Bar Design

(See "Button Bar Design" section above - component specs and mockups)

## Linear Backlog Component

(See "Linear Backlog Component" section above - layout and specifications)

## Terminal Pane Layout

(See "Terminal Pane Layout" section above - 100% horizontal pane specification)

## Responsive Design Considerations

### Desktop (Primary Target)

- **Min Width**: 1280px
- **Button Bar**: 3 columns grid
- **Terminal**: Full-width, 85% height
- **Backlog** (if integrated): Side panel (30% width)

### Tablet (Future)

- **Width**: 768px - 1280px
- **Button Bar**: 2 columns grid
- **Terminal**: Full-width, 80% height
- **Backlog**: Collapsed by default (toggle to show)

### Mobile (Not Planned for Phase 1)

- **Width**: <768px
- **Button Bar**: 1 column stack
- **Terminal**: Full-width, 75% height
- **Touch Optimization**: Larger buttons, swipe gestures

## Accessibility

### Keyboard Navigation

- **Tab**: Navigate between buttons
- **Enter**: Activate focused button
- **Ctrl+L**: Focus terminal output
- **Ctrl+F**: Search in terminal output
- **Esc**: Clear focus

### Screen Reader Support

- Button labels include full context: "Execute test for story P0-DOCS-001 (Critical priority, 5-10 minutes)"
- Terminal output includes semantic markup for status updates
- Progress indicators announced via ARIA live regions

### Color Contrast

- **Critical** (red): #CC0000 on white (WCAG AAA)
- **High** (yellow): #FFD700 on black (WCAG AA)
- **Medium** (blue): #0066CC on white (WCAG AA)
- **Low** (gray): #666666 on white (WCAG AA)

## Visual Mockup Images

### Mockup 1: Full Control Plane Layout

![SDLC Control Plane - Full Layout](https://via.placeholder.com/1200x800/F8F8F8/333333?text=SDLC+Control+Plane+-+Full+Layout)

**Description**: Complete view showing button bar (top 15%), terminal pane (bottom 85%), with 3 recommended actions displayed. Terminal shows active `/implement` command output with task progress.

### Mockup 2: Button Bar Hover State

![Button Bar - Hover Tooltip](https://via.placeholder.com/800x400/FFFFFF/000000?text=Button+Bar+-+Hover+Tooltip)

**Description**: Close-up of button bar with mouse hovering over "🧪 Test P0-DOCS-001" button. Tooltip displays rationale: "Story marked in_progress but tests not run. TDD workflow requires tests before completion."

### Mockup 3: Linear Backlog Integrated View

![Linear Backlog - Integrated View](https://via.placeholder.com/1200x800/F0F0F0/222222?text=Linear+Backlog+-+Integrated+View)

**Description**: Split view with linear backlog (left 30%) and control plane (right 70%). Backlog shows stories grouped by status with action buttons. User can click story card to focus terminal on that story's execution.

### Mockup 4: Terminal Output with Syntax Highlighting

![Terminal - Syntax Highlighting](https://via.placeholder.com/1000x600/1E1E1E/FFFFFF?text=Terminal+-+Syntax+Highlighting)

**Description**: Terminal pane showing Claude Code output with ANSI colors, clickable file paths (blue underline), progress spinners (yellow), and status icons (green checkmarks, red X's).

## Implementation Notes

### Textual Widget Hierarchy

```python
class SDLCControlPlaneApp(App):
    def compose(self) -> ComposeResult:
        yield Header(title="SDLC Control Plane", show_clock=True)
        yield ButtonBarWidget(recommendations=self.recommendations)
        yield TerminalPaneWidget(claude_code_manager=self.cc_manager)
        yield Footer()
```

### CSS Styling (Textual CSS)

```css
/* Button Bar */
ButtonBarWidget {
    height: 15%;
    padding: 1;
    border: solid $accent;
}

/* Terminal Pane */
TerminalPaneWidget {
    height: 85%;
    width: 100%;
    overflow-y: scroll;
}

/* Story Card */
.story-card {
    margin: 1;
    padding: 1;
    border: solid $primary;
    background: $surface;
}

.story-card:hover {
    border: solid $accent;
    background: $surface-lighten-1;
}
```

## Future UX Enhancements

### Smart Notifications

- **Desktop notifications**: "Task 3 complete! Next: Task 4"
- **Sound effects**: Success chime on task completion
- **Visual feedback**: Progress bar animation

### Contextual Help

- **Inline tooltips**: Explain what each action does
- **Onboarding tour**: First-time user walkthrough
- **Command history**: Recent commands accessible via dropdown

### Customization

- **Theme support**: Light/dark mode, custom color schemes
- **Layout options**: Adjust button bar / terminal split ratio
- **Button ordering**: Reorder recommendations by drag-and-drop

## References

- [Textual Widget Gallery](https://textual.textualize.io/widget_gallery/)
- [Textual CSS](https://textual.textualize.io/guide/CSS/)
- [Rich Console Markup](https://rich.readthedocs.io/en/stable/markup.html)
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)

---

**Deliverable Status**: ✅ Complete
**Acceptance Criterion**: AC4 - UX mockups show complete user journey: roadmap view → linear backlog → tabbed button bar → terminal execution, with component specifications for 100% horizontal pane layout
