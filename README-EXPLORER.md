# Report Explorer Auto-Start

The Report Explorer web application now **automatically starts** when you run any SDLC command, providing real-time observability into your development workflow.

## Auto-Start Behavior

The explorer automatically starts in the background when you run:
- `make backlog-next`
- `make backlog-status`
- `make backlog-in-progress`
- `make backlog-blocked`
- `make session-start`
- `make governance`
- `make test-gate`

## Access the Explorer

Once started, the Report Explorer is available at:
**http://localhost:3000**

## Manual Control

### Start manually (foreground):
```bash
make explorer
```

### Stop background process:
```bash
make stop-explorer
```

### Check if running:
```bash
# If running, PID is stored in .explorer.pid
cat .explorer.pid
```

## Logs

Background process logs are stored in:
```
.logs/explorer.log
```

## How It Works

1. **Smart Detection**: Before starting, checks if explorer is already running
2. **Background Mode**: Runs as background process (nohup)
3. **PID Tracking**: Stores process ID in `.explorer.pid`
4. **Auto-Install**: Installs npm dependencies if needed
5. **Silent Operation**: Only shows startup message on first launch

## Benefits

- **Always Available**: Explorer is ready whenever you need it
- **Real-Time Monitoring**: See reports as they're generated
- **Zero Friction**: No need to remember to start it
- **Resource Efficient**: Only one instance runs at a time

## Troubleshooting

### Explorer not starting?
```bash
# Check logs
cat .logs/explorer.log

# Manually install dependencies
make explorer-install

# Try starting manually
make explorer
```

### Port 3000 already in use?
```bash
# Find and kill the process using port 3000
lsof -ti:3000 | xargs kill -9

# Or modify the port in observability/reports/explorer/package.json
```

### Clean restart?
```bash
# Stop explorer
make stop-explorer

# Remove PID file
rm -f .explorer.pid

# Start again
make backlog-status
```
