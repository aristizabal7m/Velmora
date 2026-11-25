from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException

from velmora.api.deps import (
    get_admin_investment_service,
    get_investment_service,
    get_user_investment_service,
)
from velmora.core.errors import ValidationError
from velmora.domain.models import (
    Investment,
    Recommendation,
    RiskLevel,
    RiskProfile,
)
from velmora.services.investments import InvestmentService

router = APIRouter(prefix="/investments", tags=["inversiones"])


@router.get("")
def list_investments(
    risk: RiskLevel | None = None,
    category: str | None = None,
    min_amount: Decimal | None = None,
    max_amount: Decimal | None = None,
    service: InvestmentService = Depends(get_investment_service),
) -> list[Investment]:
    try:
        return service.search(risk, category, min_amount, max_amount)
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/recommendations")
def recommendations(
    profile: RiskProfile = RiskProfile.MODERADO,
    service: InvestmentService = Depends(get_investment_service),
) -> list[Recommendation]:
    return service.recommendations(profile)


@router.get("/mine")
def list_for_user(
    service: InvestmentService = Depends(get_user_investment_service),
) -> list[Investment]:
    return service.search()


@router.get("/all")
def list_all_for_admin(
    service: InvestmentService = Depends(get_admin_investment_service),
) -> list[Investment]:
    return service.search()


@router.get("/{slug}")
def get_investment(
    slug: str,
    service: InvestmentService = Depends(get_investment_service),
) -> Investment:
    investment = service.detail(slug)
    if investment is None:
        raise HTTPException(status_code=404, detail="Inversión no encontrada")
    return investment
