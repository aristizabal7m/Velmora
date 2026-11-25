from fastapi import APIRouter, Depends

from velmora.core.security import get_current_user
from velmora.domain.models import AuthenticatedUser

router = APIRouter(prefix="/auth", tags=["autenticación"])


@router.get("/me")
def current_user(
    user: AuthenticatedUser = Depends(get_current_user),
) -> AuthenticatedUser:
    return user.model_copy(update={"token": ""})
