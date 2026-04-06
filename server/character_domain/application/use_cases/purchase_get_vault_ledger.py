"""Get the immutable Star Dust vault ledger for a user."""

from __future__ import annotations

import uuid

from character_domain.application.dtos import VaultLedgerEntryResponse, VaultLedgerResponse
from character_domain.domain.services.purchase_manager import PurchaseManager


class PurchaseGetVaultLedgerUseCase:

    def __init__(self, purchase_manager: PurchaseManager) -> None:
        self._pm = purchase_manager

    async def execute(
        self, user_id: uuid.UUID, limit: int = 50
    ) -> VaultLedgerResponse:
        entries = await self._pm.get_vault_ledger(user_id, limit)
        return VaultLedgerResponse(
            user_id=user_id,
            entries=[
                VaultLedgerEntryResponse(
                    id=e.id,
                    vault_id=e.vault_id,
                    user_id=e.user_id,
                    delta=e.delta,
                    reason=e.reason.value,
                    description=e.description,
                    balance_after=e.balance_after,
                    reference_id=e.reference_id,
                    created_at=e.created_at,
                )
                for e in entries
            ],
            total=len(entries),
        )
