"""
Ghosting penalty escalation tiers — PRD §3.1.3 Ghosting table.

1 day       → −66 HP (standard double penalty)
2 days      → −66 HP/day + −10 HP extra
3–4 days    → −66 HP/day + −15 HP extra
5–6 days    → Instant drop to 1 HP
7 days      → Instant drop to 0 HP (dead state)
7–29 days   → HP locked at 0, re-engagement ritual required
30 days     → Account permanently killed
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class GhostingTier(str, Enum):
    NONE = "none"
    STANDARD = "standard"              # 1 day
    ESCALATING = "escalating"          # 2 days
    SEVERE = "severe"                  # 3-4 days
    CRITICAL_SURVIVAL = "critical_survival"  # 5-6 days
    DEAD = "dead"                      # 7 days
    LOCKED = "locked"                  # 7-29 days
    PERMANENT_DEATH = "permanent_death"  # 30+ days


@dataclass(frozen=True)
class GhostingLevel:
    consecutive_days: int

    @property
    def tier(self) -> GhostingTier:
        if self.consecutive_days <= 0:
            return GhostingTier.NONE
        if self.consecutive_days == 1:
            return GhostingTier.STANDARD
        if self.consecutive_days == 2:
            return GhostingTier.ESCALATING
        if self.consecutive_days <= 4:
            return GhostingTier.SEVERE
        if self.consecutive_days <= 6:
            return GhostingTier.CRITICAL_SURVIVAL
        if self.consecutive_days == 7:
            return GhostingTier.DEAD
        if self.consecutive_days <= 29:
            return GhostingTier.LOCKED
        return GhostingTier.PERMANENT_DEATH

    def compute_hp_override(self) -> int | None:
        """
        Returns a forced HP value for tiers that bypass normal damage.
        None means use standard damage calculation.
        """
        tier = self.tier
        if tier == GhostingTier.CRITICAL_SURVIVAL:
            return 1
        if tier in (GhostingTier.DEAD, GhostingTier.LOCKED, GhostingTier.PERMANENT_DEATH):
            return 0
        return None

    def compute_extra_damage(self) -> int:
        """Additional damage on top of the base −66 ghosting penalty."""
        tier = self.tier
        if tier == GhostingTier.ESCALATING:
            return 10
        if tier == GhostingTier.SEVERE:
            return 15
        return 0

    @property
    def requires_feather(self) -> bool:
        """Ghosting 7-29 days: HP locked at 0, requires Phoenix Feather."""
        return self.tier == GhostingTier.LOCKED

    @property
    def is_permanently_dead(self) -> bool:
        return self.tier == GhostingTier.PERMANENT_DEATH
