"""SQLAlchemy implementation of IPhoenixFeatherRepository."""

from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from character_domain.domain.entities.phoenix_feather import PhoenixFeather
from character_domain.domain.interfaces.phoenix_feather_repository import (
    IPhoenixFeatherRepository,
)
from character_domain.domain.value_objects.reaper_enums import FeatherStatus
from character_domain.infrastructure.persistence.models.phoenix_feather_model import (
    PhoenixFeatherModel,
)


class SqlAlchemyPhoenixFeatherRepository(IPhoenixFeatherRepository):

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @staticmethod
    def _to_entity(m: PhoenixFeatherModel) -> PhoenixFeather:
        return PhoenixFeather(
            id=m.id,
            user_id=m.user_id,
            character_id=m.character_id,
            status=FeatherStatus(m.status),
            price_paid_stardust=m.price_paid_stardust,
            acquired_at=m.acquired_at,
            used_at=m.used_at,
        )

    @staticmethod
    def _to_model(e: PhoenixFeather) -> PhoenixFeatherModel:
        return PhoenixFeatherModel(
            id=e.id,
            user_id=e.user_id,
            character_id=e.character_id,
            status=e.status.value,
            price_paid_stardust=e.price_paid_stardust,
            acquired_at=e.acquired_at,
            used_at=e.used_at,
        )

    async def save(self, feather: PhoenixFeather) -> None:
        self._session.add(self._to_model(feather))
        await self._session.flush()

    async def update(self, feather: PhoenixFeather) -> None:
        m = await self._session.get(PhoenixFeatherModel, feather.id)
        if m is None:
            raise ValueError(f"PhoenixFeather {feather.id} not found.")
        for attr in (
            "character_id",
            "status",
            "used_at",
        ):
            setattr(m, attr, getattr(feather, attr))
        await self._session.flush()

    async def find_available_for_user(
        self, user_id: uuid.UUID
    ) -> Optional[PhoenixFeather]:
        stmt = (
            select(PhoenixFeatherModel)
            .where(
                PhoenixFeatherModel.user_id == user_id,
                PhoenixFeatherModel.status == FeatherStatus.AVAILABLE.value,
            )
            .limit(1)
        )
        result = await self._session.execute(stmt)
        m = result.scalar_one_or_none()
        return self._to_entity(m) if m else None

    async def find_by_id(self, feather_id: uuid.UUID) -> Optional[PhoenixFeather]:
        m = await self._session.get(PhoenixFeatherModel, feather_id)
        return self._to_entity(m) if m else None

    async def count_available_for_user(self, user_id: uuid.UUID) -> int:
        stmt = select(func.count(PhoenixFeatherModel.id)).where(
            PhoenixFeatherModel.user_id == user_id,
            PhoenixFeatherModel.status == FeatherStatus.AVAILABLE.value,
        )
        result = await self._session.execute(stmt)
        return result.scalar_one()
