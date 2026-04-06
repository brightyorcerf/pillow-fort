"""
HashedPassword value object.

Wraps the already-hashed string so the domain layer never touches raw
passwords. Hashing strategy is injected via the PasswordHasher interface
(ISP / DIP compliance).
"""

from __future__ import annotations


class HashedPassword:

    __slots__ = ("_hash",)

    def __init__(self, hash_value: str) -> None:
        if not hash_value:
            raise ValueError("Password hash cannot be empty.")
        self._hash = hash_value

    @property
    def value(self) -> str:
        return self._hash

    def __eq__(self, other: object) -> bool:
        if isinstance(other, HashedPassword):
            return self._hash == other._hash
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self._hash)

    def __repr__(self) -> str:
        return "HashedPassword(***)"
