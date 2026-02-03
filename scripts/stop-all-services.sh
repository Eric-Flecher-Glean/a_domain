#!/bin/bash
# Stop all web services

EXPLORER_PID=".explorer.pid"
PORTAL_PID=".portal.pid"
DATAOPS_PID=".dataops.pid"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo ""
echo -e "${YELLOW}🛑 Stopping all web services...${NC}"
echo ""

# Function to stop a service
stop_service() {
    local pid_file=$1
    local service_name=$2

    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if ps -p "$pid" > /dev/null 2>&1; then
            echo -e "   Stopping $service_name (PID: $pid)..."
            kill "$pid" 2>/dev/null
            rm -f "$pid_file"
            echo -e "${GREEN}   ✓ $service_name stopped${NC}"
        else
            rm -f "$pid_file"
            echo -e "   ℹ️  $service_name was not running"
        fi
    else
        echo -e "   ℹ️  $service_name was not running"
    fi
}

# Stop all services
stop_service "$PORTAL_PID" "Developer Portal"
stop_service "$EXPLORER_PID" "Report Explorer"
stop_service "$DATAOPS_PID" "DataOps API"

echo ""
echo -e "${GREEN}✅ All services stopped${NC}"
echo ""
