"""
RevivalAttempt entity — tracks each attempt to revive a dead character.

Records the method used, HP restored, success/failure status,
and links back to the death record that triggered it.

PRD §3.1.3 — Revival Paths.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from character_domain.domain.value_objects.reaper_enums import RevivalMethod


@dataclass
class RevivalAttempt:
    id: uuid.UUID
    character_id: uuid.UUID
    death_record_id: uuid.UUID
    method: RevivalMethod
    hp_restored_to: int
    success: bool
    fail_reason: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @classmethod
    def create_success(
        cls,
        character_id: uuid.UUID,
        death_record_id: uuid.UUID,
        method: RevivalMethod,
        hp_restored_to: int,
    ) -> RevivalAttempt:
        return cls(
            id=uuid.uuid4(),
            character_id=character_id,
            death_record_id=death_record_id,
            method=method,
            hp_restored_to=hp_restored_to,
            success=True,
        )

    @classmethod
    def create_failure(
        cls,
        character_id: uuid.UUID,
        death_record_id: uuid.UUID,
        method: RevivalMethod,
        reason: str,
    ) -> RevivalAttempt:
        return cls(
            id=uuid.uuid4(),
            character_id=character_id,
            death_record_id=death_record_id,
            method=method,
            hp_restored_to=0,
            success=False,
            fail_reason=reason,
        )
