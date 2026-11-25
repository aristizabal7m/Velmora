from typing import Protocol

from velmora.domain.models import (
    Investment,
    Recommendation,
    RiskLevel,
    RiskProfile,
)


class RecommendationStrategy(Protocol):
    @property
    def profile(self) -> RiskProfile: ...

    def score(self, investment: Investment) -> float: ...


class ConservativeStrategy:
    @property
    def profile(self) -> RiskProfile:
        return RiskProfile.CONSERVADOR

    def score(self, investment: Investment) -> float:
        return {RiskLevel.BAJO: 1.0, RiskLevel.MEDIO: 0.3, RiskLevel.ALTO: 0.0}[
            investment.risk_level
        ]


class ModerateStrategy:
    @property
    def profile(self) -> RiskProfile:
        return RiskProfile.MODERADO

    def score(self, investment: Investment) -> float:
        return {RiskLevel.BAJO: 0.6, RiskLevel.MEDIO: 1.0, RiskLevel.ALTO: 0.4}[
            investment.risk_level
        ]


class AggressiveStrategy:
    @property
    def profile(self) -> RiskProfile:
        return RiskProfile.AGRESIVO

    def score(self, investment: Investment) -> float:
        return {RiskLevel.BAJO: 0.2, RiskLevel.MEDIO: 0.6, RiskLevel.ALTO: 1.0}[
            investment.risk_level
        ]


class RecommendationContext:
    def __init__(self, strategy: RecommendationStrategy | None = None) -> None:
        self._strategy: RecommendationStrategy = (
            strategy if strategy is not None else ConservativeStrategy()
        )

    def set_strategy(self, strategy: RecommendationStrategy) -> None:
        self._strategy = strategy

    def recommend(
        self, investments: list[Investment], limit: int = 5
    ) -> list[Recommendation]:
        scored = [
            (investment, self._strategy.score(investment))
            for investment in investments
        ]
        scored.sort(key=lambda item: (-item[1], item[0].minimum_amount))
        return [
            Recommendation(
                investment=investment,
                score=score,
                reason=(
                    f"Perfil {self._strategy.profile.value}: "
                    f"riesgo {investment.risk_level.value}"
                ),
            )
            for investment, score in scored[:limit]
        ]
