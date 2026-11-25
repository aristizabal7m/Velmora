from abc import ABC, abstractmethod
from dataclasses import replace
from typing import Protocol

from supabase import Client, create_client

from velmora.core.config import settings
from velmora.core.errors import ValidationError
from velmora.domain.models import (
    Category,
    Investment,
    InvestmentQuery,
    Lesson,
)
from velmora.patterns.adapter import StorageAccess, SupabaseStorageAdapter
from velmora.repositories.base import InvestmentRepository
from velmora.repositories.supabase import SupabaseInvestmentRepository


class DataAccess(Protocol):
    def list_investments(self, query: InvestmentQuery) -> list[Investment]: ...

    def get_by_slug(self, slug: str) -> Investment | None: ...

    def list_categories(self) -> list[Category]: ...

    def list_lessons(self) -> list[Lesson]: ...


class UserDataAccess:
    def __init__(self, repository: InvestmentRepository) -> None:
        self._repository = repository

    def list_investments(self, query: InvestmentQuery) -> list[Investment]:
        return self._repository.list_investments(query)

    def get_by_slug(self, slug: str) -> Investment | None:
        return self._repository.get_by_slug(slug)

    def list_categories(self) -> list[Category]:
        return self._repository.list_categories()

    def list_lessons(self) -> list[Lesson]:
        return self._repository.list_lessons()


class AdminDataAccess:
    def __init__(self, repository: InvestmentRepository) -> None:
        self._repository = repository

    def list_investments(self, query: InvestmentQuery) -> list[Investment]:
        return self._repository.list_investments(replace(query, published_only=False))

    def get_by_slug(self, slug: str) -> Investment | None:
        return self._repository.get_by_slug(slug)

    def list_categories(self) -> list[Category]:
        return self._repository.list_categories()

    def list_lessons(self) -> list[Lesson]:
        return self._repository.list_lessons()


class UserStorageAccess:
    def __init__(self, adapter: StorageAccess) -> None:
        self._adapter = adapter

    def public_url(self, bucket: str, path: str) -> str:
        if bucket == "avatars":
            raise ValidationError("Los avatares son privados")
        return self._adapter.public_url(bucket, path)


class AdminStorageAccess:
    def __init__(self, adapter: StorageAccess) -> None:
        self._adapter = adapter

    def public_url(self, bucket: str, path: str) -> str:
        return self._adapter.public_url(bucket, path)


class AccessFactory(ABC):
    @abstractmethod
    def create_data_access(self) -> DataAccess: ...

    @abstractmethod
    def create_storage_access(self) -> StorageAccess: ...


class UserAccessFactory(AccessFactory):
    def __init__(self, jwt: str) -> None:
        client = create_client(
            settings.supabase_url, settings.supabase_publishable_key
        )
        client.postgrest.auth(jwt)
        self._client: Client = client

    def create_data_access(self) -> DataAccess:
        return UserDataAccess(SupabaseInvestmentRepository(self._client))

    def create_storage_access(self) -> StorageAccess:
        return UserStorageAccess(SupabaseStorageAdapter(self._client))


class AdminAccessFactory(AccessFactory):
    def __init__(self) -> None:
        if not settings.supabase_secret_key:
            raise ValidationError("Falta la credencial administrativa de Supabase")
        self._client: Client = create_client(
            settings.supabase_url, settings.supabase_secret_key
        )

    def create_data_access(self) -> DataAccess:
        return AdminDataAccess(SupabaseInvestmentRepository(self._client))

    def create_storage_access(self) -> StorageAccess:
        return AdminStorageAccess(SupabaseStorageAdapter(self._client))
