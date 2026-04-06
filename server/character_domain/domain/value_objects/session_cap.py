"""
Dynamic session length cap — PRD §3.1.5a Cognitive Viability Ceiling.

The cap scales with the user's 14-day average to feel fair,
with 6 hours as the universal hard ceiling.

14-Day Average    Suggested Cap    Hard Ceiling
< 30 min          90 min           2 hrs
30–60 min         2 hrs            3 hrs
60–90 min         3 hrs            4 hrs
90–180 min        4 hrs            5 hrs
180+ min          5 hrs            6 hrs

Hard ceiling: 6 hours for ALL users, no exceptions.
"""

from __future__ import annotations

from dataclasses import dataclass

UNIVERSAL_HARD_CEILING_MINUTES = 360  # 6 hours


@dataclass(frozen=True)
class SessionCap:
    suggested_cap_minutes: int
    hard_ceiling_minutes: int

    @classmethod
    def from_average(cls, avg_daily_minutes: float) -> "SessionCap":
        if avg_daily_minutes < 30:
            return cls(suggested_cap_minutes=90, hard_ceiling_minutes=120)
        if avg_daily_minutes < 60:
            return cls(suggested_cap_minutes=120, hard_ceiling_minutes=180)
        if avg_daily_minutes < 90:
            return cls(suggested_cap_minutes=180, hard_ceiling_minutes=240)
        if avg_daily_minutes < 180:
            return cls(suggested_cap_minutes=240, hard_ceiling_minutes=300)
        return cls(suggested_cap_minutes=300, hard_ceiling_minutes=UNIVERSAL_HARD_CEILING_MINUTES)

    @property
    def can_auto_raise(self) -> bool:
        """
        PRD: if user consistently hits their cap for 7 consecutive days
        without missing, system can auto-raise it.
        """
        return True  # Flag — actual check is in the use case
