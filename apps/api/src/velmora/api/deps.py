from fastapi import Depends

from velmora.core.security import (
    get_current_user,
    get_profile_repository,
    require_admin,
)
from velmora.db.clients import anonymous_client, user_client
from velmora.domain.models import AuthenticatedUser
from velmora.patterns.abstract_factory import (
    AdminAccessFactory,
    DataAccess,
    UserAccessFactory,
)
from velmora.patterns.decorator import TTLCache, decorate
from velmora.patterns.observer import (
    ActivityObserver,
    LessonCompletedPublisher,
    PersistentProgressObserver,
)
from velmora.repositories.base import (
    InvestmentRepository,
    ProfileRepository,
    ProgressRepository,
)
from velmora.repositories.supabase import (
    SupabaseInvestmentRepository,
    SupabaseProgressRepository,
)
from velmora.services.investments import InvestmentService
from velmora.services.profile import ProfileService
from velmora.services.progress import ProgressService

# Cachés de proceso: sobreviven entre peticiones dentro de la misma instancia.
_PUBLIC_CACHE = TTLCache(ttl_seconds=60, max_entries=256)
_USER_CACHE = TTLCache(ttl_seconds=60, max_entries=512)


def get_public_repository() -> InvestmentRepository:
    return decorate(
        SupabaseInvestmentRepository(anonymous_client()),
        scope="public",
        cache=_PUBLIC_CACHE,
    )


def get_investment_service(
    repository: InvestmentRepository = Depends(get_public_repository),
) -> InvestmentService:
    return InvestmentService(repository)


def get_user_repository(
    user: AuthenticatedUser = Depends(get_current_user),
) -> InvestmentRepository:
    factory = UserAccessFactory(user.token)
    return decorate(
        factory.create_data_access(), scope=f"user:{user.id}", cache=_USER_CACHE
    )


def get_user_investment_service(
    repository: InvestmentRepository = Depends(get_user_repository),
) -> InvestmentService:
    return InvestmentService(repository)


def get_admin_data_access() -> DataAccess:
    return AdminAccessFactory().create_data_access()


def get_admin_repository(
    _user: AuthenticatedUser = Depends(require_admin),
    data_access: DataAccess = Depends(get_admin_data_access),
) -> InvestmentRepository:
    return data_access


def get_admin_investment_service(
    repository: InvestmentRepository = Depends(get_admin_repository),
) -> InvestmentService:
    return InvestmentService(repository)


def get_progress_repository(
    user: AuthenticatedUser = Depends(get_current_user),
) -> ProgressRepository:
    return SupabaseProgressRepository(user_client(user.token))


def get_progress_service(
    repository: ProgressRepository = Depends(get_progress_repository),
) -> ProgressService:
    publisher = LessonCompletedPublisher()
    publisher.subscribe(PersistentProgressObserver(repository))
    publisher.subscribe(ActivityObserver())
    return ProgressService(publisher, repository)


def get_profile_service(
    profiles: ProfileRepository = Depends(get_profile_repository),
    progress: ProgressRepository = Depends(get_progress_repository),
    catalog: InvestmentService = Depends(get_investment_service),
) -> ProfileService:
    return ProfileService(profiles, progress, catalog)
