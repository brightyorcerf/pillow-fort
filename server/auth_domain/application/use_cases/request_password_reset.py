"""
Request Password Reset use case.

Security: always returns success even if email doesn't exist
(prevents email enumeration attacks).
"""

from __future__ import annotations

import secrets
from datetime import datetime, timedelta, timezone

from auth_domain.application.dtos import PasswordResetRequest
from auth_domain.domain.interfaces import IEmailService, IUserRepository
from auth_domain.domain.value_objects import Email


class RequestPasswordResetUseCase:

    RESET_TOKEN_TTL_HOURS = 1

    def __init__(
        self,
        user_repo: IUserRepository,
        email_service: IEmailService,
    ) -> None:
        self._user_repo = user_repo
        self._email_service = email_service

    async def execute(self, request: PasswordResetRequest) -> dict[str, str]:
        email = Email(request.email)
        user = await self._user_repo.find_by_email(email)

        if user is not None:
            token = secrets.token_urlsafe(32)
            expires = datetime.now(timezone.utc) + timedelta(
                hours=self.RESET_TOKEN_TTL_HOURS
            )
            user.initiate_password_reset(token=token, expires=expires)
            await self._user_repo.update(user)
            await self._email_service.send_password_reset_email(
                to=str(email), token=token
            )

        # Always return same message — no email enumeration
        return {
            "message": "If an account with that email exists, a reset link has been sent."
        }
