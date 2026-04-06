"""Get user's dual-currency balances (Coins + Star Dust)."""

from __future__ import annotations

import uuid

from character_domain.application.dtos import BalancesResponse
from character_domain.domain.services.purchase_manager import PurchaseManager


class PurchaseGetBalancesUseCase:

    def __init__(self, purchase_manager: PurchaseManager) -> None:
        self._pm = purchase_manager

    async def execute(self, user_id: uuid.UUID) -> BalancesResponse:
        data = await self._pm.get_balances(user_id)
        return BalancesResponse(**data)
