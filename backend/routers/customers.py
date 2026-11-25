
from fastapi import APIRouter, HTTPException

from backend.services import customer_service


router = APIRouter(
    prefix="/api/v1/customers",
    tags=["Customer Operations"]
)


# 1. Unresolved Payment Complaints
@router.get("/unresolved-payment-complaints")
def get_unresolved_payment_complaints():
    try:
        return customer_service.get_unresolved_payment_complaints()
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve unresolved payment complaints"
        )


# 2. Customer Complaint Summary
@router.get("/complaint-summary")
def get_complaint_summary():
    try:
        return customer_service.get_complaint_summary()
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve complaint summary"
        )
