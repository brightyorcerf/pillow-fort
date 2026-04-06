"""
Refresh token entity — tracks token lifecycle for secure rotation.

Implements the Token Rotation pattern: each refresh yields a new token
and invalidates the old one, limiting the window for stolen tokens.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone


class RefreshToken:

    def __init__(
        self,
        id: uuid.UUID,
        user_id: uuid.UUID,
        token_hash: str,
        device_fingerprint: str | None,
        ip_address: str | None,
        expires_at: datetime,
        is_revoked: bool = False,
        replaced_by: uuid.UUID | None = None,
        created_at: datetime | None = None,
    ):
        self._id = id
        self._user_id = user_id
        self._token_hash = token_hash
        self._device_fingerprint = device_fingerprint
        self._ip_address = ip_address
        self._expires_at = expires_at
        self._is_revoked = is_revoked
        self._replaced_by = replaced_by
        self._created_at = created_at or datetime.now(timezone.utc)

    # ── Factory ────────────────────────────────────────────────────────

    @classmethod
    def create(
        cls,
        user_id: uuid.UUID,
        token_hash: str,
        expires_at: datetime,
        device_fingerprint: str | None = None,
        ip_address: str | None = None,
    ) -> RefreshToken:
        return cls(
            id=uuid.uuid4(),
            user_id=user_id,
            token_hash=token_hash,
            device_fingerprint=device_fingerprint,
            ip_address=ip_address,
            expires_at=expires_at,
        )

    # ── Properties ─────────────────────────────────────────────────────

    @property
    def id(self) -> uuid.UUID:
        return self._id

    @property
    def user_id(self) -> uuid.UUID:
        return self._user_id

    @property
    def token_hash(self) -> str:
        return self._token_hash

    @property
    def device_fingerprint(self) -> str | None:
        return self._device_fingerprint

    @property
    def ip_address(self) -> str | None:
        return self._ip_address

    @property
    def expires_at(self) -> datetime:
        return self._expires_at

    @property
    def is_revoked(self) -> bool:
        return self._is_revoked

    @property
    def replaced_by(self) -> uuid.UUID | None:
        return self._replaced_by

    @property
    def created_at(self) -> datetime:
        return self._created_at

    # ── Domain behaviour ───────────────────────────────────────────────

    @property
    def is_expired(self) -> bool:
        return datetime.now(timezone.utc) >= self._expires_at

    @property
    def is_usable(self) -> bool:
        return not self._is_revoked and not self.is_expired

    def revoke(self, replaced_by: uuid.UUID | None = None) -> None:
        self._is_revoked = True
        self._replaced_by = replaced_by

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, RefreshToken):
            return NotImplemented
        return self._id == other._id

    def __hash__(self) -> int:
        return hash(self._id)
