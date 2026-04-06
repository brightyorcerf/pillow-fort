"""
PhoenixFeather entity — premium revival item purchased with Star Dust.

A Phoenix Feather allows instant revival without consuming a ritual slot.
Feathers have a lifecycle: AVAILABLE → USED or EXPIRED.

PRD §3.1.3 — Phoenix Feather revival path.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from character_domain.domain.value_objects.reaper_enums import FeatherStatus


@dataclass
class PhoenixFeather:
    """
    Invariants:
      - Once USED or EXPIRED, status is final
      - price_paid_stardust >= 0
    """

    id: uuid.UUID
    user_id: uuid.UUID
    character_id: Optional[uuid.UUID]     # Bound to character on use
    status: FeatherStatus
    price_paid_stardust: int
    acquired_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    used_at: Optional[datetime] = None

    @classmethod
    def purchase(
        cls,
        user_id: uuid.UUID,
        price_stardust: int,
    ) -> PhoenixFeather:
        return cls(
            id=uuid.uuid4(),
            user_id=user_id,
            character_id=None,
            status=FeatherStatus.AVAILABLE,
            price_paid_stardust=price_stardust,
        )

    @classmethod
    def grant_free(cls, user_id: uuid.UUID) -> "PhoenixFeather":
        """Grant a free Phoenix Feather (e.g. onboarding bonus)."""
        return cls(
            id=uuid.uuid4(),
            user_id=user_id,
            character_id=None,
            status=FeatherStatus.AVAILABLE,
            price_paid_stardust=0,
        )

    @property
    def is_available(self) -> bool:
        return self.status == FeatherStatus.AVAILABLE

    def use(self, character_id: uuid.UUID) -> None:
        """Consume the feather to revive a character."""
        if not self.is_available:
            raise ValueError("Feather is not available for use.")
        self.status = FeatherStatus.USED
        self.character_id = character_id
        self.used_at = datetime.now(timezone.utc)

    def expire(self) -> None:
        """Mark the feather as expired (e.g. season end)."""
        if not self.is_available:
            return
        self.status = FeatherStatus.EXPIRED
