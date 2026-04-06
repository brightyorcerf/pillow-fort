"""
Get revival attempt history for a character via the Reaper.
"""

from __future__ import annotations

import uuid

from character_domain.application.dtos import RevivalAttemptResponse, RevivalHistoryResponse
from character_domain.domain.services.reaper import Reaper


class ReaperRevivalHistoryUseCase:

    def __init__(self, reaper: Reaper) -> None:
        self._reaper = reaper

    async def execute(self, character_id: uuid.UUID) -> RevivalHistoryResponse:
        attempts = await self._reaper.get_revival_history(character_id)

        return RevivalHistoryResponse(
            character_id=character_id,
            attempts=[
                RevivalAttemptResponse(
                    id=a.id,
                    character_id=a.character_id,
                    death_record_id=a.death_record_id,
                    method=a.method.value,
                    hp_restored_to=a.hp_restored_to,
                    success=a.success,
                    fail_reason=a.fail_reason,
                    created_at=a.created_at,
                )
                for a in attempts
            ],
            total_attempts=len(attempts),
            successful_revivals=sum(1 for a in attempts if a.success),
        )
