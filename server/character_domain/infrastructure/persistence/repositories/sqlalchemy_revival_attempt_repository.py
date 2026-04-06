"""SQLAlchemy implementation of IRevivalAttemptRepository."""

from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from character_domain.domain.entities.revival_attempt import RevivalAttempt
from character_domain.domain.interfaces.revival_attempt_repository import (
    IRevivalAttemptRepository,
)
from character_domain.domain.value_objects.reaper_enums import RevivalMethod
from character_domain.infrastructure.persistence.models.revival_attempt_model import (
    RevivalAttemptModel,
)


class SqlAlchemyRevivalAttemptRepository(IRevivalAttemptRepository):

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @staticmethod
    def _to_entity(m: RevivalAttemptModel) -> RevivalAttempt:
        return RevivalAttempt(
            id=m.id,
            character_id=m.character_id,
            death_record_id=m.death_record_id,
            method=RevivalMethod(m.method),
            hp_restored_to=m.hp_restored_to,
            success=m.success,
            fail_reason=m.fail_reason,
            created_at=m.created_at,
        )

    @staticmethod
    def _to_model(e: RevivalAttempt) -> RevivalAttemptModel:
        return RevivalAttemptModel(
            id=e.id,
            character_id=e.character_id,
            death_record_id=e.death_record_id,
            method=e.method.value,
            hp_restored_to=e.hp_restored_to,
            success=e.success,
            fail_reason=e.fail_reason,
            created_at=e.created_at,
        )

    async def save(self, attempt: RevivalAttempt) -> None:
        self._session.add(self._to_model(attempt))
        await self._session.flush()

    async def find_by_id(self, attempt_id: uuid.UUID) -> Optional[RevivalAttempt]:
        m = await self._session.get(RevivalAttemptModel, attempt_id)
        return self._to_entity(m) if m else None

    async def find_all_for_character(
        self, character_id: uuid.UUID
    ) -> list[RevivalAttempt]:
        stmt = (
            select(RevivalAttemptModel)
            .where(RevivalAttemptModel.character_id == character_id)
            .order_by(RevivalAttemptModel.created_at.desc())
        )
        result = await self._session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]

    async def count_successful_for_character(
        self, character_id: uuid.UUID
    ) -> int:
        stmt = select(func.count(RevivalAttemptModel.id)).where(
            RevivalAttemptModel.character_id == character_id,
            RevivalAttemptModel.success is True,
        )
        result = await self._session.execute(stmt)
        return result.scalar_one()
