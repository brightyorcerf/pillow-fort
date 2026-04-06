"""
Domain events — used for cross-boundary communication without coupling.

Follows the Observer / Event-Driven pattern. Events are raised by aggregates
and dispatched by the application layer after persistence succeeds.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass(frozen=True)
class DomainEvent:
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True)
class UserRegistered(DomainEvent):
    user_id: uuid.UUID = field(default_factory=uuid.uuid4)
    email: str = ""


@dataclass(frozen=True)
class EmailVerified(DomainEvent):
    user_id: uuid.UUID = field(default_factory=uuid.uuid4)


@dataclass(frozen=True)
class PasswordChanged(DomainEvent):
    user_id: uuid.UUID = field(default_factory=uuid.uuid4)


@dataclass(frozen=True)
class UserLoggedIn(DomainEvent):
    user_id: uuid.UUID = field(default_factory=uuid.uuid4)
    ip_address: str = ""


@dataclass(frozen=True)
class SuspiciousLoginDetected(DomainEvent):
    user_id: uuid.UUID = field(default_factory=uuid.uuid4)
    ip_address: str = ""
    reason: str = ""
