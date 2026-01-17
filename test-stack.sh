#!/bin/bash
# test-stack.sh - Test EmberLearn full stack functionality

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

API_URL="http://localhost:8000"
FRONTEND_URL="http://localhost:3000"

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}EmberLearn Stack Tests${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# Test 1: Health check
echo -e "${YELLOW}[Test 1/6] Health Check...${NC}"
if response=$(curl -s "$API_URL/health"); then
    echo -e "${GREEN}✓ Backend is running${NC}"
else
    echo -e "${RED}✗ Backend is not responding. Make sure to run ./start.sh first${NC}"
    exit 1
fi

# Test 2: Status endpoint
echo -e "${YELLOW}[Test 2/6] API Status...${NC}"
if response=$(curl -s "$API_URL/api/status"); then
    echo -e "${GREEN}✓ Status endpoint working${NC}"
    echo "  Response: $response"
else
    echo -e "${RED}✗ Status endpoint failed${NC}"
    exit 1
fi

# Test 3: Register user
echo -e "${YELLOW}[Test 3/6] User Registration...${NC}"
REGISTER_RESPONSE=$(curl -s -X POST "$API_URL/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@emberlearn.ai",
    "password": "testpass123",
    "full_name": "Test User"
  }')

if echo "$REGISTER_RESPONSE" | grep -q "access_token"; then
    echo -e "${GREEN}✓ User registration successful${NC}"
    # Extract token for next tests
    TOKEN=$(echo "$REGISTER_RESPONSE" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
else
    echo -e "${RED}✗ User registration failed${NC}"
    echo "  Response: $REGISTER_RESPONSE"
    exit 1
fi

# Test 4: Get current user
echo -e "${YELLOW}[Test 4/6] Get Current User...${NC}"
if response=$(curl -s -X GET "$API_URL/api/auth/me" \
  -H "Authorization: Bearer $TOKEN"); then
    if echo "$response" | grep -q "test@emberlearn.ai"; then
        echo -e "${GREEN}✓ Authentication working${NC}"
    else
        echo -e "${RED}✗ User mismatch${NC}"
        exit 1
    fi
else
    echo -e "${RED}✗ Get user failed${NC}"
    exit 1
fi

# Test 5: Chat endpoint with triage
echo -e "${YELLOW}[Test 5/6] Chat API (with Triage)...${NC}"
CHAT_RESPONSE=$(curl -s -X POST "$API_URL/api/chat" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "query": "How do for loops work?",
    "student_id": "test-user"
  }')

if echo "$CHAT_RESPONSE" | grep -q "response"; then
    echo -e "${GREEN}✓ Chat API working${NC}"
    echo "  Routed to: $(echo "$CHAT_RESPONSE" | grep -o '"routed_to":"[^"]*' | cut -d'"' -f4)"
else
    echo -e "${RED}✗ Chat API failed${NC}"
    echo "  Response: $CHAT_RESPONSE"
    exit 1
fi

# Test 6: Direct agent endpoints
echo -e "${YELLOW}[Test 6/6] Direct Agent Endpoints...${NC}"
CONCEPTS_RESPONSE=$(curl -s -X POST "$API_URL/api/concepts" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "query": "Explain list comprehensions"
  }')

if echo "$CONCEPTS_RESPONSE" | grep -q "response"; then
    echo -e "${GREEN}✓ Concepts agent working${NC}"
else
    echo -e "${RED}✗ Concepts agent failed${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}✓ All tests passed!${NC}"
echo -e "${GREEN}================================${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo "1. Open ${FRONTEND_URL} in your browser"
echo "2. Register a new account or login"
echo "3. Try the chat interface with queries like:"
echo "   - 'How do for loops work?'"
echo "   - 'Give me a coding exercise'"
echo "   - 'Debug my code'"
echo "   - 'Review this code: def hello(): print(\"hi\")'"
echo ""
echo -e "${BLUE}API Documentation: ${API_URL}/docs${NC}"
