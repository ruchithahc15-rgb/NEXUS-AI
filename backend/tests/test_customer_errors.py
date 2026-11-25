
from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_unresolved_complaints_endpoint_method_not_allowed():
    response = client.post(
        "/api/v1/customers/unresolved-payment-complaints"
    )

    assert response.status_code == 405


def test_complaint_summary_endpoint_method_not_allowed():
    response = client.post(
        "/api/v1/customers/complaint-summary"
    )

    assert response.status_code == 405


def test_unknown_customer_endpoint():
    response = client.get(
        "/api/v1/customers/unknown-endpoint"
    )

    assert response.status_code == 404
