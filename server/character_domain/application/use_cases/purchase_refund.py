"""Refund a completed transaction."""

from __future__ import annotations

import uuid

from character_domain.application.dtos import TransactionResponse
from character_domain.domain.services.purchase_manager import PurchaseManager


class PurchaseRefundUseCase:

    def __init__(self, purchase_manager: PurchaseManager) -> None:
        self._pm = purchase_manager

    async def execute(self, transaction_id: uuid.UUID) -> TransactionResponse:
        txn = await self._pm.refund_transaction(transaction_id)
        return TransactionResponse(
            id=txn.id,
            user_id=txn.user_id,
            item_id=txn.item_id,
            offer_id=txn.offer_id,
            item_name=txn.item_name,
            currency=txn.currency.value,
            amount_paid=txn.amount_paid,
            status=txn.status.value,
            fail_reason=txn.fail_reason,
            refunded_at=txn.refunded_at,
            created_at=txn.created_at,
        )
