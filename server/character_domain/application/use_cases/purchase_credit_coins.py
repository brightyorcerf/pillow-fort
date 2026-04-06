"""Credit coins to a user's wallet."""

from __future__ import annotations

import uuid

from character_domain.application.dtos import WalletResponse
from character_domain.domain.services.purchase_manager import PurchaseManager


class PurchaseCreditCoinsUseCase:

    def __init__(self, purchase_manager: PurchaseManager) -> None:
        self._pm = purchase_manager

    async def execute(
        self, user_id: uuid.UUID, amount: int, reason: str = "Study reward"
    ) -> WalletResponse:
        wallet = await self._pm.credit_coins(user_id, amount, reason)
        return WalletResponse(
            id=wallet.id,
            user_id=wallet.user_id,
            coin_balance=wallet.coin_balance,
            total_coins_earned=wallet.total_coins_earned,
            total_coins_spent=wallet.total_coins_spent,
            created_at=wallet.created_at,
            updated_at=wallet.updated_at,
        )
