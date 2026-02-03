#!/bin/bash
# Ensure all web services are running in the background

set -e

EXPLORER_DIR="observability/reports/explorer"
PORTAL_DIR="web-portal"
DATAOPS_MODULE="sdlc_framework.dataops.api.app:app"

# PID files
EXPLORER_PID=".explorer.pid"
PORTAL_PID=".portal.pid"
DATAOPS_PID=".dataops.pid"

# Log files
LOG_DIR=".logs"
mkdir -p "$LOG_DIR"
EXPLORER_LOG="$LOG_DIR/explorer.log"
PORTAL_LOG="$LOG_DIR/portal.log"
DATAOPS_LOG="$LOG_DIR/dataops.log"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if process is running
is_running() {
    local pid_file=$1
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if ps -p "$pid" > /dev/null 2>&1; then
            return 0  # Running
        else
            rm -f "$pid_file"
            return 1  # Not running
        fi
    fi
    return 1  # Not running
}

# Function to start Report Explorer
start_explorer() {
    if is_running "$EXPLORER_PID"; then
        return 0  # Already running
    fi

    echo -e "${YELLOW}🚀 Starting Report Explorer...${NC}"

    # Install dependencies if needed
    if [ ! -d "$EXPLORER_DIR/node_modules" ]; then
        echo "   📦 Installing dependencies..."
        cd "$EXPLORER_DIR" && npm install --silent > /dev/null 2>&1
        cd - > /dev/null
    fi

    # Get absolute path to logs
    EXPLORER_LOG_FULL=$(pwd)/"$EXPLORER_LOG"
    EXPLORER_PID_FULL=$(pwd)/"$EXPLORER_PID"

    # Start in background
    cd "$EXPLORER_DIR"
    nohup npm start > "$EXPLORER_LOG_FULL" 2>&1 &
    echo $! > "$EXPLORER_PID_FULL"
    cd - > /dev/null

    echo -e "${GREEN}   ✓ Report Explorer running at http://localhost:3000${NC}"
}

# Function to start Developer Portal
start_portal() {
    if is_running "$PORTAL_PID"; then
        return 0  # Already running
    fi

    echo -e "${YELLOW}🚀 Starting Developer Portal...${NC}"

    # Start in background
    nohup node "$PORTAL_DIR/server.js" > "$PORTAL_LOG" 2>&1 &
    echo $! > "$PORTAL_PID"

    echo -e "${GREEN}   ✓ Developer Portal running at http://localhost:3001${NC}"
}

# Function to start DataOps API
start_dataops() {
    if is_running "$DATAOPS_PID"; then
        return 0  # Already running
    fi

    echo -e "${YELLOW}🚀 Starting DataOps API...${NC}"

    # Check if uvicorn is available
    if ! command -v uvicorn &> /dev/null; then
        echo "   ⚠️  uvicorn not found, skipping DataOps API"
        echo "   💡 Install with: pip install uvicorn fastapi sqlalchemy"
        return 0  # Don't fail, just skip
    fi

    # Start in background
    nohup uvicorn "$DATAOPS_MODULE" --host 0.0.0.0 --port 8000 > "$DATAOPS_LOG" 2>&1 &
    echo $! > "$DATAOPS_PID"

    echo -e "${GREEN}   ✓ DataOps API running at http://localhost:8000${NC}"
}

# Main execution
echo ""
echo -e "${GREEN}════════════════════════════════════════${NC}"
echo -e "${GREEN}   a_domain Web Services${NC}"
echo -e "${GREEN}════════════════════════════════════════${NC}"
echo ""

# Start all services
start_portal
start_explorer
start_dataops

echo ""
echo -e "${GREEN}✅ All services started!${NC}"
echo ""
echo -e "Access your services:"
echo -e "  ${GREEN}• Developer Portal:${NC}  http://localhost:3001"
echo -e "  ${GREEN}• Report Explorer:${NC}   http://localhost:3000"
echo -e "  ${GREEN}• DataOps API:${NC}       http://localhost:8000/docs"
echo ""
echo -e "Logs located in: ${YELLOW}$LOG_DIR/${NC}"
echo ""

# Wait a moment for services to initialize
sleep 2
