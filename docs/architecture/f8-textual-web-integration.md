# F8 Textual-Web Integration Architecture

**Story**: P0-A2A-F8-000 - SDLC Control Plane & Interactive Roadmap
**Task**: Task 3 - Textual-Web Integration Architecture
**Author**: Claude Code
**Date**: 2026-01-30
**Status**: Draft

## Executive Summary

This document specifies the architecture for deploying the SDLC Control Plane as a browser-accessible Textual TUI application. The design leverages `textual serve` and `textual-web` to run the Textual app in a browser while maintaining full Claude Code terminal capabilities and backlog state synchronization with the roadmap HTML.

**Key Architectural Decisions**:
- Use `textual serve` for development, `textual-web` for production deployment
- WebSocket-based communication for real-time updates
- Shared state management via JSON file bridge between roadmap HTML and Textual app
- Process lifecycle management for Claude Code subprocess

## Deployment Architecture

### Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────────┐
│                           Browser (Client)                            │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │  Tab 1: Roadmap HTML (Static)                                   │ │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐│ │
│  │  │ Timeline View   │  │ Story Cards     │  │ Linear Backlog  ││ │
│  │  │ (Phases 1-4)    │  │ (Kanban)        │  │ (Priority List) ││ │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘│ │
│  │                                                                  │ │
│  │  JavaScript:                                                    │ │
│  │  - Reads IMPLEMENTATION_BACKLOG.yaml → renders backlog view    │ │
│  │  - Writes user context to .sdlc/.context.json                  │ │
│  │  - Detects story selection → updates context file              │ │
│  │  - Auto-refreshes on file changes (polling or file watcher)    │ │
│  └─────────────────────────────────────────────────────────────────┘ │
│                                                                        │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │  Tab 2: Textual Control Plane (via textual serve/textual-web)  │ │
│  │  ┌─────────────────────────────────────────────────────────────┐│ │
│  │  │  WebSocket Connection (ws://localhost:8080 or https://...)  ││ │
│  │  └─────────────────────────────────────────────────────────────┘│ │
│  │                                                                  │ │
│  │  ┌─────────────────────────────────────────────────────────────┐│ │
│  │  │  Textual TUI Rendered in Browser                            ││ │
│  │  │  ┌──────────────────────────────────────────────────────┐  ││ │
│  │  │  │  Recommended Actions (Button Bar)                    │  ││ │
│  │  │  │  [🧪 Test F1-001] [⚙️ Continue F8-000] [▶️ Start...] │  ││ │
│  │  │  └──────────────────────────────────────────────────────┘  ││ │
│  │  │  ┌──────────────────────────────────────────────────────┐  ││ │
│  │  │  │  Terminal Output (RichLog Widget)                    │  ││ │
│  │  │  │                                                       │  ││ │
│  │  │  │  > /implement P0-A2A-F8-000                          │  ││ │
│  │  │  │  Starting implementation for F8-000...               │  ││ │
│  │  │  │  [Task 1] Terminal widget evaluation: ✅ Complete    │  ││ │
│  │  │  │  [Task 2] Recommendation engine: ✅ Complete         │  ││ │
│  │  │  │  [Task 3] Architecture design: 🔄 In Progress...     │  ││ │
│  │  │  │                                                       │  ││ │
│  │  │  └──────────────────────────────────────────────────────┘  ││ │
│  │  └─────────────────────────────────────────────────────────────┘│ │
│  └─────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────┘
                                    ▲
                                    │ WebSocket (bidirectional)
                                    ▼
┌──────────────────────────────────────────────────────────────────────┐
│                      Server (Backend)                                 │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │  Textual Serve / Textual-Web Server                            │  │
│  │  (Python Process)                                              │  │
│  │                                                                 │  │
│  │  ┌──────────────────────────────────────────────────────────┐ │  │
│  │  │  SDLC Control Plane Textual App                          │ │  │
│  │  │                                                           │ │  │
│  │  │  Components:                                             │ │  │
│  │  │  - RecommendationEngine (reads backlog + context)       │ │  │
│  │  │  - ButtonBarWidget (displays smart actions)             │ │  │
│  │  │  - TerminalOutputWidget (RichLog displaying output)     │ │  │
│  │  │  - ClaudeCodeManager (subprocess lifecycle)             │ │  │
│  │  └──────────────────────────────────────────────────────────┘ │  │
│  │                                                                 │  │
│  │  ┌──────────────────────────────────────────────────────────┐ │  │
│  │  │  Shared State Manager                                    │ │  │
│  │  │  - Watches .sdlc/.context.json for user view updates    │ │  │
│  │  │  - Reads IMPLEMENTATION_BACKLOG.yaml                     │ │  │
│  │  │  - Generates recommendations on state change             │ │  │
│  │  └──────────────────────────────────────────────────────────┘ │  │
│  │                                                                 │  │
│  │  ┌──────────────────────────────────────────────────────────┐ │  │
│  │  │  Claude Code Subprocess                                  │ │  │
│  │  │  - Spawned via pty/subprocess                            │ │  │
│  │  │  - stdin: receives commands from button clicks           │ │  │
│  │  │  - stdout/stderr: streamed to TerminalOutputWidget       │ │  │
│  │  │  - Persistent session across button interactions         │ │  │
│  │  └──────────────────────────────────────────────────────────┘ │  │
│  └────────────────────────────────────────────────────────────────┘  │
│                                                                        │
│  File System:                                                         │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │  .sdlc/IMPLEMENTATION_BACKLOG.yaml  (source of truth)          │  │
│  │  .sdlc/.context.json  (user view state, written by roadmap JS) │  │
│  │  .sdlc/.session_state.json  (terminal session persistence)     │  │
│  └────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────┘
```

### Deployment Models

#### Development Mode: `textual serve`

```bash
# Start Textual app in browser (development)
cd /path/to/repo
textual serve sdlc_control_plane.py --port 8080

# Browser opens to http://localhost:8080
# WebSocket connection: ws://localhost:8080
```

**Characteristics**:
- ✅ Fast iteration (hot reload)
- ✅ Simple setup (single command)
- ✅ Runs locally on developer machine
- ⚠️ Not suitable for production (no auth, single user)

#### Production Mode: `textual-web`

```bash
# Deploy Textual app with textual-web (production)
textual-web --app sdlc_control_plane.py --public --auth

# Generates public URL: https://xxx.textual.run
# Multi-user support with authentication
```

**Characteristics**:
- ✅ Public URL (share with team)
- ✅ Multi-user sessions
- ✅ Authentication support
- ✅ Persistent deployment
- ⚠️ Requires textual-web service account

### Hybrid Deployment (Recommended for Phase 1)

**Setup**:
1. **Roadmap HTML**: Served via local HTTP server or GitHub Pages
2. **Textual Control Plane**: `textual serve` on localhost
3. **User workflow**: Open roadmap HTML → click "Launch Control Plane" button → opens localhost:8080

**Advantages**:
- No dependency on external services (runs entirely local)
- Simple setup for proof-of-concept
- Easy to upgrade to textual-web later

## Session Management

### Session Lifecycle

```
User Opens Textual Control Plane
│
├─ STEP 1: Initialize Session
│  │
│  ├─ Generate session_id (UUID)
│  ├─ Load backlog state (IMPLEMENTATION_BACKLOG.yaml)
│  ├─ Load user context (.sdlc/.context.json)
│  ├─ Restore previous terminal session (if exists)
│  └─ Spawn Claude Code subprocess (if not running)
│
├─ STEP 2: Active Session
│  │
│  ├─ File watcher monitors:
│  │  ├─ IMPLEMENTATION_BACKLOG.yaml (backlog changes)
│  │  └─ .sdlc/.context.json (user view changes)
│  │
│  ├─ On file change:
│  │  ├─ Reload state
│  │  └─ Regenerate recommendations
│  │
│  ├─ On button click:
│  │  ├─ Inject command into Claude Code stdin
│  │  ├─ Stream output to terminal widget
│  │  └─ Update session state
│  │
│  └─ WebSocket heartbeat (every 30s)
│
└─ STEP 3: Session Termination
   │
   ├─ User closes browser tab OR timeout (30 min idle)
   ├─ Save session state (.sdlc/.session_state.json)
   ├─ Keep Claude Code subprocess running (allow resume)
   └─ Clean up resources
```

### Session State Schema

```json
{
  "session_id": "uuid-v4",
  "user": "eric.flecher",
  "started_at": "2026-01-30T10:00:00Z",
  "last_active": "2026-01-30T10:15:00Z",

  "backlog_snapshot": {
    "last_loaded": "2026-01-30T10:00:00Z",
    "file_hash": "sha256:abc123...",
    "current_story": "P0-A2A-F8-000"
  },

  "user_context": {
    "viewing_story": "P0-A2A-F8-000",
    "viewing_phase": "phase-1",
    "last_action": "/implement P0-A2A-F8-000",
    "last_action_time": "2026-01-30T10:10:00Z"
  },

  "terminal_session": {
    "claude_code_pid": 12345,
    "working_directory": "/Users/eric.flecher/Workbench/projects/a_domain",
    "command_history": [
      "/implement P0-A2A-F8-000",
      "Task 1 completed"
    ],
    "output_buffer": "... terminal output ..."
  },

  "recommendations_cache": [
    {
      "rank": 1,
      "command": "/test functional P0-DOCS-001",
      "generated_at": "2026-01-30T10:15:00Z"
    }
  ]
}
```

### Session Persistence

**Scenario 1: Browser Refresh**
- Session state restored from `.sdlc/.session_state.json`
- Claude Code subprocess reconnected (same PID)
- Terminal output buffer restored
- User continues where they left off

**Scenario 2: Browser Closed (Idle Timeout)**
- Claude Code subprocess kept alive for 30 minutes
- Session state saved to disk
- Next session can resume if within timeout window

**Scenario 3: Concurrent Sessions (Future)**
- Multiple browser tabs can share same Claude Code process
- Lock mechanism prevents concurrent command execution
- Output broadcast to all connected sessions

## Communication Layer

### WebSocket Protocol

#### Connection Establishment

```javascript
// Client-side (browser)
const ws = new WebSocket('ws://localhost:8080/ws');

ws.onopen = () => {
  console.log('Connected to SDLC Control Plane');

  // Send initial handshake
  ws.send(JSON.stringify({
    type: 'handshake',
    session_id: localStorage.getItem('session_id') || null,
    user: 'eric.flecher',
    context: {
      viewing_story: 'P0-A2A-F8-000',
      viewing_phase: 'phase-1'
    }
  }));
};

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  handleMessage(message);
};
```

#### Message Types

```python
# Server → Client messages

# 1. Session initialized
{
  "type": "session_init",
  "session_id": "uuid",
  "recommendations": [...],
  "terminal_output": "Welcome to SDLC Control Plane..."
}

# 2. Recommendations updated
{
  "type": "recommendations_update",
  "recommendations": [
    {
      "rank": 1,
      "command": "/implement P0-A2A-F1-001",
      "button_label": "▶️ Start F1-001",
      "rationale": "Next P0 story with no blockers"
    }
  ]
}

# 3. Terminal output
{
  "type": "terminal_output",
  "output": "Starting implementation...\n",
  "timestamp": "2026-01-30T10:15:30Z"
}

# 4. Command completed
{
  "type": "command_complete",
  "command": "/implement P0-A2A-F8-000",
  "exit_code": 0,
  "duration_ms": 45000
}

# 5. Error
{
  "type": "error",
  "error_code": "SUBPROCESS_FAILED",
  "message": "Claude Code subprocess crashed",
  "details": "..."
}
```

```python
# Client → Server messages

# 1. Button click (execute command)
{
  "type": "execute_command",
  "command": "/implement P0-A2A-F1-001",
  "story_id": "P0-A2A-F1-001"
}

# 2. Context update (user viewing different story)
{
  "type": "context_update",
  "user_context": {
    "viewing_story": "P0-A2A-F1-002",
    "viewing_phase": "phase-1"
  }
}

# 3. Heartbeat (keep-alive)
{
  "type": "ping",
  "timestamp": "2026-01-30T10:15:00Z"
}
```

### File-Based State Bridge

**Problem**: Roadmap HTML (static) needs to communicate with Textual app (dynamic)

**Solution**: Shared JSON file as communication bridge

#### Context File: `.sdlc/.context.json`

```json
{
  "user_view": {
    "viewing_story": "P0-A2A-F8-000",
    "viewing_phase": "phase-1",
    "last_updated": "2026-01-30T10:15:00Z"
  },

  "roadmap_state": {
    "selected_story_ids": ["P0-A2A-F8-000", "P0-A2A-F1-001"],
    "filter": "P0",
    "sort": "priority"
  }
}
```

**Workflow**:
1. **Roadmap HTML**: User clicks story card → JavaScript writes to `.sdlc/.context.json`
2. **Textual App**: File watcher detects change → reloads context → regenerates recommendations
3. **Button Bar**: Updates to show actions relevant to selected story

#### File Watcher Implementation

```python
# Server-side (Textual app)
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ContextFileHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith('.context.json'):
            # Reload user context
            context = load_context_file()

            # Regenerate recommendations
            recommendations = recommendation_engine.generate(backlog, context)

            # Update button bar
            update_button_bar(recommendations)

observer = Observer()
observer.schedule(ContextFileHandler(), path='.sdlc/', recursive=False)
observer.start()
```

## Deployment Architecture

(See "Deployment Architecture" section above)

## Session Management

(See "Session Management" section above)

## Communication Layer

(See "Communication Layer" section above)

## Security Considerations

### Authentication

**Development Mode**: No authentication (localhost only)

**Production Mode**: textual-web provides:
- GitHub OAuth integration
- Email-based authentication
- API key authentication for automation

### Command Validation

**Risk**: Button click injecting arbitrary commands into terminal

**Mitigation**:
```python
ALLOWED_COMMANDS = [
    '/implement',
    '/test',
    '/quality',
    '/commit',
    '/help'
]

def validate_command(command: str) -> bool:
    """Only allow SDLC commands, not arbitrary shell."""
    cmd_prefix = command.split()[0]
    return cmd_prefix in ALLOWED_COMMANDS
```

### Input Sanitization

- Commands are templates (e.g., `/implement {story_id}`)
- `story_id` validated against backlog before injection
- No user-supplied freeform text in commands

### Process Isolation

- Claude Code subprocess runs with same privileges as user
- File system access limited to repository directory
- No network access beyond what Claude Code normally allows

## Performance Considerations

### Latency Targets

- **WebSocket roundtrip**: <50ms (localhost), <200ms (remote)
- **Recommendation generation**: <50ms (cached), <200ms (cold start)
- **Terminal output streaming**: Real-time (<10ms per line)
- **File watcher reaction**: <100ms from file change to UI update

### Optimization Strategies

1. **Backlog Caching**: Parse YAML once, cache in memory, invalidate on file change
2. **Recommendation Memoization**: Cache recommendations for same backlog state
3. **Incremental Updates**: Only regenerate affected recommendations on state change
4. **Output Buffering**: Batch terminal output updates (every 50ms) to reduce WebSocket messages

### Resource Management

- **Memory**: Keep terminal output buffer limited (last 10,000 lines)
- **CPU**: File watcher uses inotify (Linux) / FSEvents (macOS) for efficiency
- **Network**: Compress WebSocket messages for large payloads

## Failure Modes and Recovery

### Scenario 1: Claude Code Subprocess Crash

**Detection**: Monitor subprocess PID and exit code

**Recovery**:
1. Display error in terminal widget
2. Offer "Restart Claude Code" button
3. Attempt auto-restart (max 3 retries)
4. Preserve session state for manual recovery

### Scenario 2: WebSocket Disconnection

**Detection**: Missed heartbeat (30s timeout)

**Recovery**:
1. Client auto-reconnect (exponential backoff)
2. Server maintains session state for 5 minutes
3. Reconnect restores terminal output buffer

### Scenario 3: File Watcher Failure

**Detection**: File changes not triggering updates

**Recovery**:
1. Fallback to polling (check files every 5 seconds)
2. Log warning to terminal
3. Suggest restart if polling also fails

## Deployment Checklist

### Development Deployment

- [ ] Install dependencies: `pip install textual watchdog`
- [ ] Implement SDLC Control Plane Textual app (`sdlc_control_plane.py`)
- [ ] Create `.sdlc/.context.json` template
- [ ] Add file watcher for backlog and context files
- [ ] Test with: `textual serve sdlc_control_plane.py`

### Production Deployment (Future)

- [ ] Set up textual-web account
- [ ] Configure authentication (GitHub OAuth)
- [ ] Deploy app: `textual-web --app sdlc_control_plane.py --public`
- [ ] Test multi-user sessions
- [ ] Set up monitoring and error tracking

## Future Enhancements

### Real-Time Collaboration

- **Multi-user sessions**: See what teammates are working on
- **Shared terminal**: Pair programming mode
- **Activity feed**: "Eric started implementing F1-001"

### Advanced State Sync

- **WebSocket for all state**: Replace file-based bridge with WebSocket messages
- **Bi-directional updates**: Textual app can update roadmap HTML in real-time
- **Optimistic UI updates**: Update UI before server confirms

### Mobile Support

- **Responsive Textual UI**: Adapt layout for mobile browsers
- **Touch-optimized buttons**: Larger tap targets
- **Simplified view**: Collapse terminal output on mobile

## References

- [Textual Serve Documentation](https://textual.textualize.io/guide/devtools/#textual-serve)
- [Textual Web](https://github.com/Textualize/textual-web)
- [WebSocket Protocol](https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API)
- [Watchdog File System Monitoring](https://pythonhosted.org/watchdog/)

---

**Deliverable Status**: ✅ Complete
**Acceptance Criterion**: AC3 - Architecture diagrams document Textual-web deployment model, browser ↔ Python communication layer, and session management for Claude Code context preservation
