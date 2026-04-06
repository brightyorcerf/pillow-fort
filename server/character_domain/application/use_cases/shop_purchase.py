from __future__ import annotations

import uuid
from typing import Any

from character_domain.application.dtos.purchase_dtos import ShopPurchaseRequest
from character_domain.application.use_cases.purchase_buy_item import PurchaseBuyItemUseCase
from character_domain.application.use_cases.purchase_buy_offer import PurchaseBuyOfferUseCase


class ShopPurchaseUseCase:
    def __init__(
        self,
        buy_item: PurchaseBuyItemUseCase,
        buy_offer: PurchaseBuyOfferUseCase,
    ) -> None:
        self._buy_item = buy_item
        self._buy_offer = buy_offer

    async def execute(self, user_id: uuid.UUID, request: ShopPurchaseRequest) -> dict[str, Any]:
        """
        Dispatches to either buy a regular store item or a special offer.
        Note: The underlying use cases return dicts with message/details.
        """
        if request.type == "item":
            result = await self._buy_item.execute(
                user_id=user_id,
                item_id=request.target_id,
                player_level=request.player_level,
            )
            return {"status": "success", "type": "item", **result}
            
        elif request.type == "offer":
            result = await self._buy_offer.execute(
                user_id=user_id,
                offer_id=request.target_id,
            )
            return {"status": "success", "type": "offer", **result}
            
        raise ValueError(f"Unknown purchase type: {request.type}")
