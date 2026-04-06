"""Confirm Password Reset use case."""

from __future__ import annotations

import uuid

from auth_domain.application.dtos import PasswordResetConfirm
from auth_domain.domain.exceptions import (
    InvalidCredentialsException,
    UserNotFoundException,
)
from auth_domain.domain.interfaces import (
    IEventPublisher,
    IPasswordHasher,
    IRefreshTokenRepository,
    IUserRepository,
)


class ConfirmPasswordResetUseCase:

    def __init__(
        self,
        user_repo: IUserRepository,
        password_hasher: IPasswordHasher,
        refresh_token_repo: IRefreshTokenRepository,
        event_publisher: IEventPublisher,
    ) -> None:
        self._user_repo = user_repo
        self._hasher = password_hasher
        self._refresh_repo = refresh_token_repo
        self._event_publisher = event_publisher

    async def execute(
        self, user_id: uuid.UUID, request: PasswordResetConfirm
    ) -> dict[str, str]:
        user = await self._user_repo.find_by_id(user_id)
        if user is None:
            raise UserNotFoundException()

        if not user.validate_password_reset_token(request.token):
            raise InvalidCredentialsException("Invalid or expired reset token.")

        new_hash = self._hasher.hash(request.new_password)
        user.change_password(new_hash)
        await self._user_repo.update(user)

        # Invalidate all existing sessions on password change
        await self._refresh_repo.revoke_all_for_user(user.id)

        await self._event_publisher.publish_all(user.domain_events)
        user.clear_events()

        return {"message": "Password has been reset successfully."}
