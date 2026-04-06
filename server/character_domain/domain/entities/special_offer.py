"""
SpecialOffer entity — time-limited bundle deals in the shop.

A special offer bundles multiple store items at a discounted price,
available for a limited time and potentially gated by player level.

PRD §3.3 — Store class diagram.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from character_domain.domain.value_objects.price import Price
from character_domain.domain.value_objects.purchase_enums import CurrencyType


class SpecialOffer:
    """
    Invariants:
      - bundled_item_ids is non-empty
      - expires_at > created_at
      - bundle_price.effective_amount < sum of individual item prices
    """

    def __init__(
        self,
        id: uuid.UUID,
        title: str,
        description: str,
        bundled_item_ids: list[uuid.UUID],
        bundle_currency: CurrencyType,
        bundle_price: int,
        original_total: int,
        required_level: int = 0,
        is_active: bool = True,
        expires_at: Optional[datetime] = None,
        image_url: str | None = None,
        created_at: Optional[datetime] = None,
    ) -> None:
        self._id = id
        self._title = title
        self._description = description
        self._bundled_item_ids = list(bundled_item_ids)
        self._price = Price(
            currency=bundle_currency,
            original_amount=original_total,
            discounted_amount=bundle_price,
        )
        self._required_level = required_level
        self._is_active = is_active
        self._expires_at = expires_at
        self._image_url = image_url
        self._created_at = created_at or datetime.now(timezone.utc)

    @classmethod
    def create(
        cls,
        title: str,
        description: str,
        bundled_item_ids: list[uuid.UUID],
        bundle_currency: CurrencyType,
        bundle_price: int,
        original_total: int,
        required_level: int = 0,
        expires_at: Optional[datetime] = None,
        image_url: str | None = None,
    ) -> SpecialOffer:
        return cls(
            id=uuid.uuid4(),
            title=title,
            description=description,
            bundled_item_ids=bundled_item_ids,
            bundle_currency=bundle_currency,
            bundle_price=bundle_price,
            original_total=original_total,
            required_level=required_level,
            expires_at=expires_at,
            image_url=image_url,
        )

    # ── Properties ─────────────────────────────────────────────────────

    @property
    def id(self) -> uuid.UUID:
        return self._id

    @property
    def title(self) -> str:
        return self._title

    @property
    def description(self) -> str:
        return self._description

    @property
    def bundled_item_ids(self) -> list[uuid.UUID]:
        return list(self._bundled_item_ids)

    @property
    def price(self) -> Price:
        return self._price

    @property
    def required_level(self) -> int:
        return self._required_level

    @property
    def is_active(self) -> bool:
        return self._is_active

    @property
    def expires_at(self) -> Optional[datetime]:
        return self._expires_at

    @property
    def image_url(self) -> str | None:
        return self._image_url

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def discount_percent(self) -> int:
        return self._price.discount_percent

    # ── Query ──────────────────────────────────────────────────────────

    def is_expired(self) -> bool:
        if self._expires_at is None:
            return False
        return datetime.now(timezone.utc) > self._expires_at

    def is_available(self, player_level: int) -> bool:
        return (
            self._is_active
            and not self.is_expired()
            and player_level >= self._required_level
        )

    # ── Mutations ──────────────────────────────────────────────────────

    def deactivate(self) -> None:
        self._is_active = False
