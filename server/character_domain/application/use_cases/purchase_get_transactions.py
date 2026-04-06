"""Get a user's transaction (purchase) history."""

from __future__ import annotations

import uuid

from character_domain.application.dtos import TransactionHistoryResponse, TransactionResponse
from character_domain.domain.services.purchase_manager import PurchaseManager


class PurchaseGetTransactionsUseCase:

    def __init__(self, purchase_manager: PurchaseManager) -> None:
        self._pm = purchase_manager

    async def execute(
        self, user_id: uuid.UUID, limit: int = 50
    ) -> TransactionHistoryResponse:
        txns = await self._pm.get_transaction_history(user_id, limit)
        return TransactionHistoryResponse(
            user_id=user_id,
            transactions=[
                TransactionResponse(
                    id=t.id,
                    user_id=t.user_id,
                    item_id=t.item_id,
                    offer_id=t.offer_id,
                    item_name=t.item_name,
                    currency=t.currency.value,
                    amount_paid=t.amount_paid,
                    status=t.status.value,
                    fail_reason=t.fail_reason,
                    refunded_at=t.refunded_at,
                    created_at=t.created_at,
                )
                for t in txns
            ],
            total=len(txns),
        )
