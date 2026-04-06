"""Repository interface for OwnedItem (user inventory)."""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from typing import Optional

from character_domain.domain.entities.owned_item import OwnedItem
from character_domain.domain.value_objects.purchase_enums import ItemType


class IInventoryRepository(ABC):

    @abstractmethod
    async def save(self, item: OwnedItem) -> None: ...

    @abstractmethod
    async def update(self, item: OwnedItem) -> None: ...

    @abstractmethod
    async def find_by_id(self, owned_id: uuid.UUID) -> Optional[OwnedItem]: ...

    @abstractmethod
    async def find_by_user(self, user_id: uuid.UUID) -> list[OwnedItem]: ...

    @abstractmethod
    async def find_by_user_and_item(
        self, user_id: uuid.UUID, item_id: uuid.UUID
    ) -> Optional[OwnedItem]: ...

    @abstractmethod
    async def find_by_user_and_type(
        self, user_id: uuid.UUID, item_type: ItemType
    ) -> list[OwnedItem]: ...

    @abstractmethod
    async def count_by_user_and_item(
        self, user_id: uuid.UUID, item_id: uuid.UUID
    ) -> int: ...
