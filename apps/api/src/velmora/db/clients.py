from functools import lru_cache

from fastapi import HTTPException
from supabase import Client, create_client

from velmora.core.config import settings


def _require_url() -> None:
    if not settings.supabase_url:
        raise HTTPException(status_code=503, detail="Supabase no configurado")


@lru_cache(maxsize=1)
def anonymous_client() -> Client:
    """Cliente compartido con la clave pública; solo ve lo que RLS permite a anon."""
    _require_url()
    return create_client(settings.supabase_url, settings.supabase_publishable_key)


@lru_cache(maxsize=1)
def admin_client() -> Client:
    """Cliente compartido con la clave secreta; omite RLS. Solo para rutas admin."""
    _require_url()
    return create_client(settings.supabase_url, settings.supabase_secret_key)


def user_client(jwt: str) -> Client:
    """Cliente por petición que actúa como el usuario (RLS con auth.uid()).

    No se comparte entre peticiones porque lleva el JWT del usuario.
    """
    _require_url()
    client = create_client(settings.supabase_url, settings.supabase_publishable_key)
    client.postgrest.auth(jwt)
    return client
