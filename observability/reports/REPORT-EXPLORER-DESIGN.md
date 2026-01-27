# Report Explorer - Design Specification
**Date**: January 26, 2026
**Purpose**: Simple web app to browse, search, and explore workflow timeline reports

---

## Overview

A lightweight web application that provides a dashboard to:
- Browse all generated timeline reports
- Search and filter by date, status, task
- View summary statistics
- Quick preview reports
- Compare multiple reports side-by-side

---

## User Stories

### US-1: Browse All Reports
**As a** developer debugging workflows
**I want to** see a list of all my timeline reports
**So that** I can quickly find the session I'm looking for

**Acceptance Criteria:**
- [ ] Grid/list view of all reports
- [ ] Shows session ID, date, task, status, duration
- [ ] Sorted by date (newest first)
- [ ] Click to open full report in new tab

### US-2: Search and Filter
**As a** developer
**I want to** search reports by task description or filter by status
**So that** I can narrow down to relevant sessions

**Acceptance Criteria:**
- [ ] Search box filters by task text
- [ ] Filter by status (success, error, all)
- [ ] Filter by date range
- [ ] Shows result count

### US-3: View Statistics
**As a** team lead
**I want to** see summary statistics across all workflows
**So that** I can understand system health

**Acceptance Criteria:**
- [ ] Total runs today/week/all-time
- [ ] Success rate percentage
- [ ] Average duration
- [ ] Error distribution

### US-4: Quick Preview
**As a** developer
**I want to** preview a report without leaving the explorer
**So that** I can quickly check if it's the one I need

**Acceptance Criteria:**
- [ ] Hover shows tooltip with basic info
- [ ] Click shows preview panel with embedded iframe
- [ ] Preview shows task, timeline, and errors

### US-5: Compare Reports (Future)
**As a** developer iterating on prompts
**I want to** compare two reports side-by-side
**So that** I can see what changed between attempts

**Acceptance Criteria:**
- [ ] Select multiple reports (checkbox)
- [ ] "Compare" button opens comparison view
- [ ] Side-by-side timelines
- [ ] Diff of prompts

---

## Wireframes

### Main Dashboard View

```
┌─────────────────────────────────────────────────────────────────┐
│  📊 Workflow Report Explorer                    [Refresh] [⚙️]  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  📈 Summary Statistics                                          │
│  ┌──────────────┬──────────────┬──────────────┬──────────────┐ │
│  │ Total Runs   │ Success Rate │ Avg Duration │ Errors       │ │
│  │     47       │    89%       │   1.2s       │    5         │ │
│  └──────────────┴──────────────┴──────────────┴──────────────┘ │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ 🔍 Search: [___________________]  📅 [Last 7 days ▼]    │  │
│  │                                                           │  │
│  │ Status: [All ▼] [Success] [Error]        47 results     │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Session ID              Date         Task        Status │   │
│  ├─────────────────────────────────────────────────────────┤   │
│  │ 39842164-c4e6...  Jan 26, 7:02 PM  Test UX... ✅ 807ms │ →  │
│  │ aecafbc7-4bf1...  Jan 27, 12:01 AM Test UX... ✅ 806ms │ →  │
│  │ f892c4a1-3d5e...  Jan 26, 3:35 PM  Summariz... ✅ 1.2s │ →  │
│  │ 2b4d89c0-1a7f...  Jan 26, 2:15 PM  Code rev... ❌ 503ms │ →  │
│  │ ...                                                      │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  [< Prev]  Page 1 of 3  [Next >]                               │
└─────────────────────────────────────────────────────────────────┘
```

### Report Preview Panel

```
┌─────────────────────────────────────────────────────────────────┐
│  Report List (Left)               │  Preview (Right)            │
├───────────────────────────────────┼─────────────────────────────┤
│                                   │  Session: 39842164-c4e6...  │
│  [✓] 39842164... Jan 26 ✅       │  Date: Jan 26, 2026 7:02 PM │
│  [ ] aecafbc7... Jan 27 ✅       │  Status: ✅ Success         │
│  [ ] f892c4a1... Jan 26 ✅       │  Duration: 807ms            │
│  [ ] 2b4d89c0... Jan 26 ❌       │                             │
│                                   │  Task:                      │
│  [Compare Selected (1)]           │  "Test the new timeline UX  │
│                                   │   improvements"             │
│                                   │                             │
│                                   │  Timeline:                  │
│                                   │  ┌─────────────────────┐   │
│                                   │  │ [Embedded iframe]   │   │
│                                   │  │ Shows actual        │   │
│                                   │  │ timeline report     │   │
│                                   │  └─────────────────────┘   │
│                                   │                             │
│                                   │  [Open Full Report]         │
└───────────────────────────────────┴─────────────────────────────┘
```

### Comparison View (Future - Story CD-1)

```
┌─────────────────────────────────────────────────────────────────┐
│  Compare: 39842164 vs aecafbc7                    [Close] [×]   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Attempt #1 (Failed)              │  Attempt #2 (Success)      │
│  ────────────────────────────────┼────────────────────────────  │
│  Date: Jan 26, 6:00 PM            │  Date: Jan 27, 12:01 AM    │
│  Status: ❌ Error                 │  Status: ✅ Success        │
│  Duration: 503ms                  │  Duration: 806ms           │
│  Score: 62/100                    │  Score: 100/100 (+38)      │
│                                   │                             │
│  Timeline:                        │  Timeline:                  │
│  [Generation] ──────── 250ms      │  [Generation] ──────── 504ms│
│  [Validation] ── 253ms ❌         │  [Validation] ─── 302ms ✅ │
│                                   │                             │
│  Prompt Diff:                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ - Missing <examples> section                             │  │
│  │ + Added 3 examples                                       │  │
│  │ ~ Modified output_format structure                       │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Component Specifications

### 1. Statistics Cards

```css
.stat-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  color: #111827;
}

.stat-label {
  font-size: 14px;
  color: #6b7280;
  margin-top: 4px;
}

.stat-trend {
  font-size: 12px;
  color: #10b981; /* green for positive */
  margin-top: 8px;
}
```

### 2. Report List Item

```css
.report-item {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  padding: 16px;
  margin-bottom: 12px;
  cursor: pointer;
  transition: all 200ms ease;
}

.report-item:hover {
  border-color: #3b82f6;
  box-shadow: 0 4px 8px rgba(59, 130, 246, 0.1);
}

.report-item.selected {
  background: #eff6ff;
  border-color: #3b82f6;
}

.status-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.status-success {
  background: #d1fae5;
  color: #065f46;
}

.status-error {
  background: #fee2e2;
  color: #991b1b;
}
```

### 3. Search and Filter Bar

```html
<div class="filter-bar">
  <div class="search-input">
    <input
      type="text"
      placeholder="Search by task description..."
      id="searchInput"
    />
  </div>

  <div class="filter-group">
    <label>Date Range:</label>
    <select id="dateFilter">
      <option value="today">Today</option>
      <option value="week">Last 7 days</option>
      <option value="month">Last 30 days</option>
      <option value="all">All time</option>
    </select>
  </div>

  <div class="filter-group">
    <label>Status:</label>
    <button class="filter-btn active" data-status="all">All</button>
    <button class="filter-btn" data-status="success">✅ Success</button>
    <button class="filter-btn" data-status="error">❌ Error</button>
  </div>

  <div class="result-count">
    <span id="resultCount">47</span> results
  </div>
</div>
```

---

## Data Model

### Report Metadata (extracted from HTML/JSON)

```json
{
  "sessionId": "39842164-c4e6-4d3f-8bfd-60dc7cf97eea",
  "date": "2026-01-26T19:02:38.649Z",
  "task": "Test the new timeline UX improvements",
  "status": "success",
  "duration": 807,
  "workflowId": "prompt-generation",
  "attempts": 1,
  "qualityScore": 100,
  "errors": [],
  "stages": [
    {
      "name": "Prompt Generation",
      "duration": 502,
      "status": "success"
    },
    {
      "name": "Prompt Validation",
      "duration": 304,
      "status": "success"
    }
  ],
  "outputPath": "output/ab-prompt.xml",
  "reportPath": "observability/reports-output/39842164-c4e6-4d3f-8bfd-60dc7cf97eea-timeline.html"
}
```

---

## API Endpoints (Node.js Backend)

### GET /api/reports
List all reports with metadata

**Query Parameters:**
- `status`: filter by success/error/all
- `dateFrom`: start date (ISO 8601)
- `dateTo`: end date (ISO 8601)
- `search`: search in task description
- `page`: pagination (default: 1)
- `limit`: results per page (default: 20)

**Response:**
```json
{
  "total": 47,
  "page": 1,
  "limit": 20,
  "reports": [
    {
      "sessionId": "39842164-c4e6-4d3f-8bfd-60dc7cf97eea",
      "date": "2026-01-26T19:02:38.649Z",
      "task": "Test the new timeline UX improvements",
      "status": "success",
      "duration": 807,
      "qualityScore": 100,
      "reportUrl": "/reports/39842164-c4e6-4d3f-8bfd-60dc7cf97eea-timeline.html"
    }
  ]
}
```

### GET /api/reports/:sessionId
Get detailed report metadata

**Response:**
```json
{
  "sessionId": "39842164-c4e6-4d3f-8bfd-60dc7cf97eea",
  "date": "2026-01-26T19:02:38.649Z",
  "task": "Test the new timeline UX improvements",
  "status": "success",
  "duration": 807,
  "stages": [...],
  "errors": [],
  "metadata": {...}
}
```

### GET /api/stats
Get summary statistics

**Response:**
```json
{
  "totalRuns": 47,
  "successRate": 89,
  "avgDuration": 1203,
  "totalErrors": 5,
  "runsByDay": {
    "2026-01-26": 12,
    "2026-01-27": 3
  },
  "errorsByType": {
    "ValidationError": 3,
    "GenerationError": 2
  }
}
```

### GET /api/compare/:sessionId1/:sessionId2
Compare two reports (Future - Story CD-1)

**Response:**
```json
{
  "report1": {...},
  "report2": {...},
  "diff": {
    "durationDelta": 303,
    "scoreDelta": 38,
    "promptDiff": "...",
    "stageComparison": [...]
  }
}
```

---

## Technology Stack

### Frontend
- **HTML5/CSS3**: Modern, semantic markup
- **Vanilla JavaScript**: No frameworks (keep it simple)
- **CSS Grid/Flexbox**: Responsive layout
- **Fetch API**: AJAX requests to backend

### Backend
- **Node.js**: JavaScript runtime
- **Express.js**: Web framework
- **File System**: Read HTML/JSON reports
- **JSDOM** (optional): Parse HTML for metadata extraction

### Build/Run
```bash
# No build step needed
npm install
npm start

# Opens browser to http://localhost:3000
```

---

## File Structure

```
observability/
├── reports/
│   ├── explorer/                    # NEW: Report Explorer App
│   │   ├── index.html              # Main dashboard
│   │   ├── styles.css              # All styles
│   │   ├── app.js                  # Frontend logic
│   │   └── server.js               # Node.js backend
│   ├── reports-output/             # Existing timeline reports
│   └── ...
```

---

## Implementation Plan

### Phase 1: Basic List View (2-3 hours)
**Goal**: Show all reports in a simple list

**Tasks:**
- [ ] Create `explorer/` directory structure
- [ ] Build Node.js server with Express
- [ ] Scan `reports-output/` for HTML files
- [ ] Extract metadata from HTML (parse TIMELINE_DATA)
- [ ] Create `/api/reports` endpoint
- [ ] Build frontend list view
- [ ] Add click to open report in new tab

**Deliverable**: Working report browser with basic list

### Phase 2: Search & Filter (1-2 hours)
**Goal**: Enable searching and filtering

**Tasks:**
- [ ] Add search input (filter by task)
- [ ] Add status filter buttons
- [ ] Add date range filter
- [ ] Implement client-side filtering
- [ ] Show result count
- [ ] Add pagination

**Deliverable**: Searchable, filterable report list

### Phase 3: Statistics Dashboard (1-2 hours)
**Goal**: Show summary stats

**Tasks:**
- [ ] Create `/api/stats` endpoint
- [ ] Calculate total runs, success rate, avg duration
- [ ] Build stat cards UI
- [ ] Add charts (optional - Chart.js)

**Deliverable**: Dashboard with statistics

### Phase 4: Preview Panel (2-3 hours)
**Goal**: Preview reports without leaving explorer

**Tasks:**
- [ ] Add preview panel to UI
- [ ] Embed report in iframe
- [ ] Show metadata in preview header
- [ ] Add "Open Full Report" button

**Deliverable**: In-app report preview

### Phase 5: Comparison (Future - Story CD-1)
**Goal**: Compare two reports side-by-side

**Tasks:**
- [ ] Add checkbox selection
- [ ] Create comparison view
- [ ] Implement prompt diff algorithm
- [ ] Show timeline comparison
- [ ] Calculate deltas

**Deliverable**: Side-by-side report comparison

---

## Minimal Viable Product (4 hours)

### Must Have:
✅ List all reports with metadata
✅ Search by task description
✅ Filter by status (success/error)
✅ Click to open full report
✅ Basic statistics (total, success rate)

### Nice to Have:
⭐ Date range filtering
⭐ Pagination
⭐ Preview panel
⭐ Responsive mobile layout

### Future:
🔮 Comparison view
🔮 Charts/graphs
🔮 Export to CSV
🔮 Real-time updates (WebSocket)

---

## Design Tokens

### Colors
```css
:root {
  --color-primary: #3b82f6;
  --color-success: #10b981;
  --color-error: #ef4444;
  --color-warning: #f59e0b;

  --color-bg: #f9fafb;
  --color-surface: #ffffff;
  --color-border: #e5e7eb;

  --color-text-primary: #111827;
  --color-text-secondary: #6b7280;
}
```

### Typography
```css
--font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
--font-size-xs: 12px;
--font-size-sm: 14px;
--font-size-base: 16px;
--font-size-lg: 18px;
--font-size-xl: 24px;
--font-size-2xl: 32px;
```

### Spacing
```css
--space-xs: 4px;
--space-sm: 8px;
--space-md: 16px;
--space-lg: 24px;
--space-xl: 32px;
--space-2xl: 48px;
```

---

## Accessibility Requirements

- [ ] Keyboard navigation (Tab, Enter, Escape)
- [ ] ARIA labels for all interactive elements
- [ ] Focus indicators
- [ ] Screen reader announcements
- [ ] High contrast mode support
- [ ] Responsive text (rem units)

---

## Next Steps

1. **Review this design** with user
2. **Get approval** on scope and approach
3. **Start Phase 1** (Basic List View)
4. **Test with real data**
5. **Iterate** based on feedback

---

**Questions?**
- Should we include charts/graphs?
- Do you want real-time updates when new reports are generated?
- Should comparison view be part of MVP or Phase 2?

**Document Version**: 1.0
**Last Updated**: January 26, 2026
**Status**: ✅ Ready for Implementation
