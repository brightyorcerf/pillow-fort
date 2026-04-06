"""
Record a character death via the Reaper service.
"""

from __future__ import annotations

import uuid

from character_domain.application.dtos import DeathRecordResponse
from character_domain.domain.exceptions import CharacterNotFoundException
from character_domain.domain.interfaces import ICharacterRepository
from character_domain.domain.services.reaper import Reaper
from character_domain.domain.value_objects.reaper_enums import DeathCause


class ReaperKillUseCase:

    def __init__(
        self, reaper: Reaper, char_repo: ICharacterRepository
    ) -> None:
        self._reaper = reaper
        self._char_repo = char_repo

    async def execute(
        self, character_id: uuid.UUID, cause: str
    ) -> DeathRecordResponse:
        character = await self._char_repo.find_by_id(character_id)
        if character is None:
            raise CharacterNotFoundException()

        record = await self._reaper.kill(character, DeathCause(cause))
        await self._char_repo.update(character)

        return DeathRecordResponse(
            id=record.id,
            character_id=record.character_id,
            cause=record.cause.value,
            hp_at_death=record.hp_at_death,
            total_hours_in_life=record.total_hours_in_life,
            consecutive_ghost_days_at_death=record.consecutive_ghost_days_at_death,
            rituals_used_at_death=record.rituals_used_at_death,
            longest_streak_at_death=record.longest_streak_at_death,
            eulogy_generated=record.eulogy_generated,
            is_permanent=record.is_permanent,
            died_at=record.died_at,
        )
