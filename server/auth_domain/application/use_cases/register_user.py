"""
Register User use case.

Single Responsibility: handles only the registration flow.
Dependencies are injected via constructor (DIP).
"""

from __future__ import annotations

import secrets

from auth_domain.application.dtos import RegisterRequest, UserProfileResponse
from auth_domain.domain.entities.user import User
from auth_domain.domain.exceptions import UserAlreadyExistsException
from auth_domain.domain.interfaces import (
    IEmailService,
    IEventPublisher,
    IPasswordHasher,
    IUserRepository,
)
from auth_domain.domain.value_objects import Email


class RegisterUserUseCase:

    def __init__(
        self,
        user_repo: IUserRepository,
        password_hasher: IPasswordHasher,
        email_service: IEmailService,
        event_publisher: IEventPublisher,
    ) -> None:
        self._user_repo = user_repo
        self._hasher = password_hasher
        self._email_service = email_service
        self._event_publisher = event_publisher

    async def execute(self, request: RegisterRequest) -> UserProfileResponse:
        email = Email(request.email)

        if await self._user_repo.exists_by_email(email):
            raise UserAlreadyExistsException()

        hashed_pw = self._hasher.hash(request.password)
        verification_token = secrets.token_urlsafe(32)

        user = User.register(
            email=email,
            hashed_password=hashed_pw,
            username=request.username,
            verification_token=verification_token,
        )

        await self._user_repo.save(user)

        # Side effects after successful persistence
        await self._email_service.send_verification_email(
            to=str(email), token=verification_token
        )
        await self._event_publisher.publish_all(user.domain_events)
        user.clear_events()

        return UserProfileResponse(
            id=user.id,
            email=str(user.email),
            username=user.username,
            roles=user.roles,
            is_email_verified=user.is_email_verified,
            created_at=user.created_at,
        )
