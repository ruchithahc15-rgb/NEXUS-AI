
from fastapi import APIRouter, HTTPException, Query

from backend.services import business_service


router = APIRouter(
    prefix="/api/v1/business",
    tags=["Business Intelligence"]
)


# 1. Monthly Sales
@router.get("/monthly-sales")
def get_monthly_sales():
    try:
        return business_service.get_monthly_sales_data()
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve monthly sales data"
        )



# 2. Revenue Comparison
@router.get("/revenue-comparison")
def compare_revenue(
    from_month: str = Query(
        ...,
        pattern=r"^\d{4}-(0[1-9]|1[0-2])$"
    ),
    to_month: str = Query(
        ...,
        pattern=r"^\d{4}-(0[1-9]|1[0-2])$"
    )
):
    try:
        if from_month > to_month:
            raise HTTPException(
                status_code=400,
                detail="from_month cannot be later than to_month"
            )

        return business_service.get_revenue_comparison(
            from_month, to_month
        )

    except LookupError as error:
        raise HTTPException(status_code=404, detail=str(error))

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unable to compare monthly revenue"
        )

# 3. Payment Failure Analysis
@router.get("/payment-failure-analysis")
def payment_failure_analysis(
    month: str = Query(
        default="2026-10",
        pattern=r"^\d{4}-(0[1-9]|1[0-2])$"
    )
):
    try:
        return business_service.get_payment_failure_analysis(month)
    except LookupError as error:
        raise HTTPException(status_code=404, detail=str(error))
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unable to analyze payment failures"
        )


# 4. Product Revenue Analysis
@router.get("/product-revenue-analysis")
def product_revenue_analysis(
    from_month: str = Query(
        default="2026-09",
        pattern=r"^\d{4}-(0[1-9]|1[0-2])$"
    ),
    to_month: str = Query(
        default="2026-10",
        pattern=r"^\d{4}-(0[1-9]|1[0-2])$"
    )
):
    try:
        return business_service.get_product_revenue_analysis(
            from_month, to_month
        )
    except LookupError as error:
        raise HTTPException(status_code=404, detail=str(error))
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unable to analyze product revenue"
        )


# 5. Regional Revenue Analysis
@router.get("/regional-revenue-analysis")
def regional_revenue_analysis(
    from_month: str = Query(
        default="2026-09",
        pattern=r"^\d{4}-(0[1-9]|1[0-2])$"
    ),
    to_month: str = Query(
        default="2026-10",
        pattern=r"^\d{4}-(0[1-9]|1[0-2])$"
    )
):
    try:
        return business_service.get_regional_revenue_analysis(
            from_month, to_month
        )
    except LookupError as error:
        raise HTTPException(status_code=404, detail=str(error))
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unable to analyze regional revenue"
        )
