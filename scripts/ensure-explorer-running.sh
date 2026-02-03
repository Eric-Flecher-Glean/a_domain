#!/bin/bash
# Ensure Report Explorer is running in the background

EXPLORER_DIR="observability/reports/explorer"
PID_FILE=".explorer.pid"
LOG_FILE=".logs/explorer.log"

# Create logs directory if it doesn't exist
mkdir -p .logs

# Function to check if explorer is running
is_running() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            return 0  # Running
        else
            rm -f "$PID_FILE"
            return 1  # Not running
        fi
    fi
    return 1  # Not running
}

# Function to start explorer
start_explorer() {
    echo "🚀 Starting Report Explorer in background..."

    # Install dependencies if needed
    if [ ! -d "$EXPLORER_DIR/node_modules" ]; then
        echo "📦 Installing explorer dependencies..."
        cd "$EXPLORER_DIR" && npm install --silent > /dev/null 2>&1
        cd - > /dev/null
    fi

    # Start explorer in background
    cd "$EXPLORER_DIR"
    nohup npm start > "../../../$LOG_FILE" 2>&1 &
    EXPLORER_PID=$!
    cd - > /dev/null

    # Save PID
    echo "$EXPLORER_PID" > "$PID_FILE"

    # Wait a moment for server to start
    sleep 2

    echo "✅ Report Explorer running at http://localhost:3000 (PID: $EXPLORER_PID)"
    echo "📋 Logs: $LOG_FILE"
}

# Main logic
if is_running; then
    # Already running, do nothing (silent)
    exit 0
else
    start_explorer
fi
