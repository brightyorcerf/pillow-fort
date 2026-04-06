"""Verify Email use case."""

from __future__ import annotations

from auth_domain.application.dtos import VerifyEmailRequest
from auth_domain.domain.exceptions import UserNotFoundException
from auth_domain.domain.interfaces import IEventPublisher, IUserRepository


class VerifyEmailUseCase:

    def __init__(
        self,
        user_repo: IUserRepository,
        event_publisher: IEventPublisher,
    ) -> None:
        self._user_repo = user_repo
        self._event_publisher = event_publisher

    async def execute(self, request: VerifyEmailRequest) -> None:
        # We need to find the user by verification token — scan is acceptable
        # for a token-based lookup. In production, index or use a dedicated table.
        # For now, we'll expect the presentation layer to extract user_id from
        # the verification link or token payload.
        raise NotImplementedError(
            "VerifyEmailUseCase requires user_id context — "
            "see verify_email_with_user_id below."
        )

    async def execute_with_user_id(
        self, user_id, token: str
    ) -> dict[str, str]:
        import uuid as _uuid
        uid = _uuid.UUID(user_id) if isinstance(user_id, str) else user_id

        user = await self._user_repo.find_by_id(uid)
        if user is None:
            raise UserNotFoundException()

        user.verify_email(token)
        await self._user_repo.update(user)

        await self._event_publisher.publish_all(user.domain_events)
        user.clear_events()

        return {"message": "Email verified successfully."}
