"""
Get the HP audit timeline for a character via Anubis.
"""

from __future__ import annotations

import uuid

from character_domain.application.dtos import (
    HPLogEntry,
    HPTimelineResponse,
)
from character_domain.domain.services.anubis import Anubis


class GetHPTimelineUseCase:

    def __init__(self, anubis: Anubis) -> None:
        self._anubis = anubis

    async def execute(
        self, character_id: uuid.UUID, limit: int = 50
    ) -> HPTimelineResponse:
        logs = await self._anubis.get_hp_timeline(character_id, limit)

        entries = [
            HPLogEntry(
                id=log.id,
                old_hp=log.old_hp,
                new_hp=log.new_hp,
                delta=log.delta,
                reason=log.reason.value,
                description=log.description,
                shield_used=log.shield_used,
                triggered_death=log.triggered_death,
                created_at=log.created_at,
            )
            for log in logs
        ]

        return HPTimelineResponse(
            character_id=character_id,
            entries=entries,
            total_count=len(entries),
        )
