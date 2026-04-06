"""Token pair value object returned after successful authentication."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TokenPair:
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int = 900  # seconds (15 min default)
