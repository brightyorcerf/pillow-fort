"""Logout use case — revokes the provided refresh token."""

from __future__ import annotations

from auth_domain.domain.interfaces import IRefreshTokenRepository, ITokenService


class LogoutUseCase:

    def __init__(
        self,
        token_service: ITokenService,
        refresh_token_repo: IRefreshTokenRepository,
    ) -> None:
        self._token_service = token_service
        self._refresh_repo = refresh_token_repo

    async def execute(self, raw_refresh_token: str) -> dict[str, str]:
        token_hash = self._token_service.hash_refresh_token(raw_refresh_token)
        stored = await self._refresh_repo.find_by_token_hash(token_hash)

        if stored is not None and not stored.is_revoked:
            stored.revoke()
            await self._refresh_repo.update(stored)

        return {"message": "Logged out successfully."}
