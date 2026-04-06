"""
Revive a dead character using a Phoenix Feather via the Reaper.
"""

from __future__ import annotations

import uuid

from character_domain.application.dtos import RevivalAttemptResponse
from character_domain.domain.exceptions import CharacterNotFoundException
from character_domain.domain.interfaces import ICharacterRepository
from character_domain.domain.services.reaper import Reaper


class ReaperFeatherReviveUseCase:

    def __init__(
        self, reaper: Reaper, char_repo: ICharacterRepository
    ) -> None:
        self._reaper = reaper
        self._char_repo = char_repo

    async def execute(self, character_id: uuid.UUID) -> RevivalAttemptResponse:
        character = await self._char_repo.find_by_id(character_id)
        if character is None:
            raise CharacterNotFoundException()

        attempt = await self._reaper.revive_with_feather(character)
        await self._char_repo.update(character)

        return RevivalAttemptResponse(
            id=attempt.id,
            character_id=attempt.character_id,
            death_record_id=attempt.death_record_id,
            method=attempt.method.value,
            hp_restored_to=attempt.hp_restored_to,
            success=attempt.success,
            fail_reason=attempt.fail_reason,
            created_at=attempt.created_at,
        )
