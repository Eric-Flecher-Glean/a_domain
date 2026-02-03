# 🚀 a_domain Quick Start Guide

## Open Your Developer Portal

```bash
make portal
```

**That's it!** Your browser will open to: **http://localhost:3001**

---

## What You'll See

A beautiful unified home page with:

### 📊 Report Explorer
Browse workflow timeline reports with search and filtering
- **URL**: http://localhost:3000
- **Status**: 🟢 Live

### 🔌 DataOps API
REST API with interactive Swagger documentation
- **URL**: http://localhost:8000/docs
- **Status**: ⚠️ *Install uvicorn to enable*

### 📚 Documentation
Quick links to:
- Product Roadmap
- Architecture
- System Overview
- Coverage Reports

---

## Auto-Start Magic ✨

Services automatically start when you run:
```bash
make backlog-status
make session-start
make governance
# ... any SDLC command!
```

---

## Service Control

```bash
# Start all services
make start-services

# Stop all services
make stop-services

# Open portal
make portal
```

---

## Optional: Install DataOps API

The DataOps API requires Python dependencies:

```bash
# Install with pip
pip install uvicorn fastapi sqlalchemy

# Or with uv (faster)
uv pip install uvicorn fastapi sqlalchemy

# Then restart services
make stop-services
make start-services
```

---

## Troubleshooting

### Services not starting?
```bash
# View logs
cat .logs/portal.log
cat .logs/explorer.log

# Clean restart
make stop-services
rm -f .*.pid
make start-services
```

### Port already in use?
```bash
# Kill processes on ports
lsof -ti:3001 | xargs kill -9
lsof -ti:3000 | xargs kill -9
lsof -ti:8000 | xargs kill -9
```

---

## What's Running?

Check process status:
```bash
# View running services
ps -p $(cat .portal.pid)
ps -p $(cat .explorer.pid)

# View logs in real-time
tail -f .logs/*.log
```

---

## 🎯 Your Development Workflow

1. **Run any SDLC command** → Services auto-start
2. **Open http://localhost:3001** → Beautiful portal
3. **Click service cards** → Explore your UX surfaces
4. **Services stay running** → Ready for next command

**Enjoy!** 🎊

---

## Full Documentation

- **Portal Guide**: `README-PORTAL.md`
- **Explorer Guide**: `README-EXPLORER.md`
- **Technical Summary**: `WEB-SERVICES-SUMMARY.md`
- **Help**: `make help`
