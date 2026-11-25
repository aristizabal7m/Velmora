from fastapi import Depends, HTTPException
from supabase import Client, create_client

from velmora.core.config import settings
from velmora.core.security import get_current_user, require_admin
from velmora.domain.models import AuthenticatedUser
from velmora.patterns.abstract_factory import (
    AdminAccessFactory,
    UserAccessFactory,
)
from velmora.patterns.decorator import decorate
from velmora.patterns.observer import (
    ActivityObserver,
    LessonCompletedPublisher,
    ProgressObserver,
)
from velmora.repositories.base import InvestmentRepository
from velmora.repositories.supabase import SupabaseInvestmentRepository
from velmora.services.investments import InvestmentService
from velmora.services.progress import ProgressService


def _anonymous_client() -> Client:
    if not settings.supabase_url:
        raise HTTPException(status_code=503, detail="Supabase no configurado")
    return create_client(
        settings.supabase_url, settings.supabase_publishable_key
    )


def get_public_repository() -> InvestmentRepository:
    return SupabaseInvestmentRepository(_anonymous_client())


def get_investment_service(
    repository: InvestmentRepository = Depends(get_public_repository),
) -> InvestmentService:
    return InvestmentService(repository)


def get_user_repository(
    user: AuthenticatedUser = Depends(get_current_user),
) -> InvestmentRepository:
    factory = UserAccessFactory(user.token)
    return decorate(factory.create_data_access(), scope=str(user.id))


def get_user_investment_service(
    repository: InvestmentRepository = Depends(get_user_repository),
) -> InvestmentService:
    return InvestmentService(repository)


def get_admin_repository(
    _user: AuthenticatedUser = Depends(require_admin),
) -> InvestmentRepository:
    return AdminAccessFactory().create_data_access()


def get_admin_investment_service(
    repository: InvestmentRepository = Depends(get_admin_repository),
) -> InvestmentService:
    return InvestmentService(repository)


def get_progress_service() -> ProgressService:
    publisher = LessonCompletedPublisher()
    publisher.subscribe(ProgressObserver())
    publisher.subscribe(ActivityObserver())
    return ProgressService(publisher)
