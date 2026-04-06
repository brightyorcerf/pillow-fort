"""
Password hasher interface (ISP — single responsibility).

The domain knows it needs hashing and verification, but not *how*.
Infrastructure chooses bcrypt / argon2id / etc.
"""

from abc import ABC, abstractmethod

from auth_domain.domain.value_objects.hashed_password import HashedPassword


class IPasswordHasher(ABC):

    @abstractmethod
    def hash(self, plain_password: str) -> HashedPassword:
        ...

    @abstractmethod
    def verify(self, plain_password: str, hashed: HashedPassword) -> bool:
        ...
