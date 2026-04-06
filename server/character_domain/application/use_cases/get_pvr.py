"""
Get Personal Viable Range (PVR) — PRD §3.1.5.

Calculated from the user's study history to personalise goal guardrails.
"""

from __future__ import annotations

import uuid

from character_domain.application.dtos import PvrResponse
from character_domain.domain.exceptions import CharacterNotFoundException
from character_domain.domain.interfaces import (
    ICharacterRepository,
    ICovenantRepository,
    IStudySessionRepository,
)
from character_domain.domain.value_objects.session_cap import SessionCap


class GetPvrUseCase:

    def __init__(
        self,
        char_repo: ICharacterRepository,
        covenant_repo: ICovenantRepository,
        session_repo: IStudySessionRepository,
    ) -> None:
        self._char_repo = char_repo
        self._covenant_repo = covenant_repo
        self._session_repo = session_repo

    async def execute(self, character_id: uuid.UUID) -> PvrResponse:
        character = await self._char_repo.find_by_id(character_id)
        if character is None:
            raise CharacterNotFoundException()

        avg_7d = await self._covenant_repo.get_average_actual_minutes(character_id, days=7)
        longest = await self._session_repo.get_longest_session_minutes(character_id)
        avg_14d = await self._covenant_repo.get_average_actual_minutes(character_id, days=14)
        cap = SessionCap.from_average(avg_14d)

        return PvrResponse(
            average_daily_minutes_7d=round(avg_7d, 1),
            longest_session_ever=longest,
            current_streak_health=character.health_state.value,
            suggested_cap_minutes=cap.suggested_cap_minutes,
            hard_ceiling_minutes=cap.hard_ceiling_minutes,
        )
