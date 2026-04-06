"""
Argon2id password hasher — OWASP-recommended algorithm.

Argon2id is the current industry standard (winner of the Password Hashing
Competition), resistant to both GPU and side-channel attacks.

Implements IPasswordHasher (DIP).
"""

from __future__ import annotations

import argon2

from auth_domain.domain.interfaces.password_hasher import IPasswordHasher
from auth_domain.domain.value_objects.hashed_password import HashedPassword


class Argon2PasswordHasher(IPasswordHasher):
    """
    Parameters follow OWASP 2024 recommendations:
      - time_cost=3 (iterations)
      - memory_cost=65536 (64 MiB)
      - parallelism=4
    """

    def __init__(
        self,
        time_cost: int = 3,
        memory_cost: int = 65536,
        parallelism: int = 4,
    ) -> None:
        self._hasher = argon2.PasswordHasher(
            time_cost=time_cost,
            memory_cost=memory_cost,
            parallelism=parallelism,
            hash_len=32,
            salt_len=16,
            type=argon2.Type.ID,  # argon2id
        )

    def hash(self, plain_password: str) -> HashedPassword:
        hashed = self._hasher.hash(plain_password)
        return HashedPassword(hashed)

    def verify(self, plain_password: str, hashed: HashedPassword) -> bool:
        try:
            return self._hasher.verify(hashed.value, plain_password)
        except argon2.exceptions.VerifyMismatchError:
            return False
        except argon2.exceptions.InvalidHashError:
            return False
