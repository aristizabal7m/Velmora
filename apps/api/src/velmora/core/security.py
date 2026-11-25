import logging
from functools import lru_cache
from uuid import UUID

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import PyJWKClient

from velmora.core.config import settings
from velmora.domain.models import AuthenticatedUser

logger = logging.getLogger("velmora")
_bearer = HTTPBearer(auto_error=False)


@lru_cache
def _jwks_client(url: str) -> PyJWKClient:
    return PyJWKClient(url)


def verify_token(token: str) -> AuthenticatedUser:
    if not settings.supabase_url or not settings.jwks_url:
        logger.error("La verificación JWT requiere SUPABASE_URL y JWKS")
        raise HTTPException(status_code=503, detail="Autenticación no configurada")

    try:
        signing_key = _jwks_client(settings.jwks_url).get_signing_key_from_jwt(token)
        claims = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256", "ES256"],
            audience="authenticated",
            issuer=f"{settings.supabase_url}/auth/v1",
            options={"require": ["exp", "sub", "iss", "aud"]},
        )
        email = claims.get("email")
        return AuthenticatedUser(
            id=UUID(str(claims["sub"])),
            role=str(claims.get("role", "authenticated")),
            email=str(email) if email is not None else None,
            token=token,
        )
    except (jwt.PyJWTError, ValueError, KeyError, TypeError) as exc:
        logger.info("Token JWT rechazado: %s", type(exc).__name__)
        raise HTTPException(status_code=401, detail="Credenciales inválidas") from exc


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> AuthenticatedUser:
    if credentials is None:
        raise HTTPException(status_code=401, detail="Credenciales ausentes")
    return verify_token(credentials.credentials)


def require_admin(
    user: AuthenticatedUser = Depends(get_current_user),
) -> AuthenticatedUser:
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Permisos insuficientes")
    return user
