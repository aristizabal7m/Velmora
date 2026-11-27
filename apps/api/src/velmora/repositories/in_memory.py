from datetime import datetime
from uuid import UUID

from velmora.domain.models import (
    Category,
    Investment,
    InvestmentQuery,
    Lesson,
    Profile,
    RiskProfile,
)
from velmora.repositories.base import (
    InvestmentRepository,
    ProfileRepository,
    ProgressRepository,
)


class InMemoryInvestmentRepository(InvestmentRepository):
    def __init__(
        self,
        investments: list[Investment] | None = None,
        categories: list[Category] | None = None,
        lessons: list[Lesson] | None = None,
    ) -> None:
        self._investments = investments or []
        self._categories = categories or []
        self._lessons = lessons or []

    def list_investments(self, query: InvestmentQuery) -> list[Investment]:
        category_ids: set[str] | None = None
        if query.category_slug is not None:
            category_ids = {
                str(category.id)
                for category in self._categories
                if category.slug == query.category_slug
            }

        return [
            investment
            for investment in self._investments
            if (not query.published_only or investment.published)
            and (
                query.risk_level is None
                or investment.risk_level == query.risk_level
            )
            and (
                category_ids is None
                or str(investment.category_id) in category_ids
            )
            and (
                query.min_amount is None
                or investment.minimum_amount >= query.min_amount
            )
            and (
                query.max_amount is None
                or investment.minimum_amount <= query.max_amount
            )
        ]

    def get_by_slug(self, slug: str) -> Investment | None:
        return next(
            (item for item in self._investments if item.slug == slug),
            None,
        )

    def list_categories(self) -> list[Category]:
        return [category for category in self._categories if category.published]

    def list_lessons(self) -> list[Lesson]:
        return [lesson for lesson in self._lessons if lesson.published]


class InMemoryProgressRepository(ProgressRepository):
    def __init__(self) -> None:
        self._completed: dict[tuple[UUID, UUID], datetime] = {}

    def mark_completed(
        self, user_id: UUID, lesson_id: UUID, completed_at: datetime
    ) -> None:
        self._completed.setdefault((user_id, lesson_id), completed_at)

    def completed_lesson_ids(self, user_id: UUID) -> list[UUID]:
        return [lesson for (owner, lesson) in self._completed if owner == user_id]


class InMemoryProfileRepository(ProfileRepository):
    def __init__(self, roles: dict[UUID, str] | None = None) -> None:
        self._profiles = {
            user_id: Profile(id=user_id, role=role)
            for user_id, role in (roles or {}).items()
        }

    def get_role(self, user_id: UUID) -> str | None:
        profile = self._profiles.get(user_id)
        return profile.role if profile is not None else None

    def get_profile(self, user_id: UUID) -> Profile | None:
        return self._profiles.get(user_id)

    def set_risk_profile(self, user_id: UUID, risk_profile: RiskProfile) -> Profile:
        current = self._profiles.get(user_id, Profile(id=user_id))
        updated = current.model_copy(update={"risk_profile": risk_profile})
        self._profiles[user_id] = updated
        return updated
