"""
Subject types and minimum goal thresholds — PRD §3.1.4.

Subject Type      Minimum Valid Goal
Study session     25 minutes (1 Pomodoro)
Reading           15 minutes
Practice/revision 20 minutes
"""

from __future__ import annotations

from enum import Enum


class SubjectType(str, Enum):
    STUDY_SESSION = "study_session"
    READING = "reading"
    PRACTICE_REVISION = "practice_revision"

    @property
    def minimum_goal_minutes(self) -> int:
        return {
            SubjectType.STUDY_SESSION: 25,
            SubjectType.READING: 15,
            SubjectType.PRACTICE_REVISION: 20,
        }[self]
