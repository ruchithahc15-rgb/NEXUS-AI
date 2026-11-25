
from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_revenue_comparison_missing_parameters():
    response = client.get(
        "/api/v1/business/revenue-comparison"
    )

    assert response.status_code == 422


def test_revenue_comparison_missing_from_month():
    response = client.get(
        "/api/v1/business/revenue-comparison",
        params={"to_month": "2026-10"}
    )

    assert response.status_code == 422


def test_revenue_comparison_missing_to_month():
    response = client.get(
        "/api/v1/business/revenue-comparison",
        params={"from_month": "2026-09"}
    )

    assert response.status_code == 422


def test_revenue_comparison_invalid_date_range():
    response = client.get(
        "/api/v1/business/revenue-comparison",
        params={
            "from_month": "2026-10",
            "to_month": "2026-09"
        }
    )

    assert response.status_code in [400, 422]
