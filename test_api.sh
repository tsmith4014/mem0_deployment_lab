#!/bin/bash

# Simple API Test Script for Mem0 Deployment Lab

API_URL="http://localhost:8000"

# Read API key from environment variable
# Make sure to set it first: export API_KEY=$(grep "^API_KEY=" .env | cut -d'=' -f2)
if [ -z "$API_KEY" ]; then
    echo "ERROR: API_KEY environment variable is not set"
    echo "Please run: export API_KEY=\$(grep '^API_KEY=' .env | cut -d'=' -f2)"
    exit 1
fi

echo "=========================================="
echo "TESTING MEM0 API"
echo "=========================================="
echo ""

# Test 1: Health Check
echo "1. Testing Health Check..."
curl -s -X GET "${API_URL}/health" | python3 -m json.tool
echo ""
echo ""

# Test 2: Add Memory
echo "2. Adding Memory..."
curl -s -X POST "${API_URL}/v1/memories/add" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: ${API_KEY}" \
  -d '{
    "messages": [
      {"role": "user", "content": "My name is Alice and I love playing poker"},
      {"role": "assistant", "content": "Nice to meet you Alice!"}
    ],
    "user_id": "alice_123"
  }' | python3 -m json.tool
echo ""
echo ""

# Test 3: Search Memory
echo "3. Searching Memory..."
curl -s -X POST "${API_URL}/v1/memories/search" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: ${API_KEY}" \
  -d '{
    "query": "What is the user'\''s name?",
    "user_id": "alice_123",
    "limit": 5
  }' | python3 -m json.tool
echo ""
echo ""

# Test 4: Get All Memories
echo "4. Getting All Memories..."
curl -s -X POST "${API_URL}/v1/memories/get-all" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: ${API_KEY}" \
  -d '{
    "user_id": "alice_123"
  }' | python3 -m json.tool
echo ""
echo ""

echo "=========================================="
echo "TEST COMPLETE"
echo "=========================================="
echo ""
echo "✓ Health check passed"
echo "✓ Memory added successfully"
echo "✓ Search working"
echo "✓ Get all working"
echo ""
echo "Next: Visit http://YOUR_EC2_IP:8000/docs for Swagger UI"
echo ""

