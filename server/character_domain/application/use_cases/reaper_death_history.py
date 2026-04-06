"""
Get death history for a character via the Reaper.
"""

from __future__ import annotations

import uuid

from character_domain.application.dtos import DeathHistoryResponse, DeathRecordResponse
from character_domain.domain.services.reaper import Reaper


class ReaperDeathHistoryUseCase:

    def __init__(self, reaper: Reaper) -> None:
        self._reaper = reaper

    async def execute(self, character_id: uuid.UUID) -> DeathHistoryResponse:
        records = await self._reaper.get_death_history(character_id)

        return DeathHistoryResponse(
            character_id=character_id,
            deaths=[
                DeathRecordResponse(
                    id=r.id,
                    character_id=r.character_id,
                    cause=r.cause.value,
                    hp_at_death=r.hp_at_death,
                    total_hours_in_life=r.total_hours_in_life,
                    consecutive_ghost_days_at_death=r.consecutive_ghost_days_at_death,
                    rituals_used_at_death=r.rituals_used_at_death,
                    longest_streak_at_death=r.longest_streak_at_death,
                    eulogy_generated=r.eulogy_generated,
                    is_permanent=r.is_permanent,
                    died_at=r.died_at,
                )
                for r in records
            ],
            total_deaths=len(records),
        )
