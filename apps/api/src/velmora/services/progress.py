from datetime import UTC, datetime
from uuid import UUID

from velmora.patterns.observer import (
    LessonCompleted,
    LessonCompletedPublisher,
)
from velmora.repositories.base import ProgressRepository


class ProgressService:
    def __init__(
        self, publisher: LessonCompletedPublisher, repository: ProgressRepository
    ) -> None:
        self._publisher = publisher
        self._repository = repository

    def complete(self, user_id: UUID, lesson_id: UUID) -> LessonCompleted:
        event = LessonCompleted(
            user_id=user_id,
            lesson_id=lesson_id,
            completed_at=datetime.now(UTC),
        )
        self._publisher.notify(event)
        return event

    def completed_lesson_ids(self, user_id: UUID) -> list[UUID]:
        return self._repository.completed_lesson_ids(user_id)
