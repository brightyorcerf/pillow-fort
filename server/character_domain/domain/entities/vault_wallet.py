"""
VaultWallet entity — persistent Star Dust storage.

"The Vault" is a high-security, cross-session wallet that survives
character death and even account deletion + re-registration
(tied to primary identity — Google/Apple ID).

PRD §3.2.5 — Proof of Purchase Guarantee.
PRD §3.3 — Star Dust currency persistence.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional


class VaultWallet:
    """
    Invariants:
      - star_dust_balance >= 0
      - Tied to user identity, not character
      - Persists across character deaths and account resets
    """

    def __init__(
        self,
        id: uuid.UUID,
        user_id: uuid.UUID,
        star_dust_balance: int = 0,
        total_star_dust_purchased: int = 0,
        total_star_dust_spent: int = 0,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ) -> None:
        self._id = id
        self._user_id = user_id
        self._star_dust_balance = max(0, star_dust_balance)
        self._total_star_dust_purchased = total_star_dust_purchased
        self._total_star_dust_spent = total_star_dust_spent
        self._created_at = created_at or datetime.now(timezone.utc)
        self._updated_at = updated_at or datetime.now(timezone.utc)

    @classmethod
    def create(cls, user_id: uuid.UUID) -> VaultWallet:
        return cls(id=uuid.uuid4(), user_id=user_id)

    # ── Properties ─────────────────────────────────────────────────────

    @property
    def id(self) -> uuid.UUID:
        return self._id

    @property
    def user_id(self) -> uuid.UUID:
        return self._user_id

    @property
    def star_dust_balance(self) -> int:
        return self._star_dust_balance

    @property
    def total_star_dust_purchased(self) -> int:
        return self._total_star_dust_purchased

    @property
    def total_star_dust_spent(self) -> int:
        return self._total_star_dust_spent

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        return self._updated_at

    # ── Mutations ──────────────────────────────────────────────────────

    def _touch(self) -> None:
        self._updated_at = datetime.now(timezone.utc)

    def can_afford(self, amount: int) -> bool:
        return self._star_dust_balance >= amount

    def credit(self, amount: int, is_purchase: bool = True) -> None:
        """
        Add Star Dust to the vault.
        is_purchase=True means real-money top-up; False means refund/gift.
        """
        if amount <= 0:
            raise ValueError("Credit amount must be positive.")
        self._star_dust_balance += amount
        if is_purchase:
            self._total_star_dust_purchased += amount
        self._touch()

    def debit(self, amount: int) -> None:
        """Spend Star Dust on a premium item."""
        if amount <= 0:
            raise ValueError("Debit amount must be positive.")
        if not self.can_afford(amount):
            raise ValueError("Insufficient Star Dust balance.")
        self._star_dust_balance -= amount
        self._total_star_dust_spent += amount
        self._touch()

    def refund(self, amount: int) -> None:
        """Refund Star Dust from a cancelled transaction."""
        if amount <= 0:
            raise ValueError("Refund amount must be positive.")
        self._star_dust_balance += amount
        self._total_star_dust_spent -= amount
        self._touch()
