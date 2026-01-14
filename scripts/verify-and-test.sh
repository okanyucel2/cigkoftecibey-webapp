#!/bin/bash
# scripts/verify-and-test.sh
# Run after EVERY task to ensure system is working
# Usage: ./scripts/verify-and-test.sh [optional-playwright-test-file]

set -e
PROJECT_ROOT="/Users/okan.yucel/Desktop/genesisv3/projects/cigkoftecibey-webapp"
cd "$PROJECT_ROOT"

echo "=========================================="
echo "GENESIS Session Verification Script"
echo "=========================================="
echo ""

# Step 1: Kill zombie processes
echo "Step 1: Cleaning up zombie processes..."
kill $(lsof -ti:19049) 2>/dev/null && echo "  Killed process on 19049" || echo "  Port 19049 clear"
kill $(lsof -ti:9049) 2>/dev/null && echo "  Killed process on 9049" || echo "  Port 9049 clear"
sleep 2

# Step 2: Ensure Docker is running
echo ""
echo "Step 2: Ensuring Docker is running..."
if ! docker info > /dev/null 2>&1; then
  echo "  Starting Docker..."
  open -a Docker
  # Wait for Docker to start (max 30 seconds)
  for i in {1..30}; do
    if docker info > /dev/null 2>&1; then
      echo "  Docker started!"
      break
    fi
    sleep 1
  done
fi

# Step 3: Start database container
echo ""
echo "Step 3: Starting database..."
docker start cigkofte-db 2>/dev/null || echo "  Container already running or doesn't exist"
sleep 3

# Verify database
if docker exec cigkofte-db pg_isready -U postgres > /dev/null 2>&1; then
  echo "  Database ready"
else
  echo "  Database NOT ready"
  exit 1
fi

# Step 4: Start backend
echo ""
echo "Step 4: Starting backend..."
cd "$PROJECT_ROOT/backend"
PYTHONPATH=. nohup uvicorn app.main:app --host 0.0.0.0 --port 9049 --reload > /tmp/cigkofte-backend.log 2>&1 &
sleep 5

# Verify backend
HEALTH=$(curl -s http://localhost:9049/api/health 2>/dev/null | jq -r '.status' 2>/dev/null)
if [ "$HEALTH" = "healthy" ]; then
  echo "  Backend healthy"
else
  echo "  Backend NOT healthy"
  echo "  Check logs: tail -50 /tmp/cigkofte-backend.log"
  exit 1
fi

# Step 5: Start frontend
echo ""
echo "Step 5: Starting frontend..."
cd "$PROJECT_ROOT/frontend"
nohup npm run dev -- --port 19049 --host > /tmp/cigkofte-frontend.log 2>&1 &
sleep 5

# Verify frontend
if curl -s http://localhost:19049 2>/dev/null | grep -q "<!DOCTYPE html>"; then
  echo "  Frontend serving"
else
  echo "  Frontend NOT serving"
  echo "  Check logs: tail -50 /tmp/cigkofte-frontend.log"
  exit 1
fi

# Step 6: Login test
echo ""
echo "Step 6: Testing login..."
LOGIN_RESP=$(curl -s -X POST http://localhost:9049/api/auth/login-json \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@cigkofte.com", "password": "admin123"}' 2>/dev/null)
TOKEN=$(echo "$LOGIN_RESP" | jq -r '.access_token' 2>/dev/null)

if [ -n "$TOKEN" ] && [ "$TOKEN" != "null" ] && [ ${#TOKEN} -gt 20 ]; then
  echo "  Login successful (token: ${#TOKEN} chars)"
else
  echo "  Login FAILED"
  echo "  Response: $LOGIN_RESP"
  exit 1
fi

# Step 7: Run specific test (if provided)
if [ -n "$1" ]; then
  echo ""
  echo "Step 7: Running Playwright test: $1"
  cd "$PROJECT_ROOT/frontend"
  npx playwright test "$1" --reporter=list
  if [ $? -eq 0 ]; then
    echo "  Test passed"
  else
    echo "  Test FAILED"
    exit 1
  fi
fi

echo ""
echo "=========================================="
echo "ALL VERIFICATIONS PASSED!"
echo "=========================================="
echo ""
echo "System ready at:"
echo "  Frontend: http://localhost:19049"
echo "  Backend:  http://localhost:9049"
echo "  Login:    admin@cigkofte.com / admin123"
echo ""
