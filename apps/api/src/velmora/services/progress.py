from datetime import UTC, datetime
from uuid import UUID

from velmora.patterns.observer import (
    LessonCompleted,
    LessonCompletedPublisher,
)


class ProgressService:
    def __init__(self, publisher: LessonCompletedPublisher) -> None:
        self._publisher = publisher

    def complete(self, user_id: UUID, lesson_id: UUID) -> LessonCompleted:
        event = LessonCompleted(
            user_id=user_id,
            lesson_id=lesson_id,
            completed_at=datetime.now(UTC),
        )
        self._publisher.notify(event)
        return event
