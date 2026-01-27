# Design Quick Reference Guide
**Date**: January 26, 2026
**For**: UX Delta Review P0 Stories

---

## 📁 Document Structure

### Main Documents
1. **UX-DELTA-REVIEW-2026-01-26.md** (Comprehensive UX Analysis)
   - User personas
   - Journey maps
   - Heuristic evaluation
   - User stories
   - Design recommendations

2. **UX-DELTA-NEXT-STEPS.md** (Implementation Roadmap)
   - Top 5 P0 stories prioritized
   - ROI calculations
   - Week-by-week plan
   - Success metrics

3. **UX-WIREFRAMES-DESIGNS.md** (This Document - Design Specs) ✅
   - Wireframes for all 5 stories
   - Interaction diagrams
   - Component specifications
   - Implementation code samples

---

## 🎨 Design Summary by Story

### Story DV-1: View Generated Prompt Inline
**Page Location**: Lines 11-330

**Key Wireframes**:
- Before/After comparison (current vs. proposed)
- Tabbed modal interface (Overview | Prompt XML | Trace Data)
- Syntax-highlighted XML display
- Copy/Download/Open actions

**Key Components**:
- Modal container (900px max-width)
- Tab navigation (3 tabs)
- XML container with scroll (400px max-height)
- Action buttons (Primary/Secondary/Tertiary styles)

**Interaction Flow**: Click block → Modal opens → Switch to XML tab → View/Copy prompt

**Implementation Priority**: 🔥🔥🔥🔥🔥 HIGHEST

---

### Story DV-2: Show Input Task Prominently
**Page Location**: Lines 332-535

**Key Wireframes**:
- Header layout (before/after)
- Task truncation for long text
- Expandable task details modal
- Tooltip for overflow text

**Key Components**:
- Task description container (left border, background)
- Typography hierarchy (18px, weight 500)
- Tooltip styling (dark theme)
- Info icon interaction

**Interaction Flow**: Task displays → Hover for full text → Click (ⓘ) for details

**Implementation Priority**: 🔥🔥🔥🔥 VERY HIGH (Quick win)

---

### Story DV-3: Link Validation Feedback to Prompt Sections
**Page Location**: Lines 537-850

**Key Wireframes**:
- Clickable feedback cards (before/after)
- Severity indicators (⚠️ critical, ℹ️ info)
- Highlighted XML sections (yellow/red boxes)
- Template suggestions in highlights
- Quality score breakdown

**Key Components**:
- Feedback item cards (clickable, color-coded)
- XML highlight boxes (yellow = missing, red = critical)
- Template suggestion blocks
- Score visualization bars

**Interaction Flow**: Click feedback → Tab switches → XML highlights → Auto-scroll to issue

**Implementation Priority**: 🔥🔥🔥🔥 HIGH

---

### Story CD-1: Compare Attempts Side-by-Side
**Page Location**: Lines 852-1137

**Key Wireframes**:
- Entry point banner (multiple attempts detected)
- Split-screen timeline comparison
- Prompt diff view (left vs. right)
- Diff statistics summary
- Synchronized scrolling

**Key Components**:
- Comparison container (2-column grid)
- Diff highlighting (green=added, red=removed, yellow=missing)
- Quality score delta visualization
- Sync toggle controls

**Interaction Flow**: Detect attempts → Show banner → Click compare → Split-screen loads → View diff

**Implementation Priority**: 🔥🔥🔥 MEDIUM-HIGH

---

### Story QA-1: Copy Prompt to Clipboard
**Page Location**: Lines 1139-1420

**Key Wireframes**:
- Button states (default, copying, success, error)
- Toast notification (alternative approach)
- State transitions timeline

**Key Components**:
- Copy button (3 states with animations)
- Toast notification (optional)
- Icon handling
- Error fallback UI

**Interaction Flow**: Click copy → Copying state → Success (2s) → Return to default

**Implementation Priority**: 🔥🔥 MEDIUM (Easy win, complements DV-1)

---

## 📐 Component Library

### Colors
```
Primary:    #3b82f6 (Blue)
Success:    #10b981 (Green)
Warning:    #f59e0b (Orange)
Error:      #ef4444 (Red)
Info:       #6366f1 (Indigo)

Generation: #8b5cf6 (Purple)
Validation: #10b981 (Green)
Feedback:   #f59e0b (Orange)

Text Dark:  #111827, #374151
Text Gray:  #6b7280, #9ca3af
Border:     #d1d5db, #e5e7eb
Background: #f9fafb, #ffffff
```

### Typography Scale
```
H1 (Page Title):     28px, weight 700
H2 (Section):        20px, weight 600
H3 (Subsection):     16px, weight 600
Task Description:    18px, weight 500  ← NEW
Body Text:           14px, weight 400
Small Text:          12px, weight 400
Code/Monospace:      13px, Fira Code
```

### Spacing System
```
xs:  4px
sm:  8px
md:  12px
lg:  16px
xl:  24px
2xl: 32px
3xl: 48px
```

### Border Radius
```
Small:  4px
Medium: 6px
Large:  8px
XL:     12px
```

### Shadows
```
Small:  0 1px 3px rgba(0,0,0,0.1)
Medium: 0 4px 6px rgba(0,0,0,0.1)
Large:  0 10px 15px rgba(0,0,0,0.3)
```

---

## 🔄 State Transitions

### Modal States
```
CLOSED → LOADING → OVERVIEW_TAB → PROMPT_XML_TAB → XML_VIEWING → COPIED
   ↑                                    ↓
   └────────────── CLOSED ←─────────────┘
```

### Button States
```
DEFAULT → COPYING → SUCCESS → (2s timeout) → DEFAULT
                  ↘ ERROR → (3s timeout) → DEFAULT
```

### Comparison Mode
```
TIMELINE_VIEW → COMPARISON_BANNER → SPLIT_SCREEN → PROMPT_DIFF → EXIT
      ↑                                                              ↓
      └──────────────────────────────────────────────────────────────┘
```

---

## 🎯 Implementation Checklist

### Phase 1: DV-1 + DV-2 + QA-1 (Week 1)

**DV-1: View Prompt Inline**
- [ ] Add tabs to modal HTML
- [ ] Load output file content
- [ ] Implement Prism.js syntax highlighting
- [ ] Add scrollable container (max-height: 400px)
- [ ] Create button group (Copy/Download/Open)
- [ ] Test with large files (>10 KB)

**DV-2: Show Task Prominently**
- [ ] Add task container to header
- [ ] Implement truncation logic (80 chars)
- [ ] Add tooltip for long tasks
- [ ] Style with left border accent
- [ ] Make clickable for details (optional)

**QA-1: Copy to Clipboard**
- [ ] Implement navigator.clipboard.writeText()
- [ ] Add button state transitions
- [ ] Create toast notification (optional)
- [ ] Add fallback for old browsers
- [ ] Test clipboard permissions
- [ ] Add ARIA announcements

---

### Phase 2: DV-3 + CD-1 (Weeks 2-3)

**DV-3: Link Feedback to Sections**
- [ ] Parse validation feedback
- [ ] Map feedback to XML sections
- [ ] Implement click handlers
- [ ] Add highlight rendering
- [ ] Create template suggestions
- [ ] Implement auto-scroll
- [ ] Add quality score breakdown

**CD-1: Compare Attempts**
- [ ] Detect multiple attempts
- [ ] Create split-screen layout
- [ ] Implement diff algorithm
- [ ] Add synchronized scrolling
- [ ] Create diff legend
- [ ] Add comparison statistics
- [ ] Implement responsive mobile view

---

## 📱 Responsive Breakpoints

```
Mobile:     < 768px   (Stack vertical, simplified)
Tablet:     768-1199px (Side-by-side, smaller fonts)
Desktop:    ≥ 1200px  (Full features, optimal layout)
```

### Responsive Adjustments
- **DV-1**: Mobile uses smaller font (11px monospace)
- **DV-2**: Mobile truncates task at 50 chars
- **CD-1**: Mobile shows tabs instead of split-screen
- **QA-1**: Mobile buttons stack vertically

---

## 🧪 Testing Matrix

### Browser Support
- [ ] Chrome 90+ (Primary)
- [ ] Firefox 88+ (Primary)
- [ ] Safari 14+ (Primary)
- [ ] Edge 90+ (Secondary)
- [ ] Mobile Safari iOS 14+ (Secondary)
- [ ] Chrome Mobile Android (Secondary)

### Feature Detection
- [ ] Clipboard API (navigator.clipboard)
- [ ] CSS Grid support
- [ ] Flexbox support
- [ ] Smooth scrolling
- [ ] ViewBox SVG support

### Accessibility
- [ ] Screen reader (NVDA/VoiceOver)
- [ ] Keyboard navigation only
- [ ] Color contrast (WCAG AA)
- [ ] Focus indicators
- [ ] ARIA labels

---

## 🚀 Quick Start Guide

### To implement DV-1 (highest priority):

1. **Read the wireframes** (Lines 11-330)
2. **Copy component specs** (Lines 200-280)
3. **Follow interaction diagram** (Line 160-195)
4. **Use code samples** (Embedded in wireframes)
5. **Test checklist** (Browser compatibility)

### Minimal 4-hour implementation:
1. Add `outputContent` to TIMELINE_DATA
2. Create "Prompt XML" section in modal
3. Add syntax highlighting CSS
4. Implement copy button
5. Test and deploy

**Result**: 80% of value, 20% of effort

---

## 📚 Additional Resources

### External Libraries
- **Syntax Highlighting**: Prism.js or Highlight.js
- **Diff Algorithm**: diff-match-patch or jsdiff
- **Icons**: Unicode emoji (no library needed)

### Design Tools
- Figma template: (Future: export wireframes to Figma)
- Component storybook: (Future: Storybook documentation)

### Documentation
- UX Metrics Dashboard: (Future: track improvement metrics)
- User Testing Results: (Future: record user feedback)

---

## 💡 Pro Tips

1. **Start with DV-1**: Highest impact, unlocks other features
2. **Use browser DevTools**: Test responsive layouts easily
3. **Implement progressively**: Ship DV-1 → DV-2 → QA-1 → DV-3 → CD-1
4. **Test with real data**: Use actual workflow failures
5. **Get user feedback early**: Show DV-1 prototype to 2-3 engineers
6. **Measure metrics**: Track time-to-view-prompt before/after

---

## 🔗 Cross-References

- **UX Review**: See UX-DELTA-REVIEW-2026-01-26.md
- **Next Steps**: See UX-DELTA-NEXT-STEPS.md
- **Implementation**: See UX-IMPROVEMENTS-IMPLEMENTED.md
- **Original Review**: See UX-REVIEW-2026-01-26.md

---

**Document Version**: 1.0
**Last Updated**: January 26, 2026
**Status**: ✅ Ready for Implementation
