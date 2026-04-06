"""Repository interface for StoreItem catalog."""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from typing import Optional

from character_domain.domain.entities.store_item import StoreItem
from character_domain.domain.value_objects.purchase_enums import CategoryType, ItemType


class IStoreItemRepository(ABC):

    @abstractmethod
    async def save(self, item: StoreItem) -> None: ...

    @abstractmethod
    async def update(self, item: StoreItem) -> None: ...

    @abstractmethod
    async def find_by_id(self, item_id: uuid.UUID) -> Optional[StoreItem]: ...

    @abstractmethod
    async def find_by_name(self, name: str) -> Optional[StoreItem]: ...

    @abstractmethod
    async def find_active_by_category(self, category: CategoryType) -> list[StoreItem]: ...

    @abstractmethod
    async def find_active_by_type(self, item_type: ItemType) -> list[StoreItem]: ...

    @abstractmethod
    async def find_all_active(self) -> list[StoreItem]: ...

    @abstractmethod
    async def exists_by_name(self, name: str) -> bool: ...
