#!/bin/bash
# start.sh - Start both backend and frontend servers

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}EmberLearn Full Stack Startup${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# Check if setup has been run
if [ ! -d "backend/venv" ] || [ ! -d "frontend/node_modules" ]; then
    echo -e "${RED}❌ Setup not completed. Please run ./setup.sh first.${NC}"
    exit 1
fi

# Function to cleanup on exit
cleanup() {
    echo ""
    echo -e "${YELLOW}Shutting down servers...${NC}"
    if [ -n "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
    fi
    exit 0
}

trap cleanup SIGINT SIGTERM EXIT

# Start backend in background
echo -e "${BLUE}Starting backend server...${NC}"
cd backend
source venv/bin/activate

# Check if .env exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  No .env file found. Creating from .env.example...${NC}"
    cp .env.example .env
fi

python main.py &
BACKEND_PID=$!
echo -e "${GREEN}✓ Backend started (PID: $BACKEND_PID)${NC}"
sleep 2

# Check if backend started successfully
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo -e "${RED}❌ Backend failed to start. Check logs above.${NC}"
    exit 1
fi

cd ..

# Start frontend
echo -e "${BLUE}Starting frontend server...${NC}"
cd frontend

# Check if .env.local exists
if [ ! -f ".env.local" ]; then
    echo -e "${YELLOW}⚠️  No .env.local file found. Creating...${NC}"
    echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
fi

echo -e "${GREEN}✓ Starting development server...${NC}"
echo ""
echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}✓ EmberLearn is running!${NC}"
echo -e "${GREEN}================================${NC}"
echo ""
echo -e "Frontend: ${BLUE}http://localhost:3000${NC}"
echo -e "Backend:  ${BLUE}http://localhost:8000${NC}"
echo -e "API Docs: ${BLUE}http://localhost:8000/docs${NC}"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop all servers${NC}"
echo ""

npm run dev

# If npm exits, cleanup will trigger
