from __future__ import annotations

import uuid

from character_domain.application.dtos.purchase_dtos import ShopTransactionsResponse
from character_domain.application.use_cases.purchase_get_transactions import PurchaseGetTransactionsUseCase
from character_domain.application.use_cases.purchase_get_vault_ledger import PurchaseGetVaultLedgerUseCase


class GetShopTransactionsUseCase:
    def __init__(
        self,
        get_transactions: PurchaseGetTransactionsUseCase,
        get_vault_ledger: PurchaseGetVaultLedgerUseCase,
    ) -> None:
        self._get_transactions = get_transactions
        self._get_vault_ledger = get_vault_ledger

    async def execute(self, user_id: uuid.UUID) -> ShopTransactionsResponse:
        transactions = await self._get_transactions.execute(user_id)
        vault_ledger = await self._get_vault_ledger.execute(user_id)

        return ShopTransactionsResponse(
            transactions=transactions,
            vault_ledger=vault_ledger,
        )
