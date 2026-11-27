from uuid import UUID

from fastapi.testclient import TestClient


def test_profile_starts_without_risk_profile(
    client: TestClient, risk_lesson_id: UUID
) -> None:
    body = client.get("/api/v1/profile").json()

    assert body["risk_profile"] is None
    assert body["completed_lessons"] == 0
    assert body["total_lessons"] == 2
    assert body["risk_lesson_id"] == str(risk_lesson_id)
    assert body["can_choose_risk_profile"] is False


def test_risk_profile_requires_risk_lesson(client: TestClient, lesson_id: UUID) -> None:
    # Completar otra lección no habilita el perfil.
    client.post(f"/api/v1/lessons/{lesson_id}/complete")

    response = client.put(
        "/api/v1/profile/risk-profile", json={"risk_profile": "agresivo"}
    )

    assert response.status_code == 409
    assert "Riesgo y rentabilidad" in response.json()["detail"]


def test_full_flow_lesson_profile_recommendations(
    client: TestClient, risk_lesson_id: UUID
) -> None:
    assert client.get("/api/v1/investments/recommendations/me").status_code == 409

    client.post(f"/api/v1/lessons/{risk_lesson_id}/complete")
    unlocked = client.get("/api/v1/profile").json()
    assert unlocked["can_choose_risk_profile"] is True
    assert unlocked["completed_lessons"] == 1

    saved = client.put(
        "/api/v1/profile/risk-profile", json={"risk_profile": "agresivo"}
    )
    assert saved.status_code == 200
    assert saved.json()["risk_profile"] == "agresivo"

    recommendations = client.get("/api/v1/investments/recommendations/me").json()
    assert recommendations[0]["investment"]["slug"] == "acciones"

    client.put("/api/v1/profile/risk-profile", json={"risk_profile": "conservador"})
    recommendations = client.get("/api/v1/investments/recommendations/me").json()
    assert recommendations[0]["investment"]["slug"] == "cdt-bancario"


def test_invalid_risk_profile_returns_422(
    client: TestClient, risk_lesson_id: UUID
) -> None:
    client.post(f"/api/v1/lessons/{risk_lesson_id}/complete")

    response = client.put(
        "/api/v1/profile/risk-profile", json={"risk_profile": "temerario"}
    )

    assert response.status_code == 422


def test_profile_routes_require_authentication(anonymous_client: TestClient) -> None:
    assert anonymous_client.get("/api/v1/profile").status_code == 401
    assert (
        anonymous_client.put(
            "/api/v1/profile/risk-profile", json={"risk_profile": "moderado"}
        ).status_code
        == 401
    )
    assert (
        anonymous_client.get("/api/v1/investments/recommendations/me").status_code
        == 401
    )
