from collections.abc import Iterator
from decimal import Decimal
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient

from velmora.api.deps import (
    get_admin_repository,
    get_investment_service,
    get_user_repository,
)
from velmora.core.security import get_current_user
from velmora.domain.models import (
    AuthenticatedUser,
    Category,
    Investment,
    Lesson,
    RiskLevel,
)
from velmora.main import app
from velmora.repositories.in_memory import InMemoryInvestmentRepository
from velmora.services.investments import InvestmentService


@pytest.fixture
def category() -> Category:
    return Category(id=uuid4(), name="CDT", slug="cdt", published=True)


@pytest.fixture
def repository(category: Category) -> InMemoryInvestmentRepository:
    investments = [
        Investment(
            id=uuid4(),
            name="CDT bancario",
            slug="cdt-bancario",
            summary="Tasa fija",
            minimum_amount=Decimal("100000"),
            risk_level=RiskLevel.BAJO,
            category_id=category.id,
            published=True,
            disclaimer="No garantiza rendimientos.",
        ),
        Investment(
            id=uuid4(),
            name="FIC moderado",
            slug="fic-moderado",
            summary="Fondo colectivo",
            minimum_amount=Decimal("500000"),
            risk_level=RiskLevel.MEDIO,
            category_id=category.id,
            published=True,
            disclaimer="No garantiza rendimientos.",
        ),
        Investment(
            id=uuid4(),
            name="Acciones",
            slug="acciones",
            summary="Renta variable",
            minimum_amount=Decimal("1000000"),
            risk_level=RiskLevel.ALTO,
            category_id=category.id,
            published=True,
            disclaimer="No garantiza rendimientos.",
        ),
    ]
    lessons = [
        Lesson(
            id=uuid4(),
            title="Qué es una inversión",
            slug="que-es-una-inversion",
            content="Texto",
        )
    ]
    return InMemoryInvestmentRepository(investments, [category], lessons)


@pytest.fixture
def user() -> AuthenticatedUser:
    return AuthenticatedUser(id=uuid4(), role="authenticated", token="token-de-prueba")


@pytest.fixture
def client(
    repository: InMemoryInvestmentRepository, user: AuthenticatedUser
) -> Iterator[TestClient]:
    app.dependency_overrides[get_investment_service] = (
        lambda: InvestmentService(repository)
    )
    app.dependency_overrides[get_user_repository] = lambda: repository
    app.dependency_overrides[get_current_user] = lambda: user
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def admin_client(
    repository: InMemoryInvestmentRepository, user: AuthenticatedUser
) -> Iterator[TestClient]:
    admin = user.model_copy(update={"role": "admin"})
    app.dependency_overrides[get_investment_service] = (
        lambda: InvestmentService(repository)
    )
    app.dependency_overrides[get_admin_repository] = lambda: repository
    app.dependency_overrides[get_current_user] = lambda: admin
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def anonymous_client(repository: InMemoryInvestmentRepository) -> Iterator[TestClient]:
    app.dependency_overrides[get_investment_service] = (
        lambda: InvestmentService(repository)
    )
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def lesson_id(repository: InMemoryInvestmentRepository) -> UUID:
    return repository.list_lessons()[0].id
