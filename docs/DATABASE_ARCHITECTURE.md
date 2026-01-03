# Database Architecture Decision

**Date:** 2026-01-03
**Status:** DECIDED
**Decision:** Use Docker PostgreSQL on port 5433

---

## Context

The cigkoftecibey-webapp project had TWO PostgreSQL databases running simultaneously:

| Database | Port | Location | Purpose |
|----------|------|----------|---------|
| Local PostgreSQL | 5432 | `brew services` | Historical (installed before Docker) |
| Docker PostgreSQL | 5433 | `cigkofte-db` container | Containerized, version-controlled |

This caused configuration confusion:
- App sometimes connected to 5432 (local)
- App sometimes connected to 5433 (Docker)
- Migrations ran on different databases at different times
- Health checks passed but didn't verify WHICH database

---

## Decision

**Use Docker PostgreSQL exclusively (port 5433)**

### Rationale

| Factor | Docker (5433) | Local (5432) |
|--------|---------------|--------------|
| Consistency | Same env local/CI/prod | Varies by machine |
| Isolation | Per-project containers | Shared instance |
| Multi-project | Clean separation | Port conflict risk |
| Version control | docker-compose.yml tracked | Invisible config |
| New developer | `docker-compose up` | Install, configure, create DB |
| Render.com prod | Cloud PostgreSQL (similar model) | Different paradigm |

### Technical Details

**Docker container:** `cigkofte-db`
**External port:** 5433 (what app connects to)
**Internal port:** 5432 (what PostgreSQL reports via `inet_server_port()`)

**Configuration files:**
- `backend/.env`: `DATABASE_URL=postgresql://postgres:postgres@localhost:5433/cigkofte`
- `backend/app/config.py`: Default changed to port 5433
- `backend/alembic.ini`: `sqlalchemy.url` uses port 5433

---

## Health Check Verification (P0.42)

The `/api/health/deep` endpoint now includes `database_identity` check:

**Local (Docker):**
```json
{
  "database_identity": {
    "status": "pass",
    "database_name": "cigkofte",
    "port": 5432,
    "expected_prefix": "cigkofte",
    "environment": "local"
  }
}
```

**Production (Render):**
```json
{
  "database_identity": {
    "status": "pass",
    "database_name": "cigkofte_abc123",
    "port": 5432,
    "expected_prefix": "cigkofte",
    "environment": "production"
  }
}
```

**Production Safety:**
- Uses prefix matching (`startswith("cigkofte")`) to support Render's `cigkofte_xxxx` naming
- Port is logged but not strictly validated (varies by environment)
- Detects environment automatically based on database name

---

## Cleanup Steps Performed

1. ✅ Updated `app/config.py` default to 5433
2. ✅ Updated `alembic.ini` to 5433
3. ✅ Created `.env` with explicit DATABASE_URL
4. ✅ Stopped local PostgreSQL (`brew services stop postgresql@14`)
5. ✅ Added `database_identity` check to HealthChecker
6. ✅ Verified only Docker PostgreSQL running

---

## Preventing Regression

### Health Check
- `/api/health/deep` verifies database identity
- Will report "degraded" if wrong database connected

### Startup Validation (Future P0.43)
- App should validate DATABASE_URL on startup
- Warn if using default config
- Log connection details

### Docker Commands
```bash
# Start database
docker-compose up -d db

# Check container
docker ps | grep cigkofte-db

# Connect manually
PGPASSWORD=postgres psql -h localhost -p 5433 -U postgres -d cigkofte
```

---

## FAQ

**Q: Why does health check show port 5432 when I connect to 5433?**
A: Docker NAT maps external 5433 → internal 5432. PostgreSQL's `inet_server_port()` returns the internal port.

**Q: Can I use local PostgreSQL instead?**
A: Not recommended. Docker provides isolation and consistency. Update all config if you must.

**Q: What if health check fails on database_identity?**
A: Check: 1) Docker running? 2) .env correct? 3) Local PostgreSQL stopped?

---

*Architecture decision recorded for future reference and onboarding.*
