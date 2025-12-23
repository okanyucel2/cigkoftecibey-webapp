#!/bin/bash

# Cigkoftecibey Webapp - Full Restart Script
# Usage: ./full_restart.sh [backend|frontend|all]

set -e

PROJECT_DIR="/Users/okan.yucel/cigkoftecibey-webapp"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[OK]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Stop backend (uvicorn on port 8000)
stop_backend() {
    log_info "Stopping backend..."

    # Find and kill uvicorn processes on port 8000
    PIDS=$(lsof -ti:8000 2>/dev/null || true)
    if [ -n "$PIDS" ]; then
        echo "$PIDS" | xargs kill -9 2>/dev/null || true
        log_success "Backend stopped (PIDs: $PIDS)"
    else
        log_warn "Backend was not running"
    fi
}

# Stop frontend (vite on port 5174 only)
stop_frontend() {
    log_info "Stopping frontend..."

    # Find and kill vite/node processes on port 5174 only (5175 is another project)
    PIDS=$(lsof -ti:5174 2>/dev/null || true)
    if [ -n "$PIDS" ]; then
        echo "$PIDS" | xargs kill -9 2>/dev/null || true
        log_success "Frontend stopped ($(echo "$PIDS" | wc -l | tr -d ' ') processes)"
    else
        log_warn "Frontend was not running"
    fi
}

# Start backend
start_backend() {
    log_info "Starting backend..."

    cd "$BACKEND_DIR"
    source venv/bin/activate

    # Run migrations first
    log_info "Running database migrations..."
    alembic upgrade head 2>/dev/null || log_warn "Migration check skipped"

    # Start uvicorn in background
    nohup uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > /tmp/backend.log 2>&1 &

    # Wait and verify
    sleep 2
    if lsof -ti:8000 > /dev/null 2>&1; then
        log_success "Backend started on http://localhost:8000"
    else
        log_error "Backend failed to start. Check /tmp/backend.log"
        return 1
    fi
}

# Start frontend
start_frontend() {
    log_info "Starting frontend..."

    cd "$FRONTEND_DIR"

    # Start vite in background
    nohup npm run dev > /tmp/frontend.log 2>&1 &

    # Wait and verify on port 5174
    sleep 3
    if lsof -ti:5174 > /dev/null 2>&1; then
        log_success "Frontend started on http://localhost:5174"
    else
        log_error "Frontend failed to start (port 5174 not available). Check /tmp/frontend.log"
        return 1
    fi
}

# Show status
show_status() {
    echo ""
    log_info "Service Status:"

    if lsof -ti:8000 > /dev/null 2>&1; then
        echo -e "  Backend:  ${GREEN}Running${NC} (port 8000)"
    else
        echo -e "  Backend:  ${RED}Stopped${NC}"
    fi

    # Check frontend on port 5174
    if lsof -ti:5174 > /dev/null 2>&1; then
        echo -e "  Frontend: ${GREEN}Running${NC} (port 5174)"
    else
        echo -e "  Frontend: ${RED}Stopped${NC}"
    fi
    echo ""
}

# Main
case "${1:-all}" in
    backend)
        stop_backend
        sleep 1
        start_backend
        ;;
    frontend)
        stop_frontend
        sleep 1
        start_frontend
        ;;
    stop)
        stop_backend
        stop_frontend
        ;;
    status)
        show_status
        exit 0
        ;;
    all|restart|*)
        echo ""
        echo "=================================="
        echo "  Cigkoftecibey Full Restart"
        echo "=================================="
        echo ""
        stop_backend
        stop_frontend
        sleep 1
        start_backend
        start_frontend
        ;;
esac

show_status

echo "Logs:"
echo "  Backend:  tail -f /tmp/backend.log"
echo "  Frontend: tail -f /tmp/frontend.log"
echo ""
