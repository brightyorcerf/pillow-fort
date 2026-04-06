"""
Character-domain FastAPI dependencies.

Resolves the *character_id* from the authenticated user's JWT.
Re-uses the auth domain's ``get_current_user`` dependency so we
never duplicate token-parsing logic (DRY / Single Responsibility).
"""

from __future__ import annotations

import uuid

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from auth_domain.presentation.dependencies import get_current_user
from auth_domain.presentation.dependencies.db_dependencies import (
    get_char_container,
    get_db_session,
)
from character_domain.domain.exceptions import CharacterNotFoundException


async def get_current_character_id(
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
    char_container=Depends(get_char_container),
) -> uuid.UUID:
    """
    Resolve the character that belongs to the authenticated user.

    The character_id is looked up via the user_id embedded in the JWT.
    This keeps every character route implicitly authenticated.
    """
    user_id = uuid.UUID(current_user["sub"])
    char_repo = char_container.character_repo(session)
    character = await char_repo.find_by_user_id(user_id)

    if character is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No character found. Complete onboarding first.",
        )
    return character.id


async def get_current_user_id(
    current_user: dict = Depends(get_current_user),
) -> uuid.UUID:
    """Extract user_id from JWT — used by create-character (no character yet)."""
    return uuid.UUID(current_user["sub"])
