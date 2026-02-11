# Web Navigation & Information Hierarchy Architecture

**Feature ID:** P0-UI-F9000
**Version:** 1.0.0
**Status:** Architecture Complete
**Last Updated:** 2026-02-11

---

## Executive Summary

This document defines the information architecture, navigation hierarchy, and URL structure for the a_domain web-based platform. It establishes a unified navigation system supporting role-based views, progressive feature disclosure, and consistent user experience across 7+ existing pages and 7+ planned features.

### Key Decisions

- **Navigation Model:** Hybrid (role-based primary nav + contextual breadcrumbs)
- **URL Pattern:** Service-based clean URLs (`/{category}/{feature}/{detail?}`)
- **Feature Visibility:** Progressive disclosure based on story completion status
- **Responsive Strategy:** Hybrid (mobile-friendly ops, desktop-primary analysis)
- **Role Support:** 4 roles (Developer, PM, Stakeholder, Ops)

---

## Table of Contents

1. [Information Architecture](#information-architecture)
2. [Navigation Hierarchy](#navigation-hierarchy)
3. [URL Structure](#url-structure)
4. [Sitemap](#sitemap)
5. [Role-Based Access](#role-based-access)
6. [Page Inventory](#page-inventory)
7. [Navigation Patterns](#navigation-patterns)
8. [Information Scent](#information-scent)
9. [Wayfinding Mechanisms](#wayfinding-mechanisms)
10. [Design Rationale](#design-rationale)

---

## 1. Information Architecture

### 1.1 High-Level Structure

```
a_domain Platform
├── Operations (Ops)
│   ├── Testing & Validation
│   ├── Monitoring & Reports
│   └── System Health
├── Planning
│   ├── Product Roadmap
│   ├── Story Management
│   └── Backlog
├── Metrics & Analytics
│   ├── Documentation Coverage
│   ├── Timeline Reports
│   └── Velocity Tracking
├── Documentation
│   ├── Architecture Docs
│   ├── API Documentation
│   └── User Guides
└── A2A Platform (Future)
    ├── Journey Orchestration
    ├── Dataset Discovery
    ├── Flow Builder
    └── Knowledge Workspace
```

### 1.2 Information Categories

| Category | Purpose | Primary Users | Depth |
|----------|---------|---------------|-------|
| **Operations** | Real-time operational tasks | Developers, Ops | 2-3 levels |
| **Planning** | Product planning and roadmap | PMs, Stakeholders | 3-4 levels |
| **Metrics** | Analytics and reporting | All roles | 2-3 levels |
| **Documentation** | Reference and guides | All roles | 2-4 levels |
| **A2A Platform** | Advanced agent features | Developers, PMs | 3-5 levels |

### 1.3 Content Types

1. **Dashboards** - Real-time operational interfaces (Testing, Monitoring)
2. **Visualizations** - Complex data displays (Roadmap timeline, Coverage reports)
3. **Detail Pages** - Deep-dive content (Story pages, Documentation)
4. **Portals** - Entry points and aggregators (Developer Portal)
5. **APIs** - Programmatic interfaces (DataOps API, Swagger)

---

## 2. Navigation Hierarchy

### 2.1 Primary Navigation (Role-Based)

#### Developer Role
```
Primary Nav: [Ops] [Docs] [API]
├── Ops
│   ├── Testing Dashboard
│   └── Monitoring
├── Docs
│   ├── Architecture
│   └── Guides
└── API
    ├── DataOps API (Swagger)
    └── ReDoc
```

#### PM Role
```
Primary Nav: [Planning] [Metrics]
├── Planning
│   ├── Roadmap
│   ├── Stories
│   └── Backlog
└── Metrics
    ├── Coverage
    └── Velocity
```

#### Stakeholder Role
```
Primary Nav: [Planning] [Metrics]
├── Planning
│   └── Roadmap (high-level view)
└── Metrics
    ├── Coverage
    └── Progress
```

#### Ops Role
```
Primary Nav: [Ops] [Metrics]
├── Ops
│   ├── Testing
│   ├── Monitoring
│   └── Health
└── Metrics
    └── Timeline
```

### 2.2 Secondary Navigation (Contextual)

- **Breadcrumbs** - Show current location and path (all pages except home)
- **Quick Actions** - Context-sensitive shortcuts (header menu)
- **Related Links** - Cross-references within content (sidebars)
- **Footer Links** - Global utilities and documentation

### 2.3 Navigation Depth Guidelines

| Level | Description | Example | Max Depth |
|-------|-------------|---------|-----------|
| 1 | Category | `/planning` | N/A |
| 2 | Feature | `/planning/roadmap` | All pages |
| 3 | Detail | `/planning/stories/P0-UI-F9000` | Most pages |
| 4 | Sub-detail | `/planning/stories/P0-UI-F9000/tasks` | Limited |
| 5+ | Deep detail | Avoid | Exceptional |

**Rule:** Keep navigation ≤ 3 clicks from home to any page.

---

## 3. URL Structure

### 3.1 URL Pattern

**Format:** `/{category}/{feature}/{detail?}/{sub-detail?}`

- **Category:** ops, planning, metrics, docs, api, a2a
- **Feature:** Specific service or page type
- **Detail:** Resource ID or sub-page (optional)
- **Sub-detail:** Nested resource (rare, avoid when possible)

### 3.2 URL Examples

#### Current Pages (Migrated URLs)

| Old URL | New URL | Type |
|---------|---------|------|
| `/tests-dashboard` | `/ops/testing` | Dashboard |
| `/web-portal/tests-dashboard.html` | `/ops/testing` | Dashboard |
| `/observability/reports/explorer/index.html` | `/ops/monitoring` | Dashboard |
| `/docs/roadmaps/roadmap.html` | `/planning/roadmap` | Visualization |
| `/docs/roadmaps/stories/P0-UI-F9000.html` | `/planning/stories/P0-UI-F9000` | Detail |
| `/docs/reports/documentation-coverage.html` | `/metrics/coverage` | Report |
| `/web-portal/index.html` | `/` | Portal |

#### Planned Features (Future URLs)

| Feature | URL | Story ID |
|---------|-----|----------|
| SDLC Control Plane | `/planning/control-plane` | P0-A2A-F8000 |
| Document Registry | `/docs/registry` | P0-DOCS-005 |
| Journey Dashboard | `/a2a/journey` | P0-A2A-F1001 |
| Dataset Discovery | `/a2a/datasets` | P0-A2A-F2001 |
| Flow Builder | `/a2a/flow-builder` | P0-A2A-F3001 |
| Knowledge Workspace | `/a2a/workspace` | P0-A2A-F5001 |
| Ceremony Scheduler | `/a2a/ceremonies` | P0-A2A-F6001 |

### 3.3 URL Conventions

1. **Lowercase only** - `/ops/testing` (not `/Ops/Testing`)
2. **Hyphens for multi-word** - `/flow-builder` (not `/flowBuilder` or `/flow_builder`)
3. **No file extensions** - `/roadmap` (not `/roadmap.html`)
4. **Plural for collections** - `/stories` (not `/story`)
5. **Singular for resources** - `/stories/:id` (not `/stories/:ids`)
6. **IDs preserve format** - `/stories/P0-UI-F9000` (preserve case and hyphens)

### 3.4 Query Parameters

Use query params for filtering, sorting, search:

- `/planning/roadmap?phase=1&priority=P0` - Filter roadmap
- `/ops/testing?suite=integration` - Filter test suite
- `/metrics/coverage?view=summary` - Change view mode
- `/docs?q=navigation` - Search documentation

**Rule:** State-changing actions use query params, resource identity uses path.

### 3.5 URL Redirects (Migration)

All old URLs redirect with **HTTP 301** (permanent redirect):

```
/tests-dashboard → 301 → /ops/testing
/docs/roadmaps/roadmap.html → 301 → /planning/roadmap
```

**Implementation:** Server-side redirect configuration or client-side routing.

---

## 4. Sitemap

### 4.1 Complete Sitemap (Current + Planned)

```
/ (Developer Portal)
│
├── /ops (Operations)
│   ├── /ops/testing (Testing Dashboard) ✅ LIVE
│   ├── /ops/monitoring (Report Explorer) ✅ LIVE
│   └── /ops/health (System Health) [PLANNED]
│
├── /planning (Planning & Roadmap)
│   ├── /planning/roadmap (Product Roadmap) ✅ LIVE
│   ├── /planning/stories (Story List) [PLANNED]
│   ├── /planning/stories/:story_id (Story Detail) ✅ LIVE (71 pages)
│   ├── /planning/backlog (Backlog View) [PLANNED]
│   └── /planning/control-plane (SDLC Control Plane) 🚧 IN PROGRESS (P0-A2A-F8000)
│
├── /metrics (Metrics & Reports)
│   ├── /metrics/coverage (Documentation Coverage) ✅ LIVE
│   ├── /metrics/timeline/:report_id (Timeline Report) ✅ LIVE (multiple)
│   └── /metrics/velocity (Team Velocity) [PLANNED]
│
├── /docs (Documentation)
│   ├── /docs/architecture (Architecture Docs) ✅ LIVE
│   ├── /docs/system-overview (System Overview) ✅ LIVE
│   ├── /docs/index (Documentation Index) ✅ LIVE
│   └── /docs/registry (Document Registry) 🚧 IN PROGRESS (P0-DOCS-005)
│
├── /api (API Endpoints)
│   ├── /api/docs (DataOps API - Swagger) ✅ LIVE (port 8000)
│   └── /api/redoc (DataOps API - ReDoc) ✅ LIVE (port 8000)
│
└── /a2a (Agent-to-Agent Platform)
    ├── /a2a/journey (Journey Orchestration) [PLANNED] (P0-A2A-F1001)
    ├── /a2a/datasets (Dataset Discovery) [PLANNED] (P0-A2A-F2001)
    ├── /a2a/flow-builder (Visual Flow Builder) [PLANNED] (P0-A2A-F3001)
    ├── /a2a/workspace (Knowledge Workspace) [PLANNED] (P0-A2A-F5001)
    └── /a2a/ceremonies (Team Ceremonies) [PLANNED] (P0-A2A-F6001)
```

**Legend:**
- ✅ LIVE - Currently available
- 🚧 IN PROGRESS - P0 story completed, implementation in progress
- [PLANNED] - Not started, visible in roadmap only

### 4.2 XML Sitemap Structure

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <!-- Current Live Pages -->
  <url>
    <loc>https://a-domain.local/</loc>
    <priority>1.0</priority>
    <changefreq>daily</changefreq>
  </url>
  <url>
    <loc>https://a-domain.local/ops/testing</loc>
    <priority>0.9</priority>
    <changefreq>hourly</changefreq>
  </url>
  <url>
    <loc>https://a-domain.local/planning/roadmap</loc>
    <priority>0.9</priority>
    <changefreq>daily</changefreq>
  </url>
  <!-- ... additional URLs ... -->
</urlset>
```

---

## 5. Role-Based Access

### 5.1 Role Definitions

| Role | Primary Tasks | Nav Access | Landing Page |
|------|---------------|------------|--------------|
| **Developer** | Testing, API integration, implementation | Ops, Docs, API | `/ops/testing` |
| **PM** | Planning, roadmap, backlog management | Planning, Metrics | `/planning/roadmap` |
| **Stakeholder** | Progress visibility, high-level oversight | Planning, Metrics | `/planning/roadmap` |
| **Ops** | System health, monitoring, testing | Ops, Metrics | `/ops/monitoring` |

### 5.2 Navigation Visibility Matrix

| Page/Feature | Developer | PM | Stakeholder | Ops |
|--------------|-----------|----|-----------|----|
| **Developer Portal** | ✅ | ✅ | ✅ | ✅ |
| Testing Dashboard | ✅ | ❌ | ❌ | ✅ |
| Report Explorer | ✅ | ✅ | ❌ | ✅ |
| Product Roadmap | ✅ | ✅ | ✅ | ❌ |
| Story Pages | ✅ | ✅ | ❌ | ❌ |
| Coverage Reports | ✅ | ✅ | ✅ | ✅ |
| Timeline Reports | ✅ | ❌ | ❌ | ✅ |
| DataOps API | ✅ | ❌ | ❌ | ❌ |
| **Status Bar** | ✅ | ❌ | ❌ | ✅ |

**Note:** All roles can access all pages via direct URL, but navigation only shows role-relevant links.

### 5.3 Progressive Disclosure Rules

Feature visibility based on story status:

```yaml
Visibility Rules:
  not_started:
    nav_link: false
    roadmap: true
    badge: null
    action: Visible in roadmap only

  p0_completed:
    nav_link: true
    roadmap: true
    badge: "🚧 Coming Soon" | "🧪 Beta"
    action: Show in nav with badge, link to roadmap or stub

  implemented:
    nav_link: true
    roadmap: true
    badge: null
    action: Full access, no badge
```

**Example:**
- **P0-A2A-F8000** (SDLC Control Plane) - P0 completed → Show with "🚧 Coming Soon" badge
- **P0-A2A-F1001** (Journey Dashboard) - Not started → Roadmap only, no nav link
- **Testing Dashboard** - Implemented → Full access, no badge

---

## 6. Page Inventory

### 6.1 Current Live Pages (7 core + 71 generated)

| ID | Page | URL | Port | Technology | Responsive |
|----|------|-----|------|------------|------------|
| 1 | Developer Portal | `/` | Root | HTML/CSS/JS | Mobile-friendly |
| 2 | Testing Dashboard | `/ops/testing` | 3001 | WebSocket | Mobile-friendly |
| 3 | Report Explorer | `/ops/monitoring` | 3000 | Express.js | Desktop-primary |
| 4 | Product Roadmap | `/planning/roadmap` | Static | SVG/JS | Desktop-only |
| 5 | Story Pages (×71) | `/planning/stories/:id` | Static | HTML | Desktop-primary |
| 6 | Coverage Report | `/metrics/coverage` | Static | HTML | Desktop-primary |
| 7 | Timeline Reports | `/metrics/timeline/:id` | Static | SVG/Canvas | Desktop-only |

### 6.2 Planned Features (7 pages)

| ID | Feature | URL | Story | Status | Priority |
|----|---------|-----|-------|--------|----------|
| 8 | SDLC Control Plane | `/planning/control-plane` | P0-A2A-F8000 | In Progress | P0 |
| 9 | Document Registry | `/docs/registry` | P0-DOCS-005 | Planned | P1 |
| 10 | Journey Dashboard | `/a2a/journey` | P0-A2A-F1001 | Planned | P0 |
| 11 | Dataset Discovery | `/a2a/datasets` | P0-A2A-F2001 | Planned | P0 |
| 12 | Flow Builder | `/a2a/flow-builder` | P0-A2A-F3001 | Planned | P1 |
| 13 | Knowledge Workspace | `/a2a/workspace` | P0-A2A-F5001 | Planned | P1 |
| 14 | Ceremony Scheduler | `/a2a/ceremonies` | P0-A2A-F6001 | Planned | P1 |

**Total:** 85 pages (7 core + 71 stories + 7 planned)

---

## 7. Navigation Patterns

### 7.1 Primary Navigation Pattern

**Type:** Horizontal tabs in header (role-based)

```
[a_domain Logo] [Dev | Planning | Ops | Metrics | Docs] [Actions] [Help] [Role ▼]
```

**Behavior:**
- Tabs filter based on selected role
- Active tab highlighted with underline
- Clicking tab shows dropdown submenu (if applicable)
- Mobile: Collapses to hamburger menu

### 7.2 Breadcrumb Pattern

**Type:** Hierarchical path (auto-generated from URL)

```
Home > Planning > Stories > P0-UI-F9000
```

**Behavior:**
- Each segment clickable except current page
- Separator: " > "
- Max 5 levels, truncate middle with "..."
- Mobile: Collapse to "< Back" button

### 7.3 Quick Actions Pattern

**Type:** Dropdown menu from header icon

```
⚡ Quick Actions
  🧪 Run Tests
  📊 Latest Report
  🗺️ View Roadmap
  📖 Documentation
```

**Behavior:**
- Actions filter based on role
- Click outside to close
- Keyboard: Escape to dismiss
- Each action = direct navigation or command execution

### 7.4 Status Indicator Pattern

**Type:** Sub-header bar with service health

```
🟢 Testing  🟢 Reports  🟢 API     All Systems Operational
```

**Behavior:**
- Auto-refresh every 10s
- Click indicator → navigate to service
- Hover → show last check time
- Visible to Developer and Ops roles only

---

## 8. Information Scent

### 8.1 Label Clarity

**Principle:** Labels must clearly indicate destination content.

| Good Labels | Poor Labels | Rationale |
|-------------|-------------|-----------|
| "Testing Dashboard" | "Dashboard" | Specific purpose clear |
| "Product Roadmap" | "Planning" | Differentiates from backlog |
| "Documentation Coverage" | "Docs" | Specifies type of doc page |
| "Story P0-UI-F9000" | "Story Details" | Unique identifier visible |

### 8.2 Progressive Disclosure Signals

**Badges communicate feature state:**

- **🚧 Coming Soon** - Feature planned, not implemented
- **🧪 Beta** - Feature functional but experimental
- **✨ New** - Recently added feature
- **No badge** - Stable, fully implemented

### 8.3 Contextual Hints

- **Breadcrumbs** - Show location in hierarchy
- **Page titles** - Match nav labels for consistency
- **URLs** - Reflect content structure (information scent in URL)
- **Icons** - Supplement labels with visual cues

---

## 9. Wayfinding Mechanisms

### 9.1 Orientation Mechanisms

1. **Logo/Home Link** - Always top-left, always clickable
2. **Breadcrumbs** - "You are here" indicator
3. **Active Tab** - Highlight current section
4. **Page Title** - Reinforces location
5. **URL** - Reflects hierarchy

### 9.2 Navigation Aids

1. **Persistent Header** - Sticky navigation at top
2. **Role Indicator** - Shows active role (👤 Developer)
3. **Status Bar** - Contextual system state
4. **Quick Actions** - Frequent task shortcuts
5. **Footer Links** - Global utilities always accessible

### 9.3 Search & Discovery (Phase 2)

**Current:** No search (navigate via structure)
**Future:** Global search box in header

```
[🔍 Search across docs, stories, and pages...]
```

**Scope:** Documentation, story IDs, page titles, content snippets

---

## 10. Design Rationale

### 10.1 Why Hybrid Navigation?

**Decision:** Combine role-based primary nav with contextual breadcrumbs

**Rationale:**
- **Role-based** reduces clutter for focused workflows
- **Breadcrumbs** essential for deep story/report navigation
- **Hybrid** supports both quick access and exploration
- Matches mental models: roles = tasks, breadcrumbs = location

**Alternatives Considered:**
- ❌ Flat navigation - Too many items, overwhelming
- ❌ Pure hierarchical - Slow for frequent tasks
- ❌ Search-first - Requires knowing what to search for

### 10.2 Why Service-Based URLs?

**Decision:** `/{category}/{feature}` pattern

**Rationale:**
- **Logical grouping** by function (ops, planning, metrics)
- **Scalable** - easy to add new categories
- **SEO-friendly** - descriptive paths
- **Memorable** - structure reflects mental model

**Alternatives Considered:**
- ❌ Feature-based (A2A-centric) - Excludes existing ops/planning pages
- ❌ Keep current - Inconsistent, hard to extend
- ❌ Flat structure - No hierarchy, URL explosion

### 10.3 Why Progressive Disclosure?

**Decision:** Hide planned features from nav until P0 completed

**Rationale:**
- **Manage expectations** - users don't expect incomplete features
- **Prevent frustration** - no broken links or "coming soon" dead ends
- **Roadmap as roadmap** - planned work visible in roadmap, not nav
- **TDD philosophy** - don't expose what doesn't work

**Alternatives Considered:**
- ❌ Show all with badges - Cluttered, confusing
- ❌ Hide completely - Lack of visibility into future
- ✅ **Chosen approach** - Roadmap shows future, nav shows present

### 10.4 Why Role-Based Navigation?

**Decision:** Filter navigation by user role

**Rationale:**
- **Reduce cognitive load** - only show relevant sections
- **Improve task efficiency** - fewer distractions
- **Support diverse users** - developers ≠ stakeholders
- **Foundation for auth** - easy to extend to permissions

**Alternatives Considered:**
- ❌ Single nav for all - Information overload
- ❌ User customization - Too much choice, configuration burden
- ✅ **Chosen approach** - Predefined roles, easy switching

### 10.5 Why Hybrid Responsive Strategy?

**Decision:** Mobile-friendly ops, desktop-primary analysis

**Rationale:**
- **Usage patterns** - monitoring on-the-go, deep work at desk
- **Pragmatic** - complex visualizations need screen space
- **Resource-efficient** - prioritize mobile for high-value pages
- **User expectations** - developers expect desktop tools

**Alternatives Considered:**
- ❌ Mobile-first all - Timeline viz impossible on mobile
- ❌ Desktop-only - Ops can't check tests remotely
- ✅ **Chosen approach** - Hybrid based on page purpose

---

## Appendix A: URL Migration Mapping

Complete mapping of old URLs to new clean URLs:

```yaml
url_migrations:
  # Portal
  /web-portal/index.html: /
  /index.html: /

  # Operations
  /tests-dashboard: /ops/testing
  /web-portal/tests-dashboard.html: /ops/testing
  /observability/reports/explorer/index.html: /ops/monitoring

  # Planning
  /docs/roadmaps/roadmap.html: /planning/roadmap
  /docs/roadmaps/stories/: /planning/stories/
  /docs/roadmaps/stories/P0-*.html: /planning/stories/P0-*
  /docs/roadmaps/stories/P1-*.html: /planning/stories/P1-*
  /docs/roadmaps/stories/P2-*.html: /planning/stories/P2-*

  # Metrics
  /docs/reports/documentation-coverage.html: /metrics/coverage
  /observability/reports-output/*-timeline.html: /metrics/timeline/*

  # Documentation
  /ARCHITECTURE-SUMMARY.md: /docs/architecture
  /SYSTEM-OVERVIEW.md: /docs/system-overview
  /DOCUMENTATION-INDEX.md: /docs/index

  # API
  http://localhost:8000/docs: /api/docs
  http://localhost:8000/redoc: /api/redoc
```

---

## Appendix B: Navigation Configuration Schema

```yaml
# config/navigation-config.yaml

navigation:
  roles:
    developer:
      sections: [ops, docs, api]
      landing: /ops/testing
      quick_actions:
        - label: Run Tests
          action: navigate /ops/testing
        - label: Latest Report
          action: navigate /ops/monitoring

    pm:
      sections: [planning, metrics]
      landing: /planning/roadmap
      quick_actions:
        - label: View Roadmap
          action: navigate /planning/roadmap
        - label: Coverage Report
          action: navigate /metrics/coverage

    stakeholder:
      sections: [planning, metrics]
      landing: /planning/roadmap
      quick_actions:
        - label: View Roadmap
          action: navigate /planning/roadmap

    ops:
      sections: [ops, metrics]
      landing: /ops/monitoring
      quick_actions:
        - label: System Health
          action: show status detail
        - label: Monitoring
          action: navigate /ops/monitoring

  routes:
    - path: /
      component: DeveloperPortal
      title: a_domain Developer Portal
      roles: [all]

    - path: /ops/testing
      component: TestingDashboard
      title: Testing Dashboard
      roles: [developer, ops]
      responsive: mobile-friendly

    - path: /planning/roadmap
      component: RoadmapViewer
      title: Product Roadmap
      roles: [developer, pm, stakeholder]
      responsive: desktop-only

    # ... additional routes ...

  feature_flags:
    sdlc_control_plane:
      enabled: false
      status: in_progress
      badge: coming_soon
      story_id: P0-A2A-F8000

    # ... additional flags ...
```

---

## Document Metadata

**Authors:** Requirements Chat Session (P0-UI-F9000)
**Reviewers:** TBD
**Approval Status:** Pending
**Related Documents:**
- `output/requirements/ui-navigation-requirements.yaml`
- `output/figma/ui-navigation-design.yaml`
- `output/ui/page-inventory.yaml`

**Change History:**
- 2026-02-11: Initial architecture document created
