"""Repository interface for RefreshToken entity."""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from typing import Optional

from auth_domain.domain.entities.refresh_token import RefreshToken


class IRefreshTokenRepository(ABC):

    @abstractmethod
    async def save(self, token: RefreshToken) -> None:
        ...

    @abstractmethod
    async def find_by_token_hash(self, token_hash: str) -> Optional[RefreshToken]:
        ...

    @abstractmethod
    async def revoke_all_for_user(self, user_id: uuid.UUID) -> None:
        """Revoke every active refresh token for a user (e.g. on password change)."""
        ...

    @abstractmethod
    async def update(self, token: RefreshToken) -> None:
        ...

    @abstractmethod
    async def delete_expired(self) -> int:
        """Housekeeping — remove expired tokens. Returns count deleted."""
        ...
