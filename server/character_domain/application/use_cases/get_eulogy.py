"""Get Eulogy — PRD §3.2 "The Eulogy" report for a dead character."""

from __future__ import annotations

import uuid

from character_domain.application.dtos import EulogyResponse
from character_domain.domain.exceptions import CharacterNotFoundException
from character_domain.domain.interfaces import ICharacterRepository


class GetEulogyUseCase:

    def __init__(self, char_repo: ICharacterRepository) -> None:
        self._char_repo = char_repo

    async def execute(self, character_id: uuid.UUID) -> EulogyResponse:
        character = await self._char_repo.find_by_id(character_id)
        if character is None:
            raise CharacterNotFoundException()

        eulogy = character.generate_eulogy()
        return EulogyResponse(**eulogy)
