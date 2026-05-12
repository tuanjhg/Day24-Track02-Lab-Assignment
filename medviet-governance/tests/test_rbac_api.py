from fastapi.testclient import TestClient

from src.api.main import app


client = TestClient(app)


def auth_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


class TestRBACAPI:
    def test_admin_can_read_raw_patient_data(self):
        response = client.get("/api/patients/raw", headers=auth_header("token-alice"))

        assert response.status_code == 200
        assert len(response.json()) == 10
        assert "cccd" in response.json()[0]

    def test_ml_engineer_cannot_read_raw_patient_data(self):
        response = client.get("/api/patients/raw", headers=auth_header("token-bob"))

        assert response.status_code == 403

    def test_ml_engineer_can_read_anonymized_training_data(self):
        response = client.get("/api/patients/anonymized", headers=auth_header("token-bob"))

        assert response.status_code == 200
        payload = response.json()
        assert len(payload) == 10
        assert "nam_sinh" in payload[0]
        assert "ngay_sinh" not in payload[0]

    def test_data_analyst_can_read_aggregated_metrics_only(self):
        metrics_response = client.get(
            "/api/metrics/aggregated",
            headers=auth_header("token-carol"),
        )
        raw_response = client.get("/api/patients/raw", headers=auth_header("token-carol"))

        assert metrics_response.status_code == 200
        assert "patients_by_disease" in metrics_response.json()
        assert raw_response.status_code == 403

    def test_intern_cannot_access_production_endpoints(self):
        raw_response = client.get("/api/patients/raw", headers=auth_header("token-dave"))
        metrics_response = client.get(
            "/api/metrics/aggregated",
            headers=auth_header("token-dave"),
        )

        assert raw_response.status_code == 403
        assert metrics_response.status_code == 403

    def test_missing_token_returns_401(self):
        response = client.get("/api/patients/raw")

        assert response.status_code == 401
