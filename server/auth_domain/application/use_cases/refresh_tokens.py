"""
Refresh Tokens use case — implements token rotation.

Security:
  - Old refresh token is revoked immediately upon use.
  - If a revoked token is presented (replay attack), ALL tokens for that
    user are revoked (automatic compromise detection).
  - New refresh token is issued with a fresh expiry.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from auth_domain.application.dtos import RefreshTokenRequest, TokenResponse
from auth_domain.domain.entities.refresh_token import RefreshToken
from auth_domain.domain.exceptions import (
    InvalidCredentialsException,
    TokenExpiredException,
    TokenRevokedException,
    UserNotFoundException,
)
from auth_domain.domain.interfaces import (
    IRefreshTokenRepository,
    ITokenService,
    IUserRepository,
)


class RefreshTokensUseCase:

    REFRESH_TOKEN_TTL_DAYS = 30

    def __init__(
        self,
        user_repo: IUserRepository,
        token_service: ITokenService,
        refresh_token_repo: IRefreshTokenRepository,
    ) -> None:
        self._user_repo = user_repo
        self._token_service = token_service
        self._refresh_repo = refresh_token_repo

    async def execute(
        self,
        request: RefreshTokenRequest,
        ip_address: str | None = None,
    ) -> TokenResponse:
        token_hash = self._token_service.hash_refresh_token(request.refresh_token)
        stored = await self._refresh_repo.find_by_token_hash(token_hash)

        if stored is None:
            raise InvalidCredentialsException("Invalid refresh token.")

        # Replay detection — if token was already used/revoked, nuke everything
        if stored.is_revoked:
            await self._refresh_repo.revoke_all_for_user(stored.user_id)
            raise TokenRevokedException(
                "Refresh token reuse detected — all sessions revoked."
            )

        if stored.is_expired:
            raise TokenExpiredException("Refresh token has expired.")

        user = await self._user_repo.find_by_id(stored.user_id)
        if user is None:
            raise UserNotFoundException()

        user.check_account_access()

        # Rotate: revoke old, issue new
        new_raw = self._token_service.create_refresh_token()
        new_hash = self._token_service.hash_refresh_token(new_raw)

        new_refresh = RefreshToken.create(
            user_id=user.id,
            token_hash=new_hash,
            expires_at=datetime.now(timezone.utc)
            + timedelta(days=self.REFRESH_TOKEN_TTL_DAYS),
            device_fingerprint=stored.device_fingerprint,
            ip_address=ip_address,
        )

        stored.revoke(replaced_by=new_refresh.id)
        await self._refresh_repo.update(stored)
        await self._refresh_repo.save(new_refresh)

        access_token = self._token_service.create_access_token(
            user_id=user.id, roles=user.roles
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=new_raw,
            token_type="Bearer",
            expires_in=900,
        )
