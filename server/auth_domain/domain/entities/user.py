"""
User aggregate root entity.

Follows the Entity pattern — identity-based equality, encapsulated state
mutation through domain methods, and invariant enforcement at the boundary.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from auth_domain.domain.value_objects import Email, HashedPassword, OAuthProvider
from auth_domain.domain.events import DomainEvent, UserRegistered, EmailVerified, PasswordChanged
from auth_domain.domain.exceptions import (
    AccountLockedException,
    EmailAlreadyVerifiedException,
    InvalidCredentialsException,
)


class User:
    """Aggregate root for the authentication bounded context."""

    MAX_FAILED_ATTEMPTS = 5

    def __init__(
        self,
        id: uuid.UUID,
        email: Email,
        hashed_password: Optional[HashedPassword],
        username: str,
        roles: list[str],
        is_email_verified: bool = False,
        is_active: bool = True,
        failed_login_attempts: int = 0,
        locked_until: Optional[datetime] = None,
        oauth_provider: Optional[OAuthProvider] = None,
        oauth_provider_id: Optional[str] = None,
        email_verification_token: Optional[str] = None,
        password_reset_token: Optional[str] = None,
        password_reset_expires: Optional[datetime] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self._id = id
        self._email = email
        self._hashed_password = hashed_password
        self._username = username
        self._roles = list(roles)
        self._is_email_verified = is_email_verified
        self._is_active = is_active
        self._failed_login_attempts = failed_login_attempts
        self._locked_until = locked_until
        self._oauth_provider = oauth_provider
        self._oauth_provider_id = oauth_provider_id
        self._email_verification_token = email_verification_token
        self._password_reset_token = password_reset_token
        self._password_reset_expires = password_reset_expires
        self._created_at = created_at or datetime.now(timezone.utc)
        self._updated_at = updated_at or datetime.now(timezone.utc)
        self._domain_events: list[DomainEvent] = []

    # ── Factory Methods (creational patterns) ──────────────────────────

    @classmethod
    def register(
        cls,
        email: Email,
        hashed_password: HashedPassword,
        username: str,
        verification_token: str,
    ) -> User:
        """Factory for local registration. Enforces creation invariants."""
        user = cls(
            id=uuid.uuid4(),
            email=email,
            hashed_password=hashed_password,
            username=username,
            roles=["player"],
            email_verification_token=verification_token,
        )
        user._record_event(UserRegistered(user_id=user.id, email=str(email)))
        return user

    @classmethod
    def from_oauth(
        cls,
        email: Email,
        username: str,
        provider: OAuthProvider,
        provider_id: str,
    ) -> User:
        """Factory for OAuth-based registration — no password needed."""
        return cls(
            id=uuid.uuid4(),
            email=email,
            hashed_password=None,
            username=username,
            roles=["player"],
            is_email_verified=True,  # OAuth providers verify email
            oauth_provider=provider,
            oauth_provider_id=provider_id,
        )

    # ── Properties (read-only access) ──────────────────────────────────

    @property
    def id(self) -> uuid.UUID:
        return self._id

    @property
    def email(self) -> Email:
        return self._email

    @property
    def hashed_password(self) -> Optional[HashedPassword]:
        return self._hashed_password

    @property
    def username(self) -> str:
        return self._username

    @property
    def roles(self) -> list[str]:
        return list(self._roles)

    @property
    def is_email_verified(self) -> bool:
        return self._is_email_verified

    @property
    def is_active(self) -> bool:
        return self._is_active

    @property
    def failed_login_attempts(self) -> int:
        return self._failed_login_attempts

    @property
    def locked_until(self) -> Optional[datetime]:
        return self._locked_until

    @property
    def oauth_provider(self) -> Optional[OAuthProvider]:
        return self._oauth_provider

    @property
    def oauth_provider_id(self) -> Optional[str]:
        return self._oauth_provider_id

    @property
    def email_verification_token(self) -> Optional[str]:
        return self._email_verification_token

    @property
    def password_reset_token(self) -> Optional[str]:
        return self._password_reset_token

    @property
    def password_reset_expires(self) -> Optional[datetime]:
        return self._password_reset_expires

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        return self._updated_at

    @property
    def domain_events(self) -> list[DomainEvent]:
        return list(self._domain_events)

    # ── Domain Behaviour ───────────────────────────────────────────────

    @property
    def is_locked(self) -> bool:
        if self._locked_until is None:
            return False
        return datetime.now(timezone.utc) < self._locked_until

    def verify_email(self, token: str) -> None:
        if self._is_email_verified:
            raise EmailAlreadyVerifiedException()
        if self._email_verification_token != token:
            raise InvalidCredentialsException("Invalid verification token.")
        self._is_email_verified = True
        self._email_verification_token = None
        self._touch()
        self._record_event(EmailVerified(user_id=self.id))

    def record_failed_login(self, lock_duration_minutes: int = 15) -> None:
        self._failed_login_attempts += 1
        if self._failed_login_attempts >= self.MAX_FAILED_ATTEMPTS:
            from datetime import timedelta
            self._locked_until = datetime.now(timezone.utc) + timedelta(
                minutes=lock_duration_minutes
            )
        self._touch()

    def record_successful_login(self) -> None:
        self._failed_login_attempts = 0
        self._locked_until = None
        self._touch()

    def check_account_access(self) -> None:
        """Guard — raises if the account cannot be used right now."""
        if not self._is_active:
            raise AccountLockedException("Account has been deactivated.")
        if self.is_locked:
            raise AccountLockedException(
                f"Account locked until {self._locked_until.isoformat()}."
            )

    def change_password(self, new_hashed_password: HashedPassword) -> None:
        self._hashed_password = new_hashed_password
        self._password_reset_token = None
        self._password_reset_expires = None
        self._touch()
        self._record_event(PasswordChanged(user_id=self.id))

    def initiate_password_reset(self, token: str, expires: datetime) -> None:
        self._password_reset_token = token
        self._password_reset_expires = expires
        self._touch()

    def validate_password_reset_token(self, token: str) -> bool:
        if self._password_reset_token is None or self._password_reset_expires is None:
            return False
        if self._password_reset_token != token:
            return False
        return datetime.now(timezone.utc) < self._password_reset_expires

    def assign_role(self, role: str) -> None:
        if role not in self._roles:
            self._roles.append(role)
            self._touch()

    def revoke_role(self, role: str) -> None:
        if role in self._roles:
            self._roles.remove(role)
            self._touch()

    def deactivate(self) -> None:
        self._is_active = False
        self._touch()

    # ── Internal helpers ───────────────────────────────────────────────

    def _touch(self) -> None:
        self._updated_at = datetime.now(timezone.utc)

    def _record_event(self, event: DomainEvent) -> None:
        self._domain_events.append(event)

    def clear_events(self) -> None:
        self._domain_events.clear()

    # ── Identity-based equality ────────────────────────────────────────

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, User):
            return NotImplemented
        return self._id == other._id

    def __hash__(self) -> int:
        return hash(self._id)
