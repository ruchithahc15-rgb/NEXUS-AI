
from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_monthly_sales_endpoint():
    response = client.get("/api/v1/business/monthly-sales")

    assert response.status_code == 200
    assert isinstance(response.json(), dict)
    assert response.json()["status"] == "success"
    assert isinstance(response.json()["data"], list)


def test_revenue_comparison_endpoint():
    response = client.get(
        "/api/v1/business/revenue-comparison",
        params={
            "from_month": "2026-09",
            "to_month": "2026-10"
        }
    )

    assert response.status_code == 200
    assert response.json()["status"] == "success"

    comparison = response.json()["comparison"]

    assert comparison["from_month"] == "2026-09"
    assert comparison["to_month"] == "2026-10"
    assert "revenue_change_percentage" in comparison


def test_payment_failure_analysis_endpoint():
    response = client.get(
        "/api/v1/business/payment-failure-analysis",
        params={"month": "2026-10"}
    )

    assert response.status_code == 200
    assert isinstance(response.json(), dict)


def test_product_revenue_analysis_endpoint():
    response = client.get(
        "/api/v1/business/product-revenue-analysis",
        params={
            "from_month": "2026-09",
            "to_month": "2026-10"
        }
    )

    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert isinstance(response.json()["data"], list)
    assert len(response.json()["data"]) > 0

def test_regional_revenue_analysis_endpoint():
    response = client.get(
        "/api/v1/business/regional-revenue-analysis",
        params={
            "from_month": "2026-09",
            "to_month": "2026-10"
        }
    )

    assert response.status_code == 200
    assert isinstance(response.json(), dict)
    assert response.json()["status"] == "success"
    assert isinstance(response.json()["data"], list)
