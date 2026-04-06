"""
EulogyService interface — generates the permanent record of a
character's life achievements ("Promises Kept").

The Reaper delegates eulogy generation to this service when a
character dies. The resulting Eulogy captures hours studied,
streaks, rank achieved, and other metrics.

PRD §3.2 — The Eulogy.
"""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass(frozen=True)
class Eulogy:
    """Immutable record of a character's lifetime achievements."""
    id: uuid.UUID
    character_id: uuid.UUID
    user_id: uuid.UUID
    death_record_id: uuid.UUID
    character_name: str
    total_study_hours: float
    longest_streak: int
    rank_achieved: str
    life_shields_earned: int
    rituals_completed: int
    total_covenants_signed: int
    total_covenants_kept: int
    born_at: datetime
    died_at: datetime
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class IEulogyService(ABC):
    """
    Port for eulogy generation.

    Concrete implementation may:
      - Query repositories for lifetime stats
      - Format a rich eulogy document
      - Store it permanently in a vault
    """

    @abstractmethod
    async def generate(
        self,
        character_id: uuid.UUID,
        user_id: uuid.UUID,
        death_record_id: uuid.UUID,
    ) -> Eulogy:
        """Generate and persist a full eulogy for the dead character."""
        ...

    @abstractmethod
    async def find_by_character(
        self, character_id: uuid.UUID
    ) -> list[Eulogy]:
        """Retrieve all eulogies for a character (multiple lives)."""
        ...

    @abstractmethod
    async def find_by_death_record(
        self, death_record_id: uuid.UUID
    ) -> Eulogy | None:
        """Retrieve the eulogy for a specific death."""
        ...
