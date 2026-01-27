# Workflow Timeline Reports

Visual HTML timeline reports generated from OpenTelemetry observability data.

## Overview

After each workflow execution, a beautiful timeline report is automatically generated showing:
- **Horizontal timeline** with execution steps
- **Visual agent/stage rows** with duration blocks
- **Status indicators** (success ✓, warning ⚠, error ✗)
- **Metrics panel** with summary statistics
- **Bottleneck identification** highlighting slowest stages
- **Quality progression** for validation workflows

## Report Structure

```
┌──────────────────────────────────────────────────────────────────┐
│                   WORKFLOW EXECUTION TIMELINE                     │
│  Task: Create a sentiment analysis prompt                        │
│  Session ID: abc123 | Duration: 1.5s | Status: SUCCESS           │
├────────────────────────────────────────────────┬─────────────────┤
│ Timeline (horizontal swimlanes)                │ Metrics Panel   │
│                                                │                 │
│ 0s     0.5s    1.0s    1.5s                    │ Total: 1.5s     │
│ │       │       │       │                      │ Steps: 2        │
│ ├─────────────┐                                │ Success: 100%   │
│ │ Generator   │ 0.5s ✓                         │                 │
│ └─────────────┘                                │ Bottleneck:     │
│         ├─────────┐                            │ Generator       │
│         │Validator│ 0.3s ✓                     │ (0.5s, 66%)     │
│         └─────────┘                            │                 │
│                                                │ [Duration Chart]│
└────────────────────────────────────────────────┴─────────────────┘
```

## Automatic Generation

Reports are automatically generated after workflow execution:

```bash
# Run a workflow
make xml-prompt-ab TASK="Create sentiment analysis prompt"

# Report automatically generated at:
# observability/reports-output/{session-id}-timeline.html
```

## Manual Generation

Generate reports using the CLI tool:

```bash
# Generate report for latest session
node observability/reports/generate-report.js --latest

# Generate report for specific session ID
node observability/reports/generate-report.js --session-id abc123-def456

# Generate reports for all sessions today
node observability/reports/generate-report.js --all

# Generate for specific date
node observability/reports/generate-report.js --date 2026-01-26
```

## Viewing Reports

Open reports in your browser:

```bash
# View latest report
make view-latest-report

# View specific report
open observability/reports-output/{session-id}-timeline.html
```

## Report Contents

### 1. Timeline Visualization

- **Time axis**: Shows elapsed time with markers
- **Stage rows**: One row per stage/agent execution
- **Duration blocks**: Colored rectangles showing execution time
- **Status icons**: Visual indicators of success/failure
- **Event markers**: Important milestones (validation, feedback, etc.)

### 2. Metrics Panel

- **Total Duration**: Overall execution time
- **Number of Steps**: Count of execution stages
- **Success Rate**: Percentage of successful validations
- **Bottleneck**: Slowest stage identification
- **Duration Chart**: Bar chart comparing stage durations
- **Quality Progression**: Quality scores across attempts (if applicable)

### 3. Details Section

- **Status Breakdown**: Count by status type
- **Average Step Duration**: Mean execution time
- **Workflow Pattern**: Pattern type (staged-validation, sequential, etc.)
- **Number of Attempts**: Retry count (if applicable)

## Color Coding

### Status Colors

- **Green** (#10b981): Success ✓
- **Yellow** (#f59e0b): Warning ⚠
- **Red** (#ef4444): Error ✗
- **Blue** (#3b82f6): Informational ℹ

### Stage Type Colors

- **Purple** (#8b5cf6): Generation stages
- **Green** (#10b981): Validation stages
- **Yellow** (#f59e0b): Feedback stages
- **Indigo** (#6366f1): Attempt groups

## Architecture

### Data Flow

```
Workflow Execution
  ↓
OpenTelemetry Instrumentation
  ↓
JSONL Files (traces, events, logs)
  ↓
Timeline Report Generator
  ├─ Data Aggregator (reads JSONL)
  ├─ Timeline Builder (structures data)
  ├─ Metrics Calculator (computes stats)
  └─ HTML Renderer (generates report)
  ↓
HTML Report (saved to reports-output/)
```

### Components

1. **`data-aggregator.js`**: Reads and correlates JSONL observability data
2. **`timeline-builder.js`**: Builds hierarchical timeline structure
3. **`metrics-calculator.js`**: Computes summary metrics and statistics
4. **`svg-timeline.js`**: Generates SVG visualization
5. **`html-renderer.js`**: Renders complete HTML document
6. **`timeline-generator.js`**: Main orchestrator

## Customization

### Adjusting Visual Style

Edit colors in `svg-timeline.js`:

```javascript
this.colors = {
  success: '#10b981',  // Change success color
  warning: '#f59e0b',
  error: '#ef4444',
  // ...
};
```

### Adjusting Layout

Edit dimensions in `svg-timeline.js`:

```javascript
this.config = {
  width: 1200,        // Total SVG width
  rowHeight: 60,      // Height per row
  headerHeight: 80,   // Time axis height
  labelWidth: 250,    // Width of labels
  indentWidth: 20,    // Indentation per level
};
```

### Adding Custom Metrics

Extend `metrics-calculator.js`:

```javascript
calculateMetrics(timeline) {
  return {
    // Existing metrics...
    customMetric: this.calculateCustomMetric(timeline)
  };
}

calculateCustomMetric(timeline) {
  // Your calculation logic
}
```

## Workflow Pattern Support

The report generator automatically adapts to different workflow patterns:

### Staged Validation Pattern

- Groups attempts together
- Shows feedback cycles with correlation
- Highlights quality score progression
- Emphasizes validation results

### Sequential Pattern (Future)

- Shows linear progression
- Emphasizes stage ordering
- No attempt grouping

### Parallel Pattern (Future)

- Shows concurrent stages side-by-side
- Uses color-coded lanes
- Highlights synchronization points

## Troubleshooting

### No trace data found

**Problem**: `No trace data found for session {id} on {date}`

**Solution**: Ensure the session ID is correct and the date matches when the workflow was run.

```bash
# Check available sessions
ls observability/traces/
cat observability/traces/traces_2026-01-26.jsonl | grep session.id
```

### Report shows no rows

**Problem**: Report generates but timeline is empty

**Solution**: Ensure spans have parentSpanId set correctly and are being captured:

```bash
# Check span structure
cat observability/traces/traces_2026-01-26.jsonl | jq 'select(.attributes["session.id"] == "your-session-id")'
```

### SVG not rendering

**Problem**: Timeline SVG appears broken or missing

**Solution**: Check browser console for errors. Ensure SVG syntax is valid.

## Examples

### Example 1: Basic Prompt Generation

```bash
node observability/reports/generate-report.js --latest
# Opens report showing:
# - PromptGeneration: 0.5s ✓
# - PromptValidation: 0.3s ✓
# Total: 0.8s, Success Rate: 100%
```

### Example 2: Multi-Attempt Validation

```bash
node observability/reports/generate-report.js --session-id abc123
# Opens report showing:
# - Attempt #1
#   - Generator: 0.5s ✓
#   - Validator: 0.3s ⚠ (Score: 75)
# - Feedback: 0.2s
# - Attempt #2
#   - Generator: 0.6s ✓
#   - Validator: 0.4s ✓ (Score: 95)
# Total: 2.0s, Success Rate: 50%
```

## Future Enhancements

- [ ] Real-time reports with WebSocket updates
- [ ] Comparison view (side-by-side sessions)
- [ ] Analytics dashboard (aggregate view)
- [ ] Export to PDF, PNG, Markdown
- [ ] Interactive filtering (by status, agent, duration)
- [ ] Full-text search across events and logs
- [ ] Shareable report URLs
- [ ] Dark mode theme
- [ ] User annotations and notes
- [ ] Integration with Slack/email notifications

## Contributing

When adding new workflow patterns:

1. Create a pattern-specific timeline builder in `timeline-builder.js`
2. Register the pattern in `detectWorkflowPattern()`
3. Update the README with the new pattern description
4. Add test cases for the new pattern

## License

Internal tool - part of the workflow orchestration system.
