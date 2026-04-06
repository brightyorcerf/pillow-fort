"""
Get eulogies for a character via the Reaper/EulogyService.
"""

from __future__ import annotations

import uuid

from character_domain.application.dtos import ReaperEulogyResponse
from character_domain.domain.interfaces.eulogy_service import IEulogyService


class ReaperGetEulogyUseCase:

    def __init__(self, eulogy_service: IEulogyService) -> None:
        self._eulogy_service = eulogy_service

    async def execute(self, character_id: uuid.UUID) -> list[ReaperEulogyResponse]:
        eulogies = await self._eulogy_service.find_by_character(character_id)

        return [
            ReaperEulogyResponse(
                id=e.id,
                character_id=e.character_id,
                character_name=e.character_name,
                total_study_hours=e.total_study_hours,
                longest_streak=e.longest_streak,
                rank_achieved=e.rank_achieved,
                life_shields_earned=e.life_shields_earned,
                rituals_completed=e.rituals_completed,
                total_covenants_signed=e.total_covenants_signed,
                total_covenants_kept=e.total_covenants_kept,
                born_at=e.born_at,
                died_at=e.died_at,
            )
            for e in eulogies
        ]
