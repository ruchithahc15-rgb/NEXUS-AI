
from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_unresolved_payment_complaints_endpoint():
    response = client.get(
        "/api/v1/customers/unresolved-payment-complaints"
    )

    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert isinstance(response.json()["data"], list)
    assert len(response.json()["data"]) > 0


def test_complaint_summary_endpoint():
    response = client.get(
        "/api/v1/customers/complaint-summary"
    )

    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert isinstance(response.json()["summary"], dict)
