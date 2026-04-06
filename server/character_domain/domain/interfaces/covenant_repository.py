"""Repository interface for Covenant entity."""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from datetime import date
from typing import Optional

from character_domain.domain.entities.covenant import Covenant


class ICovenantRepository(ABC):

    @abstractmethod
    async def find_by_id(self, covenant_id: uuid.UUID) -> Optional[Covenant]:
        ...

    @abstractmethod
    async def find_active_for_date(
        self, character_id: uuid.UUID, covenant_date: date
    ) -> Optional[Covenant]:
        ...

    @abstractmethod
    async def save(self, covenant: Covenant) -> None:
        ...

    @abstractmethod
    async def update(self, covenant: Covenant) -> None:
        ...

    @abstractmethod
    async def get_recent(
        self, character_id: uuid.UUID, days: int = 7
    ) -> list[Covenant]:
        """Retrieve covenants from the last N days for PVR calculation."""
        ...

    @abstractmethod
    async def get_average_goal_minutes(
        self, character_id: uuid.UUID, days: int = 7
    ) -> float:
        """Average daily goal in minutes over the last N days."""
        ...

    @abstractmethod
    async def get_average_actual_minutes(
        self, character_id: uuid.UUID, days: int = 14
    ) -> float:
        """Average actual study time over the last N days (for session cap)."""
        ...
