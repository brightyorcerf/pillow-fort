"""
Auth domain use-case dependency factories.

Each function is a FastAPI dependency that lazily constructs a single
use case with a request-scoped DB session.  Only the use case needed
by the matched route is ever instantiated.
"""

from __future__ import annotations

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from auth_domain.application.use_cases import (
    ConfirmPasswordResetUseCase,
    GetUserProfileUseCase,
    LoginUserUseCase,
    LogoutUseCase,
    OAuthLoginUseCase,
    RefreshTokensUseCase,
    RegisterUserUseCase,
    RequestPasswordResetUseCase,
    VerifyEmailUseCase,
)
from auth_domain.config.container import Container as AuthContainer
from auth_domain.presentation.dependencies.db_dependencies import (
    get_auth_container,
    get_db_session,
)


async def get_register_use_case(
    session: AsyncSession = Depends(get_db_session),
    container: AuthContainer = Depends(get_auth_container),
) -> RegisterUserUseCase:
    return container.register_use_case(session)


async def get_login_use_case(
    session: AsyncSession = Depends(get_db_session),
    container: AuthContainer = Depends(get_auth_container),
) -> LoginUserUseCase:
    return container.login_use_case(session)


async def get_refresh_use_case(
    session: AsyncSession = Depends(get_db_session),
    container: AuthContainer = Depends(get_auth_container),
) -> RefreshTokensUseCase:
    return container.refresh_use_case(session)


async def get_logout_use_case(
    session: AsyncSession = Depends(get_db_session),
    container: AuthContainer = Depends(get_auth_container),
) -> LogoutUseCase:
    return container.logout_use_case(session)


async def get_verify_email_use_case(
    session: AsyncSession = Depends(get_db_session),
    container: AuthContainer = Depends(get_auth_container),
) -> VerifyEmailUseCase:
    return container.verify_email_use_case(session)


async def get_request_password_reset_use_case(
    session: AsyncSession = Depends(get_db_session),
    container: AuthContainer = Depends(get_auth_container),
) -> RequestPasswordResetUseCase:
    return container.request_password_reset_use_case(session)


async def get_confirm_password_reset_use_case(
    session: AsyncSession = Depends(get_db_session),
    container: AuthContainer = Depends(get_auth_container),
) -> ConfirmPasswordResetUseCase:
    return container.confirm_password_reset_use_case(session)


async def get_oauth_login_use_case(
    session: AsyncSession = Depends(get_db_session),
    container: AuthContainer = Depends(get_auth_container),
) -> OAuthLoginUseCase:
    return container.oauth_login_use_case(session)


async def get_profile_use_case(
    session: AsyncSession = Depends(get_db_session),
    container: AuthContainer = Depends(get_auth_container),
) -> GetUserProfileUseCase:
    return container.get_profile_use_case(session)
