"""Get a user's inventory of owned items."""

from __future__ import annotations

import uuid

from character_domain.application.dtos import InventoryResponse, OwnedItemResponse
from character_domain.domain.services.purchase_manager import PurchaseManager


class PurchaseGetInventoryUseCase:

    def __init__(self, purchase_manager: PurchaseManager) -> None:
        self._pm = purchase_manager

    async def execute(self, user_id: uuid.UUID) -> InventoryResponse:
        items = await self._pm.get_inventory(user_id)
        return InventoryResponse(
            user_id=user_id,
            items=[
                OwnedItemResponse(
                    id=item.id,
                    user_id=item.user_id,
                    item_id=item.item_id,
                    item_name=item.item_name,
                    item_type=item.item_type.value,
                    quantity=item.quantity,
                    is_consumable=item.is_consumable,
                    is_equipped=item.is_equipped,
                    acquired_at=item.acquired_at,
                )
                for item in items
            ],
            total=len(items),
        )
