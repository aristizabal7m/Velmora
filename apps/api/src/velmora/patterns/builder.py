from dataclasses import dataclass, field, replace
from decimal import Decimal

from velmora.core.errors import ValidationError
from velmora.domain.models import InvestmentQuery, RiskLevel


def _to_decimal(value: Decimal | int | str) -> Decimal:
    amount = Decimal(str(value))
    if amount < 0:
        raise ValidationError("Los montos no pueden ser negativos")
    return amount


@dataclass(frozen=True)
class InvestmentQueryBuilder:
    _query: InvestmentQuery = field(default_factory=InvestmentQuery)

    def with_risk(self, risk: RiskLevel | str) -> "InvestmentQueryBuilder":
        return replace(
            self,
            _query=self._query.model_copy(
                update={"risk_level": RiskLevel(risk)}
            ),
        )

    def with_category(self, slug: str) -> "InvestmentQueryBuilder":
        return replace(
            self, _query=self._query.model_copy(update={"category_slug": slug})
        )

    def with_min_amount(self, amount: Decimal | int | str) -> "InvestmentQueryBuilder":
        return replace(
            self,
            _query=self._query.model_copy(
                update={"min_amount": _to_decimal(amount)}
            ),
        )

    def with_max_amount(self, amount: Decimal | int | str) -> "InvestmentQueryBuilder":
        return replace(
            self,
            _query=self._query.model_copy(
                update={"max_amount": _to_decimal(amount)}
            ),
        )

    def including_unpublished(self) -> "InvestmentQueryBuilder":
        return replace(
            self,
            _query=self._query.model_copy(update={"published_only": False}),
        )

    def build(self) -> InvestmentQuery:
        minimum = self._query.min_amount
        maximum = self._query.max_amount
        if minimum is not None and maximum is not None and minimum > maximum:
            raise ValidationError("El monto mínimo no puede superar el máximo")
        return self._query
