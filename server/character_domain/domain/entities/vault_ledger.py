"""
VaultLedger entity — immutable audit record for Star Dust transactions.

Every vault operation (purchase, spending, rebirth rebate, refund)
is recorded as an immutable ledger entry for full auditability.

PRD §3.2.5 — "Every transaction is stored in an immutable ledger."
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone

from character_domain.domain.value_objects.purchase_enums import VaultLedgerReason


@dataclass(frozen=True)
class VaultLedger:
    """
    Immutable audit record. Once created, never modified.

    Positive delta = credit, negative delta = debit.
    """

    id: uuid.UUID
    vault_id: uuid.UUID
    user_id: uuid.UUID
    delta: int                        # +N for credit, -N for debit
    reason: VaultLedgerReason
    description: str
    balance_after: int                # Snapshot of vault balance after operation
    reference_id: uuid.UUID | None    # e.g. transaction_id or feather_id
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @classmethod
    def create(
        cls,
        vault_id: uuid.UUID,
        user_id: uuid.UUID,
        delta: int,
        reason: VaultLedgerReason,
        description: str,
        balance_after: int,
        reference_id: uuid.UUID | None = None,
    ) -> VaultLedger:
        return cls(
            id=uuid.uuid4(),
            vault_id=vault_id,
            user_id=user_id,
            delta=delta,
            reason=reason,
            description=description,
            balance_after=balance_after,
            reference_id=reference_id,
        )
