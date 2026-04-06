"""
HP event types and their values — directly from PRD §3.1.3.

Damage events (unproductive behaviour) and Recovery events (productive behaviour)
are modelled as value objects so the rules live in the domain, not in config.
"""

from __future__ import annotations

from enum import Enum
from dataclasses import dataclass


# ── Damage Events ──────────────────────────────────────────────────────

class HpEventType(str, Enum):
    # Damage
    MISSED_DAILY_GOAL = "missed_daily_goal"
    GHOSTING = "ghosting"
    STUDIED_LESS_THAN_50_PCT = "studied_less_than_50_pct"
    STUDIED_LESS_THAN_25_PCT = "studied_less_than_25_pct"
    SKIPPED_SCHEDULED_SESSION = "skipped_scheduled_session"
    PUSHED_TASK = "pushed_task"
    CONSECUTIVE_MISS_2_DAYS = "consecutive_miss_2_days"
    CONSECUTIVE_MISS_3_PLUS_DAYS = "consecutive_miss_3_plus_days"
    DOWNWARD_TREND_4_DAYS = "downward_trend_4_days"
    DOWNWARD_TREND_5_PLUS_DAYS = "downward_trend_5_plus_days"
    DOWNWARD_TREND_7_DAYS = "downward_trend_7_days"

    # Recovery
    HIT_DAILY_GOAL = "hit_daily_goal"
    EXCEEDED_GOAL_25 = "exceeded_goal_25"
    EXCEEDED_GOAL_50 = "exceeded_goal_50"
    EXCEEDED_GOAL_100 = "exceeded_goal_100"
    STREAK_3_DAY = "streak_3_day"
    STREAK_7_DAY = "streak_7_day"
    BONUS_TASK_COMPLETED = "bonus_task_completed"
    REFLECTION_LOGGED = "reflection_logged"
    TREND_RECOVERY_BONUS = "trend_recovery_bonus"


# PRD §3.1.3 damage table
_DAMAGE_VALUES: dict[HpEventType, int] = {
    HpEventType.MISSED_DAILY_GOAL: -33,
    HpEventType.GHOSTING: -66,
    HpEventType.STUDIED_LESS_THAN_50_PCT: -20,
    HpEventType.STUDIED_LESS_THAN_25_PCT: -28,
    HpEventType.SKIPPED_SCHEDULED_SESSION: -15,
    HpEventType.PUSHED_TASK: -10,
    HpEventType.CONSECUTIVE_MISS_2_DAYS: -10,
    HpEventType.CONSECUTIVE_MISS_3_PLUS_DAYS: -15,
    HpEventType.DOWNWARD_TREND_4_DAYS: -5,
    HpEventType.DOWNWARD_TREND_5_PLUS_DAYS: -10,
    HpEventType.DOWNWARD_TREND_7_DAYS: -15,
}

# PRD §3.1.3 recovery table
_RECOVERY_VALUES: dict[HpEventType, int] = {
    HpEventType.HIT_DAILY_GOAL: 10,
    HpEventType.EXCEEDED_GOAL_25: 15,
    HpEventType.EXCEEDED_GOAL_50: 20,
    HpEventType.EXCEEDED_GOAL_100: 25,
    HpEventType.STREAK_3_DAY: 10,
    HpEventType.STREAK_7_DAY: 20,
    HpEventType.BONUS_TASK_COMPLETED: 5,
    HpEventType.REFLECTION_LOGGED: 3,
    HpEventType.TREND_RECOVERY_BONUS: 5,
}


@dataclass(frozen=True)
class HpDamageEvent:
    event_type: HpEventType
    reason: str

    @property
    def hp_change(self) -> int:
        return _DAMAGE_VALUES.get(self.event_type, 0)


@dataclass(frozen=True)
class HpRecoveryEvent:
    event_type: HpEventType
    reason: str

    @property
    def hp_change(self) -> int:
        return _RECOVERY_VALUES.get(self.event_type, 0)
