"""
Reaper domain enums — death causes, revival methods, penance/ritual statuses.

The Reaper is the single authority over death and all revival paths.
These enums define the vocabulary for death records, revival attempts,
penance streaks, and phoenix feather lifecycle.

PRD §3.2, §3.1.3 Ritual Progression, Sequence Diagrams §6.
"""

from __future__ import annotations

from enum import Enum


class DeathCause(str, Enum):
    """How a character died — recorded on every DeathRecord."""
    MISSED_GOAL = "missed_goal"
    GHOSTING_7_DAYS = "ghosting_7_days"
    GHOSTING_30_DAYS = "ghosting_30_days"           # Permanent
    PENANCE_FAILURE = "penance_failure"
    RITUAL_EXHAUSTED = "ritual_exhausted"            # All 3 rituals used + ghosted again
    TREND_DEATH = "trend_death"                      # HP depleted via downward trend
    HP_DEPLETED = "hp_depleted"                      # Generic HP hit zero


class RevivalMethod(str, Enum):
    """How the character was brought back."""
    PHOENIX_FEATHER = "phoenix_feather"              # Instant premium revival
    PENANCE_STREAK = "penance_streak"                # 7-day 100% goal streak while ghost
    RE_ENGAGEMENT_RITUAL = "re_engagement_ritual"    # 3-tier ritual system
    FREE_FIRST = "free_first"                        # First death is free (PRD mercy rule)
    UNFAIR_DEATH = "unfair_death"                    # Server error / crash compensation


class PenanceStatus(str, Enum):
    """Status of a penance streak attempt."""
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"


class RitualStatus(str, Enum):
    """Status of a re-engagement ritual."""
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    ABANDONED = "abandoned"


class FeatherStatus(str, Enum):
    """Lifecycle status of a Phoenix Feather."""
    AVAILABLE = "available"
    USED = "used"
    EXPIRED = "expired"
