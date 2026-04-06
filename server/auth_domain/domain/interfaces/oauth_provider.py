"""
OAuth provider interface (Strategy pattern).

Each social login provider (Google, Apple) implements this interface.
The application layer selects the right strategy at runtime.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class OAuthUserInfo:
    """Normalised user profile returned by any OAuth provider."""

    provider_id: str
    email: str
    name: str
    picture_url: str | None = None
    email_verified: bool = True


class IOAuthProvider(ABC):

    @property
    @abstractmethod
    def provider_name(self) -> str:
        ...

    @abstractmethod
    async def get_authorization_url(self, state: str, redirect_uri: str) -> str:
        ...

    @abstractmethod
    async def exchange_code(self, code: str, redirect_uri: str) -> OAuthUserInfo:
        """Exchange authorisation code for user info."""
        ...
