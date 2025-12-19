#!/bin/bash

# DS-STAR Unified Startup Script
# Starts both backend and frontend together

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to cleanup background processes on exit
cleanup() {
    echo ""
    echo -e "${YELLOW}Shutting down DS-STAR...${NC}"
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
    fi
    exit 0
}

# Trap EXIT and SIGINT to cleanup
trap cleanup EXIT INT TERM

echo "======================================"
echo "DS-STAR Application Launcher"
echo "======================================"
echo ""

# Check if backend directory exists
if [ ! -d "backend" ]; then
    echo -e "${YELLOW}Error: backend directory not found${NC}"
    exit 1
fi

# Check if frontend directory exists
if [ ! -d "frontend" ]; then
    echo -e "${YELLOW}Error: frontend directory not found${NC}"
    exit 1
fi

# Check for OpenAI API key
if [ -z "$OPENAI_API_KEY" ]; then
    echo -e "${YELLOW}Warning: OPENAI_API_KEY environment variable is not set${NC}"
    echo "Please set your OpenAI API key:"
    echo "  export OPENAI_API_KEY=\"sk-your-key-here\""
    echo ""
    read -p "Do you want to continue anyway? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo -e "${BLUE}Starting Backend Server...${NC}"
echo "Backend will run on http://localhost:8000"
cd backend
python server.py &
BACKEND_PID=$!
cd ..

# Wait a moment for backend to start
sleep 2

# Check if backend is still running
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo -e "${YELLOW}Error: Backend failed to start${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} Backend started (PID: $BACKEND_PID)"
echo ""

echo -e "${BLUE}Starting Frontend...${NC}"
echo "Frontend will run on http://localhost:3000"
echo ""
echo -e "${GREEN}Application is ready!${NC}"
echo "Press Ctrl+C to stop both services"
echo "======================================"
echo ""

# Start frontend in foreground
cd frontend
npm run dev

# This line will be reached when frontend exits
cleanup
