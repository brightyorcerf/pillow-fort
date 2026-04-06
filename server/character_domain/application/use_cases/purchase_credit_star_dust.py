"""Credit Star Dust to a user's vault."""

from __future__ import annotations

import uuid

from character_domain.application.dtos import VaultWalletResponse
from character_domain.domain.services.purchase_manager import PurchaseManager
from character_domain.domain.value_objects.purchase_enums import VaultLedgerReason


class PurchaseCreditStarDustUseCase:

    def __init__(self, purchase_manager: PurchaseManager) -> None:
        self._pm = purchase_manager

    async def execute(
        self,
        user_id: uuid.UUID,
        amount: int,
        reason: str = "PURCHASE",
        description: str = "Star Dust top-up",
    ) -> VaultWalletResponse:
        vault = await self._pm.credit_star_dust(
            user_id=user_id,
            amount=amount,
            reason=VaultLedgerReason(reason),
            description=description,
        )
        return VaultWalletResponse(
            id=vault.id,
            user_id=vault.user_id,
            star_dust_balance=vault.star_dust_balance,
            total_star_dust_purchased=vault.total_star_dust_purchased,
            total_star_dust_spent=vault.total_star_dust_spent,
            created_at=vault.created_at,
            updated_at=vault.updated_at,
        )
