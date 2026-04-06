"""
Record daily penance progress for a dead character via the Reaper.
"""

from __future__ import annotations

import uuid

from character_domain.application.dtos import PenanceStreakResponse
from character_domain.domain.exceptions import CharacterNotFoundException
from character_domain.domain.interfaces import ICharacterRepository
from character_domain.domain.services.reaper import Reaper


class ReaperPenanceProgressUseCase:

    def __init__(
        self, reaper: Reaper, char_repo: ICharacterRepository
    ) -> None:
        self._reaper = reaper
        self._char_repo = char_repo

    async def execute(
        self, character_id: uuid.UUID, goal_hit: bool
    ) -> PenanceStreakResponse:
        character = await self._char_repo.find_by_id(character_id)
        if character is None:
            raise CharacterNotFoundException()

        penance = await self._reaper.check_penance_progress(character, goal_hit)
        await self._char_repo.update(character)

        return PenanceStreakResponse(
            id=penance.id,
            character_id=penance.character_id,
            attempt_number=penance.attempt_number,
            required_days=penance.required_days,
            days_completed=penance.days_completed,
            days_remaining=penance.days_remaining,
            progress_pct=penance.progress_pct,
            status=penance.status.value,
            started_at=penance.started_at,
            completed_at=penance.completed_at,
            failed_at=penance.failed_at,
        )
