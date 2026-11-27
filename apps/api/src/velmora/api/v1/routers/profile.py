from fastapi import APIRouter, Depends

from velmora.api.deps import get_profile_service
from velmora.core.security import get_current_user
from velmora.domain.models import AuthenticatedUser, MyProfile, RiskProfileUpdate
from velmora.services.profile import ProfileService

router = APIRouter(prefix="/profile", tags=["perfil"])


@router.get("")
def my_profile(
    user: AuthenticatedUser = Depends(get_current_user),
    profiles: ProfileService = Depends(get_profile_service),
) -> MyProfile:
    return profiles.overview(user.id)


@router.put("/risk-profile")
def choose_risk_profile(
    body: RiskProfileUpdate,
    user: AuthenticatedUser = Depends(get_current_user),
    profiles: ProfileService = Depends(get_profile_service),
) -> MyProfile:
    """Guarda el perfil de riesgo; requiere la lección de riesgo completada."""
    return profiles.choose_risk_profile(user.id, body.risk_profile)
