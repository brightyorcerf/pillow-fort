"""
Notification service interface for the Anubis domain service.

Anubis triggers notifications when HP thresholds are crossed,
death occurs, or important milestones are reached. The concrete
implementation (push notification, email, in-app) lives in
the infrastructure layer.
"""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from enum import Enum


class NotificationType(str, Enum):
    HP_LOW_WARNING = "hp_low_warning"           # HP dropped below 33
    HP_CRITICAL = "hp_critical"                 # HP at or below 10
    DEATH = "death"                             # Character died
    PERMANENT_DEATH = "permanent_death"         # 30-day ghost → permanent
    GHOSTING_ESCALATION = "ghosting_escalation" # Ghosting tier increased
    STREAK_MILESTONE = "streak_milestone"       # 3, 7, 14, 30, 90, etc.
    RANK_UP = "rank_up"                         # Rank promotion
    LIFE_SHIELD_EARNED = "life_shield_earned"   # 14-day streak shield
    LIFE_SHIELD_USED = "life_shield_used"       # Auto-saved from death
    TREND_WARNING = "trend_warning"             # Downward trend detected
    WEEKLY_REPORT = "weekly_report"             # Weekly consistency summary
    RITUAL_AVAILABLE = "ritual_available"       # Can start a ritual
    FLOW_STATE_ACHIEVED = "flow_state_achieved" # 90+ min session


class INotificationService(ABC):
    """
    Port for push / in-app notifications.

    Concrete implementations may use:
      - Firebase Cloud Messaging
      - Apple Push Notification Service
      - In-app notification table + SSE/WebSocket
    """

    @abstractmethod
    async def send(
        self,
        user_id: uuid.UUID,
        notification_type: NotificationType,
        title: str,
        body: str,
        data: dict | None = None,
    ) -> None:
        """Send a single notification."""
        ...

    @abstractmethod
    async def send_batch(
        self,
        user_ids: list[uuid.UUID],
        notification_type: NotificationType,
        title: str,
        body: str,
        data: dict | None = None,
    ) -> None:
        """Send the same notification to multiple users."""
        ...
