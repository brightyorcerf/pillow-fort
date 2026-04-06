"""SQLAlchemy implementation of IHPLogRepository."""

from __future__ import annotations

import uuid
from datetime import date, datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from character_domain.domain.entities.hp_log import HPLog
from character_domain.domain.interfaces.hp_log_repository import IHPLogRepository
from character_domain.domain.value_objects.hp_change_result import HPChangeReason
from character_domain.infrastructure.persistence.models.hp_log_model import HPLogModel


class SqlAlchemyHPLogRepository(IHPLogRepository):

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @staticmethod
    def _to_entity(m: HPLogModel) -> HPLog:
        return HPLog(
            id=m.id,
            character_id=m.character_id,
            old_hp=m.old_hp,
            new_hp=m.new_hp,
            delta=m.delta,
            reason=HPChangeReason(m.reason),
            description=m.description,
            shield_used=m.shield_used,
            triggered_death=m.triggered_death,
            created_at=m.created_at,
        )

    @staticmethod
    def _to_model(e: HPLog) -> HPLogModel:
        return HPLogModel(
            id=e.id,
            character_id=e.character_id,
            old_hp=e.old_hp,
            new_hp=e.new_hp,
            delta=e.delta,
            reason=e.reason.value,
            description=e.description,
            shield_used=e.shield_used,
            triggered_death=e.triggered_death,
            created_at=e.created_at,
        )

    async def create(self, log: HPLog) -> None:
        self._session.add(self._to_model(log))
        await self._session.flush()

    async def get_by_character(
        self, character_id: uuid.UUID, limit: int = 50
    ) -> list[HPLog]:
        stmt = (
            select(HPLogModel)
            .where(HPLogModel.character_id == character_id)
            .order_by(HPLogModel.created_at.desc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]

    async def get_by_reason(
        self, character_id: uuid.UUID, reason: HPChangeReason, limit: int = 20
    ) -> list[HPLog]:
        stmt = (
            select(HPLogModel)
            .where(
                HPLogModel.character_id == character_id,
                HPLogModel.reason == reason.value,
            )
            .order_by(HPLogModel.created_at.desc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]

    async def get_today(self, character_id: uuid.UUID) -> list[HPLog]:
        today_start = datetime.now(timezone.utc).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        stmt = (
            select(HPLogModel)
            .where(
                HPLogModel.character_id == character_id,
                HPLogModel.created_at >= today_start,
            )
            .order_by(HPLogModel.created_at.asc())
        )
        result = await self._session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]

    async def get_for_date_range(
        self, character_id: uuid.UUID, start_date: date, end_date: date
    ) -> list[HPLog]:
        start_dt = datetime.combine(start_date, datetime.min.time()).replace(
            tzinfo=timezone.utc
        )
        end_dt = datetime.combine(end_date, datetime.max.time()).replace(
            tzinfo=timezone.utc
        )
        stmt = (
            select(HPLogModel)
            .where(
                HPLogModel.character_id == character_id,
                HPLogModel.created_at >= start_dt,
                HPLogModel.created_at <= end_dt,
            )
            .order_by(HPLogModel.created_at.asc())
        )
        result = await self._session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]

    async def get_total_delta_today(self, character_id: uuid.UUID) -> int:
        today_start = datetime.now(timezone.utc).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        stmt = select(func.coalesce(func.sum(HPLogModel.delta), 0)).where(
            HPLogModel.character_id == character_id,
            HPLogModel.created_at >= today_start,
        )
        result = await self._session.execute(stmt)
        return result.scalar_one()
