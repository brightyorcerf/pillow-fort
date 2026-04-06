"""
StoreItem entity — a purchasable item in the shop catalog.

Each item has a type, category, price (in either currency),
and an optional town-hall-level gate for progression-locked items.

PRD §3.3 — Shop system class diagram.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from character_domain.domain.value_objects.price import Price
from character_domain.domain.value_objects.purchase_enums import (
    CategoryType,
    CurrencyType,
    ItemType,
)


class StoreItem:
    """
    Invariants:
      - price.effective_amount >= 0
      - required_level >= 0
      - An item belongs to exactly one category
    """

    def __init__(
        self,
        id: uuid.UUID,
        name: str,
        description: str,
        item_type: ItemType,
        category: CategoryType,
        price_currency: CurrencyType,
        price_amount: int,
        discounted_amount: int | None = None,
        required_level: int = 0,
        is_active: bool = True,
        max_per_user: int | None = None,  # None = unlimited
        image_url: str | None = None,
        metadata: dict | None = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ) -> None:
        self._id = id
        self._name = name
        self._description = description
        self._item_type = item_type
        self._category = category
        self._price = Price(
            currency=price_currency,
            original_amount=price_amount,
            discounted_amount=discounted_amount,
        )
        self._required_level = required_level
        self._is_active = is_active
        self._max_per_user = max_per_user
        self._image_url = image_url
        self._metadata = metadata or {}
        self._created_at = created_at or datetime.now(timezone.utc)
        self._updated_at = updated_at or datetime.now(timezone.utc)

    @classmethod
    def create(
        cls,
        name: str,
        description: str,
        item_type: ItemType,
        category: CategoryType,
        price_currency: CurrencyType,
        price_amount: int,
        required_level: int = 0,
        max_per_user: int | None = None,
        image_url: str | None = None,
        metadata: dict | None = None,
    ) -> StoreItem:
        return cls(
            id=uuid.uuid4(),
            name=name,
            description=description,
            item_type=item_type,
            category=category,
            price_currency=price_currency,
            price_amount=price_amount,
            required_level=required_level,
            max_per_user=max_per_user,
            image_url=image_url,
            metadata=metadata,
        )

    # ── Properties ─────────────────────────────────────────────────────

    @property
    def id(self) -> uuid.UUID:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    @property
    def item_type(self) -> ItemType:
        return self._item_type

    @property
    def category(self) -> CategoryType:
        return self._category

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
    def max_per_user(self) -> int | None:
        return self._max_per_user

    @property
    def image_url(self) -> str | None:
        return self._image_url

    @property
    def metadata(self) -> dict:
        return dict(self._metadata)

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        return self._updated_at

    # ── Mutations ──────────────────────────────────────────────────────

    def _touch(self) -> None:
        self._updated_at = datetime.now(timezone.utc)

    def is_unlocked(self, player_level: int) -> bool:
        """Check if the player meets the level requirement."""
        return player_level >= self._required_level

    def activate(self) -> None:
        self._is_active = True
        self._touch()

    def deactivate(self) -> None:
        self._is_active = False
        self._touch()

    def update_price(
        self,
        price_amount: int,
        discounted_amount: int | None = None,
    ) -> None:
        self._price = Price(
            currency=self._price.currency,
            original_amount=price_amount,
            discounted_amount=discounted_amount,
        )
        self._touch()

    def set_discount(self, discounted_amount: int) -> None:
        self._price = Price(
            currency=self._price.currency,
            original_amount=self._price.original_amount,
            discounted_amount=discounted_amount,
        )
        self._touch()

    def remove_discount(self) -> None:
        self._price = Price(
            currency=self._price.currency,
            original_amount=self._price.original_amount,
            discounted_amount=None,
        )
        self._touch()
