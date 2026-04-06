"""Apply the 25% coin death penalty (called by Reaper on character death)."""

from __future__ import annotations

import uuid

from character_domain.application.dtos import DeathPenaltyResponse
from character_domain.domain.services.purchase_manager import PurchaseManager


class PurchaseDeathPenaltyUseCase:

    def __init__(self, purchase_manager: PurchaseManager) -> None:
        self._pm = purchase_manager

    async def execute(self, user_id: uuid.UUID) -> DeathPenaltyResponse:
        coins_lost = await self._pm.apply_death_coin_penalty(user_id)
        return DeathPenaltyResponse(
            user_id=user_id,
            coins_lost=coins_lost,
        )
