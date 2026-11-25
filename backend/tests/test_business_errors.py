
from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_revenue_comparison_with_invalid_month():
    response = client.get(
        "/api/v1/business/revenue-comparison",
        params={
            "from_month": "invalid",
            "to_month": "2026-10"
        }
    )

    assert response.status_code in [400, 422]


def test_payment_analysis_with_invalid_month():
    response = client.get(
        "/api/v1/business/payment-failure-analysis",
        params={"month": "invalid"}
    )

    assert response.status_code in [400, 422]
