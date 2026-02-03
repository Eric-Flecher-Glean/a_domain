# a_domain Developer Portal

A unified home page providing access to all web UX surfaces in the a_domain project.

## Overview

The Developer Portal is your central hub for accessing:
- **Report Explorer** - Browse workflow timeline reports
- **DataOps API** - REST API with Swagger UI documentation
- **Static Documentation** - Architecture, roadmaps, and coverage reports

## Quick Start

### Automatic (Recommended)

All web services **auto-start** when you run any SDLC command:

```bash
make backlog-status    # Auto-starts all services
```

Then open: **http://localhost:3001**

### Manual Start

```bash
# Start all services
make ensure-services

# Or individually
node web-portal/server.js           # Portal at :3001
cd observability/reports/explorer && npm start  # Explorer at :3000
uvicorn sdlc_framework.dataops.api.app:app --port 8000  # API at :8000
```

## Services

### 1. Developer Portal (Port 3001)
**URL**: http://localhost:3001

The unified landing page with:
- Service cards for all web apps
- Real-time service status indicators
- Quick links to documentation
- Beautiful, responsive design

**Technology**: Node.js static server

---

### 2. Report Explorer (Port 3000)
**URL**: http://localhost:3000

Interactive dashboard for browsing workflow reports:
- Search and filter reports
- View execution metrics
- Timeline visualization
- Success/failure tracking

**Technology**: Express.js + Vanilla JavaScript

---

### 3. DataOps API (Port 8000)
**URLs**:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- API Root: http://localhost:8000

REST API for dataset and template management:
- Dataset lifecycle operations
- Template discovery and recommendations
- OAuth 2.0 authentication
- Full OpenAPI documentation

**Technology**: FastAPI + Uvicorn

---

## Auto-Start Configuration

Web services automatically start when running:
- `make backlog-next`
- `make backlog-status`
- `make backlog-in-progress`
- `make backlog-blocked`
- `make session-start`
- `make governance`
- `make test-gate`
- `make register-artifacts`

## Manual Control

### Start all services:
```bash
make ensure-services
```

### Stop all services:
```bash
make stop-services
```

### Check running services:
```bash
# Check PID files
ls -la .*.pid

# Check logs
ls -la .logs/
```

## Architecture

```
a_domain/
├── web-portal/                    # Developer Portal (Port 3001)
│   ├── index.html                 # Landing page
│   └── server.js                  # Static file server
├── observability/
│   └── reports/
│       ├── explorer/              # Report Explorer (Port 3000)
│       │   ├── server.js
│       │   ├── app.js
│       │   └── index.html
│       └── reports-output/        # Generated timeline reports
└── sdlc_framework/
    └── dataops/
        └── api/                   # DataOps API (Port 8000)
            ├── app.py
            └── routes/
```

## Process Management

### PID Files (track running processes)
- `.portal.pid` - Developer Portal process ID
- `.explorer.pid` - Report Explorer process ID
- `.dataops.pid` - DataOps API process ID

### Log Files (debugging)
- `.logs/portal.log` - Portal server logs
- `.logs/explorer.log` - Explorer server logs
- `.logs/dataops.log` - DataOps API logs

## Service Health Checks

The Developer Portal includes real-time status indicators that:
- Check service availability every 10 seconds
- Show green dot when service is reachable
- Show red dot when service is down
- Automatically detect service restarts

## Troubleshooting

### Services not starting?

```bash
# Check logs
cat .logs/portal.log
cat .logs/explorer.log
cat .logs/dataops.log

# Manual restart
make stop-services
make ensure-services
```

### Port already in use?

```bash
# Find and kill process on port 3001
lsof -ti:3001 | xargs kill -9

# Find and kill process on port 3000
lsof -ti:3000 | xargs kill -9

# Find and kill process on port 8000
lsof -ti:8000 | xargs kill -9
```

### Clean restart?

```bash
# Stop everything
make stop-services

# Remove PID files
rm -f .*.pid

# Remove logs (optional)
rm -f .logs/*.log

# Start fresh
make ensure-services
```

### Explorer dependencies missing?

```bash
cd observability/reports/explorer
npm install
cd ../../..
```

### DataOps API not available?

```bash
# Check if uvicorn is installed
which uvicorn

# Install if needed
pip install uvicorn fastapi sqlalchemy

# Or with uv
uv pip install uvicorn fastapi sqlalchemy
```

## Features

### Developer Portal Features
- 🎨 Beautiful gradient design
- 📱 Fully responsive (mobile, tablet, desktop)
- 🔴/🟢 Real-time service status
- 🔗 Direct links to all services
- 📚 Quick access to documentation
- ⚡ Fast, lightweight static server

### Integration Features
- 🚀 Auto-starts with SDLC commands
- 🔄 Smart duplicate detection (won't restart running services)
- 📝 Comprehensive logging
- 🛑 Clean shutdown handling
- 💾 PID file management

## Development

### Adding a New Service

1. Add service card to `web-portal/index.html`
2. Add start logic to `scripts/ensure-all-services.sh`
3. Add stop logic to `scripts/stop-all-services.sh`
4. Update this documentation

### Customizing the Portal

Edit `web-portal/index.html`:
- Modify styles in `<style>` section
- Add/remove service cards
- Update documentation links
- Change color scheme

### Changing Ports

**Portal**: Edit `web-portal/server.js`
```javascript
const PORT = process.env.PORT || 3001;  // Change here
```

**Explorer**: Edit `observability/reports/explorer/server.js`
```javascript
const PORT = process.env.PORT || 3000;  // Change here
```

**DataOps API**: Edit startup command in `scripts/ensure-all-services.sh`
```bash
uvicorn "$DATAOPS_MODULE" --host 0.0.0.0 --port 8000  # Change port here
```

## Best Practices

1. **Always use `make ensure-services`** rather than starting services manually
2. **Check logs** in `.logs/` directory when debugging
3. **Use `make stop-services`** before shutting down your machine
4. **Keep the portal open** in a browser tab for quick service access
5. **Run SDLC commands** to automatically ensure services are running

## Links

- [Explorer Documentation](../README-EXPLORER.md)
- [DataOps API Demo](../sdlc_framework/dataops/api/demo_api.py)
- [Architecture Summary](../ARCHITECTURE-SUMMARY.md)
- [Project README](../README.md)
