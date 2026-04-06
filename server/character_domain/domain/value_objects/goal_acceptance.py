"""
Goal acceptance and PVR (Personal Viable Range) results — PRD §3.1.5.

Goal vs. Average    Label         System Response
Above average       Stretch       Soft encouragement
At average          Baseline      Accepted silently
20–40% below avg    Slow Start    Accepted silently
40–60% below avg    Low Day       Accepted with gentle note
Below 60% of avg    Floor Breach  Warning + reduced HP gain
Below minimum       Invalid       Rejected
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class GoalAcceptanceLabel(str, Enum):
    STRETCH = "stretch"
    BASELINE = "baseline"
    SLOW_START = "slow_start"
    LOW_DAY = "low_day"
    FLOOR_BREACH = "floor_breach"
    INVALID = "invalid"


@dataclass(frozen=True)
class GoalAcceptanceResult:
    label: GoalAcceptanceLabel
    accepted: bool
    hp_gain_multiplier: float
    message: str

    @classmethod
    def evaluate(cls, goal_minutes: int, average_minutes: float, minimum_minutes: int) -> "GoalAcceptanceResult":
        if goal_minutes < minimum_minutes:
            return cls(
                label=GoalAcceptanceLabel.INVALID,
                accepted=False,
                hp_gain_multiplier=0.0,
                message=f"Too short to count. Minimum is {minimum_minutes} minutes.",
            )

        if average_minutes <= 0:
            # New user — no history, accept anything above minimum
            return cls(
                label=GoalAcceptanceLabel.BASELINE,
                accepted=True,
                hp_gain_multiplier=1.0,
                message="",
            )

        ratio = goal_minutes / average_minutes

        if ratio >= 1.0:
            return cls(
                label=GoalAcceptanceLabel.STRETCH,
                accepted=True,
                hp_gain_multiplier=1.0,
                message="Ambitious! Go for it.",
            )
        if ratio >= 0.8:
            return cls(
                label=GoalAcceptanceLabel.BASELINE,
                accepted=True,
                hp_gain_multiplier=1.0,
                message="",
            )
        if ratio >= 0.6:
            return cls(
                label=GoalAcceptanceLabel.SLOW_START,
                accepted=True,
                hp_gain_multiplier=1.0,
                message="",
            )
        if ratio >= 0.4:
            return cls(
                label=GoalAcceptanceLabel.LOW_DAY,
                accepted=True,
                hp_gain_multiplier=1.0,
                message="Taking it easy today? That's okay.",
            )
        # Below 40% of average
        return cls(
            label=GoalAcceptanceLabel.FLOOR_BREACH,
            accepted=True,
            hp_gain_multiplier=0.5,
            message="This goal is well below your usual. HP gain will be reduced.",
        )
