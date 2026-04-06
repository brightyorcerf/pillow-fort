"""
DeathRecord entity — immutable record of a character's death.

Created by the Reaper every time a character dies. Captures the full
context: cause, HP at death, ghost days, total study hours, whether
the eulogy was generated, and whether the death is permanent.

PRD §3.2 — The Eulogy / Death & Revival.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from character_domain.domain.value_objects.reaper_enums import DeathCause


@dataclass
class DeathRecord:
    """
    Invariants:
      - Once created, only eulogy_generated and is_permanent may change
      - Tracks full snapshot of character state at time of death
    """

    id: uuid.UUID
    character_id: uuid.UUID
    user_id: uuid.UUID
    cause: DeathCause
    hp_at_death: int
    total_hours_in_life: float
    consecutive_ghost_days_at_death: int
    rituals_used_at_death: int
    longest_streak_at_death: int
    eulogy_generated: bool = False
    is_permanent: bool = False
    promises_id: Optional[uuid.UUID] = None
    died_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @classmethod
    def create(
        cls,
        character_id: uuid.UUID,
        user_id: uuid.UUID,
        cause: DeathCause,
        hp_at_death: int,
        total_hours_in_life: float,
        consecutive_ghost_days_at_death: int,
        rituals_used_at_death: int,
        longest_streak_at_death: int,
        is_permanent: bool = False,
    ) -> DeathRecord:
        return cls(
            id=uuid.uuid4(),
            character_id=character_id,
            user_id=user_id,
            cause=cause,
            hp_at_death=hp_at_death,
            total_hours_in_life=total_hours_in_life,
            consecutive_ghost_days_at_death=consecutive_ghost_days_at_death,
            rituals_used_at_death=rituals_used_at_death,
            longest_streak_at_death=longest_streak_at_death,
            is_permanent=is_permanent,
        )

    def mark_eulogy_generated(self, promises_id: uuid.UUID) -> None:
        self.eulogy_generated = True
        self.promises_id = promises_id

    def mark_permanent(self) -> None:
        self.is_permanent = True
