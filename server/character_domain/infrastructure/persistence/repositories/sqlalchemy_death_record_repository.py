"""SQLAlchemy implementation of IDeathRecordRepository."""

from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from character_domain.domain.entities.death_record import DeathRecord
from character_domain.domain.interfaces.death_record_repository import (
    IDeathRecordRepository,
)
from character_domain.domain.value_objects.reaper_enums import DeathCause
from character_domain.infrastructure.persistence.models.death_record_model import (
    DeathRecordModel,
)


class SqlAlchemyDeathRecordRepository(IDeathRecordRepository):

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @staticmethod
    def _to_entity(m: DeathRecordModel) -> DeathRecord:
        return DeathRecord(
            id=m.id,
            character_id=m.character_id,
            user_id=m.user_id,
            cause=DeathCause(m.cause),
            hp_at_death=m.hp_at_death,
            total_hours_in_life=m.total_hours_in_life,
            consecutive_ghost_days_at_death=m.consecutive_ghost_days_at_death,
            rituals_used_at_death=m.rituals_used_at_death,
            longest_streak_at_death=m.longest_streak_at_death,
            eulogy_generated=m.eulogy_generated,
            is_permanent=m.is_permanent,
            promises_id=m.promises_id,
            died_at=m.died_at,
        )

    @staticmethod
    def _to_model(e: DeathRecord) -> DeathRecordModel:
        return DeathRecordModel(
            id=e.id,
            character_id=e.character_id,
            user_id=e.user_id,
            cause=e.cause.value,
            hp_at_death=e.hp_at_death,
            total_hours_in_life=e.total_hours_in_life,
            consecutive_ghost_days_at_death=e.consecutive_ghost_days_at_death,
            rituals_used_at_death=e.rituals_used_at_death,
            longest_streak_at_death=e.longest_streak_at_death,
            eulogy_generated=e.eulogy_generated,
            is_permanent=e.is_permanent,
            promises_id=e.promises_id,
            died_at=e.died_at,
        )

    async def save(self, record: DeathRecord) -> None:
        self._session.add(self._to_model(record))
        await self._session.flush()

    async def update(self, record: DeathRecord) -> None:
        m = await self._session.get(DeathRecordModel, record.id)
        if m is None:
            raise ValueError(f"DeathRecord {record.id} not found.")
        for attr in (
            "eulogy_generated",
            "is_permanent",
            "promises_id",
        ):
            setattr(m, attr, getattr(record, attr))
        await self._session.flush()

    async def find_by_id(self, record_id: uuid.UUID) -> Optional[DeathRecord]:
        m = await self._session.get(DeathRecordModel, record_id)
        return self._to_entity(m) if m else None

    async def find_latest_for_character(
        self, character_id: uuid.UUID
    ) -> Optional[DeathRecord]:
        stmt = (
            select(DeathRecordModel)
            .where(DeathRecordModel.character_id == character_id)
            .order_by(DeathRecordModel.died_at.desc())
            .limit(1)
        )
        result = await self._session.execute(stmt)
        m = result.scalar_one_or_none()
        return self._to_entity(m) if m else None

    async def find_all_for_character(
        self, character_id: uuid.UUID
    ) -> list[DeathRecord]:
        stmt = (
            select(DeathRecordModel)
            .where(DeathRecordModel.character_id == character_id)
            .order_by(DeathRecordModel.died_at.desc())
        )
        result = await self._session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]

    async def count_for_character(self, character_id: uuid.UUID) -> int:
        stmt = select(func.count(DeathRecordModel.id)).where(
            DeathRecordModel.character_id == character_id
        )
        result = await self._session.execute(stmt)
        return result.scalar_one()
