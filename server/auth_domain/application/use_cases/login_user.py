"""
Login User use case.

Security measures:
  - Constant-time password comparison (via argon2)
  - Account lockout after N failed attempts
  - Records device fingerprint and IP for refresh token binding
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from auth_domain.application.dtos import LoginRequest, TokenResponse
from auth_domain.domain.entities.refresh_token import RefreshToken
from auth_domain.domain.exceptions import (
    InvalidCredentialsException,
    UserNotFoundException,
)
from auth_domain.domain.interfaces import (
    IEventPublisher,
    IPasswordHasher,
    IRefreshTokenRepository,
    ITokenService,
    IUserRepository,
)
from auth_domain.domain.value_objects import Email


class LoginUserUseCase:

    REFRESH_TOKEN_TTL_DAYS = 30

    def __init__(
        self,
        user_repo: IUserRepository,
        token_service: ITokenService,
        password_hasher: IPasswordHasher,
        refresh_token_repo: IRefreshTokenRepository,
        event_publisher: IEventPublisher,
    ) -> None:
        self._user_repo = user_repo
        self._token_service = token_service
        self._hasher = password_hasher
        self._refresh_repo = refresh_token_repo
        self._event_publisher = event_publisher

    async def execute(
        self,
        request: LoginRequest,
        ip_address: str | None = None,
    ) -> TokenResponse:
        email = Email(request.email)
        user = await self._user_repo.find_by_email(email)

        if user is None:
            raise UserNotFoundException("Invalid email or password.")

        user.check_account_access()

        if user.hashed_password is None:
            raise InvalidCredentialsException(
                "This account uses social login. Please sign in with your OAuth provider."
            )

        if not self._hasher.verify(request.password, user.hashed_password):
            user.record_failed_login()
            await self._user_repo.update(user)
            raise InvalidCredentialsException("Invalid email or password.")

        # Successful login
        user.record_successful_login()
        await self._user_repo.update(user)

        # Create token pair
        access_token = self._token_service.create_access_token(
            user_id=user.id, roles=user.roles
        )
        raw_refresh = self._token_service.create_refresh_token()
        refresh_hash = self._token_service.hash_refresh_token(raw_refresh)

        refresh_entity = RefreshToken.create(
            user_id=user.id,
            token_hash=refresh_hash,
            expires_at=datetime.now(timezone.utc)
            + timedelta(days=self.REFRESH_TOKEN_TTL_DAYS),
            device_fingerprint=request.device_fingerprint,
            ip_address=ip_address,
        )
        await self._refresh_repo.save(refresh_entity)

        await self._event_publisher.publish_all(user.domain_events)
        user.clear_events()

        return TokenResponse(
            access_token=access_token,
            refresh_token=raw_refresh,
            token_type="Bearer",
            expires_in=900,
        )
