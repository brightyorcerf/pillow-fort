"""
Repository interface for User aggregate (DIP — depend on abstraction).

Follows the Repository pattern — the domain defines what persistence
operations it needs; infrastructure provides the implementation.
"""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from typing import Optional

from auth_domain.domain.entities.user import User
from auth_domain.domain.value_objects.email import Email


class IUserRepository(ABC):

    @abstractmethod
    async def find_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        ...

    @abstractmethod
    async def find_by_email(self, email: Email) -> Optional[User]:
        ...

    @abstractmethod
    async def find_by_oauth(
        self, provider: str, provider_id: str
    ) -> Optional[User]:
        ...

    @abstractmethod
    async def save(self, user: User) -> None:
        ...

    @abstractmethod
    async def update(self, user: User) -> None:
        ...

    @abstractmethod
    async def exists_by_email(self, email: Email) -> bool:
        ...
