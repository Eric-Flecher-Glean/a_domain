# F8 Browser-Roadmap Bridge Design

**Story**: P0-A2A-F8-000 - SDLC Control Plane & Interactive Roadmap
**Task**: Task 5 - Browser-Roadmap Bridge Design
**Author**: Claude Code
**Date**: 2026-01-30
**Status**: Draft

## Executive Summary

This document specifies the data flow and communication contract between the static roadmap HTML (client-side JavaScript) and the Textual Control Plane (server-side Python). The bridge enables the Textual app to receive user context (which story is being viewed) and generate contextually relevant recommendations.

**Key Design Decisions**:
- **File-based bridge** for Phase 1 (JSON file shared between processes)
- **WebSocket upgrade path** for Phase 2 (real-time bidirectional communication)
- **Polling with file watcher** for state synchronization
- **Unidirectional data flow**: Roadmap HTML → Context File → Textual App

## Data Flow Diagram

### High-Level Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                        Browser Process                          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Roadmap HTML (docs/roadmaps/roadmap.html)               │  │
│  │                                                           │  │
│  │  JavaScript:                                             │  │
│  │  ┌────────────────────────────────────────────────────┐ │  │
│  │  │  1. User clicks story card (e.g., P0-A2A-F8-000)   │ │  │
│  │  │  2. Extract story context (ID, phase, priority)    │ │  │
│  │  │  3. Write to .sdlc/.context.json                   │ │  │
│  │  └────────────────────────────────────────────────────┘ │  │
│  │                                                           │  │
│  │  ┌────────────────────────────────────────────────────┐ │  │
│  │  │  File System API (or fetch with file: protocol)    │ │  │
│  │  └────────────────────────────────────────────────────┘ │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────┘
                           │
                           │ Write
                           ▼
┌────────────────────────────────────────────────────────────────┐
│                    Shared File System                           │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  .sdlc/.context.json                                     │  │
│  │  {                                                       │  │
│  │    "viewing_story": "P0-A2A-F8-000",                    │  │
│  │    "viewing_phase": "phase-1",                          │  │
│  │    "last_updated": "2026-01-30T10:15:00Z"               │  │
│  │  }                                                       │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────┘
                           │
                           │ Watch (inotify / FSEvents)
                           ▼
┌────────────────────────────────────────────────────────────────┐
│                    Textual App Process                          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  SDLC Control Plane (sdlc_control_plane.py)             │  │
│  │                                                           │  │
│  │  Python:                                                 │  │
│  │  ┌────────────────────────────────────────────────────┐ │  │
│  │  │  1. File watcher detects .context.json change      │ │  │
│  │  │  2. Read and parse new context                     │ │  │
│  │  │  3. Load backlog (IMPLEMENTATION_BACKLOG.yaml)     │ │  │
│  │  │  4. Generate recommendations (context-aware)       │ │  │
│  │  │  5. Update button bar UI                           │ │  │
│  │  └────────────────────────────────────────────────────┘ │  │
│  │                                                           │  │
│  │  ┌────────────────────────────────────────────────────┐ │  │
│  │  │  Watchdog Library (file system events)             │ │  │
│  │  └────────────────────────────────────────────────────┘ │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────┘
```

### Sequence Diagram: User Interaction Flow

```
User          Roadmap HTML       .context.json      Textual App       Claude Code
│                  │                    │                 │                 │
│ Click Story      │                    │                 │                 │
│ "F8-000" ──────► │                    │                 │                 │
│                  │                    │                 │                 │
│                  │ Write context      │                 │                 │
│                  │ ──────────────────►│                 │                 │
│                  │                    │                 │                 │
│                  │                    │ File change     │                 │
│                  │                    │ event ─────────►│                 │
│                  │                    │                 │                 │
│                  │                    │ Read context    │                 │
│                  │                    │ ◄───────────────│                 │
│                  │                    │                 │                 │
│                  │                    │                 │ Load backlog    │
│                  │                    │                 │ (YAML parse)    │
│                  │                    │                 │                 │
│                  │                    │                 │ Generate        │
│                  │                    │                 │ recommendations │
│                  │                    │                 │                 │
│                  │                    │                 │ Update button   │
│                  │                    │                 │ bar UI          │
│                  │                    │                 │                 │
│ View updated     │                    │                 │                 │
│ buttons ◄────────────────────────────────────────────────│                 │
│                  │                    │                 │                 │
│ Click button     │                    │                 │                 │
│ "Continue" ──────────────────────────────────────────────►                 │
│                  │                    │                 │                 │
│                  │                    │                 │ Inject command  │
│                  │                    │                 │ ───────────────►│
│                  │                    │                 │                 │
│                  │                    │                 │ Stream output   │
│                  │                    │                 │ ◄───────────────│
│                  │                    │                 │                 │
│ View terminal    │                    │                 │                 │
│ output ◄─────────────────────────────────────────────────│                 │
│                  │                    │                 │                 │
```

## JS-Python API Contract

### Context File Schema (JSON)

**File Location**: `.sdlc/.context.json`

**Schema Definition**:

```typescript
// TypeScript interface for client-side validation
interface UserContext {
  version: string;              // Schema version (e.g., "1.0")
  timestamp: string;            // ISO 8601 timestamp
  user: string;                 // User identifier (email or username)

  // Primary context (required)
  viewing_story: string | null; // Story ID user is viewing
  viewing_phase: string | null; // Phase ID (e.g., "phase-1")

  // Secondary context (optional)
  selected_stories: string[];   // Multi-select support
  active_filter: {
    priority: string | null;    // "P0", "P1", "P2", "P3"
    status: string | null;      // "not_started", "in_progress", "completed"
    type: string | null;        // "Feature", "Infrastructure", etc.
  };

  // Session metadata
  session_id: string;           // UUID for session tracking
  page_url: string;             // Current page URL
  scroll_position: number;      // For state restoration
}
```

**Example Context File**:

```json
{
  "version": "1.0",
  "timestamp": "2026-01-30T10:15:23.456Z",
  "user": "eric.flecher",

  "viewing_story": "P0-A2A-F8-000",
  "viewing_phase": "phase-1",

  "selected_stories": ["P0-A2A-F8-000"],
  "active_filter": {
    "priority": "P0",
    "status": null,
    "type": null
  },

  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "page_url": "file:///path/to/docs/roadmaps/roadmap.html",
  "scroll_position": 1024
}
```

### JavaScript Implementation (Roadmap HTML)

**File**: `docs/roadmaps/roadmap.html` (embedded script)

```javascript
// Context Manager - Handles writing user context to JSON file
class ContextManager {
  constructor(contextFilePath = '.sdlc/.context.json') {
    this.contextFilePath = contextFilePath;
    this.sessionId = this.getOrCreateSessionId();
    this.debounceTimer = null;
  }

  // Get or create session ID (stored in localStorage)
  getOrCreateSessionId() {
    let sessionId = localStorage.getItem('sdlc_session_id');
    if (!sessionId) {
      sessionId = this.generateUUID();
      localStorage.setItem('sdlc_session_id', sessionId);
    }
    return sessionId;
  }

  generateUUID() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, c => {
      const r = Math.random() * 16 | 0;
      const v = c === 'x' ? r : (r & 0x3 | 0x8);
      return v.toString(16);
    });
  }

  // Write context to file (debounced to avoid excessive writes)
  writeContext(context) {
    // Debounce writes (max 1 per 500ms)
    clearTimeout(this.debounceTimer);
    this.debounceTimer = setTimeout(() => {
      this._writeContextNow(context);
    }, 500);
  }

  async _writeContextNow(context) {
    const fullContext = {
      version: "1.0",
      timestamp: new Date().toISOString(),
      user: this.getUserEmail(), // From metadata or auth
      session_id: this.sessionId,
      page_url: window.location.href,
      scroll_position: window.scrollY,
      ...context
    };

    try {
      // Option 1: Use File System Access API (modern browsers)
      await this.writeViaFileSystemAPI(fullContext);
    } catch (err) {
      console.warn('File System API not available, using fallback');

      // Option 2: Fallback to fetch with file: protocol (requires local server)
      await this.writeViaFetch(fullContext);
    }
  }

  async writeViaFileSystemAPI(context) {
    // Requires user permission (one-time prompt)
    const fileHandle = await window.showSaveFilePicker({
      suggestedName: '.context.json',
      startIn: 'downloads',
      types: [{
        description: 'JSON Context File',
        accept: {'application/json': ['.json']}
      }]
    });

    const writable = await fileHandle.createWritable();
    await writable.write(JSON.stringify(context, null, 2));
    await writable.close();
  }

  async writeViaFetch(context) {
    // Requires local HTTP server with write endpoint
    const response = await fetch('http://localhost:3000/api/context', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(context)
    });

    if (!response.ok) {
      throw new Error(`Failed to write context: ${response.statusText}`);
    }
  }

  getUserEmail() {
    // Extract from document metadata or environment
    return document.querySelector('meta[name="author"]')?.content || 'unknown';
  }
}

// Usage in roadmap HTML event handlers
const contextManager = new ContextManager();

// Event: User clicks story card
document.querySelectorAll('.story-card').forEach(card => {
  card.addEventListener('click', (event) => {
    const storyId = event.currentTarget.dataset.storyId;
    const phase = event.currentTarget.dataset.phase;

    // Write context immediately
    contextManager.writeContext({
      viewing_story: storyId,
      viewing_phase: phase,
      selected_stories: [storyId],
      active_filter: {
        priority: getCurrentFilter(),
        status: null,
        type: null
      }
    });

    // Visual feedback
    highlightStory(storyId);
  });
});

function getCurrentFilter() {
  const filterSelect = document.getElementById('priority-filter');
  return filterSelect ? filterSelect.value : null;
}

function highlightStory(storyId) {
  // Remove previous highlight
  document.querySelectorAll('.story-card').forEach(c => c.classList.remove('highlighted'));

  // Add highlight to selected story
  const card = document.querySelector(`[data-story-id="${storyId}"]`);
  if (card) {
    card.classList.add('highlighted');
  }
}
```

### Python Implementation (Textual App)

**File**: `sdlc_control_plane.py`

```python
import json
import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from typing import Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class UserContext:
    """Parsed user context from .context.json"""
    version: str
    timestamp: datetime
    user: str
    viewing_story: Optional[str]
    viewing_phase: Optional[str]
    selected_stories: list[str]
    active_filter: dict
    session_id: str
    page_url: str
    scroll_position: int


class ContextFileWatcher(FileSystemEventHandler):
    """Watches .sdlc/.context.json for changes and triggers recommendation updates."""

    def __init__(self, app, context_file_path: Path):
        self.app = app
        self.context_file_path = context_file_path
        self.last_modified = 0

    def on_modified(self, event):
        if event.src_path != str(self.context_file_path):
            return

        # Debounce rapid file changes (avoid duplicate processing)
        current_time = time.time()
        if current_time - self.last_modified < 0.5:
            return

        self.last_modified = current_time

        # Read and parse context
        try:
            context = self.read_context()
            self.app.update_context(context)
        except Exception as e:
            self.app.log_error(f"Failed to read context: {e}")

    def read_context(self) -> UserContext:
        """Read and validate context file."""
        with open(self.context_file_path, 'r') as f:
            data = json.load(f)

        # Validate schema version
        if data.get('version') != '1.0':
            raise ValueError(f"Unsupported context schema version: {data.get('version')}")

        return UserContext(
            version=data['version'],
            timestamp=datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00')),
            user=data['user'],
            viewing_story=data.get('viewing_story'),
            viewing_phase=data.get('viewing_phase'),
            selected_stories=data.get('selected_stories', []),
            active_filter=data.get('active_filter', {}),
            session_id=data['session_id'],
            page_url=data['page_url'],
            scroll_position=data.get('scroll_position', 0)
        )


class SDLCControlPlaneApp:
    """Main Textual app with context awareness."""

    def __init__(self):
        self.context_file_path = Path('.sdlc/.context.json')
        self.current_context: Optional[UserContext] = None
        self.file_watcher = None

    def start_file_watcher(self):
        """Start watching context file for changes."""
        handler = ContextFileWatcher(self, self.context_file_path)
        observer = Observer()
        observer.schedule(handler, path=str(self.context_file_path.parent), recursive=False)
        observer.start()
        self.file_watcher = observer

    def update_context(self, context: UserContext):
        """Called when context file changes - regenerate recommendations."""
        self.current_context = context

        # Reload backlog (in case it changed too)
        backlog = self.load_backlog()

        # Generate context-aware recommendations
        recommendations = self.recommendation_engine.generate(
            backlog,
            user_context=context
        )

        # Update button bar UI
        self.button_bar.update_recommendations(recommendations)

        # Log context change
        self.log_info(f"Context updated: viewing {context.viewing_story}")

    def load_backlog(self):
        """Load and parse IMPLEMENTATION_BACKLOG.yaml"""
        # Implementation from Task 2 (recommendation engine)
        pass
```

## Data Flow Diagram

(See "Data Flow Diagram" section above for complete architecture and sequence diagrams)

## JS-Python API Contract

(See "JS-Python API Contract" section above for schema definitions and implementations)

## State Synchronization

### Synchronization Strategy

**Challenge**: Roadmap HTML and Textual app are separate processes with no direct IPC.

**Solution**: File-based communication with file watcher pattern

#### Write-Read Cycle

```
Roadmap HTML (Write)         File System              Textual App (Read)
      │                           │                           │
      │ User clicks story         │                           │
      │                           │                           │
      │ Generate context JSON     │                           │
      │                           │                           │
      │ Write to .context.json ──►│                           │
      │                           │                           │
      │                           │ File modified event ─────►│
      │                           │                           │
      │                           │ Read .context.json ◄──────│
      │                           │                           │
      │                           │                           │ Parse JSON
      │                           │                           │
      │                           │                           │ Update UI
      │                           │                           │ (button bar)
      │                           │                           │
      │ ◄───────────────────────────────────────────────────  │
      │ (User sees updated recommendations in browser)        │
```

### Conflict Resolution

**Scenario**: Rapid clicks on different stories

**Problem**: Multiple writes to `.context.json` in quick succession

**Solution**: Debouncing on both sides

1. **JavaScript (Write Side)**: Debounce writes (max 1 per 500ms)
2. **Python (Read Side)**: Debounce file events (ignore changes within 500ms of last read)

**Code Example** (JavaScript):

```javascript
// Debounce rapid context updates
let debounceTimer = null;

function updateContext(context) {
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(() => {
    writeContextToFile(context);
  }, 500);
}
```

### File Locking

**Problem**: Race condition if both processes access file simultaneously

**Solution**: Atomic writes with temp file + rename

**Python Implementation**:

```python
import tempfile
import os

def write_context_atomic(context: dict, file_path: Path):
    """Write context with atomic rename (no partial reads)."""

    # Write to temp file first
    temp_fd, temp_path = tempfile.mkstemp(dir=file_path.parent, suffix='.tmp')
    try:
        with os.fdopen(temp_fd, 'w') as f:
            json.dump(context, f, indent=2)

        # Atomic rename (replaces old file)
        os.rename(temp_path, file_path)
    except Exception:
        # Clean up temp file on error
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise
```

## Alternative: WebSocket Upgrade Path (Phase 2)

### Why WebSocket?

**Limitations of File-Based Bridge**:
- ⚠️ Latency (file writes + polling/watching)
- ⚠️ No bidirectional communication (Textual app can't push updates to roadmap)
- ⚠️ File system dependencies (won't work on read-only filesystems)

**WebSocket Advantages**:
- ✅ Real-time bidirectional communication
- ✅ Lower latency (<50ms roundtrip)
- ✅ Server can push updates to client (e.g., "Story completed, update roadmap UI")

### WebSocket Architecture

```
Roadmap HTML (Browser)              Textual App (Server)
      │                                     │
      │ WebSocket connection                │
      │ ws://localhost:8080/context ───────►│
      │                                     │
      │ Send context update                 │
      │ {viewing_story: "F8-000"} ─────────►│
      │                                     │
      │                                     │ Generate recommendations
      │                                     │
      │ Receive recommendations             │
      │ ◄───────────────────────────────────│
      │ {recommendations: [...]}            │
      │                                     │
      │ Render buttons in roadmap HTML      │
```

### WebSocket API Contract

**Client → Server Messages**:

```typescript
{
  "type": "context_update",
  "data": {
    "viewing_story": "P0-A2A-F8-000",
    "viewing_phase": "phase-1"
  }
}
```

**Server → Client Messages**:

```typescript
{
  "type": "recommendations",
  "data": {
    "recommendations": [
      {
        "rank": 1,
        "command": "/implement P0-A2A-F8-000",
        "button_label": "⚙️ Continue F8-000",
        "urgency": "high"
      }
    ]
  }
}

{
  "type": "story_updated",
  "data": {
    "story_id": "P0-A2A-F8-000",
    "status": "completed"
  }
}
```

### Migration Path

**Phase 1**: File-based bridge (MVP)
- Simple, no server required for roadmap HTML
- Works offline
- Proof of concept

**Phase 2**: Hybrid (file + WebSocket)
- Roadmap HTML can opt-in to WebSocket for real-time updates
- Fallback to file-based if WebSocket unavailable
- Best of both worlds

**Phase 3**: Full WebSocket
- Remove file-based bridge
- All communication via WebSocket
- Requires running Textual server

## Security Considerations

### File-Based Bridge Security

**Risks**:
- 🔴 Context file readable by any process on system
- 🔴 Malicious process could write fake context

**Mitigations**:
- ✅ File permissions: `chmod 600 .sdlc/.context.json` (owner read/write only)
- ✅ Schema validation: Reject malformed or invalid context
- ✅ Rate limiting: Ignore context updates faster than 100ms

### WebSocket Security (Phase 2)

**Risks**:
- 🔴 CSRF attacks on WebSocket endpoint
- 🔴 Unauthorized clients connecting

**Mitigations**:
- ✅ Origin validation: Check `Origin` header matches expected domain
- ✅ Authentication token: Require session token in WebSocket handshake
- ✅ TLS encryption: Use `wss://` in production (not `ws://`)

## Performance Considerations

### File-Based Bridge Performance

**Benchmarks** (Estimated):

| Operation                  | Latency | Notes                          |
|----------------------------|---------|--------------------------------|
| Write .context.json        | 1-5ms   | Depends on disk speed          |
| File watcher triggers      | 10-50ms | OS-dependent (inotify vs poll) |
| Read and parse JSON        | 1-2ms   | Small file (~1KB)              |
| **Total roundtrip**        | **12-57ms** | Acceptable for UX          |

**Optimization**:
- Cache parsed backlog YAML (avoid re-parsing on every context update)
- Use binary format (MessagePack) instead of JSON for faster parsing

### WebSocket Performance (Phase 2)

**Benchmarks** (Estimated):

| Operation                  | Latency | Notes                       |
|----------------------------|---------|------------------------------|
| WebSocket message send     | 1-2ms   | Localhost                   |
| Server processing          | 5-10ms  | Generate recommendations    |
| WebSocket message receive  | 1-2ms   | Localhost                   |
| **Total roundtrip**        | **7-14ms** | 4x faster than file-based |

## Testing Strategy

### Integration Test: File-Based Bridge

```python
def test_context_file_update_triggers_recommendation_refresh():
    """Verify file watcher detects context changes and updates recommendations."""

    # Setup
    app = SDLCControlPlaneApp()
    app.start_file_watcher()

    # Write context file
    context = {
        "version": "1.0",
        "viewing_story": "P0-A2A-F8-000",
        "timestamp": datetime.now().isoformat()
    }
    write_context_file('.sdlc/.context.json', context)

    # Wait for file watcher to trigger
    time.sleep(0.6)  # Account for debounce

    # Verify app received context update
    assert app.current_context.viewing_story == "P0-A2A-F8-000"

    # Verify recommendations regenerated
    assert len(app.button_bar.recommendations) > 0
    assert any("F8-000" in r.button_label for r in app.button_bar.recommendations)
```

### End-to-End Test

```javascript
// Test in roadmap HTML (browser console)
async function testContextBridge() {
  // Simulate user clicking story card
  const storyCard = document.querySelector('[data-story-id="P0-A2A-F8-000"]');
  storyCard.click();

  // Wait for context write
  await sleep(1000);

  // Verify context file written
  const response = await fetch('http://localhost:3000/api/context');
  const context = await response.json();

  console.assert(context.viewing_story === "P0-A2A-F8-000", "Context not written");

  // Verify Textual app received context (check button bar visually)
  console.log("✅ Context bridge test passed");
}
```

## Future Enhancements

### Bidirectional Data Flow

Current: **Roadmap → Textual** (one-way)

Future: **Roadmap ↔ Textual** (two-way)

**Use Cases**:
- Textual app notifies roadmap when story completes → roadmap updates status indicator
- Textual app highlights currently executing story in roadmap timeline
- Textual app pushes progress updates (e.g., "Task 3/5 complete")

### State Persistence

- Save context across browser sessions (localStorage)
- Restore user's last-viewed story on page reload
- Sync context across multiple browser tabs (BroadcastChannel API)

### Analytics & Telemetry

- Track which stories users click most (identify high-interest work)
- Measure time between context update and button click (UX latency)
- Log recommendation acceptance rate (which suggestions users follow)

## References

- [File System Access API](https://developer.mozilla.org/en-US/docs/Web/API/File_System_Access_API)
- [Watchdog Python Library](https://pythonhosted.org/watchdog/)
- [WebSocket API](https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API)
- [JSON Schema Specification](https://json-schema.org/)

---

**Deliverable Status**: ✅ Complete
**Acceptance Criterion**: AC5 - Data flow documented for roadmap HTML → Textual app integration, including JavaScript-Python bridge contract and backlog state synchronization mechanism
