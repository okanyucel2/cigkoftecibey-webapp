from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import bcrypt
import traceback
import sys

# Monkey patch bcrypt for passlib compatibility - ROBUST VERSION
try:
    if not hasattr(bcrypt, "__about__"):
        class About:
            __version__ = getattr(bcrypt, "__version__", "4.0.1")
        bcrypt.__about__ = About()
except Exception as e:
    print(f"Warning: Failed to patch bcrypt: {e}", file=sys.stderr)

from app.config import settings
from app.middleware import RequestLoggingMiddleware
from app.logging_config import setup_logging
from app.api import auth, purchases, expenses, reports, production, staff_meals, personnel, online_sales, branches, users, invitation_codes, courier_expenses, ai_insights, cash_difference, import_history, categorization, payments, health

# Startup Configuration Validation (P0.43)
def validate_configuration():
    """Validate configuration on startup - log warnings for potential issues."""
    import os

    # Check DATABASE_URL
    db_url = settings.DATABASE_URL
    print(f"\n{'='*60}", file=sys.stderr)
    print(f"STARTUP CONFIG VALIDATION", file=sys.stderr)
    print(f"{'='*60}", file=sys.stderr)

    # Extract port from DATABASE_URL for logging
    if "localhost:" in db_url:
        port = db_url.split("localhost:")[1].split("/")[0]
        print(f"DATABASE: localhost:{port}", file=sys.stderr)

        # Warn if using local PostgreSQL (5432) instead of Docker (5433)
        if port == "5432":
            print(f"⚠️  WARNING: Using port 5432 (local PostgreSQL)", file=sys.stderr)
            print(f"   Expected: port 5433 (Docker PostgreSQL)", file=sys.stderr)
            print(f"   See: docs/DATABASE_ARCHITECTURE.md", file=sys.stderr)
    else:
        print(f"DATABASE: {db_url[:50]}...", file=sys.stderr)

    # Check if .env exists
    if os.path.exists(".env"):
        print(f"CONFIG: .env file found ✓", file=sys.stderr)
    else:
        print(f"⚠️  WARNING: No .env file - using defaults", file=sys.stderr)

    print(f"{'='*60}\n", file=sys.stderr)

# Run validation on module load
validate_configuration()

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Global 500 Handler for Debugging
@app.middleware("http")
async def debug_exception_handler(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        print(f"\nCRITICAL ERROR: {request.method} {request.url.path}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal Server Error", "debug_trace": str(e)}
        )

# Identity Header Middleware (Prevents Port Confusion)
@app.middleware("http")
async def add_identity_header(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Service-Name"] = "cigkoftecibey-webapp"
    response.headers["X-Service-Port"] = "8000"
    return response

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request logging middleware
app.add_middleware(RequestLoggingMiddleware)

# Routers
app.include_router(auth.router, prefix="/api")
app.include_router(purchases.router, prefix="/api")
app.include_router(expenses.router, prefix="/api")
app.include_router(reports.router, prefix="/api")
app.include_router(production.router, prefix="/api")
app.include_router(staff_meals.router, prefix="/api")
app.include_router(personnel.router, prefix="/api")
app.include_router(online_sales.router, prefix="/api")
app.include_router(branches.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(ai_insights.router, prefix="/api")
app.include_router(invitation_codes.router, prefix="/api")
app.include_router(courier_expenses.router, prefix="/api")
app.include_router(cash_difference.router, prefix="/api")
app.include_router(import_history.router, prefix="/api")
app.include_router(categorization.router, prefix="/api")
app.include_router(payments.router, prefix="/api")
app.include_router(health.router, prefix="/api")


@app.get("/")
def root():
    return {"message": "Cig Kofte Yonetim Sistemi API", "docs": "/api/docs"}

# Forced reload trigger
