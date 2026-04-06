"""
Codeforces-inspired ranking system.

PRD §3.4.1 — Ranks based on Active Streak:
  Newbie → Pupil → Specialist → Expert →
  Candidate Master → Master → Grandmaster
"""

from __future__ import annotations

from enum import Enum


class Rank(str, Enum):
    NEWBIE = "newbie"
    PUPIL = "pupil"
    SPECIALIST = "specialist"
    EXPERT = "expert"
    CANDIDATE_MASTER = "candidate_master"
    MASTER = "master"
    GRANDMASTER = "grandmaster"

    @classmethod
    def from_streak(cls, streak_days: int) -> "Rank":
        if streak_days >= 365:
            return cls.GRANDMASTER
        if streak_days >= 180:
            return cls.MASTER
        if streak_days >= 90:
            return cls.CANDIDATE_MASTER
        if streak_days >= 30:
            return cls.EXPERT
        if streak_days >= 14:
            return cls.SPECIALIST
        if streak_days >= 7:
            return cls.PUPIL
        return cls.NEWBIE

    @property
    def aura_color(self) -> str:
        """Aura color unlocked at each rank (PRD §3.4.1)."""
        return {
            Rank.NEWBIE: "#B0BEC5",          # grey
            Rank.PUPIL: "#81C784",           # green
            Rank.SPECIALIST: "#64B5F6",      # blue
            Rank.EXPERT: "#BA68C8",          # purple
            Rank.CANDIDATE_MASTER: "#FFB74D", # orange
            Rank.MASTER: "#EF5350",          # red
            Rank.GRANDMASTER: "#FFD54F",     # gold
        }[self]
