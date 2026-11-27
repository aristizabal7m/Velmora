from datetime import datetime
from typing import Protocol
from uuid import UUID

from velmora.domain.models import Category, Investment, InvestmentQuery, Lesson


class InvestmentRepository(Protocol):
    def list_investments(self, query: InvestmentQuery) -> list[Investment]: ...

    def get_by_slug(self, slug: str) -> Investment | None: ...

    def list_categories(self) -> list[Category]: ...

    def list_lessons(self) -> list[Lesson]: ...


class ProgressRepository(Protocol):
    def mark_completed(
        self, user_id: UUID, lesson_id: UUID, completed_at: datetime
    ) -> None: ...

    def completed_lesson_ids(self, user_id: UUID) -> list[UUID]: ...


class ProfileRepository(Protocol):
    def get_role(self, user_id: UUID) -> str | None: ...
