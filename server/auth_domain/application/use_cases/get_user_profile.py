"""Get User Profile use case (query)."""

from __future__ import annotations

import uuid

from auth_domain.application.dtos import UserProfileResponse
from auth_domain.domain.exceptions import UserNotFoundException
from auth_domain.domain.interfaces import IUserRepository


class GetUserProfileUseCase:

    def __init__(self, user_repo: IUserRepository) -> None:
        self._user_repo = user_repo

    async def execute(self, user_id: uuid.UUID) -> UserProfileResponse:
        user = await self._user_repo.find_by_id(user_id)
        if user is None:
            raise UserNotFoundException()

        return UserProfileResponse(
            id=user.id,
            email=str(user.email),
            username=user.username,
            roles=user.roles,
            is_email_verified=user.is_email_verified,
            created_at=user.created_at,
        )
