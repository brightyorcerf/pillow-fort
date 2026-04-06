"""
Role and Permission entities for RBAC (Role-Based Access Control).

Follows the Composite pattern for permission aggregation.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Permission:
    """Immutable value-like entity representing a single permission."""

    id: uuid.UUID
    name: str          # e.g. "store:purchase", "admin:ban_player"
    description: str

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Permission):
            return NotImplemented
        return self.name == other.name

    def __hash__(self) -> int:
        return hash(self.name)


@dataclass
class Role:
    """
    Named collection of permissions.

    Standard roles for the game:
      - player:  basic gameplay + store access
      - moderator: player + moderation actions
      - admin:  full access
    """

    id: uuid.UUID
    name: str
    description: str
    permissions: list[Permission] = field(default_factory=list)

    def has_permission(self, permission_name: str) -> bool:
        return any(p.name == permission_name for p in self.permissions)

    def grant(self, permission: Permission) -> None:
        if permission not in self.permissions:
            self.permissions.append(permission)

    def revoke(self, permission_name: str) -> None:
        self.permissions = [
            p for p in self.permissions if p.name != permission_name
        ]
