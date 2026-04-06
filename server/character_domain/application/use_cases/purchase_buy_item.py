"""Purchase a single store item."""

from __future__ import annotations

import uuid

from character_domain.application.dtos import PurchaseResultResponse
from character_domain.domain.services.purchase_manager import PurchaseManager


class PurchaseBuyItemUseCase:

    def __init__(self, purchase_manager: PurchaseManager) -> None:
        self._pm = purchase_manager

    async def execute(
        self, user_id: uuid.UUID, item_id: uuid.UUID, player_level: int = 0
    ) -> PurchaseResultResponse:
        result = await self._pm.purchase_item(user_id, item_id, player_level)
        return PurchaseResultResponse(
            success=result.success,
            transaction_id=result.transaction_id,
            owned_item_id=result.owned_item_id,
            reason=result.reason,
        )
