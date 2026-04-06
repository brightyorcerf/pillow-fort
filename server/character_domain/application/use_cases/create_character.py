"""Create Character use case — called during onboarding."""

from __future__ import annotations

import uuid

from character_domain.application.dtos import CreateCharacterRequest, CharacterStatusResponse
from character_domain.domain.entities.character import Character
from character_domain.domain.entities.phoenix_feather import PhoenixFeather
from character_domain.domain.exceptions import CharacterAlreadyExistsException
from character_domain.domain.interfaces import ICharacterRepository, IEventPublisher
from character_domain.domain.interfaces.phoenix_feather_repository import IPhoenixFeatherRepository

ONBOARDING_FEATHER_COUNT = 2  # PRD: new users get 2 free Phoenix Feathers


class CreateCharacterUseCase:

    def __init__(
        self,
        char_repo: ICharacterRepository,
        event_publisher: IEventPublisher,
        feather_repo: IPhoenixFeatherRepository,
    ) -> None:
        self._char_repo = char_repo
        self._event_publisher = event_publisher
        self._feather_repo = feather_repo

    async def execute(
        self, user_id: uuid.UUID, request: CreateCharacterRequest
    ) -> CharacterStatusResponse:
        existing = await self._char_repo.find_by_user_id(user_id)
        if existing is not None and not existing.is_permanently_dead:
            raise CharacterAlreadyExistsException()

        character = Character.create(user_id=user_id, name=request.name)
        await self._char_repo.save(character)
        await self._event_publisher.publish_all(character.domain_events)
        character.clear_events()

        # Grant 2 free Phoenix Feathers (PRD onboarding)
        for _ in range(ONBOARDING_FEATHER_COUNT):
            feather = PhoenixFeather.grant_free(user_id=user_id)
            await self._feather_repo.save(feather)

        return self._to_response(character)

    @staticmethod
    def _to_response(c: Character) -> CharacterStatusResponse:
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
