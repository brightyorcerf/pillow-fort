"""
JWT token service interface.

Abstracts token creation and validation so the application layer
doesn't depend on any specific JWT library.
"""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from typing import Any


class ITokenService(ABC):

    @abstractmethod
    def create_access_token(
        self, user_id: uuid.UUID, roles: list[str], extra_claims: dict[str, Any] | None = None
    ) -> str:
        ...

    @abstractmethod
    def create_refresh_token(self) -> str:
        """Generate a cryptographically random opaque refresh token."""
        ...

    @abstractmethod
    def decode_access_token(self, token: str) -> dict[str, Any]:
        """Validate and decode an access token. Raises on invalid/expired."""
        ...

    @abstractmethod
    def hash_refresh_token(self, raw_token: str) -> str:
        """SHA-256 hash for storage — refresh tokens are never stored in plain text."""
        ...
