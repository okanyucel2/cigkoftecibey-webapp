from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api import auth, purchases, expenses, reports, production, staff_meals, personnel, online_sales, branches, users, invitation_codes, courier_expenses

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
app.include_router(invitation_codes.router, prefix="/api")
app.include_router(courier_expenses.router, prefix="/api")


@app.get("/api/health")
def health_check():
    return {"status": "healthy", "app": settings.APP_NAME}


@app.get("/")
def root():
    return {"message": "Cig Kofte Yonetim Sistemi API", "docs": "/api/docs"}
