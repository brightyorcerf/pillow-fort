"""
JWT token service — RS256 asymmetric signing.

Security choices:
  - RS256 (RSA + SHA-256) — public key can be shared for verification
    without exposing the signing key (critical for microservices).
  - Short-lived access tokens (15 min default).
  - Refresh tokens are opaque random bytes, SHA-256 hashed before storage
    so a database leak does not compromise active sessions.
  - jti (JWT ID) claim for token revocation support.

Implements ITokenService (DIP).
"""

from __future__ import annotations

import hashlib
import secrets
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt

from auth_domain.domain.exceptions import InvalidCredentialsException, TokenExpiredException
from auth_domain.domain.interfaces.token_service import ITokenService


class JWTTokenService(ITokenService):

    def __init__(
        self,
        private_key: str,
        public_key: str,
        algorithm: str = "RS256",
        access_token_ttl_minutes: int = 15,
        refresh_token_bytes: int = 32,
        issuer: str = "auth-domain",
    ) -> None:
        self._private_key = private_key
        self._public_key = public_key
        self._algorithm = algorithm
        self._access_ttl = timedelta(minutes=access_token_ttl_minutes)
        self._refresh_bytes = refresh_token_bytes
        self._issuer = issuer

    def create_access_token(
        self,
        user_id: uuid.UUID,
        roles: list[str],
        extra_claims: dict[str, Any] | None = None,
    ) -> str:
        now = datetime.now(timezone.utc)
        payload: dict[str, Any] = {
            "sub": str(user_id),
            "roles": roles,
            "iat": now,
            "exp": now + self._access_ttl,
            "iss": self._issuer,
            "jti": str(uuid.uuid4()),
        }
        if extra_claims:
            payload.update(extra_claims)
        return jwt.encode(payload, self._private_key, algorithm=self._algorithm)

    def create_refresh_token(self) -> str:
        return secrets.token_urlsafe(self._refresh_bytes)

    def decode_access_token(self, token: str) -> dict[str, Any]:
        try:
            return jwt.decode(
                token,
                self._public_key,
                algorithms=[self._algorithm],
                issuer=self._issuer,
                options={"require": ["sub", "exp", "iat", "iss", "jti"]},
            )
        except jwt.ExpiredSignatureError:
            raise TokenExpiredException("Access token has expired.")
        except jwt.InvalidTokenError as e:
            raise InvalidCredentialsException(f"Invalid token: {e}")

    def hash_refresh_token(self, raw_token: str) -> str:
        return hashlib.sha256(raw_token.encode()).hexdigest()
