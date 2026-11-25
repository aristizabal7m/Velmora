from velmora.domain.models import (
    Category,
    Investment,
    InvestmentQuery,
    Lesson,
)
from velmora.repositories.base import InvestmentRepository


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
