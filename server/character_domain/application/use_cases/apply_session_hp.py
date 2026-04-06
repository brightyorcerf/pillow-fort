"""
Apply HP gain from a completed study session via Anubis.

This use case is called after a session completes. It delegates all
HP calculation to the Anubis domain service and persists the result.
"""

from __future__ import annotations

from character_domain.application.dtos import ApplySessionHPRequest, HPChangeResponse
from character_domain.domain.exceptions import (
    CharacterNotFoundException,
    SessionNotFoundException,
)
from character_domain.domain.interfaces import (
    ICharacterRepository,
    IStudySessionRepository,
)
from character_domain.domain.services.anubis import Anubis


class ApplySessionHPUseCase:

    def __init__(
        self,
        anubis: Anubis,
        char_repo: ICharacterRepository,
        session_repo: IStudySessionRepository,
    ) -> None:
        self._anubis = anubis
        self._char_repo = char_repo
        self._session_repo = session_repo

    async def execute(self, request: ApplySessionHPRequest) -> HPChangeResponse:
        session = await self._session_repo.find_by_id(request.session_id)
        if session is None:
            raise SessionNotFoundException()

        character = await self._char_repo.find_by_id(session.character_id)
        if character is None:
            raise CharacterNotFoundException()

        result = await self._anubis.apply_session_hp(
            character=character,
            duration_minutes=request.duration_minutes,
            goal_minutes=request.goal_minutes,
            hp_gain_multiplier=request.hp_gain_multiplier,
        )

        # Add study minutes to character
        character.add_study_minutes(request.duration_minutes)
        await self._char_repo.update(character)

        return HPChangeResponse(
            character_id=result.character_id,
            old_hp=result.old_hp,
            new_hp=result.new_hp,
            delta=result.delta,
            reason=result.reason.value,
            description=result.description,
            shield_used=result.shield_used,
            triggered_death=result.triggered_death,
            timestamp=result.timestamp,
        )
