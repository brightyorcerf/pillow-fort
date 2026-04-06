"""
Price value object — immutable representation of an item's cost.

Supports dual-currency pricing and discount calculations.
PRD §3.3 — Coins are cheap-item currency, Star Dust is premium.
"""

from __future__ import annotations

from dataclasses import dataclass

from character_domain.domain.value_objects.purchase_enums import CurrencyType


@dataclass(frozen=True)
class Price:
    """
    Immutable price tag.

    Invariants:
      - original_amount >= 0
      - discounted_amount >= 0 and <= original_amount
    """

    currency: CurrencyType
    original_amount: int
    discounted_amount: int | None = None  # None means no discount

    @property
    def effective_amount(self) -> int:
        """What the buyer actually pays."""
        if self.discounted_amount is not None:
            return self.discounted_amount
        return self.original_amount

    @property
    def is_on_sale(self) -> bool:
        return (
            self.discounted_amount is not None
            and self.discounted_amount < self.original_amount
        )

    @property
    def discount_percent(self) -> int:
        """Percentage discount (0–100)."""
        if not self.is_on_sale or self.original_amount == 0:
            return 0
        return round(
            (1 - self.discounted_amount / self.original_amount) * 100
        )

    def __post_init__(self):
        if self.original_amount < 0:
            raise ValueError("original_amount must be >= 0")
        if self.discounted_amount is not None and self.discounted_amount < 0:
            raise ValueError("discounted_amount must be >= 0")
        if (
            self.discounted_amount is not None
            and self.discounted_amount > self.original_amount
        ):
            raise ValueError("discounted_amount cannot exceed original_amount")
