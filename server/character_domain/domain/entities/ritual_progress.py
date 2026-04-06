"""
Ritual progress entity — tracks a user's journey through a re-engagement ritual.

PRD §3.1.3:
  - If the user ghosts mid-ritual, the ritual resets from step 1
  - Progress is separate from the HP bar
  - Reflection answers are stored for future rituals
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from character_domain.domain.value_objects.ritual_type import (
    RITUAL_DEFINITIONS,
    RITUAL_ORDER,
    RitualType,
)


class RitualStatus(str, Enum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"  # ghosted mid-ritual


class RitualProgress:

    def __init__(
        self,
        id: uuid.UUID,
        character_id: uuid.UUID,
        ritual_type: RitualType,
        ritual_number: int,       # 1st, 2nd, or 3rd ritual attempt
        current_step: int = 0,
        status: RitualStatus = RitualStatus.IN_PROGRESS,
        hp_restored_so_far: int = 0,
        reflection_answers: list[str] | None = None,
        started_at: Optional[datetime] = None,
        completed_at: Optional[datetime] = None,
    ):
        self._id = id
        self._character_id = character_id
        self._ritual_type = ritual_type
        self._ritual_number = ritual_number
        self._current_step = current_step
        self._status = status
        self._hp_restored_so_far = hp_restored_so_far
        self._reflection_answers = reflection_answers or []
        self._started_at = started_at or datetime.now(timezone.utc)
        self._completed_at = completed_at

    @classmethod
    def begin(cls, character_id: uuid.UUID, rituals_used: int) -> RitualProgress:
        """Start the next ritual in sequence based on how many have been used."""
        ritual_index = min(rituals_used, len(RITUAL_ORDER) - 1)
        ritual_type = RITUAL_ORDER[ritual_index]
        return cls(
            id=uuid.uuid4(),
            character_id=character_id,
            ritual_type=ritual_type,
            ritual_number=rituals_used + 1,
        )

    # ── Properties ─────────────────────────────────────────────────────

    @property
    def id(self) -> uuid.UUID:
        return self._id

    @property
    def character_id(self) -> uuid.UUID:
        return self._character_id

    @property
    def ritual_type(self) -> RitualType:
        return self._ritual_type

    @property
    def ritual_number(self) -> int:
        return self._ritual_number

    @property
    def current_step(self) -> int:
        return self._current_step

    @property
    def status(self) -> RitualStatus:
        return self._status

    @property
    def hp_restored_so_far(self) -> int:
        return self._hp_restored_so_far

    @property
    def reflection_answers(self) -> list[str]:
        return list(self._reflection_answers)

    @property
    def started_at(self) -> datetime:
        return self._started_at

    @property
    def completed_at(self) -> Optional[datetime]:
        return self._completed_at

    @property
    def total_steps(self) -> int:
        return len(RITUAL_DEFINITIONS[self._ritual_type])

    @property
    def is_complete(self) -> bool:
        return self._current_step >= self.total_steps

    @property
    def next_step_description(self) -> str | None:
        steps = RITUAL_DEFINITIONS[self._ritual_type]
        if self._current_step < len(steps):
            return steps[self._current_step].action_required
        return None

    # ── Domain behaviour ───────────────────────────────────────────────

    def advance_step(self, reflection_answer: str | None = None) -> int:
        """
        Complete the current step and advance. Returns HP restored by this step.
        """
        steps = RITUAL_DEFINITIONS[self._ritual_type]
        if self._current_step >= len(steps):
            return 0

        step = steps[self._current_step]
        self._current_step += 1
        self._hp_restored_so_far += step.hp_restored

        if reflection_answer:
            self._reflection_answers.append(reflection_answer)

        if self.is_complete:
            self._status = RitualStatus.COMPLETED
            self._completed_at = datetime.now(timezone.utc)

        return step.hp_restored

    def reset_on_ghost(self) -> None:
        """PRD: if user ghosts mid-ritual, the ritual resets from step 1."""
        self._current_step = 0
        self._hp_restored_so_far = 0
        self._status = RitualStatus.IN_PROGRESS

    def abandon(self) -> None:
        self._status = RitualStatus.ABANDONED

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, RitualProgress):
            return NotImplemented
        return self._id == other._id

    def __hash__(self) -> int:
        return hash(self._id)
