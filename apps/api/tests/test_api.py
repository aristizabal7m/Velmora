from uuid import UUID

from fastapi.testclient import TestClient

from velmora.domain.models import AuthenticatedUser


def test_list_investments_applies_filters(client: TestClient) -> None:
    response = client.get(
        "/api/v1/investments", params={"risk": "alto", "category": "cdt"}
    )

    assert response.status_code == 200
    assert [item["slug"] for item in response.json()] == ["acciones"]


def test_get_investment_detail_and_missing_slug(client: TestClient) -> None:
    found = client.get("/api/v1/investments/cdt-bancario")
    missing = client.get("/api/v1/investments/no-existe")

    assert found.status_code == 200
    assert found.json()["risk_level"] == "bajo"
    assert missing.status_code == 404


def test_categories_and_lessons_are_public(anonymous_client: TestClient) -> None:
    categories = anonymous_client.get("/api/v1/categories")
    lessons = anonymous_client.get("/api/v1/lessons")

    assert categories.status_code == 200
    assert categories.json()[0]["slug"] == "cdt"
    assert lessons.status_code == 200
    assert lessons.json()[0]["slug"] == "que-es-una-inversion"


def test_recommendations_change_with_profile(client: TestClient) -> None:
    conservative = client.get(
        "/api/v1/investments/recommendations", params={"profile": "conservador"}
    )
    aggressive = client.get(
        "/api/v1/investments/recommendations", params={"profile": "agresivo"}
    )

    assert conservative.json()[0]["investment"]["slug"] == "cdt-bancario"
    assert aggressive.json()[0]["investment"]["slug"] == "acciones"


def test_current_user_hides_token(client: TestClient, user: AuthenticatedUser) -> None:
    response = client.get("/api/v1/auth/me")

    assert response.status_code == 200
    assert response.json()["id"] == str(user.id)
    assert "token" not in response.json()


def test_protected_routes_require_authentication(
    anonymous_client: TestClient,
) -> None:
    response = anonymous_client.get("/api/v1/investments/mine")

    assert response.status_code == 401


def test_admin_route_rejects_regular_user(client: TestClient) -> None:
    response = client.get("/api/v1/investments/all")

    assert response.status_code == 403


def test_admin_route_allows_admin(admin_client: TestClient) -> None:
    response = admin_client.get("/api/v1/investments/all")

    assert response.status_code == 200
    assert len(response.json()) == 3


def test_lesson_completion_notifies_observers(
    client: TestClient, lesson_id: UUID
) -> None:
    response = client.post(f"/api/v1/lessons/{lesson_id}/complete")

    assert response.status_code == 200
    assert response.json()["lesson_id"] == str(lesson_id)


def test_invalid_amount_returns_422(client: TestClient) -> None:
    response = client.get(
        "/api/v1/investments", params={"min_amount": "-10", "max_amount": "20"}
    )

    assert response.status_code == 422
