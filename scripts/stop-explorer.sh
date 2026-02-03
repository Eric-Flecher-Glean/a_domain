#!/bin/bash
# Stop the Report Explorer background process

PID_FILE=".explorer.pid"

if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "🛑 Stopping Report Explorer (PID: $PID)..."
        kill "$PID"
        rm -f "$PID_FILE"
        echo "✅ Report Explorer stopped"
    else
        echo "ℹ️  Report Explorer not running"
        rm -f "$PID_FILE"
    fi
else
    echo "ℹ️  Report Explorer not running"
fi
