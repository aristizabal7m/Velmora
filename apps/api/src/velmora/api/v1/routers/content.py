from fastapi import APIRouter, Depends

from velmora.api.deps import get_investment_service
from velmora.domain.models import Category, Lesson
from velmora.services.investments import InvestmentService

router = APIRouter(tags=["contenido"])


@router.get("/categories")
def list_categories(
    service: InvestmentService = Depends(get_investment_service),
) -> list[Category]:
    return service.categories()


@router.get("/lessons")
def list_lessons(
    service: InvestmentService = Depends(get_investment_service),
) -> list[Lesson]:
    return service.lessons()
