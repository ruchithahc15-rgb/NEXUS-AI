
from fastapi import FastAPI, HTTPException
from sqlalchemy import text

from database.config import engine

app = FastAPI(
    title="NEXUS AI",
    description="Enterprise AI Operations & Decision Intelligence Platform",
    version="1.0.0"
)


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


@app.get("/api/v1/business/monthly-sales")
def get_monthly_sales():
    try:
        with engine.connect() as connection:
            result = connection.execute(text("""
                SELECT
                    TO_CHAR(sale_date, 'YYYY-MM') AS month,
                    COUNT(*) AS total_sales,
                    SUM(revenue) AS total_revenue,
                    ROUND(AVG(revenue), 2) AS average_order_value
                FROM sales
                GROUP BY TO_CHAR(sale_date, 'YYYY-MM')
                ORDER BY month
            """))

            records = result.mappings().all()

        return {
            "status": "success",
            "total_months": len(records),
            "data": [
                {
                    "month": row["month"],
                    "total_sales": row["total_sales"],
                    "total_revenue": float(row["total_revenue"]),
                    "average_order_value": float(row["average_order_value"])
                }
                for row in records
            ]
        }

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve monthly sales data"
        )
