"""Get Character Status use case."""

from __future__ import annotations

import uuid

from character_domain.application.dtos import CharacterStatusResponse
from character_domain.domain.exceptions import CharacterNotFoundException
from character_domain.domain.interfaces import ICharacterRepository


class GetCharacterStatusUseCase:

    def __init__(self, char_repo: ICharacterRepository) -> None:
        self._char_repo = char_repo

    async def execute(self, character_id: uuid.UUID) -> CharacterStatusResponse:
        c = await self._char_repo.find_by_id(character_id)
        if c is None:
            raise CharacterNotFoundException()
        return CharacterStatusResponse(
            id=c.id, user_id=c.user_id, name=c.name, hp=c.hp,
            health_state=c.health_state.value, rank=c.rank.value,
            aura_color=c.rank.aura_color, current_streak=c.current_streak,
            longest_streak=c.longest_streak, total_study_minutes=c.total_study_minutes,
            life_shields=c.life_shields, rituals_used=c.rituals_used,
            ghosting_days=c.ghosting_days, has_flow_state_buff=c.has_flow_state_buff,
            is_permanently_dead=c.is_permanently_dead,
            weekly_consistency_multiplier=c.weekly_consistency_multiplier,
            consecutive_below_average_days=c.consecutive_below_average_days,
            created_at=c.created_at, updated_at=c.updated_at,
        )

    async def execute_by_user(self, user_id: uuid.UUID) -> CharacterStatusResponse:
        c = await self._char_repo.find_by_user_id(user_id)
        if c is None:
            raise CharacterNotFoundException()
        return await self.execute(c.id)
