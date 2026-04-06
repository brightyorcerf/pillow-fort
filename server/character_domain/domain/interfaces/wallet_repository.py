"""Repository interface for Wallet (coin balance)."""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from typing import Optional

from character_domain.domain.entities.wallet import Wallet


class IWalletRepository(ABC):

    @abstractmethod
    async def save(self, wallet: Wallet) -> None: ...

    @abstractmethod
    async def update(self, wallet: Wallet) -> None: ...

    @abstractmethod
    async def find_by_user(self, user_id: uuid.UUID) -> Optional[Wallet]: ...

    @abstractmethod
    async def find_by_id(self, wallet_id: uuid.UUID) -> Optional[Wallet]: ...
