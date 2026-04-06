"""SQLAlchemy implementation of IRefreshTokenRepository."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from auth_domain.domain.entities.refresh_token import RefreshToken
from auth_domain.domain.interfaces.refresh_token_repository import IRefreshTokenRepository
from auth_domain.infrastructure.persistence.models.refresh_token_model import RefreshTokenModel


class SqlAlchemyRefreshTokenRepository(IRefreshTokenRepository):

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @staticmethod
    def _to_entity(model: RefreshTokenModel) -> RefreshToken:
        return RefreshToken(
            id=model.id,
            user_id=model.user_id,
            token_hash=model.token_hash,
            device_fingerprint=model.device_fingerprint,
            ip_address=model.ip_address,
            expires_at=model.expires_at,
            is_revoked=model.is_revoked,
            replaced_by=model.replaced_by,
            created_at=model.created_at,
        )

    @staticmethod
    def _to_model(entity: RefreshToken) -> RefreshTokenModel:
        return RefreshTokenModel(
            id=entity.id,
            user_id=entity.user_id,
            token_hash=entity.token_hash,
            device_fingerprint=entity.device_fingerprint,
            ip_address=entity.ip_address,
            expires_at=entity.expires_at,
            is_revoked=entity.is_revoked,
            replaced_by=entity.replaced_by,
            created_at=entity.created_at,
        )

    async def save(self, token: RefreshToken) -> None:
        model = self._to_model(token)
        self._session.add(model)
        await self._session.flush()

    async def find_by_token_hash(self, token_hash: str) -> Optional[RefreshToken]:
        stmt = select(RefreshTokenModel).where(
            RefreshTokenModel.token_hash == token_hash
        )
        result = await self._session.execute(stmt)
        row = result.scalar_one_or_none()
        return self._to_entity(row) if row else None

    async def revoke_all_for_user(self, user_id: uuid.UUID) -> None:
        stmt = (
            update(RefreshTokenModel)
            .where(
                RefreshTokenModel.user_id == user_id,
                RefreshTokenModel.is_revoked == False,  # noqa: E712
            )
            .values(is_revoked=True)
        )
        await self._session.execute(stmt)

    async def update(self, token: RefreshToken) -> None:
        model = await self._session.get(RefreshTokenModel, token.id)
        if model is None:
            raise ValueError(f"RefreshToken {token.id} not found.")
        model.is_revoked = token.is_revoked
        model.replaced_by = token.replaced_by
        await self._session.flush()

    async def delete_expired(self) -> int:
        stmt = delete(RefreshTokenModel).where(
            RefreshTokenModel.expires_at < datetime.now(timezone.utc)
        )
        result = await self._session.execute(stmt)
        return result.rowcount  # type: ignore[return-value]
