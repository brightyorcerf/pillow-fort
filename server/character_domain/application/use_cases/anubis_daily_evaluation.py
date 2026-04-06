"""
Daily evaluation orchestrator — calls Anubis.process_daily_evaluation
for all active characters. Used by the nightly cron job.
"""

from __future__ import annotations

import uuid
from datetime import date, timezone, datetime

from character_domain.application.dtos import DailyEvaluationResponse
from character_domain.domain.exceptions import CharacterNotFoundException
from character_domain.domain.interfaces import (
    ICharacterRepository,
    ICovenantRepository,
)
from character_domain.domain.services.anubis import Anubis


class AnubisDailyEvaluationUseCase:

    def __init__(
        self,
        anubis: Anubis,
        char_repo: ICharacterRepository,
        covenant_repo: ICovenantRepository,
    ) -> None:
        self._anubis = anubis
        self._char_repo = char_repo
        self._covenant_repo = covenant_repo

    async def execute(self, character_id: uuid.UUID) -> DailyEvaluationResponse:
        """
        Evaluate a single character's daily performance.
        In production, the cron iterates over all active characters
        and calls this for each one.
        """
        character = await self._char_repo.find_by_id(character_id)
        if character is None:
            raise CharacterNotFoundException()

        today = datetime.now(timezone.utc).date()

        # Get today's covenant
        covenant = await self._covenant_repo.find_active_for_date(character_id, today)

        covenant_goal = covenant.goal_minutes if covenant else None
        covenant_actual = covenant.actual_minutes if covenant else None

        # Compute consecutive ghosting days
        consecutive_ghosting = character.ghosting_days + 1 if covenant is None else 0

        # Average daily minutes for trend evaluation
        avg_daily = await self._covenant_repo.get_average_actual_minutes(
            character_id, days=7
        )

        results = await self._anubis.process_daily_evaluation(
            character=character,
            covenant_goal_minutes=covenant_goal,
            covenant_actual_minutes=covenant_actual,
            consecutive_ghosting_days=consecutive_ghosting,
            consecutive_below_average_days=character.consecutive_below_average_days,
            average_daily_minutes=avg_daily,
        )

        await self._char_repo.update(character)

        # Serialize results for response (convert dataclass results to dicts)
        serialized = {}
        for key, val in results.items():
            if val is None:
                serialized[key] = None
            elif hasattr(val, "__dict__"):
                serialized[key] = {
                    k: str(v) if isinstance(v, uuid.UUID) else v
                    for k, v in val.__dict__.items()
                    if not k.startswith("_")
                }
            else:
                serialized[key] = str(val)

        return DailyEvaluationResponse(
            character_id=character.id,
            results=serialized,
            final_hp=character.hp,
            final_state=character.health_state.value,
        )
