#!/bin/bash
# EmberLearn Full Stack Setup Script

set -e

echo "🚀 EmberLearn Full Stack Setup"
echo "=============================="

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check Python version
echo -e "${YELLOW}Checking Python version...${NC}"
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Setup Backend
echo -e "\n${YELLOW}Setting up Backend...${NC}"
cd backend

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing dependencies..."
pip install -e ".[dev]" --quiet

if [ ! -f ".env" ]; then
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo -e "${GREEN}✓ Created .env file - please update with your OpenAI API key${NC}"
fi

cd ..

# Setup Frontend
echo -e "\n${YELLOW}Setting up Frontend...${NC}"
cd frontend

if [ ! -d "node_modules" ]; then
    echo "Installing npm dependencies..."
    npm install --legacy-peer-deps
fi

if [ ! -f ".env.local" ]; then
    echo "Creating .env.local..."
    cat > .env.local << 'ENVEOF'
NEXT_PUBLIC_API_URL=http://localhost:8000
ENVEOF
fi

cd ..

echo -e "\n${GREEN}✓ Setup Complete!${NC}"
echo -e "\n${YELLOW}Next Steps:${NC}"
echo "1. Update backend/.env with your OpenAI API key"
echo "2. Run: ./start.sh"
echo "   Or manually:"
echo "   - Terminal 1: cd backend && source venv/bin/activate && python main.py"
echo "   - Terminal 2: cd frontend && npm run dev"
echo ""
echo "3. Open http://localhost:3000 in your browser"
