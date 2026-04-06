"""SQLAlchemy implementation of IPenanceStreakRepository."""

from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from character_domain.domain.entities.penance_streak import PenanceStreak
from character_domain.domain.interfaces.penance_streak_repository import (
    IPenanceStreakRepository,
)
from character_domain.domain.value_objects.reaper_enums import PenanceStatus
from character_domain.infrastructure.persistence.models.penance_streak_model import (
    PenanceStreakModel,
)


class SqlAlchemyPenanceStreakRepository(IPenanceStreakRepository):

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @staticmethod
    def _to_entity(m: PenanceStreakModel) -> PenanceStreak:
        return PenanceStreak(
            id=m.id,
            character_id=m.character_id,
            death_record_id=m.death_record_id,
            attempt_number=m.attempt_number,
            required_days=m.required_days,
            days_completed=m.days_completed,
            status=PenanceStatus(m.status),
            started_at=m.started_at,
            completed_at=m.completed_at,
            failed_at=m.failed_at,
        )

    @staticmethod
    def _to_model(e: PenanceStreak) -> PenanceStreakModel:
        return PenanceStreakModel(
            id=e.id,
            character_id=e.character_id,
            death_record_id=e.death_record_id,
            attempt_number=e.attempt_number,
            required_days=e.required_days,
            days_completed=e.days_completed,
            status=e.status.value,
            started_at=e.started_at,
            completed_at=e.completed_at,
            failed_at=e.failed_at,
        )

    async def save(self, penance: PenanceStreak) -> None:
        self._session.add(self._to_model(penance))
        await self._session.flush()

    async def update(self, penance: PenanceStreak) -> None:
        m = await self._session.get(PenanceStreakModel, penance.id)
        if m is None:
            raise ValueError(f"PenanceStreak {penance.id} not found.")
        for attr in (
            "days_completed",
            "status",
            "completed_at",
            "failed_at",
        ):
            setattr(m, attr, getattr(penance, attr))
        await self._session.flush()

    async def find_active_for_character(
        self, character_id: uuid.UUID
    ) -> Optional[PenanceStreak]:
        stmt = select(PenanceStreakModel).where(
            PenanceStreakModel.character_id == character_id,
            PenanceStreakModel.status == PenanceStatus.ACTIVE.value,
        )
        result = await self._session.execute(stmt)
        m = result.scalar_one_or_none()
        return self._to_entity(m) if m else None

    async def find_by_id(self, penance_id: uuid.UUID) -> Optional[PenanceStreak]:
        m = await self._session.get(PenanceStreakModel, penance_id)
        return self._to_entity(m) if m else None

    async def count_attempts_for_character(self, character_id: uuid.UUID) -> int:
        stmt = select(func.count(PenanceStreakModel.id)).where(
            PenanceStreakModel.character_id == character_id
        )
        result = await self._session.execute(stmt)
        return result.scalar_one()
