"""
Wallet entity — per-user dual-currency balance.

Coins are earned via study and lost partially on death (25%).
Star Dust is managed separately by the VaultWallet.

PRD §3.3 — Dual economy model.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from character_domain.domain.value_objects.purchase_enums import CurrencyType


class Wallet:
    """
    Invariants:
      - coin_balance >= 0
      - Wallet is per-user, not per-character
    """

    DEATH_COIN_LOSS_PCT = 0.25  # 25% coins lost on unrevived death

    def __init__(
        self,
        id: uuid.UUID,
        user_id: uuid.UUID,
        coin_balance: int = 0,
        total_coins_earned: int = 0,
        total_coins_spent: int = 0,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ) -> None:
        self._id = id
        self._user_id = user_id
        self._coin_balance = max(0, coin_balance)
        self._total_coins_earned = total_coins_earned
        self._total_coins_spent = total_coins_spent
        self._created_at = created_at or datetime.now(timezone.utc)
        self._updated_at = updated_at or datetime.now(timezone.utc)

    @classmethod
    def create(cls, user_id: uuid.UUID) -> Wallet:
        return cls(id=uuid.uuid4(), user_id=user_id)

    # ── Properties ─────────────────────────────────────────────────────

    @property
    def id(self) -> uuid.UUID:
        return self._id

    @property
    def user_id(self) -> uuid.UUID:
        return self._user_id

    @property
    def coin_balance(self) -> int:
        return self._coin_balance

    @property
    def total_coins_earned(self) -> int:
        return self._total_coins_earned

    @property
    def total_coins_spent(self) -> int:
        return self._total_coins_spent

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        return self._updated_at

    # ── Mutations ──────────────────────────────────────────────────────

    def _touch(self) -> None:
        self._updated_at = datetime.now(timezone.utc)

    def can_afford_coins(self, amount: int) -> bool:
        return self._coin_balance >= amount

    def credit_coins(self, amount: int) -> None:
        """Add earned coins (study rewards, streak bonuses)."""
        if amount <= 0:
            raise ValueError("Credit amount must be positive.")
        self._coin_balance += amount
        self._total_coins_earned += amount
        self._touch()

    def debit_coins(self, amount: int) -> None:
        """Spend coins on a purchase."""
        if amount <= 0:
            raise ValueError("Debit amount must be positive.")
        if not self.can_afford_coins(amount):
            raise ValueError("Insufficient coin balance.")
        self._coin_balance -= amount
        self._total_coins_spent += amount
        self._touch()

    def apply_death_penalty(self) -> int:
        """
        Lose 25% of coins on character death (unrevived).
        Returns the amount lost.
        """
        loss = int(self._coin_balance * self.DEATH_COIN_LOSS_PCT)
        self._coin_balance -= loss
        self._touch()
        return loss

    def refund_coins(self, amount: int) -> None:
        """Refund coins from a cancelled transaction."""
        if amount <= 0:
            raise ValueError("Refund amount must be positive.")
        self._coin_balance += amount
        self._total_coins_spent -= amount
        self._touch()
