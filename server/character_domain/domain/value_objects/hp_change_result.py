"""
Result types for the Anubis domain service — immutable records
returned from HP mutation operations.

These value objects carry the full audit trail of every HP change
so that the presentation layer can surface rich feedback to the user.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional


class HPChangeReason(str, Enum):
    """Canonical reasons that Anubis can mutate HP."""
    # Recovery
    SESSION_COMPLETED = "session_completed"
    DAILY_GOAL_HIT = "daily_goal_hit"
    EXCEEDED_GOAL_25 = "exceeded_goal_25"
    EXCEEDED_GOAL_50 = "exceeded_goal_50"
    EXCEEDED_GOAL_100 = "exceeded_goal_100"
    STREAK_3_BONUS = "streak_3_bonus"
    STREAK_7_BONUS = "streak_7_bonus"
    BONUS_TASK = "bonus_task"
    REFLECTION_LOGGED = "reflection_logged"
    TREND_RECOVERY = "trend_recovery"
    PROSPECT_GAIN = "prospect_gain"
    PROSPECT_LOSS = "prospect_loss"
    REVIVAL = "revival"

    # Damage
    MISSED_DAILY_GOAL = "missed_daily_goal"
    GHOSTING = "ghosting"
    STUDIED_BELOW_50_PCT = "studied_below_50_pct"
    STUDIED_BELOW_25_PCT = "studied_below_25_pct"
    SKIPPED_SESSION = "skipped_session"
    PUSHED_TASK = "pushed_task"
    CONSECUTIVE_MISS = "consecutive_miss"
    DOWNWARD_TREND = "downward_trend"
    VITALITY_DECAY = "vitality_decay"

    # Overrides
    GHOSTING_OVERRIDE = "ghosting_override"
    PERMANENT_DEATH = "permanent_death"


class TrendStatus(str, Enum):
    """Consecutive-day below-average trend severity."""
    NONE = "none"
    WARNING = "warning"          # 4 days
    ESCALATED = "escalated"      # 5-6 days
    CRITICAL = "critical"        # 7+ days


class ConsistencyLevel(str, Enum):
    """Weekly consistency tiers — determines HP gain multiplier."""
    EXCEPTIONAL = "exceptional"  # 1.5x
    BASELINE = "baseline"        # 1.0x
    STRUGGLING = "struggling"    # 0.5x
    CRITICAL = "critical"        # 0.1x


class DeathCause(str, Enum):
    """How the character died."""
    GHOSTING_7_DAY = "ghosting_7_day"
    GHOSTING_PERMANENT = "ghosting_permanent"
    HP_DEPLETED = "hp_depleted"
    VITALITY_DECAY = "vitality_decay"


class ShieldSource(str, Enum):
    """How a life shield was earned."""
    STREAK_14_DAY = "streak_14_day"
    PREMIUM_PURCHASE = "premium_purchase"


# ── Result Data Classes ───────────────────────────────────────────────


@dataclass(frozen=True)
class HPChangeResult:
    """Returned by every Anubis HP mutation — the full audit record."""
    character_id: uuid.UUID
    old_hp: int
    new_hp: int
    delta: int
    reason: HPChangeReason
    description: str
    shield_used: bool = False
    triggered_death: bool = False
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True)
class GoalValidationResult:
    """Returned by Anubis.validate_goal()."""
    accepted: bool
    label: str
    hp_gain_multiplier: float
    message: str
    suggested_cap_minutes: int
    hard_ceiling_minutes: int


@dataclass(frozen=True)
class TrendEvaluationResult:
    """Returned by Anubis.evaluate_trend()."""
    status: TrendStatus
    consecutive_below_days: int
    hp_penalty: int
    message: str


@dataclass(frozen=True)
class WeeklyConsistencyResult:
    """Returned by Anubis.compute_weekly_consistency()."""
    level: ConsistencyLevel
    multiplier: float
    days_hit: int
    days_total: int
    message: str


@dataclass(frozen=True)
class GhostingPenaltyResult:
    """Returned by Anubis.apply_ghosting_penalty()."""
    character_id: uuid.UUID
    ghosting_days: int
    tier: str
    hp_before: int
    hp_after: int
    is_dead: bool
    is_permanently_dead: bool
    requires_feather: bool
    message: str
