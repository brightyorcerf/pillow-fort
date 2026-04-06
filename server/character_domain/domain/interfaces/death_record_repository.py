"""Repository interface for DeathRecord entities."""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from typing import Optional

from character_domain.domain.entities.death_record import DeathRecord


class IDeathRecordRepository(ABC):

    @abstractmethod
    async def save(self, record: DeathRecord) -> None:
        ...

    @abstractmethod
    async def update(self, record: DeathRecord) -> None:
        ...

    @abstractmethod
    async def find_by_id(self, record_id: uuid.UUID) -> Optional[DeathRecord]:
        ...

    @abstractmethod
    async def find_latest_for_character(
        self, character_id: uuid.UUID
    ) -> Optional[DeathRecord]:
        """Most recent death record for a character."""
        ...

    @abstractmethod
    async def find_all_for_character(
        self, character_id: uuid.UUID
    ) -> list[DeathRecord]:
        """All death records, most recent first."""
        ...

    @abstractmethod
    async def count_for_character(self, character_id: uuid.UUID) -> int:
        """Total number of deaths for a character."""
        ...
