from typing import Protocol

from supabase import Client


class StorageAccess(Protocol):
    def public_url(self, bucket: str, path: str) -> str: ...


class SupabaseStorageAdapter:
    def __init__(self, client: Client) -> None:
        self._client = client

    def public_url(self, bucket: str, path: str) -> str:
        return str(self._client.storage.from_(bucket).get_public_url(path))


class InMemoryStorageAdapter:
    def __init__(self, base_url: str = "http://storage.local") -> None:
        self._base_url = base_url.rstrip("/")

    def public_url(self, bucket: str, path: str) -> str:
        return f"{self._base_url}/{bucket}/{path}"
