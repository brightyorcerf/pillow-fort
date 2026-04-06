"""Repository interface for HPLog audit records."""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from datetime import date
from typing import Optional

from character_domain.domain.entities.hp_log import HPLog
from character_domain.domain.value_objects.hp_change_result import HPChangeReason


class IHPLogRepository(ABC):

    @abstractmethod
    async def create(self, log: HPLog) -> None:
        """Persist a new HP log entry."""
        ...

    @abstractmethod
    async def get_by_character(
        self, character_id: uuid.UUID, limit: int = 50
    ) -> list[HPLog]:
        """Retrieve HP logs for a character, most recent first."""
        ...

    @abstractmethod
    async def get_by_reason(
        self, character_id: uuid.UUID, reason: HPChangeReason, limit: int = 20
    ) -> list[HPLog]:
        """Retrieve HP logs filtered by reason."""
        ...

    @abstractmethod
    async def get_today(self, character_id: uuid.UUID) -> list[HPLog]:
        """Retrieve all HP logs for today (UTC)."""
        ...

    @abstractmethod
    async def get_for_date_range(
        self, character_id: uuid.UUID, start_date: date, end_date: date
    ) -> list[HPLog]:
        """Retrieve HP logs within a date range."""
        ...

    @abstractmethod
    async def get_total_delta_today(self, character_id: uuid.UUID) -> int:
        """Sum of all HP deltas for today — net HP change."""
        ...
