"""Repository interface for Character aggregate."""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from typing import Optional

from character_domain.domain.entities.character import Character


class ICharacterRepository(ABC):

    @abstractmethod
    async def find_by_id(self, character_id: uuid.UUID) -> Optional[Character]:
        ...

    @abstractmethod
    async def find_by_user_id(self, user_id: uuid.UUID) -> Optional[Character]:
        ...

    @abstractmethod
    async def save(self, character: Character) -> None:
        ...

    @abstractmethod
    async def update(self, character: Character) -> None:
        ...
