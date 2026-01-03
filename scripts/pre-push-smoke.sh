#!/bin/bash
# Pre-Push Smoke Tests for cigkoftecibey-webapp
# Part of P0.45 Application Integration Verification
#
# Runs critical smoke tests tagged with @smoke before pushing.
# Prevents broken code from reaching remote repository.
#
# Usage:
#   ./scripts/pre-push-smoke.sh          # Run smoke tests
#   ./scripts/pre-push-smoke.sh --quick  # Skip if dev server not running
#
# Exit codes:
#   0 - All smoke tests passed
#   1 - Smoke tests failed
#   2 - Setup error (missing dependencies, etc.)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
FRONTEND_DIR="$PROJECT_ROOT/frontend"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}═══════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}  Pre-Push Smoke Tests (P0.45)${NC}"
echo -e "${YELLOW}═══════════════════════════════════════════════════════════${NC}"

# Check if frontend directory exists
if [ ! -d "$FRONTEND_DIR" ]; then
    echo -e "${RED}Error: Frontend directory not found at $FRONTEND_DIR${NC}"
    exit 2
fi

cd "$FRONTEND_DIR"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}Installing dependencies...${NC}"
    npm install
fi

# Check if Playwright is installed
if [ ! -d "node_modules/@playwright" ]; then
    echo -e "${YELLOW}Installing Playwright...${NC}"
    npx playwright install chromium
fi

# Quick mode: skip if dev server not running
if [ "$1" == "--quick" ]; then
    # Check if backend is running (port from test_config)
    if ! curl -s http://localhost:9049/health > /dev/null 2>&1; then
        echo -e "${YELLOW}Quick mode: Backend not running, skipping smoke tests${NC}"
        exit 0
    fi
fi

echo -e "\n${YELLOW}Running smoke tests...${NC}\n"

# Run Playwright smoke tests
# Uses the 'smoke' project which greps for @smoke tags
if npx playwright test --project=smoke --reporter=list; then
    echo -e "\n${GREEN}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}  ✓ All smoke tests passed - Safe to push${NC}"
    echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
    exit 0
else
    echo -e "\n${RED}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${RED}  ✗ Smoke tests failed - Push blocked${NC}"
    echo -e "${RED}  Fix the failing tests before pushing.${NC}"
    echo -e "${RED}═══════════════════════════════════════════════════════════${NC}"
    exit 1
fi
