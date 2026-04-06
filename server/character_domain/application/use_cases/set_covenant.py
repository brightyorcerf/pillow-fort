"""
Set Covenant use case — the daily "Contract Phase" (PRD §3.1.1).

Validates goal against minimum thresholds, PVR, and session cap,
then creates and optionally signs the covenant.
"""

from __future__ import annotations

import uuid
from datetime import date

from character_domain.application.dtos import SetCovenantRequest, CovenantResponse
from character_domain.domain.entities.covenant import Covenant
from character_domain.domain.exceptions import (
    CharacterNotFoundException,
    CovenantAlreadyExistsException,
    GoalAboveCeilingException,
    GoalBelowMinimumException,
)
from character_domain.domain.interfaces import ICharacterRepository, ICovenantRepository
from character_domain.domain.value_objects.goal_acceptance import GoalAcceptanceResult
from character_domain.domain.value_objects.session_cap import SessionCap
from character_domain.domain.value_objects.subject_type import SubjectType


class SetCovenantUseCase:

    def __init__(
        self,
        char_repo: ICharacterRepository,
        covenant_repo: ICovenantRepository,
    ) -> None:
        self._char_repo = char_repo
        self._covenant_repo = covenant_repo

    async def execute(
        self, character_id: uuid.UUID, request: SetCovenantRequest
    ) -> CovenantResponse:
        character = await self._char_repo.find_by_id(character_id)
        if character is None:
            raise CharacterNotFoundException()

        today = date.today()
        existing = await self._covenant_repo.find_active_for_date(character_id, today)
        if existing is not None:
            raise CovenantAlreadyExistsException()

        subject = SubjectType(request.subject_type)

        # PRD §3.1.4 — minimum goal threshold
        if request.goal_minutes < subject.minimum_goal_minutes:
            raise GoalBelowMinimumException(subject.minimum_goal_minutes)

        # PRD §3.1.5a — session cap
        avg_actual = await self._covenant_repo.get_average_actual_minutes(character_id, days=14)
        cap = SessionCap.from_average(avg_actual)
        if request.goal_minutes > cap.hard_ceiling_minutes:
            raise GoalAboveCeilingException(cap.hard_ceiling_minutes)

        # PRD §3.1.5 — PVR-based goal acceptance
        avg_goal = await self._covenant_repo.get_average_goal_minutes(character_id, days=7)
        acceptance = GoalAcceptanceResult.evaluate(
            goal_minutes=request.goal_minutes,
            average_minutes=avg_goal,
            minimum_minutes=subject.minimum_goal_minutes,
        )

        covenant = Covenant.create(
            character_id=character_id,
            covenant_date=today,
            subject_type=subject,
            goal_minutes=request.goal_minutes,
            hp_gain_multiplier=acceptance.hp_gain_multiplier,
        )

        if request.sign:
            covenant.sign()

        await self._covenant_repo.save(covenant)

        return CovenantResponse(
            id=covenant.id,
            character_id=covenant.character_id,
            covenant_date=covenant.covenant_date,
            subject_type=covenant.subject_type.value,
            goal_minutes=covenant.goal_minutes,
            actual_minutes=covenant.actual_minutes,
            status=covenant.status.value,
            is_signed=covenant.is_signed,
            hp_gain_multiplier=covenant.hp_gain_multiplier,
            goal_acceptance_label=acceptance.label.value,
            goal_acceptance_message=acceptance.message,
        )
