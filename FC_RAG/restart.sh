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

# Kill any processes on our ports
kill_port 8000  # Backend
kill_port 3000  # Frontend

# Kill specific processes
kill_process "uvicorn web_service:app"
kill_process "node.*react-scripts start"
kill_process "npm start"

# Extra cleanup for any remaining Python or Node processes related to our app
pkill -f "uvicorn"
pkill -f "node.*react-scripts"

# Wait for processes to stop
sleep 2

echo -e "${YELLOW}Starting backend service...${NC}"

# Start backend service
uvicorn web_service:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

if ps -p $BACKEND_PID > /dev/null; then
    echo -e "${GREEN}Backend service started successfully on port 8000${NC}"
else
    echo -e "${RED}Failed to start backend service${NC}"
    exit 1
fi

echo -e "${YELLOW}Starting frontend service...${NC}"

# Navigate to frontend directory and start service
cd frontend

# Build the frontend first
echo -e "${YELLOW}Building frontend...${NC}"
npm run build

# Start frontend service
npm start &
FRONTEND_PID=$!

# Wait for frontend to start
sleep 5

if ps -p $FRONTEND_PID > /dev/null; then
    echo -e "${GREEN}Frontend service started successfully${NC}"
else
    echo -e "${RED}Failed to start frontend service${NC}"
    exit 1
fi

echo -e "${GREEN}All services started successfully!${NC}"
echo -e "${YELLOW}Backend running at: ${GREEN}http://localhost:8000${NC}"
echo -e "${YELLOW}Frontend running at: ${GREEN}http://localhost:3000${NC}"

# Keep script running to maintain processes
wait
