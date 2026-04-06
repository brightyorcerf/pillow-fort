"""
Apply bonus task / reflection HP via Anubis.
"""

from __future__ import annotations

import uuid

from character_domain.application.dtos import HPChangeResponse
from character_domain.domain.exceptions import CharacterNotFoundException
from character_domain.domain.interfaces import ICharacterRepository
from character_domain.domain.services.anubis import Anubis


class ApplyBonusTaskHPUseCase:

    def __init__(self, anubis: Anubis, char_repo: ICharacterRepository) -> None:
        self._anubis = anubis
        self._char_repo = char_repo

    async def execute(self, character_id: uuid.UUID) -> HPChangeResponse:
        character = await self._char_repo.find_by_id(character_id)
        if character is None:
            raise CharacterNotFoundException()

        result = await self._anubis.apply_bonus_task_hp(character)
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


class ApplyReflectionHPUseCase:

    def __init__(self, anubis: Anubis, char_repo: ICharacterRepository) -> None:
        self._anubis = anubis
        self._char_repo = char_repo

    async def execute(self, character_id: uuid.UUID) -> HPChangeResponse:
        character = await self._char_repo.find_by_id(character_id)
        if character is None:
            raise CharacterNotFoundException()

        result = await self._anubis.apply_reflection_hp(character)
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
