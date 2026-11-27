from datetime import datetime
from typing import cast
from uuid import UUID

from supabase import Client

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


class SupabaseInvestmentRepository(InvestmentRepository):
    def __init__(self, client: Client) -> None:
        self._client = client

    def list_investments(self, query: InvestmentQuery) -> list[Investment]:
        request = self._client.table("investments").select("*")

        if query.published_only:
            request = request.eq("published", True)
        if query.risk_level is not None:
            request = request.eq("risk_level", query.risk_level.value)
        if query.min_amount is not None:
            request = request.gte("minimum_amount", str(query.min_amount))
        if query.max_amount is not None:
            request = request.lte("minimum_amount", str(query.max_amount))
        if query.category_slug is not None:
            categories = self._client.table("categories").select("id").eq(
                "slug", query.category_slug
            ).execute()
            category_rows = cast("list[dict[str, str]]", categories.data)
            category_ids = [row["id"] for row in category_rows]
            if not category_ids:
                return []
            request = request.in_("category_id", category_ids)

        response = request.execute()
        rows = cast("list[dict[str, object]]", response.data)
        return [Investment.model_validate(row) for row in rows]

    def get_by_slug(self, slug: str) -> Investment | None:
        response = (
            self._client.table("investments")
            .select("*")
            .eq("slug", slug)
            .maybe_single()
            .execute()
        )
        if response is None or response.data is None:
            return None
        return Investment.model_validate(cast("dict[str, object]", response.data))

    def list_categories(self) -> list[Category]:
        response = (
            self._client.table("categories")
            .select("*")
            .eq("published", True)
            .execute()
        )
        rows = cast("list[dict[str, object]]", response.data)
        return [Category.model_validate(row) for row in rows]

    def list_lessons(self) -> list[Lesson]:
        response = (
            self._client.table("lessons")
            .select("*")
            .eq("published", True)
            .execute()
        )
        rows = cast("list[dict[str, object]]", response.data)
        return [Lesson.model_validate(row) for row in rows]


class SupabaseProgressRepository(ProgressRepository):
    """Usa el cliente del usuario: RLS limita cada fila a auth.uid()."""

    def __init__(self, client: Client) -> None:
        self._client = client

    def mark_completed(
        self, user_id: UUID, lesson_id: UUID, completed_at: datetime
    ) -> None:
        # ignore_duplicates -> ON CONFLICT DO NOTHING: solo requiere permiso INSERT.
        self._client.table("user_progress").upsert(
            {
                "user_id": str(user_id),
                "lesson_id": str(lesson_id),
                "completed_at": completed_at.isoformat(),
            },
            on_conflict="user_id,lesson_id",
            ignore_duplicates=True,
        ).execute()

    def completed_lesson_ids(self, user_id: UUID) -> list[UUID]:
        response = (
            self._client.table("user_progress")
            .select("lesson_id")
            .eq("user_id", str(user_id))
            .execute()
        )
        rows = cast("list[dict[str, str]]", response.data)
        return [UUID(row["lesson_id"]) for row in rows]


class SupabaseProfileRepository(ProfileRepository):
    def __init__(self, client: Client) -> None:
        self._client = client

    def get_role(self, user_id: UUID) -> str | None:
        response = (
            self._client.table("profiles")
            .select("role")
            .eq("id", str(user_id))
            .maybe_single()
            .execute()
        )
        if response is None or response.data is None:
            return None
        row = cast("dict[str, str]", response.data)
        return row.get("role")

    def get_profile(self, user_id: UUID) -> Profile | None:
        response = (
            self._client.table("profiles")
            .select("id, display_name, role, risk_profile")
            .eq("id", str(user_id))
            .maybe_single()
            .execute()
        )
        if response is None or response.data is None:
            return None
        return Profile.model_validate(cast("dict[str, object]", response.data))

    def set_risk_profile(self, user_id: UUID, risk_profile: RiskProfile) -> Profile:
        # Solo UPDATE/INSERT de columnas permitidas por los grants; RLS exige
        # que la fila sea del propio usuario.
        updated = (
            self._client.table("profiles")
            .update({"risk_profile": risk_profile.value})
            .eq("id", str(user_id))
            .execute()
        )
        rows = cast("list[dict[str, object]]", updated.data)
        if not rows:
            # Usuarios creados antes del trigger handle_new_user no tienen fila.
            inserted = (
                self._client.table("profiles")
                .insert({"id": str(user_id), "risk_profile": risk_profile.value})
                .execute()
            )
            rows = cast("list[dict[str, object]]", inserted.data)
        return Profile.model_validate(rows[0])
