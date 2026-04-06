"""
Complete a study session — apply HP via Prospect Theory equation.

PRD §3.1.5: HP is now calculated using the unified Prospect Theory
equation with a +5 HP y-axis shift. No more flat lookup tables.
PRD §3.1.1: Sessions > 90 min grant "Flow State" buff.
"""

from __future__ import annotations

from character_domain.application.dtos import CompleteSessionRequest, SessionResponse
from character_domain.domain.exceptions import (
    CharacterNotFoundException,
    SessionNotFoundException,
)
from character_domain.domain.interfaces import (
    ICharacterRepository,
    ICovenantRepository,
    IEventPublisher,
    IStudySessionRepository,
)
from character_domain.domain.services.anubis import Anubis
from character_domain.domain.services.reaper import Reaper


class CompleteSessionUseCase:

    def __init__(
        self,
        char_repo: ICharacterRepository,
        covenant_repo: ICovenantRepository,
        session_repo: IStudySessionRepository,
        event_publisher: IEventPublisher,
        anubis: Anubis,
        reaper: Reaper,
    ) -> None:
        self._char_repo = char_repo
        self._covenant_repo = covenant_repo
        self._session_repo = session_repo
        self._event_publisher = event_publisher
        self._anubis = anubis
        self._reaper = reaper

    async def execute(self, request: CompleteSessionRequest) -> SessionResponse:
        session = await self._session_repo.find_by_id(request.session_id)
        if session is None:
            raise SessionNotFoundException()

        character = await self._char_repo.find_by_id(session.character_id)
        if character is None:
            raise CharacterNotFoundException()

        # Complete the session
        session.complete(duration_minutes=request.duration_minutes)

        goal_hit = False

        # Update covenant actual minutes
        covenant = await self._covenant_repo.find_by_id(session.covenant_id)
        if covenant is not None:
            covenant.add_minutes(request.duration_minutes)
            await self._covenant_repo.update(covenant)
            if request.duration_minutes >= covenant.goal_minutes:
                goal_hit = True

        penance_progress_updated = False
        if character.is_in_penance:
            await self._reaper.check_penance_progress(character, goal_hit)
            penance_progress_updated = True

        # Fetch 14-day average for PVR baseline (Prospect Theory equation needs V)
        pvr_baseline = await self._covenant_repo.get_average_actual_minutes(
            character.id, days=14
        )

        # Apply HP via Prospect Theory equation (handles both gains and losses)
        hp_change_result = await self._anubis.apply_session_hp(
            character=character,
            actual_minutes=request.duration_minutes,
            goal_minutes=covenant.goal_minutes if covenant else 0,
            pvr_baseline_minutes=pvr_baseline,
            bonus_task_completed=request.bonus_task_completed,
            reflection_completed=request.reflection_completed,
        )

        # Add study minutes
        character.add_study_minutes(request.duration_minutes)

        await self._session_repo.update(session)
        await self._char_repo.update(character)
        await self._event_publisher.publish_all(character.domain_events)
        character.clear_events()

        hp_changes = []
        if hp_change_result and hp_change_result.delta != 0:
            hp_changes.append(hp_change_result.description)

        return SessionResponse(
            id=session.id,
            character_id=session.character_id,
            covenant_id=session.covenant_id,
            started_at=session.started_at,
            ended_at=session.ended_at,
            duration_minutes=session.duration_minutes,
            status=session.status.value,
            is_verified=session.is_verified,
            hp_earned=hp_change_result.delta if hp_change_result else 0,
            old_hp=hp_change_result.old_hp if hp_change_result else character.hp,
            new_hp=hp_change_result.new_hp if hp_change_result else character.hp,
            hp_changes=hp_changes,
            grants_flow_state=character.has_flow_state_buff,
            penance_progress_updated=penance_progress_updated,
        )
