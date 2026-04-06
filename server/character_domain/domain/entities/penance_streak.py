"""
PenanceStreak entity — tracks a free revival path where the user
must hit 100% of their daily goal for 7 consecutive days while ghost.

If they miss a single day, the penance fails and must be restarted
(counting against their total revival attempts).

PRD §3.1.3 — Penance Streak revival path.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from character_domain.domain.value_objects.reaper_enums import PenanceStatus


@dataclass
class PenanceStreak:
    """
    Invariants:
      - required_days is always 7
      - days_completed in [0, required_days]
      - Once COMPLETED or FAILED, status is final
    """

    REQUIRED_DAYS = 7

    id: uuid.UUID
    character_id: uuid.UUID
    death_record_id: uuid.UUID
    attempt_number: int
    required_days: int = 7
    days_completed: int = 0
    status: PenanceStatus = PenanceStatus.ACTIVE
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
    failed_at: Optional[datetime] = None

    @classmethod
    def start(
        cls,
        character_id: uuid.UUID,
        death_record_id: uuid.UUID,
        attempt_number: int,
    ) -> PenanceStreak:
        return cls(
            id=uuid.uuid4(),
            character_id=character_id,
            death_record_id=death_record_id,
            attempt_number=attempt_number,
        )

    @property
    def is_active(self) -> bool:
        return self.status == PenanceStatus.ACTIVE

    @property
    def is_complete(self) -> bool:
        return self.status == PenanceStatus.COMPLETED

    @property
    def days_remaining(self) -> int:
        return max(0, self.required_days - self.days_completed)

    @property
    def progress_pct(self) -> float:
        return (self.days_completed / self.required_days) * 100

    def record_day_success(self) -> bool:
        """
        Record that today's goal was met at 100%.
        Returns True if penance is now complete.
        """
        if not self.is_active:
            return False

        self.days_completed += 1

        if self.days_completed >= self.required_days:
            self.status = PenanceStatus.COMPLETED
            self.completed_at = datetime.now(timezone.utc)
            return True

        return False

    def record_day_failure(self) -> None:
        """Goal was missed — penance streak is broken."""
        if not self.is_active:
            return

        self.status = PenanceStatus.FAILED
        self.failed_at = datetime.now(timezone.utc)
