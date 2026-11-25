from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class RiskLevel(StrEnum):
    BAJO = "bajo"
    MEDIO = "medio"
    ALTO = "alto"


class RiskProfile(StrEnum):
    CONSERVADOR = "conservador"
    MODERADO = "moderado"
    AGRESIVO = "agresivo"


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class Category(ORMModel):
    id: UUID
    name: str
    slug: str
    description: str | None = None
    published: bool = True


class Investment(ORMModel):
    id: UUID
    name: str
    slug: str
    summary: str
    minimum_amount: Decimal
    risk_level: RiskLevel
    horizon_months: int | None = None
    category_id: UUID | None = None
    published: bool = True
    disclaimer: str


class Lesson(ORMModel):
    id: UUID
    title: str
    slug: str
    content: str
    published: bool = True


class Profile(ORMModel):
    id: UUID
    display_name: str | None = None
    role: str = "user"
    risk_profile: RiskProfile | None = None


class UserProgress(ORMModel):
    id: UUID
    user_id: UUID
    lesson_id: UUID
    completed_at: datetime


class Bookmark(ORMModel):
    id: UUID
    user_id: UUID
    investment_id: UUID
    created_at: datetime


class AuthenticatedUser(ORMModel):
    id: UUID
    role: str = "authenticated"
    email: str | None = None
    token: str = Field(default="", repr=False, exclude=True)


class InvestmentQuery(ORMModel):
    risk_level: RiskLevel | None = None
    category_slug: str | None = None
    min_amount: Decimal | None = None
    max_amount: Decimal | None = None
    published_only: bool = True


class Recommendation(ORMModel):
    investment: Investment
    score: float
    reason: str
