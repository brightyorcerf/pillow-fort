"""Start a study session (PRD §3.1.1 — "Shadow Presence")."""

from __future__ import annotations

import uuid

from character_domain.application.dtos import StartSessionRequest, SessionResponse
from character_domain.domain.entities.study_session import StudySession
from character_domain.domain.exceptions import (
    CharacterNotFoundException,
    CovenantNotSignedException,
    SessionAlreadyActiveException,
)
from character_domain.domain.interfaces import (
    ICharacterRepository,
    ICovenantRepository,
    IStudySessionRepository,
)


class StartSessionUseCase:

    def __init__(
        self,
        char_repo: ICharacterRepository,
        covenant_repo: ICovenantRepository,
        session_repo: IStudySessionRepository,
    ) -> None:
        self._char_repo = char_repo
        self._covenant_repo = covenant_repo
        self._session_repo = session_repo

    async def execute(
        self, character_id: uuid.UUID, request: StartSessionRequest
    ) -> SessionResponse:
        character = await self._char_repo.find_by_id(character_id)
        if character is None:
            raise CharacterNotFoundException()

        covenant = await self._covenant_repo.find_by_id(request.covenant_id)
        if covenant is None or not covenant.is_signed:
            raise CovenantNotSignedException()

        active = await self._session_repo.find_active_for_character(character_id)
        if active is not None:
            raise SessionAlreadyActiveException()

        session = StudySession.start(
            character_id=character_id,
            covenant_id=request.covenant_id,
        )
        await self._session_repo.save(session)

        return SessionResponse(
            id=session.id,
            character_id=session.character_id,
            covenant_id=session.covenant_id,
            started_at=session.started_at,
            ended_at=session.ended_at,
            duration_minutes=session.duration_minutes,
            status=session.status.value,
            is_verified=session.is_verified,
        )
