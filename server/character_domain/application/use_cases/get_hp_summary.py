"""
Get today's HP change summary for a character via Anubis.
"""

from __future__ import annotations

import uuid

from character_domain.application.dtos import (
    HPSummaryEvent,
    HPSummaryResponse,
)
from character_domain.domain.services.anubis import Anubis


class GetHPSummaryUseCase:

    def __init__(self, anubis: Anubis) -> None:
        self._anubis = anubis

    async def execute(self, character_id: uuid.UUID) -> HPSummaryResponse:
        summary = await self._anubis.get_hp_summary_today(character_id)

        return HPSummaryResponse(
            date=summary["date"],
            total_changes=summary["total_changes"],
            net_delta=summary["net_delta"],
            events=[
                HPSummaryEvent(
                    reason=e["reason"],
                    delta=e["delta"],
                    description=e["description"],
                    timestamp=e["timestamp"],
                )
                for e in summary["events"]
            ],
        )
