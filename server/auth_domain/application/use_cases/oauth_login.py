"""
OAuth Login use case.

Uses the Strategy pattern — the correct IOAuthProvider is selected at
runtime based on the provider name.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from auth_domain.application.dtos import OAuthCallbackRequest, TokenResponse
from auth_domain.domain.entities.refresh_token import RefreshToken
from auth_domain.domain.entities.user import User
from auth_domain.domain.exceptions import OAuthException
from auth_domain.domain.interfaces import (
    IOAuthProvider,
    IRefreshTokenRepository,
    ITokenService,
    IUserRepository,
)
from auth_domain.domain.value_objects import Email, OAuthProvider


class OAuthLoginUseCase:

    REFRESH_TOKEN_TTL_DAYS = 30

    def __init__(
        self,
        user_repo: IUserRepository,
        token_service: ITokenService,
        refresh_token_repo: IRefreshTokenRepository,
        oauth_providers: dict[str, IOAuthProvider],
    ) -> None:
        self._user_repo = user_repo
        self._token_service = token_service
        self._refresh_repo = refresh_token_repo
        self._providers = oauth_providers

    async def get_authorization_url(
        self, provider_name: str, state: str, redirect_uri: str
    ) -> str:
        provider = self._providers.get(provider_name)
        if provider is None:
            raise OAuthException(f"Unsupported OAuth provider: {provider_name}")
        return await provider.get_authorization_url(state, redirect_uri)

    async def execute(
        self,
        request: OAuthCallbackRequest,
        redirect_uri: str,
        ip_address: str | None = None,
    ) -> TokenResponse:
        provider = self._providers.get(request.provider)
        if provider is None:
            raise OAuthException(f"Unsupported OAuth provider: {request.provider}")

        user_info = await provider.exchange_code(request.code, redirect_uri)

        # Check if user already exists via OAuth
        user = await self._user_repo.find_by_oauth(
            provider=request.provider, provider_id=user_info.provider_id
        )

        if user is None:
            # Check if email already registered via local auth
            email = Email(user_info.email)
            existing = await self._user_repo.find_by_email(email)
            if existing is not None:
                raise OAuthException(
                    "An account with this email already exists. "
                    "Please log in with your password and link your social account."
                )

            # Create new OAuth user
            user = User.from_oauth(
                email=email,
                username=user_info.name,
                provider=OAuthProvider(request.provider),
                provider_id=user_info.provider_id,
            )
            await self._user_repo.save(user)

        user.check_account_access()

        # Issue tokens
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
            ip_address=ip_address,
        )
        await self._refresh_repo.save(refresh_entity)

        return TokenResponse(
            access_token=access_token,
            refresh_token=raw_refresh,
            token_type="Bearer",
            expires_in=900,
        )
