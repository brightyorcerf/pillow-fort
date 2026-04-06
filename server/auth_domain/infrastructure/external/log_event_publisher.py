"""
Simple logging-based event publisher.

In production, swap for a message broker (RabbitMQ, Kafka, Redis Streams)
implementation — the interface keeps everything decoupled.
"""

from __future__ import annotations

import logging

from auth_domain.domain.events import DomainEvent
from auth_domain.domain.interfaces.event_publisher import IEventPublisher

logger = logging.getLogger("auth_domain.events")


class LogEventPublisher(IEventPublisher):

    async def publish(self, event: DomainEvent) -> None:
        logger.info(
            "Domain event: %s | %s",
            type(event).__name__,
            vars(event),
        )
