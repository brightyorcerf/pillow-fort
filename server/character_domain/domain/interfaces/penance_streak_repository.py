"""Repository interface for PenanceStreak entities."""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from typing import Optional

from character_domain.domain.entities.penance_streak import PenanceStreak


class IPenanceStreakRepository(ABC):

    @abstractmethod
    async def save(self, penance: PenanceStreak) -> None:
        ...

    @abstractmethod
    async def update(self, penance: PenanceStreak) -> None:
        ...

    @abstractmethod
    async def find_active_for_character(
        self, character_id: uuid.UUID
    ) -> Optional[PenanceStreak]:
        """Find the currently active penance streak (if any)."""
        ...

    @abstractmethod
    async def find_by_id(self, penance_id: uuid.UUID) -> Optional[PenanceStreak]:
        ...

    @abstractmethod
    async def count_attempts_for_character(
        self, character_id: uuid.UUID
    ) -> int:
        """Total penance attempts (including failed ones)."""
        ...
