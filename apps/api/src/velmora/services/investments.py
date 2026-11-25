from decimal import Decimal

from velmora.domain.models import (
    Category,
    Investment,
    InvestmentQuery,
    Lesson,
    Recommendation,
    RiskLevel,
    RiskProfile,
)
from velmora.patterns.builder import InvestmentQueryBuilder
from velmora.patterns.strategy import (
    AggressiveStrategy,
    ConservativeStrategy,
    ModerateStrategy,
    RecommendationContext,
    RecommendationStrategy,
)
from velmora.repositories.base import InvestmentRepository


def _strategy_for(profile: RiskProfile) -> RecommendationStrategy:
    strategies: dict[RiskProfile, RecommendationStrategy] = {
        RiskProfile.CONSERVADOR: ConservativeStrategy(),
        RiskProfile.MODERADO: ModerateStrategy(),
        RiskProfile.AGRESIVO: AggressiveStrategy(),
    }
    return strategies[profile]


class InvestmentService:
    def __init__(self, repository: InvestmentRepository) -> None:
        self._repository = repository

    def search(
        self,
        risk: RiskLevel | None = None,
        category: str | None = None,
        min_amount: Decimal | None = None,
        max_amount: Decimal | None = None,
    ) -> list[Investment]:
        builder = InvestmentQueryBuilder()
        if risk is not None:
            builder = builder.with_risk(risk)
        if category is not None:
            builder = builder.with_category(category)
        if min_amount is not None:
            builder = builder.with_min_amount(min_amount)
        if max_amount is not None:
            builder = builder.with_max_amount(max_amount)
        return self._repository.list_investments(builder.build())

    def detail(self, slug: str) -> Investment | None:
        return self._repository.get_by_slug(slug)

    def categories(self) -> list[Category]:
        return self._repository.list_categories()

    def lessons(self) -> list[Lesson]:
        return self._repository.list_lessons()

    def recommendations(self, profile: RiskProfile) -> list[Recommendation]:
        context = RecommendationContext(_strategy_for(profile))
        investments = self._repository.list_investments(InvestmentQuery())
        return context.recommend(investments)
