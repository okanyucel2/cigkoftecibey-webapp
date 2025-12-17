# Railway Deployment Guide

## Architecture

This is a **monorepo** with:
- `backend/` - FastAPI (Python 3.11)
- `frontend/` - Vue 3 + Vite + Nginx

## Deployment Steps

### 1. Create Railway Project

```bash
cd /Users/okan.yucel/cigkoftecibey-webapp
railway login
railway init
```

### 2. Add PostgreSQL Database

In Railway Dashboard:
1. Click "New" → "Database" → "PostgreSQL"
2. Copy the `DATABASE_URL` from the database service

### 3. Deploy Backend

```bash
cd backend

# Link to Railway project
railway link

# Set environment variables
railway variables set DATABASE_URL="postgresql://..."
railway variables set SECRET_KEY="your-secret-key"
railway variables set CORS_ORIGINS='["https://your-frontend.railway.app"]'

# Deploy
railway up
```

Note the backend URL (e.g., `https://cigkofte-backend.railway.app`)

### 4. Deploy Frontend

```bash
cd ../frontend

# Link to same Railway project (new service)
railway link

# Set build variable - use your backend URL
railway variables set VITE_API_URL="https://cigkofte-backend.railway.app/api"

# Deploy
railway up
```

## Environment Variables

### Backend
| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string (from Railway) |
| `SECRET_KEY` | JWT secret (generate random string) |
| `CORS_ORIGINS` | Allowed origins (frontend URL) |

### Frontend
| Variable | Description |
|----------|-------------|
| `VITE_API_URL` | Backend API URL (set at build time) |

## Local Development

```bash
# Start all services with docker-compose
docker-compose up -d

# Frontend: http://localhost:3000
# Backend: http://localhost:8000
# PostgreSQL: localhost:5433
```

## GENESIS Integration

This project is imported into GENESIS at:
- **Path:** `projects/cigkofteci-bey` (symlink)
- **Room ID:** `cigkofteci-bey`
- **Project Type:** Monorepo (backend + frontend)

To deploy via GENESIS:
1. Go to Replit Dashboard
2. Select "Cigkofteci Bey" project
3. Click "Publish" (requires Railway token in Secrets Vault)
