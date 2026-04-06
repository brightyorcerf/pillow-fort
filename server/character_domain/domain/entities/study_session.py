"""
Study session entity — tracks individual focus sessions.

PRD §3.1.4 Effort Verification:
  - App must be in foreground during the session
  - Random check-in prompts (tap to confirm still studying)
  - Invalidated if phone idle > 5 continuous minutes
  - Sessions > 90 min grant "Flow State" buff

PRD §3.1.4 Diminishing Returns on low goals:
  0–15 min   → +1 HP
  16–24 min  → +4 HP
  25–60 min  → +10 HP (normal)
  60+ min    → +15–25 HP
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Optional


class SessionStatus(str, Enum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    INVALIDATED = "invalidated"
    ABANDONED = "abandoned"


class StudySession:

    FLOW_STATE_THRESHOLD_MINUTES = 90
    IDLE_TIMEOUT_MINUTES = 5

    def __init__(
        self,
        id: uuid.UUID,
        character_id: uuid.UUID,
        covenant_id: uuid.UUID,
        started_at: datetime,
        ended_at: Optional[datetime] = None,
        duration_minutes: int = 0,
        status: SessionStatus = SessionStatus.IN_PROGRESS,
        check_in_count: int = 0,
        check_in_passed: int = 0,
        was_foreground: bool = True,
        idle_violations: int = 0,
        created_at: Optional[datetime] = None,
    ):
        self._id = id
        self._character_id = character_id
        self._covenant_id = covenant_id
        self._started_at = started_at
        self._ended_at = ended_at
        self._duration_minutes = duration_minutes
        self._status = status
        self._check_in_count = check_in_count
        self._check_in_passed = check_in_passed
        self._was_foreground = was_foreground
        self._idle_violations = idle_violations
        self._created_at = created_at or datetime.now(timezone.utc)

    @classmethod
    def start(cls, character_id: uuid.UUID, covenant_id: uuid.UUID) -> StudySession:
        return cls(
            id=uuid.uuid4(),
            character_id=character_id,
            covenant_id=covenant_id,
            started_at=datetime.now(timezone.utc),
        )

    # ── Properties ─────────────────────────────────────────────────────

    @property
    def id(self) -> uuid.UUID:
        return self._id

    @property
    def character_id(self) -> uuid.UUID:
        return self._character_id

    @property
    def covenant_id(self) -> uuid.UUID:
        return self._covenant_id

    @property
    def started_at(self) -> datetime:
        return self._started_at

    @property
    def ended_at(self) -> Optional[datetime]:
        return self._ended_at

    @property
    def duration_minutes(self) -> int:
        return self._duration_minutes

    @property
    def status(self) -> SessionStatus:
        return self._status

    @property
    def check_in_count(self) -> int:
        return self._check_in_count

    @property
    def check_in_passed(self) -> int:
        return self._check_in_passed

    @property
    def was_foreground(self) -> bool:
        return self._was_foreground

    @property
    def idle_violations(self) -> int:
        return self._idle_violations

    @property
    def grants_flow_state(self) -> bool:
        return self._duration_minutes >= self.FLOW_STATE_THRESHOLD_MINUTES

    @property
    def created_at(self) -> datetime:
        return self._created_at

    # ── Domain behaviour ───────────────────────────────────────────────

    @property
    def is_verified(self) -> bool:
        """PRD: session is valid only if effort can be verified."""
        if not self._was_foreground:
            return False
        if self._idle_violations > 0:
            return False
        if self._check_in_count > 0 and self._check_in_passed < self._check_in_count:
            return False
        return True

    def record_check_in(self, passed: bool) -> None:
        self._check_in_count += 1
        if passed:
            self._check_in_passed += 1

    def record_idle_violation(self) -> None:
        self._idle_violations += 1

    def mark_backgrounded(self) -> None:
        self._was_foreground = False

    def complete(self, duration_minutes: int) -> None:
        self._ended_at = datetime.now(timezone.utc)
        self._duration_minutes = duration_minutes
        self._status = SessionStatus.COMPLETED

    def invalidate(self, reason: str = "") -> None:
        self._ended_at = datetime.now(timezone.utc)
        self._status = SessionStatus.INVALIDATED

    def abandon(self) -> None:
        self._ended_at = datetime.now(timezone.utc)
        self._status = SessionStatus.ABANDONED

    def compute_hp_gain(self) -> int:
        """
        Diminishing returns table — PRD §3.1.4.
        Only valid, verified sessions earn HP.
        """
        if not self.is_verified or self._status != SessionStatus.COMPLETED:
            return 0
        m = self._duration_minutes
        if m <= 15:
            return 1
        if m <= 24:
            return 4
        if m <= 60:
            return 10
        return min(25, 15 + (m - 60) // 30 * 5)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, StudySession):
            return NotImplemented
        return self._id == other._id

    def __hash__(self) -> int:
        return hash(self._id)
