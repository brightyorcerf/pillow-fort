"""Repository interface for RevivalAttempt entities."""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from typing import Optional

from character_domain.domain.entities.revival_attempt import RevivalAttempt


class IRevivalAttemptRepository(ABC):

    @abstractmethod
    async def save(self, attempt: RevivalAttempt) -> None:
        ...

    @abstractmethod
    async def find_by_id(self, attempt_id: uuid.UUID) -> Optional[RevivalAttempt]:
        ...

    @abstractmethod
    async def find_all_for_character(
        self, character_id: uuid.UUID
    ) -> list[RevivalAttempt]:
        """All revival attempts, most recent first."""
        ...

    @abstractmethod
    async def count_successful_for_character(
        self, character_id: uuid.UUID
    ) -> int:
        """Total successful revivals for a character."""
        ...
