from __future__ import annotations

import uuid

from character_domain.application.dtos.purchase_dtos import ShopMeResponse
from character_domain.application.use_cases.purchase_get_balances import PurchaseGetBalancesUseCase
from character_domain.application.use_cases.purchase_get_inventory import PurchaseGetInventoryUseCase


class GetShopMeUseCase:
    def __init__(
        self,
        get_balances: PurchaseGetBalancesUseCase,
        get_inventory: PurchaseGetInventoryUseCase,
    ) -> None:
        self._get_balances = get_balances
        self._get_inventory = get_inventory

    async def execute(self, user_id: uuid.UUID) -> ShopMeResponse:
        balances = await self._get_balances.execute(user_id)
        inventory = await self._get_inventory.execute(user_id)

        return ShopMeResponse(
            balances=balances,
            inventory=inventory,
        )
