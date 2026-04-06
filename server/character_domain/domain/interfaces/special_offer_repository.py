"""Repository interface for SpecialOffer."""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from typing import Optional

from character_domain.domain.entities.special_offer import SpecialOffer


class ISpecialOfferRepository(ABC):

    @abstractmethod
    async def save(self, offer: SpecialOffer) -> None: ...

    @abstractmethod
    async def update(self, offer: SpecialOffer) -> None: ...

    @abstractmethod
    async def find_by_id(self, offer_id: uuid.UUID) -> Optional[SpecialOffer]: ...

    @abstractmethod
    async def find_all_active(self) -> list[SpecialOffer]: ...

    @abstractmethod
    async def find_available_for_level(self, player_level: int) -> list[SpecialOffer]: ...
