"""Event publisher interface for domain event dispatch."""

from abc import ABC, abstractmethod

from auth_domain.domain.events import DomainEvent


class IEventPublisher(ABC):

    @abstractmethod
    async def publish(self, event: DomainEvent) -> None:
        ...

    async def publish_all(self, events: list[DomainEvent]) -> None:
        for event in events:
            await self.publish(event)
