from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

import pytest

from velmora.core.config import settings
from velmora.core.errors import ValidationError
from velmora.domain.models import (
    Category,
    Investment,
    InvestmentQuery,
    Lesson,
    RiskLevel,
)
from velmora.patterns.abstract_factory import (
    AccessFactory,
    AdminAccessFactory,
    AdminDataAccess,
    AdminStorageAccess,
    DataAccess,
    UserDataAccess,
    UserStorageAccess,
)
from velmora.patterns.adapter import InMemoryStorageAdapter, StorageAccess
from velmora.patterns.builder import InvestmentQueryBuilder
from velmora.patterns.decorator import TTLCache, decorate
from velmora.patterns.observer import (
    ActivityObserver,
    LessonCompleted,
    LessonCompletedPublisher,
    ProgressObserver,
)
from velmora.patterns.strategy import (
    AggressiveStrategy,
    ConservativeStrategy,
    RecommendationContext,
)
from velmora.repositories.base import InvestmentRepository
from velmora.repositories.in_memory import InMemoryInvestmentRepository


class FakeFactory(AccessFactory):
    def create_data_access(self) -> DataAccess:
        return UserDataAccess(InMemoryInvestmentRepository())

    def create_storage_access(self) -> StorageAccess:
        return InMemoryStorageAdapter()


class CountingRepository(InvestmentRepository):
    def __init__(self) -> None:
        self.calls = 0

    def list_investments(self, query: InvestmentQuery) -> list[Investment]:
        self.calls += 1
        return []

    def get_by_slug(self, slug: str) -> Investment | None:
        return None

    def list_categories(self) -> list[Category]:
        return []

    def list_lessons(self) -> list[Lesson]:
        return []


def test_builder_accumulates_filters_without_mutating() -> None:
    builder = InvestmentQueryBuilder().with_risk("medio").with_min_amount(100)
    query = builder.build()

    assert query.risk_level == RiskLevel.MEDIO
    assert query.min_amount == Decimal("100")
    assert builder.build() == query


def test_builder_rejects_invalid_ranges() -> None:
    with pytest.raises(ValidationError):
        InvestmentQueryBuilder().with_min_amount(-1)

    with pytest.raises(ValidationError):
        InvestmentQueryBuilder().with_min_amount(20).with_max_amount(10).build()


def test_abstract_factory_creates_two_related_products() -> None:
    factory = FakeFactory()

    data_access = factory.create_data_access()
    storage_access = factory.create_storage_access()

    assert isinstance(data_access, UserDataAccess)
    assert storage_access.public_url("content-images", "banner.png").endswith(
        "/content-images/banner.png"
    )


def test_storage_privileges_differ_between_families() -> None:
    user_storage = UserStorageAccess(InMemoryStorageAdapter())
    admin_storage = AdminStorageAccess(InMemoryStorageAdapter())

    with pytest.raises(ValidationError):
        user_storage.public_url("avatars", "user/avatar.png")

    assert admin_storage.public_url("avatars", "user/avatar.png").endswith(
        "/avatars/user/avatar.png"
    )


def test_admin_factory_requires_secret(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "supabase_secret_key", "")

    with pytest.raises(ValidationError):
        AdminAccessFactory()


def test_cache_decorator_is_scoped_per_user() -> None:
    repository = CountingRepository()
    first = decorate(repository, "user-a")
    second = decorate(repository, "user-b")
    query = InvestmentQuery()

    first.list_investments(query)
    first.list_investments(query)
    assert repository.calls == 1

    second.list_investments(query)
    assert repository.calls == 2


def test_cache_decorator_expires_entries() -> None:
    repository = CountingRepository()
    cached = decorate(repository, "public", TTLCache(ttl_seconds=0))
    query = InvestmentQuery()

    cached.list_investments(query)
    cached.list_investments(query)

    assert repository.calls == 2


def test_ttl_cache_is_bounded() -> None:
    cache = TTLCache(ttl_seconds=60, max_entries=2)
    for key in ("a", "b", "c"):
        cache.set(key, [])

    assert cache.get("a") is None
    assert cache.get("c") == []


def test_admin_data_access_includes_unpublished(
    repository: InMemoryInvestmentRepository,
) -> None:
    admin = AdminDataAccess(repository)

    assert len(admin.list_investments(InvestmentQuery())) == 4
    assert len(repository.list_investments(InvestmentQuery())) == 3


def test_strategy_can_change_at_runtime(
    repository: InMemoryInvestmentRepository,
) -> None:
    investments = repository.list_investments(InvestmentQuery())
    context = RecommendationContext(ConservativeStrategy())

    assert context.recommend(investments)[0].investment.risk_level == RiskLevel.BAJO

    context.set_strategy(AggressiveStrategy())
    assert context.recommend(investments)[0].investment.risk_level == RiskLevel.ALTO


def test_observer_notifies_all_subscribers() -> None:
    publisher = LessonCompletedPublisher()
    progress = ProgressObserver()
    activity = ActivityObserver()
    publisher.subscribe(progress)
    publisher.subscribe(activity)
    event = LessonCompleted(uuid4(), uuid4(), datetime.now(UTC))

    publisher.notify(event)

    assert progress.events == [event]
    assert str(event.lesson_id) in activity.messages[0]
