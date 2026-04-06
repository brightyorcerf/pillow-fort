from __future__ import annotations

import uuid

from character_domain.application.dtos.revival_dtos import RevivalRequest
from character_domain.application.use_cases.reaper_feather_revive import ReaperFeatherReviveUseCase


class HandleRevivalUseCase:
    """
    Dispatcher use case that routes revival actions.
    Revival is now Phoenix Feather-only (rituals removed in PRD v2).
    """
    def __init__(
        self,
        feather_revive: ReaperFeatherReviveUseCase,
    ) -> None:
        self._feather_revive = feather_revive

    async def execute(self, character_id: uuid.UUID, request: RevivalRequest) -> dict:
        if request.method == "feather":
            result = await self._feather_revive.execute(character_id)
            return {"status": "success", "message": "Revived via Phoenix Feather", "attempt": result}

        raise ValueError(f"Unknown revival method: {request.method}. Only 'feather' is supported.")
