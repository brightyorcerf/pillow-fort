"""
Shared database and container dependencies for FastAPI.

Provides a request-scoped DB session via ``yield`` and accessors
for the DI containers stored on ``app.state``.  Every use case
that needs a session should depend on ``get_db_session`` — the
session (and its transaction) are created lazily, only when a
route that actually requires database access is matched.
"""

from __future__ import annotations

from typing import AsyncGenerator

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession


async def get_db_session(request: Request) -> AsyncGenerator[AsyncSession, None]:
    """Yield a request-scoped DB session inside a transaction."""
    factory = request.app.state.session_factory
    async with factory() as session:
        async with session.begin():
            yield session


def get_auth_container(request: Request):
    """Resolve the auth DI container from app state."""
    return request.app.state.auth_container


def get_char_container(request: Request):
    """Resolve the character DI container from app state."""
    return request.app.state.char_container
