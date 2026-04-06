"""
Logging-based notification service — development/testing implementation.

In production, replace with:
  - FirebaseNotificationService (FCM)
  - APNSNotificationService (Apple Push)
  - InAppNotificationService (DB + WebSocket/SSE)

Follows the same pattern as auth_domain's LogEventPublisher.
"""

from __future__ import annotations

import logging
import uuid
from typing import Optional

from character_domain.domain.interfaces.notification_service import (
    INotificationService,
    NotificationType,
)

logger = logging.getLogger("anubis.notifications")


class LogNotificationService(INotificationService):
    """
    Writes notifications to the application log.
    Swap for a real push service in production.
    """

    async def send(
        self,
        user_id: uuid.UUID,
        notification_type: NotificationType,
        title: str,
        body: str,
        data: dict | None = None,
    ) -> None:
        logger.info(
            "[NOTIFICATION] type=%s user=%s title='%s' body='%s' data=%s",
            notification_type.value,
            user_id,
            title,
            body,
            data or {},
        )

    async def send_batch(
        self,
        user_ids: list[uuid.UUID],
        notification_type: NotificationType,
        title: str,
        body: str,
        data: dict | None = None,
    ) -> None:
        for uid in user_ids:
            await self.send(uid, notification_type, title, body, data)
