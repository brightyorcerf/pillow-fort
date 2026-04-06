"""Get dynamic Phoenix Feather pricing."""

from __future__ import annotations

import uuid

from character_domain.application.dtos import FeatherPriceResponse
from character_domain.domain.services.purchase_manager import (
    FEATHER_BASE_PRICE_STARDUST,
    FEATHER_MAX_PRICE_STARDUST,
    PurchaseManager,
)


class PurchaseFeatherPriceUseCase:

    def __init__(self, purchase_manager: PurchaseManager) -> None:
        self._pm = purchase_manager

    async def execute(
        self, user_id: uuid.UUID, deaths_in_window: int = 0
    ) -> FeatherPriceResponse:
        price = await self._pm.get_feather_price(user_id, deaths_in_window)
        return FeatherPriceResponse(
            price_star_dust=price,
            deaths_in_window=deaths_in_window,
            base_price=FEATHER_BASE_PRICE_STARDUST,
            max_price=FEATHER_MAX_PRICE_STARDUST,
        )
