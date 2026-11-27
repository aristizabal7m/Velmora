import logging
import time
from threading import Lock

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


class TTLCache:
    """Caché en memoria con expiración y tamaño máximo (descarta lo más antiguo)."""

    def __init__(self, ttl_seconds: float = 60.0, max_entries: int = 256) -> None:
        self._ttl = ttl_seconds
        self._max_entries = max_entries
        self._entries: dict[str, tuple[float, list[Investment]]] = {}
        self._lock = Lock()

    def get(self, key: str) -> list[Investment] | None:
        with self._lock:
            entry = self._entries.get(key)
            if entry is None:
                return None
            stored_at, value = entry
            if time.monotonic() - stored_at > self._ttl:
                del self._entries[key]
                return None
            return list(value)

    def set(self, key: str, value: list[Investment]) -> None:
        with self._lock:
            self._entries.pop(key, None)
            if len(self._entries) >= self._max_entries:
                oldest = next(iter(self._entries))
                del self._entries[oldest]
            self._entries[key] = (time.monotonic(), list(value))


class CachingRepositoryDecorator:
    def __init__(
        self,
        wrapped: InvestmentRepository,
        scope: str,
        cache: TTLCache | None = None,
    ) -> None:
        self._wrapped = wrapped
        self._scope = scope
        self._cache = cache if cache is not None else TTLCache()

    def list_investments(self, query: InvestmentQuery) -> list[Investment]:
        key = f"{self._scope}:{query.model_dump_json()}"
        cached = self._cache.get(key)
        if cached is not None:
            return cached
        result = self._wrapped.list_investments(query)
        self._cache.set(key, result)
        return list(result)

    def get_by_slug(self, slug: str) -> Investment | None:
        return self._wrapped.get_by_slug(slug)

    def list_categories(self) -> list[Category]:
        return self._wrapped.list_categories()

    def list_lessons(self) -> list[Lesson]:
        return self._wrapped.list_lessons()


def decorate(
    repository: InvestmentRepository,
    scope: str,
    cache: TTLCache | None = None,
) -> InvestmentRepository:
    decorated: InvestmentRepository = CachingRepositoryDecorator(
        LoggingRepositoryDecorator(repository), scope, cache
    )
    return decorated
