from __future__ import annotations

import uuid

from character_domain.application.dtos.revival_dtos import RevivalStatusResponse
from character_domain.application.use_cases.reaper_revival_options import ReaperRevivalOptionsUseCase
from character_domain.application.use_cases.reaper_death_history import ReaperDeathHistoryUseCase
from character_domain.application.use_cases.reaper_revival_history import ReaperRevivalHistoryUseCase
from character_domain.application.use_cases.reaper_get_eulogy import ReaperGetEulogyUseCase


class GetRevivalStatusUseCase:
    def __init__(
        self,
        get_options: ReaperRevivalOptionsUseCase,
        get_death_history: ReaperDeathHistoryUseCase,
        get_revival_history: ReaperRevivalHistoryUseCase,
        get_eulogies: ReaperGetEulogyUseCase,
    ) -> None:
        self._get_options = get_options
        self._get_death_history = get_death_history
        self._get_revival_history = get_revival_history
        self._get_eulogies = get_eulogies

    async def execute(self, character_id: uuid.UUID) -> RevivalStatusResponse:
        # Options actually returns everything about active penance / ritual according to its DTO!
        # wait, ReaperRevivalOptions returns `available`, `ritual_eligible`, `active_penance`, `active_ritual`, etc.
        options = await self._get_options.execute(character_id)
        
        death_history = await self._get_death_history.execute(character_id)
        revival_history = await self._get_revival_history.execute(character_id)
        eulogies = await self._get_eulogies.execute(character_id)

        return RevivalStatusResponse(
            available=options.available,
            reason=options.reason,
            rituals_remaining=options.rituals_remaining,
            ritual_eligible=options.ritual_eligible,
            next_ritual_type=options.next_ritual_type,
            active_ritual=options.active_ritual,
            feathers_available=options.feathers_available,

            death_history=death_history,
            revival_history=revival_history,
            eulogies=eulogies.eulogies if eulogies else [],
        )
