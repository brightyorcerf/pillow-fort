"""
Email value object — immutable, self-validating.

Value objects are compared by their content, not identity.
"""

from __future__ import annotations

import re


class Email:
    """Validated, normalised email address."""

    _EMAIL_REGEX = re.compile(
        r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    )

    __slots__ = ("_value",)

    def __init__(self, value: str) -> None:
        normalised = value.strip().lower()
        if not self._EMAIL_REGEX.match(normalised):
            raise ValueError(f"Invalid email address: {value}")
        self._value = normalised

    @property
    def value(self) -> str:
        return self._value

    def __str__(self) -> str:
        return self._value

    def __repr__(self) -> str:
        return f"Email({self._value!r})"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Email):
            return self._value == other._value
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self._value)
