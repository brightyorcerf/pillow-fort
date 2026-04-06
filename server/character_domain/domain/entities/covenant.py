"""
Covenant entity — the daily "Contract Phase" (PRD §3.1.1).

Every 24 hours the user must set a daily goal and sign the covenant.
Once signed via on-screen signature, the goal is locked for the day.
"""

from __future__ import annotations

import uuid
from datetime import date, datetime, timezone
from enum import Enum
from typing import Optional

from character_domain.domain.value_objects.subject_type import SubjectType


class CovenantStatus(str, Enum):
    ACTIVE = "active"          # Goal set, timer running or waiting
    COMPLETED = "completed"    # Goal met or exceeded
    PARTIAL = "partial"        # Some progress but below goal
    MISSED = "missed"          # Day ended without meeting goal
    GHOSTED = "ghosted"        # App never opened / no covenant set


class Covenant:
    """
    Represents a single day's commitment.

    Invariants:
      - goal_minutes >= subject minimum threshold
      - goal_minutes <= hard ceiling (6 hours)
      - Once signed, goal_minutes cannot be changed
    """

    HARD_CEILING_MINUTES = 360  # PRD §3.1.5a — 6 hours universal

    def __init__(
        self,
        id: uuid.UUID,
        character_id: uuid.UUID,
        covenant_date: date,
        subject_type: SubjectType,
        goal_minutes: int,
        actual_minutes: int = 0,
        status: CovenantStatus = CovenantStatus.ACTIVE,
        is_signed: bool = False,
        signed_at: Optional[datetime] = None,
        hp_gain_multiplier: float = 1.0,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self._id = id
        self._character_id = character_id
        self._covenant_date = covenant_date
        self._subject_type = subject_type
        self._goal_minutes = min(goal_minutes, self.HARD_CEILING_MINUTES)
        self._actual_minutes = actual_minutes
        self._status = status
        self._is_signed = is_signed
        self._signed_at = signed_at
        self._hp_gain_multiplier = hp_gain_multiplier
        self._created_at = created_at or datetime.now(timezone.utc)
        self._updated_at = updated_at or datetime.now(timezone.utc)

    # ── Factory ────────────────────────────────────────────────────────

    @classmethod
    def create(
        cls,
        character_id: uuid.UUID,
        covenant_date: date,
        subject_type: SubjectType,
        goal_minutes: int,
        hp_gain_multiplier: float = 1.0,
    ) -> Covenant:
        return cls(
            id=uuid.uuid4(),
            character_id=character_id,
            covenant_date=covenant_date,
            subject_type=subject_type,
            goal_minutes=goal_minutes,
            hp_gain_multiplier=hp_gain_multiplier,
        )

    # ── Properties ─────────────────────────────────────────────────────

    @property
    def id(self) -> uuid.UUID:
        return self._id

    @property
    def character_id(self) -> uuid.UUID:
        return self._character_id

    @property
    def covenant_date(self) -> date:
        return self._covenant_date

    @property
    def subject_type(self) -> SubjectType:
        return self._subject_type

    @property
    def goal_minutes(self) -> int:
        return self._goal_minutes

    @property
    def actual_minutes(self) -> int:
        return self._actual_minutes

    @property
    def status(self) -> CovenantStatus:
        return self._status

    @property
    def is_signed(self) -> bool:
        return self._is_signed

    @property
    def signed_at(self) -> Optional[datetime]:
        return self._signed_at

    @property
    def hp_gain_multiplier(self) -> float:
        return self._hp_gain_multiplier

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        return self._updated_at

    # ── Domain behaviour ───────────────────────────────────────────────

    @property
    def completion_ratio(self) -> float:
        if self._goal_minutes <= 0:
            return 0.0
        return self._actual_minutes / self._goal_minutes

    def sign(self) -> None:
        """Lock the covenant — goal can no longer be changed."""
        self._is_signed = True
        self._signed_at = datetime.now(timezone.utc)
        self._touch()

    def add_minutes(self, minutes: int) -> None:
        self._actual_minutes += minutes
        self._touch()

    def mark_completed(self) -> None:
        self._status = CovenantStatus.COMPLETED
        self._touch()

    def mark_partial(self) -> None:
        self._status = CovenantStatus.PARTIAL
        self._touch()

    def mark_missed(self) -> None:
        self._status = CovenantStatus.MISSED
        self._touch()

    def mark_ghosted(self) -> None:
        self._status = CovenantStatus.GHOSTED
        self._touch()

    def _touch(self) -> None:
        self._updated_at = datetime.now(timezone.utc)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Covenant):
            return NotImplemented
        return self._id == other._id

    def __hash__(self) -> int:
        return hash(self._id)
