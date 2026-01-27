# Workflow Report Explorer

A simple web application to browse, search, and explore workflow timeline reports.

## Features

- **Dashboard Overview** - View summary statistics (total runs, success rate, avg duration, errors)
- **Search & Filter** - Search by task description, filter by status and date range
- **Report List** - Browse all reports with key metadata
- **Click to View** - Open any report in a new tab
- **Responsive Design** - Works on desktop, tablet, and mobile
- **Keyboard Shortcuts** - Cmd/Ctrl+R to refresh, / to focus search

## Quick Start

### From Project Root:

```bash
# Install dependencies (first time only)
make explorer-install

# Start the explorer
make explorer
```

The app will open at: **http://localhost:3000**

### Manually:

```bash
cd observability/reports/explorer

# Install dependencies
npm install

# Start server
npm start
```

## Usage

### Browse Reports

The main dashboard shows all generated timeline reports. Each card displays:
- Session ID
- Date and time
- Task description
- Status (success/error)
- Duration
- Quality score (if available)

Click any report to open it in a new tab.

### Search and Filter

- **Search Box**: Search by task description or session ID
- **Date Filter**: Filter by Today, Last 7 days, Last 30 days, or All time
- **Status Filter**: Show All, Success only, or Errors only

### Statistics

The dashboard shows summary statistics:
- **Total Runs**: Number of workflow executions
- **Success Rate**: Percentage of successful runs
- **Avg Duration**: Average execution time
- **Errors**: Number of failed runs

### Keyboard Shortcuts

- `Cmd/Ctrl + R` - Refresh data
- `/` - Focus search input
- `Enter` - Open selected report

## API Endpoints

The explorer provides a REST API:

### GET /api/reports

List all reports with filtering and pagination.

**Query Parameters:**
- `status` - Filter by success/error/all
- `dateRange` - Filter by today/week/month/all
- `search` - Search in task description
- `page` - Page number (default: 1)
- `limit` - Results per page (default: 20)

**Example:**
```bash
curl "http://localhost:3000/api/reports?status=success&dateRange=week&search=prompt"
```

### GET /api/reports/:sessionId

Get detailed metadata for a specific report.

**Example:**
```bash
curl "http://localhost:3000/api/reports/39842164-c4e6-4d3f-8bfd-60dc7cf97eea"
```

### GET /api/stats

Get summary statistics.

**Query Parameters:**
- `dateRange` - Filter stats by date range

**Example:**
```bash
curl "http://localhost:3000/api/stats?dateRange=week"
```

### GET /api/refresh

Force refresh of report cache.

**Example:**
```bash
curl "http://localhost:3000/api/refresh"
```

## Development

### Run with auto-reload:

```bash
npm run dev
```

This uses `nodemon` to automatically restart the server when files change.

### Project Structure

```
explorer/
├── server.js       # Node.js/Express backend
├── index.html      # Main dashboard UI
├── styles.css      # All styles
├── app.js          # Frontend JavaScript
├── package.json    # Dependencies
└── README.md       # This file
```

## Configuration

### Port

Default port is `3000`. Change it by setting the `PORT` environment variable:

```bash
PORT=8080 npm start
```

### Reports Directory

The server looks for reports in `../reports-output/` relative to the explorer directory.

This corresponds to `observability/reports-output/` from the project root.

## Troubleshooting

### No reports found

Make sure you've generated some reports first:

```bash
make xml-prompt-ab TASK="your task"
```

### Port already in use

If port 3000 is taken, set a different port:

```bash
PORT=8080 make explorer
```

Or kill the process using port 3000:

```bash
lsof -ti:3000 | xargs kill
```

### Reports not updating

Click the **🔄 Refresh** button to reload data from disk.

## Future Enhancements

Planned features (see REPORT-EXPLORER-DESIGN.md):

- ✅ Phase 1: Basic List View (DONE)
- ✅ Phase 2: Search & Filter (DONE)
- ✅ Phase 3: Statistics Dashboard (DONE)
- ⏳ Phase 4: Preview Panel (embedded iframe)
- ⏳ Phase 5: Comparison View (side-by-side reports)

## License

MIT
