"""Domain events for the character bounded context."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass(frozen=True)
class DomainEvent:
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True)
class CharacterCreated(DomainEvent):
    character_id: uuid.UUID = field(default_factory=uuid.uuid4)
    user_id: uuid.UUID = field(default_factory=uuid.uuid4)


@dataclass(frozen=True)
class HpChanged(DomainEvent):
    character_id: uuid.UUID = field(default_factory=uuid.uuid4)
    old_hp: int = 0
    new_hp: int = 0
    event_type: str = ""
    reason: str = ""


@dataclass(frozen=True)
class CharacterDied(DomainEvent):
    character_id: uuid.UUID = field(default_factory=uuid.uuid4)
    total_study_minutes: int = 0
    is_permanent: bool = False


@dataclass(frozen=True)
class CharacterRevived(DomainEvent):
    character_id: uuid.UUID = field(default_factory=uuid.uuid4)
    method: str = ""         # "ritual" | "phoenix_feather" | "penance_streak"
    revived_hp: int = 50


@dataclass(frozen=True)
class RankChanged(DomainEvent):
    character_id: uuid.UUID = field(default_factory=uuid.uuid4)
    old_rank: str = ""
    new_rank: str = ""


@dataclass(frozen=True)
class StreakMilestone(DomainEvent):
    character_id: uuid.UUID = field(default_factory=uuid.uuid4)
    streak_days: int = 0


@dataclass(frozen=True)
class CovenantSigned(DomainEvent):
    character_id: uuid.UUID = field(default_factory=uuid.uuid4)
    covenant_id: uuid.UUID = field(default_factory=uuid.uuid4)
    goal_minutes: int = 0


@dataclass(frozen=True)
class StudySessionCompleted(DomainEvent):
    character_id: uuid.UUID = field(default_factory=uuid.uuid4)
    session_id: uuid.UUID = field(default_factory=uuid.uuid4)
    duration_minutes: int = 0
    hp_earned: int = 0


@dataclass(frozen=True)
class RitualStepCompleted(DomainEvent):
    character_id: uuid.UUID = field(default_factory=uuid.uuid4)
    ritual_type: str = ""
    step_number: int = 0
    hp_restored: int = 0
