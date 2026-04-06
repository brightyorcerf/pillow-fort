"""
Get the active penance streak for a character via the Reaper.
"""

from __future__ import annotations

import uuid
from typing import Optional

from character_domain.application.dtos import PenanceStreakResponse
from character_domain.domain.services.reaper import Reaper


class ReaperGetPenanceUseCase:

    def __init__(self, reaper: Reaper) -> None:
        self._reaper = reaper

    async def execute(self, character_id: uuid.UUID) -> Optional[PenanceStreakResponse]:
        penance = await self._reaper.get_active_penance(character_id)
        if penance is None:
            return None

        return PenanceStreakResponse(
            id=penance.id,
            character_id=penance.character_id,
            attempt_number=penance.attempt_number,
            required_days=penance.required_days,
            days_completed=penance.days_completed,
            days_remaining=penance.days_remaining,
            progress_pct=penance.progress_pct,
            status=penance.status.value,
            started_at=penance.started_at,
            completed_at=penance.completed_at,
            failed_at=penance.failed_at,
        )
