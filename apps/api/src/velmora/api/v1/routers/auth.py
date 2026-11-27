from fastapi import APIRouter, Depends

from velmora.core.security import get_app_role, get_current_user
from velmora.domain.models import AuthenticatedUser

router = APIRouter(prefix="/auth", tags=["autenticación"])


@router.get("/me")
def current_user(
    user: AuthenticatedUser = Depends(get_current_user),
    role: str = Depends(get_app_role),
) -> AuthenticatedUser:
    return user.model_copy(update={"token": "", "role": role})
