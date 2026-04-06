"""Repository interface for Transaction records."""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from typing import Optional

from character_domain.domain.entities.transaction import Transaction


class ITransactionRepository(ABC):

    @abstractmethod
    async def save(self, txn: Transaction) -> None: ...

    @abstractmethod
    async def update(self, txn: Transaction) -> None: ...

    @abstractmethod
    async def find_by_id(self, txn_id: uuid.UUID) -> Optional[Transaction]: ...

    @abstractmethod
    async def find_by_user(
        self, user_id: uuid.UUID, limit: int = 50
    ) -> list[Transaction]: ...

    @abstractmethod
    async def count_completed_for_item(
        self, user_id: uuid.UUID, item_id: uuid.UUID
    ) -> int: ...
