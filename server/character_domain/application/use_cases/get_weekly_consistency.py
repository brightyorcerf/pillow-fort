"""
Evaluate weekly consistency and set HP gain multiplier via Anubis.
"""

from __future__ import annotations

import uuid

from character_domain.application.dtos import WeeklyConsistencyResponse
from character_domain.domain.exceptions import CharacterNotFoundException
from character_domain.domain.interfaces import (
    ICharacterRepository,
    ICovenantRepository,
)
from character_domain.domain.services.anubis import Anubis


class GetWeeklyConsistencyUseCase:

    def __init__(
        self,
        anubis: Anubis,
        char_repo: ICharacterRepository,
        covenant_repo: ICovenantRepository,
    ) -> None:
        self._anubis = anubis
        self._char_repo = char_repo
        self._covenant_repo = covenant_repo

    async def execute(self, character_id: uuid.UUID) -> WeeklyConsistencyResponse:
        character = await self._char_repo.find_by_id(character_id)
        if character is None:
            raise CharacterNotFoundException()

        # Get last 7 days of covenants to count goals met
        recent_covenants = await self._covenant_repo.get_recent(character_id, days=7)
        days_goal_met = sum(
            1 for c in recent_covenants
            if c.actual_minutes >= c.goal_minutes
        )

        result = await self._anubis.compute_weekly_consistency(
            character=character,
            days_goal_met=days_goal_met,
            days_total=7,
        )

        await self._char_repo.update(character)

        return WeeklyConsistencyResponse(
            level=result.level.value,
            multiplier=result.multiplier,
            days_hit=result.days_hit,
            days_total=result.days_total,
            message=result.message,
        )
