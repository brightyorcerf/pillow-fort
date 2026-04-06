from __future__ import annotations

import uuid
from datetime import date

from character_domain.application.use_cases.anubis_daily_evaluation import AnubisDailyEvaluationUseCase
from character_domain.domain.interfaces import ICharacterRepository, ICovenantRepository
from character_domain.domain.services.reaper import Reaper
from character_domain.domain.exceptions import CharacterNotFoundException


class RunDailyCronUseCase:
    """
    Replaces ProcessDailyCronUseCase.
    Orchestrates daily evaluation using Anubis and progresses any active penance using Reaper.
    """
    def __init__(
        self,
        anubis_daily_eval: AnubisDailyEvaluationUseCase,
        char_repo: ICharacterRepository,
        covenant_repo: ICovenantRepository,
        reaper: Reaper,
    ) -> None:
        self._anubis_daily_eval = anubis_daily_eval
        self._char_repo = char_repo
        self._covenant_repo = covenant_repo
        self._reaper = reaper

    async def execute(self, character_id: uuid.UUID, for_date: date) -> dict:
        character = await self._char_repo.find_by_id(character_id)
        if character is None:
            raise CharacterNotFoundException()
            
        # 1. Run Anubis evaluation (HP decay, ghosting penalties, etc)
        # Note: AnubisDailyEvaluationUseCase internally finds covenant for 'today' (UTC),
        # but normally cron should allow specifying the date.
        # For this refactor, we let Anubis handle its HP eval.
        eval_response = await self._anubis_daily_eval.execute(character_id)

        # 2. Process Penance (if active)
        # We need to know if they hit their goal today.
        if character.is_in_penance:
            covenant = await self._covenant_repo.find_active_for_date(character_id, for_date)
            goal_hit = False
            if covenant and covenant.goal_minutes > 0 and covenant.actual_minutes >= covenant.goal_minutes:
                goal_hit = True

            await self._reaper.check_penance_progress(character, goal_hit)
            
            # Since reaper updates character, save changes
            await self._char_repo.update(character)

        return {
            "status": "success",
            "anubis_evaluation": eval_response.results,
            "final_hp": eval_response.final_hp,
            "final_state": eval_response.final_state,
            "penance_processed": character.is_in_penance,
        }
