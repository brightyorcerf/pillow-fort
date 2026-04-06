"""
Restore a character from an unfair death via the Reaper.
"""

from __future__ import annotations

import uuid

from character_domain.application.dtos import RevivalAttemptResponse
from character_domain.domain.exceptions import (
    CharacterNotFoundException,
    DeathRecordNotFoundException,
)
from character_domain.domain.interfaces import ICharacterRepository
from character_domain.domain.interfaces.death_record_repository import IDeathRecordRepository
from character_domain.domain.services.reaper import Reaper


class ReaperRestoreUnfairDeathUseCase:

    def __init__(
        self,
        reaper: Reaper,
        char_repo: ICharacterRepository,
        death_record_repo: IDeathRecordRepository,
    ) -> None:
        self._reaper = reaper
        self._char_repo = char_repo
        self._death_record_repo = death_record_repo

    async def execute(
        self,
        character_id: uuid.UUID,
        death_record_id: uuid.UUID,
        compensation_hp: int = 100,
    ) -> RevivalAttemptResponse:
        character = await self._char_repo.find_by_id(character_id)
        if character is None:
            raise CharacterNotFoundException()

        death_record = await self._death_record_repo.find_by_id(death_record_id)
        if death_record is None:
            raise DeathRecordNotFoundException()

        attempt = await self._reaper.restore_unfair_death(
            character, death_record, compensation_hp
        )
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
