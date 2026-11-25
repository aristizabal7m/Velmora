from dataclasses import dataclass
from datetime import datetime
from typing import Protocol
from uuid import UUID


@dataclass(frozen=True)
class LessonCompleted:
    user_id: UUID
    lesson_id: UUID
    completed_at: datetime


class Observer(Protocol):
    def update(self, event: LessonCompleted) -> None: ...


class ProgressObserver:
    def __init__(self) -> None:
        self.events: list[LessonCompleted] = []

    def update(self, event: LessonCompleted) -> None:
        self.events.append(event)


class ActivityObserver:
    def __init__(self) -> None:
        self.messages: list[str] = []

    def update(self, event: LessonCompleted) -> None:
        self.messages.append(
            f"Lección {event.lesson_id} completada por {event.user_id}"
        )


class LessonCompletedPublisher:
    def __init__(self) -> None:
        self._observers: list[Observer] = []

    def subscribe(self, observer: Observer) -> None:
        self._observers.append(observer)

    def unsubscribe(self, observer: Observer) -> None:
        self._observers.remove(observer)

    def notify(self, event: LessonCompleted) -> None:
        for observer in self._observers:
            observer.update(event)
