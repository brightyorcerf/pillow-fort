"""SQLAlchemy implementation of ICovenantRepository."""

from __future__ import annotations

import uuid
from datetime import date, timedelta
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from character_domain.domain.entities.covenant import Covenant, CovenantStatus
from character_domain.domain.interfaces.covenant_repository import ICovenantRepository
from character_domain.domain.value_objects.subject_type import SubjectType
from character_domain.infrastructure.persistence.models.covenant_model import CovenantModel


class SqlAlchemyCovenantRepository(ICovenantRepository):

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @staticmethod
    def _to_entity(m: CovenantModel) -> Covenant:
        return Covenant(
            id=m.id,
            character_id=m.character_id,
            covenant_date=m.covenant_date,
            subject_type=SubjectType(m.subject_type),
            goal_minutes=m.goal_minutes,
            actual_minutes=m.actual_minutes,
            status=CovenantStatus(m.status),
            is_signed=m.is_signed,
            signed_at=m.signed_at,
            hp_gain_multiplier=m.hp_gain_multiplier,
            created_at=m.created_at,
            updated_at=m.updated_at,
        )

    @staticmethod
    def _to_model(e: Covenant) -> CovenantModel:
        return CovenantModel(
            id=e.id, character_id=e.character_id, covenant_date=e.covenant_date,
            subject_type=e.subject_type.value, goal_minutes=e.goal_minutes,
            actual_minutes=e.actual_minutes, status=e.status.value,
            is_signed=e.is_signed, signed_at=e.signed_at,
            hp_gain_multiplier=e.hp_gain_multiplier,
            created_at=e.created_at, updated_at=e.updated_at,
        )

    async def find_by_id(self, covenant_id: uuid.UUID) -> Optional[Covenant]:
        m = await self._session.get(CovenantModel, covenant_id)
        return self._to_entity(m) if m else None

    async def find_active_for_date(
        self, character_id: uuid.UUID, covenant_date: date
    ) -> Optional[Covenant]:
        stmt = select(CovenantModel).where(
            CovenantModel.character_id == character_id,
            CovenantModel.covenant_date == covenant_date,
        )
        result = await self._session.execute(stmt)
        m = result.scalar_one_or_none()
        return self._to_entity(m) if m else None

    async def save(self, covenant: Covenant) -> None:
        self._session.add(self._to_model(covenant))
        await self._session.flush()

    async def update(self, covenant: Covenant) -> None:
        m = await self._session.get(CovenantModel, covenant.id)
        if m is None:
            raise ValueError(f"Covenant {covenant.id} not found.")
        m.actual_minutes = covenant.actual_minutes
        m.status = covenant.status.value
        m.is_signed = covenant.is_signed
        m.signed_at = covenant.signed_at
        m.hp_gain_multiplier = covenant.hp_gain_multiplier
        m.updated_at = covenant.updated_at
        await self._session.flush()

    async def get_recent(self, character_id: uuid.UUID, days: int = 7) -> list[Covenant]:
        cutoff = date.today() - timedelta(days=days)
        stmt = (
            select(CovenantModel)
            .where(CovenantModel.character_id == character_id, CovenantModel.covenant_date >= cutoff)
            .order_by(CovenantModel.covenant_date.desc())
        )
        result = await self._session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]

    async def get_average_goal_minutes(self, character_id: uuid.UUID, days: int = 7) -> float:
        cutoff = date.today() - timedelta(days=days)
        stmt = select(func.avg(CovenantModel.goal_minutes)).where(
            CovenantModel.character_id == character_id,
            CovenantModel.covenant_date >= cutoff,
            CovenantModel.status != "ghosted",
        )
        result = await self._session.execute(stmt)
        return result.scalar() or 0.0

    async def get_average_actual_minutes(self, character_id: uuid.UUID, days: int = 14) -> float:
        cutoff = date.today() - timedelta(days=days)
        stmt = select(func.avg(CovenantModel.actual_minutes)).where(
            CovenantModel.character_id == character_id,
            CovenantModel.covenant_date >= cutoff,
            CovenantModel.status.in_(["completed", "partial"]),
        )
        result = await self._session.execute(stmt)
        return result.scalar() or 0.0
