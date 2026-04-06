"""
OwnedItem entity — an item in a user's inventory.

Once purchased, a store item becomes an OwnedItem. Some items are
consumable (feathers, bandages), others are permanent (themes, pets).

PRD §3.3 — Inventory class in shop system class diagram.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from character_domain.domain.value_objects.purchase_enums import ItemType


class OwnedItem:
    """
    Invariants:
      - quantity >= 0 (consumables can be depleted)
      - permanent items always have quantity = 1 and is_consumable = False
    """

    def __init__(
        self,
        id: uuid.UUID,
        user_id: uuid.UUID,
        item_id: uuid.UUID,
        item_name: str,
        item_type: ItemType,
        quantity: int = 1,
        is_consumable: bool = False,
        is_equipped: bool = False,
        acquired_at: Optional[datetime] = None,
    ) -> None:
        self._id = id
        self._user_id = user_id
        self._item_id = item_id
        self._item_name = item_name
        self._item_type = item_type
        self._quantity = max(0, quantity)
        self._is_consumable = is_consumable
        self._is_equipped = is_equipped
        self._acquired_at = acquired_at or datetime.now(timezone.utc)

    @classmethod
    def create(
        cls,
        user_id: uuid.UUID,
        item_id: uuid.UUID,
        item_name: str,
        item_type: ItemType,
        quantity: int = 1,
        is_consumable: bool = False,
    ) -> OwnedItem:
        return cls(
            id=uuid.uuid4(),
            user_id=user_id,
            item_id=item_id,
            item_name=item_name,
            item_type=item_type,
            quantity=quantity,
            is_consumable=is_consumable,
        )

    # ── Properties ─────────────────────────────────────────────────────

    @property
    def id(self) -> uuid.UUID:
        return self._id

    @property
    def user_id(self) -> uuid.UUID:
        return self._user_id

    @property
    def item_id(self) -> uuid.UUID:
        return self._item_id

    @property
    def item_name(self) -> str:
        return self._item_name

    @property
    def item_type(self) -> ItemType:
        return self._item_type

    @property
    def quantity(self) -> int:
        return self._quantity

    @property
    def is_consumable(self) -> bool:
        return self._is_consumable

    @property
    def is_equipped(self) -> bool:
        return self._is_equipped

    @property
    def acquired_at(self) -> datetime:
        return self._acquired_at

    # ── Mutations ──────────────────────────────────────────────────────

    def add_quantity(self, amount: int = 1) -> None:
        if amount <= 0:
            raise ValueError("Amount must be positive.")
        self._quantity += amount

    def consume(self, amount: int = 1) -> None:
        """Use a consumable item."""
        if not self._is_consumable:
            raise ValueError("This item is not consumable.")
        if self._quantity < amount:
            raise ValueError("Not enough quantity to consume.")
        self._quantity -= amount

    def equip(self) -> None:
        self._is_equipped = True

    def unequip(self) -> None:
        self._is_equipped = False

    def has_stock(self) -> bool:
        return self._quantity > 0
