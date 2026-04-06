"""SQLAlchemy implementation of IStudySessionRepository."""

from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from character_domain.domain.entities.study_session import SessionStatus, StudySession
from character_domain.domain.interfaces.study_session_repository import IStudySessionRepository
from character_domain.infrastructure.persistence.models.study_session_model import StudySessionModel


class SqlAlchemyStudySessionRepository(IStudySessionRepository):

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @staticmethod
    def _to_entity(m: StudySessionModel) -> StudySession:
        return StudySession(
            id=m.id, character_id=m.character_id, covenant_id=m.covenant_id,
            started_at=m.started_at, ended_at=m.ended_at,
            duration_minutes=m.duration_minutes, status=SessionStatus(m.status),
            check_in_count=m.check_in_count, check_in_passed=m.check_in_passed,
            was_foreground=m.was_foreground, idle_violations=m.idle_violations,
            created_at=m.created_at,
        )

    @staticmethod
    def _to_model(e: StudySession) -> StudySessionModel:
        return StudySessionModel(
            id=e.id, character_id=e.character_id, covenant_id=e.covenant_id,
            started_at=e.started_at, ended_at=e.ended_at,
            duration_minutes=e.duration_minutes, status=e.status.value,
            check_in_count=e.check_in_count, check_in_passed=e.check_in_passed,
            was_foreground=e.was_foreground, idle_violations=e.idle_violations,
            created_at=e.created_at,
        )

    async def find_by_id(self, session_id: uuid.UUID) -> Optional[StudySession]:
        m = await self._session.get(StudySessionModel, session_id)
        return self._to_entity(m) if m else None

    async def find_active_for_character(self, character_id: uuid.UUID) -> Optional[StudySession]:
        stmt = select(StudySessionModel).where(
            StudySessionModel.character_id == character_id,
            StudySessionModel.status == "in_progress",
        )
        result = await self._session.execute(stmt)
        m = result.scalar_one_or_none()
        return self._to_entity(m) if m else None

    async def save(self, session: StudySession) -> None:
        self._session.add(self._to_model(session))
        await self._session.flush()

    async def update(self, session: StudySession) -> None:
        m = await self._session.get(StudySessionModel, session.id)
        if m is None:
            raise ValueError(f"StudySession {session.id} not found.")
        m.ended_at = session.ended_at
        m.duration_minutes = session.duration_minutes
        m.status = session.status.value
        m.check_in_count = session.check_in_count
        m.check_in_passed = session.check_in_passed
        m.was_foreground = session.was_foreground
        m.idle_violations = session.idle_violations
        await self._session.flush()

    async def get_longest_session_minutes(self, character_id: uuid.UUID) -> int:
        stmt = select(func.max(StudySessionModel.duration_minutes)).where(
            StudySessionModel.character_id == character_id,
            StudySessionModel.status == "completed",
        )
        result = await self._session.execute(stmt)
        return result.scalar() or 0
