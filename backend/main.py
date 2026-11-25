from fastapi import FastAPI, HTTPException
from sqlalchemy import text

from database.config import engine
from backend.routers.business import router as business_router
from backend.routers.customers import router as customers_router


app = FastAPI(
    title="NEXUS AI",
    description="Enterprise AI Operations & Decision Intelligence Platform",
    version="1.0.0"
)


# Register API routers
app.include_router(business_router)
app.include_router(customers_router)


@app.get("/")
def root():
    return {
        "application": "NEXUS AI",
        "message": "NEXUS AI Backend is running!",
        "status": "operational"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "NEXUS AI Backend"
    }


@app.get("/api/v1/database/health")
def database_health():
    try:
        with engine.connect() as connection:
            result = connection.execute(
                text("SELECT current_database()")
            )
            database_name = result.scalar()

        return {
            "status": "connected",
            "database": database_name,
            "message": "NEXUS AI successfully connected to PostgreSQL"
        }

    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Database connection failed"
        )