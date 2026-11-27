from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from velmora.api.deps import get_investment_service, get_progress_service
from velmora.core.security import get_current_user
from velmora.domain.models import AuthenticatedUser
from velmora.patterns.observer import LessonCompleted
from velmora.services.investments import InvestmentService
from velmora.services.progress import ProgressService

router = APIRouter(prefix="/lessons", tags=["lecciones"])


@router.post("/{lesson_id}/complete")
def complete_lesson(
    lesson_id: UUID,
    user: AuthenticatedUser = Depends(get_current_user),
    progress: ProgressService = Depends(get_progress_service),
    investments: InvestmentService = Depends(get_investment_service),
) -> LessonCompleted:
    if not any(lesson.id == lesson_id for lesson in investments.lessons()):
        raise HTTPException(status_code=404, detail="Lección no encontrada")
    return progress.complete(user.id, lesson_id)


@router.get("/progress")
def lesson_progress(
    user: AuthenticatedUser = Depends(get_current_user),
    progress: ProgressService = Depends(get_progress_service),
) -> list[UUID]:
    return progress.completed_lesson_ids(user.id)
