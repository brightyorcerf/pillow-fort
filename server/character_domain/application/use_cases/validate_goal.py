"""
Validate a goal before committing to it — PRD §3.1.5 Smart Goal Guardrails.

Checks: minimum threshold, PVR, and session cap.
"""

from __future__ import annotations

import uuid

from character_domain.application.dtos import ValidateGoalRequest, GoalValidationResponse
from character_domain.domain.interfaces import ICovenantRepository
from character_domain.domain.value_objects.goal_acceptance import GoalAcceptanceResult
from character_domain.domain.value_objects.session_cap import SessionCap
from character_domain.domain.value_objects.subject_type import SubjectType


class ValidateGoalUseCase:

    def __init__(self, covenant_repo: ICovenantRepository) -> None:
        self._covenant_repo = covenant_repo

    async def execute(
        self, character_id: uuid.UUID, request: ValidateGoalRequest
    ) -> GoalValidationResponse:
        subject = SubjectType(request.subject_type)
        avg_goal = await self._covenant_repo.get_average_goal_minutes(character_id, days=7)
        avg_actual = await self._covenant_repo.get_average_actual_minutes(character_id, days=14)

        acceptance = GoalAcceptanceResult.evaluate(
            goal_minutes=request.goal_minutes,
            average_minutes=avg_goal,
            minimum_minutes=subject.minimum_goal_minutes,
        )
        cap = SessionCap.from_average(avg_actual)

        return GoalValidationResponse(
            accepted=acceptance.accepted,
            label=acceptance.label.value,
            hp_gain_multiplier=acceptance.hp_gain_multiplier,
            message=acceptance.message,
            suggested_cap_minutes=cap.suggested_cap_minutes,
            hard_ceiling_minutes=cap.hard_ceiling_minutes,
        )
