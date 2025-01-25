#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to kill process running on a port
kill_port() {
    local port=$1
    local pid=$(lsof -t -i:$port)
    if [ ! -z "$pid" ]; then
        echo -e "${YELLOW}Killing process on port $port (PID: $pid)${NC}"
        kill -9 $pid 2>/dev/null
    fi
}

# Function to kill process by name
kill_process() {
    local name=$1
    local pid=$(pgrep -f "$name")
    if [ ! -z "$pid" ]; then
        echo -e "${YELLOW}Killing $name process (PID: $pid)${NC}"
        kill -9 $pid 2>/dev/null
    fi
}

echo -e "${YELLOW}Cleaning up existing processes...${NC}"

# Kill backend processes
kill_port 8000
kill_process "uvicorn web_service:app"
pkill -f "uvicorn"

sleep 2

echo -e "${YELLOW}Building frontend...${NC}"
cd frontend
npm run build
cd ..

echo -e "${YELLOW}Starting backend service...${NC}"
uvicorn web_service:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

sleep 3

if ps -p $BACKEND_PID > /dev/null; then
    echo -e "${GREEN}Backend service started on port 8000${NC}"
else
    echo -e "${RED}Failed to start backend${NC}"
    exit 1
fi

echo -e "${GREEN}All services ready!${NC}"
echo -e "${YELLOW}Application running at: ${GREEN}http://localhost:8000${NC}"
wait
