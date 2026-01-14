# CLAUDE.md - Cigkofteci Bey Project Guide

## Project Overview

**Name:** Cigkofteci Bey Restaurant Management System
**Type:** Multi-tenant SaaS for restaurant operations
**Tech Stack:** FastAPI (Python), Vue 3, PostgreSQL

---

## P0.48: Frontend Integrity Check

**Rule:** Frontend changes require TypeScript validation passing BEFORE commit.

**Commands:**
- Vue projects: `npx vue-tsc --noEmit`
- Pure TypeScript: `npx tsc --noEmit`

**Enforcement:**
- No broken builds allowed in the repo
- Fix all errors before `git commit`
- Unused variables are ERRORS, not warnings

**Rationale:** Catch type errors before runtime. Essential when Docker/E2E testing unavailable.

---

## Port Allocation

| Service | Port |
|---------|------|
| Backend | 9049 |
| Frontend | 19049 |
| WebSocket | 29049 |

---

## Database

- **Type:** PostgreSQL (Docker required)
- **Port:** 5433
- **Start:** `docker-compose up -d`

---

## Testing

**E2E Tests:** Playwright
- Location: `frontend/tests/e2e/`
- Run: `cd frontend && npx playwright test`

**Backend Tests:** Pytest
- Location: `backend/tests/`
- Run: `cd backend && pytest`

---

## Inherited Protocols

This project inherits from GENESIS root:
- P0.40: TDD
- P0.47: Pre-Commit Verification
- P0.50: Destructive Action Guard
- P0.99: Session Guard

---

*Project-specific rules for cigkoftecibey-webapp*
