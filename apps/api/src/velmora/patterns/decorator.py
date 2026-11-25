import logging

from velmora.domain.models import Category, Investment, InvestmentQuery, Lesson
from velmora.repositories.base import InvestmentRepository

logger = logging.getLogger("velmora")


class LoggingRepositoryDecorator:
    def __init__(self, wrapped: InvestmentRepository) -> None:
        self._wrapped = wrapped

    def list_investments(self, query: InvestmentQuery) -> list[Investment]:
        logger.info(
            "Consultando inversiones con filtros %s",
            query.model_dump(exclude_none=True),
        )
        return self._wrapped.list_investments(query)

    def get_by_slug(self, slug: str) -> Investment | None:
        logger.info("Consultando inversión %s", slug)
        return self._wrapped.get_by_slug(slug)

    def list_categories(self) -> list[Category]:
        return self._wrapped.list_categories()

    def list_lessons(self) -> list[Lesson]:
        return self._wrapped.list_lessons()


class CachingRepositoryDecorator:
    def __init__(
        self,
        wrapped: InvestmentRepository,
        scope: str,
        cache: dict[str, list[Investment]] | None = None,
    ) -> None:
        self._wrapped = wrapped
        self._scope = scope
        self._cache = cache if cache is not None else {}

    def list_investments(self, query: InvestmentQuery) -> list[Investment]:
        key = f"{self._scope}:{query.model_dump_json()}"
        if key not in self._cache:
            self._cache[key] = self._wrapped.list_investments(query)
        return list(self._cache[key])

    def get_by_slug(self, slug: str) -> Investment | None:
        return self._wrapped.get_by_slug(slug)

    def list_categories(self) -> list[Category]:
        return self._wrapped.list_categories()

    def list_lessons(self) -> list[Lesson]:
        return self._wrapped.list_lessons()


def decorate(
    repository: InvestmentRepository,
    scope: str,
    cache: dict[str, list[Investment]] | None = None,
) -> InvestmentRepository:
    decorated: InvestmentRepository = CachingRepositoryDecorator(
        LoggingRepositoryDecorator(repository), scope, cache
    )
    return decorated
