"""
Character health states derived from HP ranges.

PRD §3.1.2 — States:
  100–67 HP  →  Healthy   (no warnings)
  66–34  HP  →  Damaged   (visible warning nudge)
  33     HP  →  Critical  (one miss away from death)
  0      HP  →  Dead      (game over, streak reset)
"""

from enum import Enum


class HealthState(str, Enum):
    HEALTHY = "healthy"
    DAMAGED = "damaged"
    CRITICAL = "critical"
    DEAD = "dead"

    @classmethod
    def from_hp(cls, hp: int) -> "HealthState":
        if hp <= 0:
            return cls.DEAD
        if hp <= 33:
            return cls.CRITICAL
        if hp <= 66:
            return cls.DAMAGED
        return cls.HEALTHY
