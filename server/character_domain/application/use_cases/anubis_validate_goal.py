"""
Validate a proposed goal through Anubis — includes PVR-aware evaluation.
"""

from __future__ import annotations

import uuid

from character_domain.application.dtos import (
    AnubisGoalValidationRequest,
    AnubisGoalValidationResponse,
)
from character_domain.domain.exceptions import CharacterNotFoundException
from character_domain.domain.interfaces import (
    ICharacterRepository,
    ICovenantRepository,
    IStudySessionRepository,
)
from character_domain.domain.services.anubis import Anubis
from character_domain.domain.value_objects.subject_type import SubjectType


class AnubisValidateGoalUseCase:

    def __init__(
        self,
        anubis: Anubis,
        char_repo: ICharacterRepository,
        covenant_repo: ICovenantRepository,
        session_repo: IStudySessionRepository,
    ) -> None:
        self._anubis = anubis
        self._char_repo = char_repo
        self._covenant_repo = covenant_repo
        self._session_repo = session_repo

    async def execute(
        self,
        character_id: uuid.UUID,
        request: AnubisGoalValidationRequest,
    ) -> AnubisGoalValidationResponse:
        character = await self._char_repo.find_by_id(character_id)
        if character is None:
            raise CharacterNotFoundException()

        subject = SubjectType(request.subject_type)

        avg_goal = await self._covenant_repo.get_average_goal_minutes(
            character_id, days=7
        )
        avg_actual = await self._covenant_repo.get_average_actual_minutes(
            character_id, days=14
        )
        longest = await self._session_repo.get_longest_session_minutes(character_id)

        result = self._anubis.validate_goal(
            goal_minutes=request.goal_minutes,
            subject_type=subject,
            average_goal_minutes=avg_goal,
            average_actual_minutes=avg_actual,
            longest_session_minutes=longest,
        )

        return AnubisGoalValidationResponse(
            accepted=result.accepted,
            label=result.label,
            hp_gain_multiplier=result.hp_gain_multiplier,
            message=result.message,
            suggested_cap_minutes=result.suggested_cap_minutes,
            hard_ceiling_minutes=result.hard_ceiling_minutes,
        )
