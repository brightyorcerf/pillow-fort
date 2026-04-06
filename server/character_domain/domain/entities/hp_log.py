"""
HP Log entity — immutable audit record of every HP mutation.

Every time Anubis changes a character's HP, an HPLog is persisted.
This provides a complete, tamper-proof audit trail for:
  - Debugging inconsistencies
  - Generating eulogies & analytics
  - Displaying the HP timeline in the UI
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone

from character_domain.domain.value_objects.hp_change_result import HPChangeReason


@dataclass
class HPLog:
    """
    Append-only audit record.

    Invariants:
      - Once created, the record is never mutated
      - Every HP mutation by Anubis MUST produce one HPLog
    """

    id: uuid.UUID
    character_id: uuid.UUID
    old_hp: int
    new_hp: int
    delta: int
    reason: HPChangeReason
    description: str
    shield_used: bool = False
    triggered_death: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @classmethod
    def create(
        cls,
        character_id: uuid.UUID,
        old_hp: int,
        new_hp: int,
        reason: HPChangeReason,
        description: str,
        shield_used: bool = False,
        triggered_death: bool = False,
    ) -> HPLog:
        return cls(
            id=uuid.uuid4(),
            character_id=character_id,
            old_hp=old_hp,
            new_hp=new_hp,
            delta=new_hp - old_hp,
            reason=reason,
            description=description,
            shield_used=shield_used,
            triggered_death=triggered_death,
        )
