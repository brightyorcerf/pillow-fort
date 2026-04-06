"""Repository interface for PhoenixFeather entities."""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from typing import Optional

from character_domain.domain.entities.phoenix_feather import PhoenixFeather


class IPhoenixFeatherRepository(ABC):

    @abstractmethod
    async def save(self, feather: PhoenixFeather) -> None:
        ...

    @abstractmethod
    async def update(self, feather: PhoenixFeather) -> None:
        ...

    @abstractmethod
    async def find_available_for_user(
        self, user_id: uuid.UUID
    ) -> Optional[PhoenixFeather]:
        """Find the first available (unused) feather for a user."""
        ...

    @abstractmethod
    async def find_by_id(self, feather_id: uuid.UUID) -> Optional[PhoenixFeather]:
        ...

    @abstractmethod
    async def count_available_for_user(self, user_id: uuid.UUID) -> int:
        """How many unused feathers does the user have?"""
        ...
