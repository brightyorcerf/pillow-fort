"""Event publisher interface (reused pattern from auth domain)."""

from abc import ABC, abstractmethod

from character_domain.domain.events import DomainEvent


class IEventPublisher(ABC):

    @abstractmethod
    async def publish(self, event: DomainEvent) -> None:
        ...

    async def publish_all(self, events: list[DomainEvent]) -> None:
        for event in events:
            await self.publish(event)
