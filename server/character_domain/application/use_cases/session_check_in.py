"""
Session check-in use case — PRD §3.1.4 Effort Verification.

Random check-in prompts during the session confirm real effort.
"""

from __future__ import annotations

from character_domain.application.dtos import SessionCheckInRequest
from character_domain.domain.exceptions import SessionNotFoundException
from character_domain.domain.interfaces import IStudySessionRepository


class SessionCheckInUseCase:

    def __init__(self, session_repo: IStudySessionRepository) -> None:
        self._session_repo = session_repo

    async def execute(self, request: SessionCheckInRequest) -> dict[str, str]:
        session = await self._session_repo.find_by_id(request.session_id)
        if session is None:
            raise SessionNotFoundException()

        session.record_check_in(passed=request.passed)
        await self._session_repo.update(session)

        return {
            "message": "Check-in recorded." if request.passed else "Check-in failed.",
            "is_verified": str(session.is_verified),
        }
