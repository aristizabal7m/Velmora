from uuid import UUID

from velmora.core.errors import PreconditionError
from velmora.domain.models import Lesson, MyProfile, Recommendation, RiskProfile
from velmora.repositories.base import ProfileRepository, ProgressRepository
from velmora.services.investments import InvestmentService

# Lección que enseña la relación riesgo/rentabilidad. Completarla habilita
# la elección del perfil de riesgo, que a su vez elige la estrategia de
# recomendación (patrón Strategy).
RISK_LESSON_SLUG = "riesgo-y-rentabilidad"


class ProfileService:
    def __init__(
        self,
        profiles: ProfileRepository,
        progress: ProgressRepository,
        catalog: InvestmentService,
    ) -> None:
        self._profiles = profiles
        self._progress = progress
        self._catalog = catalog

    def overview(self, user_id: UUID) -> MyProfile:
        lessons = self._catalog.lessons()
        published_ids = {lesson.id for lesson in lessons}
        completed = set(self._progress.completed_lesson_ids(user_id)) & published_ids
        risk_lesson = _risk_lesson(lessons)
        # Si la lección no existe (o no está publicada) no se bloquea al usuario.
        can_choose = risk_lesson is None or risk_lesson.id in completed

        profile = self._profiles.get_profile(user_id)
        return MyProfile(
            id=user_id,
            display_name=profile.display_name if profile else None,
            role=profile.role if profile else "user",
            risk_profile=profile.risk_profile if profile else None,
            completed_lessons=len(completed),
            total_lessons=len(lessons),
            risk_lesson_id=risk_lesson.id if risk_lesson else None,
            can_choose_risk_profile=can_choose,
        )

    def choose_risk_profile(self, user_id: UUID, risk: RiskProfile) -> MyProfile:
        if not self.overview(user_id).can_choose_risk_profile:
            raise PreconditionError(
                "Completa la lección «Riesgo y rentabilidad» para definir tu perfil"
            )
        self._profiles.set_risk_profile(user_id, risk)
        return self.overview(user_id)

    def recommendations(self, user_id: UUID) -> list[Recommendation]:
        profile = self._profiles.get_profile(user_id)
        if profile is None or profile.risk_profile is None:
            raise PreconditionError("Aún no has definido tu perfil de riesgo")
        return self._catalog.recommendations(profile.risk_profile)


def _risk_lesson(lessons: list[Lesson]) -> Lesson | None:
    return next((lesson for lesson in lessons if lesson.slug == RISK_LESSON_SLUG), None)
