"""
Get available revival options for a dead character.
"""

from __future__ import annotations

import uuid

from character_domain.application.dtos import (
    ActivePenanceInfo,
    RevivalOptionsResponse,
)
from character_domain.domain.exceptions import CharacterNotFoundException
from character_domain.domain.interfaces import ICharacterRepository
from character_domain.domain.services.reaper import Reaper


class ReaperRevivalOptionsUseCase:

    def __init__(
        self, reaper: Reaper, char_repo: ICharacterRepository
    ) -> None:
        self._reaper = reaper
        self._char_repo = char_repo

    async def execute(self, character_id: uuid.UUID) -> RevivalOptionsResponse:
        character = await self._char_repo.find_by_id(character_id)
        if character is None:
            raise CharacterNotFoundException()

        options = await self._reaper.get_revival_options(character)

        active_penance = None
        if options.get("active_penance"):
            p = options["active_penance"]
            active_penance = ActivePenanceInfo(
                id=p["id"],
                days_completed=p["days_completed"],
                days_remaining=p["days_remaining"],
                progress_pct=p["progress_pct"],
            )

        return RevivalOptionsResponse(
            available=options["available"],
            reason=options.get("reason"),
            penance_eligible=options.get("penance_eligible"),
            active_penance=active_penance,
            feather_eligible=options.get("feather_eligible"),
            feathers_available=options.get("feathers_available"),
            can_restore_unfair=options.get("can_restore_unfair"),
        )
