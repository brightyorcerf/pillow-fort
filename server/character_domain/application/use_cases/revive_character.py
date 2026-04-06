"""
Revive Character use case — PRD §3.2 Resurrection Paths.

Methods:
  1. Phoenix Feather (Star Dust premium currency)
  2. Penance Streak (7 days 100% goal, free)
"""

from __future__ import annotations

import uuid

from character_domain.application.dtos import CharacterStatusResponse, ReviveRequest
from character_domain.domain.exceptions import CharacterNotFoundException
from character_domain.domain.interfaces import ICharacterRepository, IEventPublisher


class ReviveCharacterUseCase:

    def __init__(
        self,
        char_repo: ICharacterRepository,
        event_publisher: IEventPublisher,
    ) -> None:
        self._char_repo = char_repo
        self._event_publisher = event_publisher

    async def execute(
        self, character_id: uuid.UUID, request: ReviveRequest
    ) -> CharacterStatusResponse:
        character = await self._char_repo.find_by_id(character_id)
        if character is None:
            raise CharacterNotFoundException()

        if request.method == "phoenix_feather":
            character.revive_with_phoenix_feather()
        elif request.method == "full_reset":
            character.full_reset()
        else:
            raise ValueError(f"Unknown revival method: {request.method}")

        await self._char_repo.update(character)
        await self._event_publisher.publish_all(character.domain_events)
        character.clear_events()

        c = character
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
