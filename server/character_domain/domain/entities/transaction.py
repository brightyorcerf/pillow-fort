"""
Transaction entity — immutable record of a purchase.

Every shop purchase (single item or bundle) generates a Transaction.
Supports refund lifecycle: PENDING → COMPLETED → REFUNDED.

PRD §3.3 — Transaction class in shop system class diagram.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from character_domain.domain.value_objects.purchase_enums import (
    CurrencyType,
    TransactionStatus,
)


class Transaction:
    """
    Invariants:
      - amount_paid >= 0
      - Status transitions: PENDING → COMPLETED | FAILED
                            COMPLETED → REFUNDED
    """

    def __init__(
        self,
        id: uuid.UUID,
        user_id: uuid.UUID,
        item_id: uuid.UUID | None,          # Single item purchase
        offer_id: uuid.UUID | None,         # Bundle/offer purchase
        item_name: str,
        currency: CurrencyType,
        amount_paid: int,
        status: TransactionStatus = TransactionStatus.PENDING,
        fail_reason: str | None = None,
        refunded_at: datetime | None = None,
        created_at: Optional[datetime] = None,
    ) -> None:
        self._id = id
        self._user_id = user_id
        self._item_id = item_id
        self._offer_id = offer_id
        self._item_name = item_name
        self._currency = currency
        self._amount_paid = amount_paid
        self._status = status
        self._fail_reason = fail_reason
        self._refunded_at = refunded_at
        self._created_at = created_at or datetime.now(timezone.utc)

    @classmethod
    def create_for_item(
        cls,
        user_id: uuid.UUID,
        item_id: uuid.UUID,
        item_name: str,
        currency: CurrencyType,
        amount_paid: int,
    ) -> Transaction:
        return cls(
            id=uuid.uuid4(),
            user_id=user_id,
            item_id=item_id,
            offer_id=None,
            item_name=item_name,
            currency=currency,
            amount_paid=amount_paid,
            status=TransactionStatus.PENDING,
        )

    @classmethod
    def create_for_offer(
        cls,
        user_id: uuid.UUID,
        offer_id: uuid.UUID,
        offer_title: str,
        currency: CurrencyType,
        amount_paid: int,
    ) -> Transaction:
        return cls(
            id=uuid.uuid4(),
            user_id=user_id,
            item_id=None,
            offer_id=offer_id,
            item_name=offer_title,
            currency=currency,
            amount_paid=amount_paid,
            status=TransactionStatus.PENDING,
        )

    # ── Properties ─────────────────────────────────────────────────────

    @property
    def id(self) -> uuid.UUID:
        return self._id

    @property
    def user_id(self) -> uuid.UUID:
        return self._user_id

    @property
    def item_id(self) -> uuid.UUID | None:
        return self._item_id

    @property
    def offer_id(self) -> uuid.UUID | None:
        return self._offer_id

    @property
    def item_name(self) -> str:
        return self._item_name

    @property
    def currency(self) -> CurrencyType:
        return self._currency

    @property
    def amount_paid(self) -> int:
        return self._amount_paid

    @property
    def status(self) -> TransactionStatus:
        return self._status

    @property
    def fail_reason(self) -> str | None:
        return self._fail_reason

    @property
    def refunded_at(self) -> datetime | None:
        return self._refunded_at

    @property
    def created_at(self) -> datetime:
        return self._created_at

    # ── Mutations ──────────────────────────────────────────────────────

    def complete(self) -> None:
        if self._status != TransactionStatus.PENDING:
            raise ValueError(f"Cannot complete transaction in {self._status.value} state.")
        self._status = TransactionStatus.COMPLETED

    def fail(self, reason: str) -> None:
        if self._status != TransactionStatus.PENDING:
            raise ValueError(f"Cannot fail transaction in {self._status.value} state.")
        self._status = TransactionStatus.FAILED
        self._fail_reason = reason

    def refund(self) -> None:
        if self._status != TransactionStatus.COMPLETED:
            raise ValueError(f"Cannot refund transaction in {self._status.value} state.")
        self._status = TransactionStatus.REFUNDED
        self._refunded_at = datetime.now(timezone.utc)
