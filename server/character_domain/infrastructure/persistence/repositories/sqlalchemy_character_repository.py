"""SQLAlchemy implementation of ICharacterRepository."""

from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from character_domain.domain.entities.character import Character
from character_domain.domain.interfaces.character_repository import ICharacterRepository
from character_domain.infrastructure.persistence.models.character_model import CharacterModel


class SqlAlchemyCharacterRepository(ICharacterRepository):

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @staticmethod
    def _to_entity(m: CharacterModel) -> Character:
        return Character(
            id=m.id,
            user_id=m.user_id,
            name=m.name,
            hp=m.hp,
            current_streak=m.current_streak,
            longest_streak=m.longest_streak,
            total_study_minutes=m.total_study_minutes,
            life_shields=m.life_shields,
            rituals_used=m.rituals_used,
            ghosting_days=m.ghosting_days,
            has_flow_state_buff=m.has_flow_state_buff,
            is_permanently_dead=m.is_permanently_dead,
            is_in_penance=m.is_in_penance,
            weekly_consistency_multiplier=m.weekly_consistency_multiplier,
            consecutive_below_average_days=m.consecutive_below_average_days,
            created_at=m.created_at,
            updated_at=m.updated_at,
        )

    @staticmethod
    def _to_model(e: Character) -> CharacterModel:
        return CharacterModel(
            id=e.id, user_id=e.user_id, name=e.name, hp=e.hp,
            current_streak=e.current_streak, longest_streak=e.longest_streak,
            total_study_minutes=e.total_study_minutes, life_shields=e.life_shields,
            rituals_used=e.rituals_used, ghosting_days=e.ghosting_days,
            has_flow_state_buff=e.has_flow_state_buff,
            is_permanently_dead=e.is_permanently_dead,
            is_in_penance=e.is_in_penance,
            weekly_consistency_multiplier=e.weekly_consistency_multiplier,
            consecutive_below_average_days=e.consecutive_below_average_days,
            created_at=e.created_at, updated_at=e.updated_at,
        )

    async def find_by_id(self, character_id: uuid.UUID) -> Optional[Character]:
        m = await self._session.get(CharacterModel, character_id)
        return self._to_entity(m) if m else None

    async def find_by_user_id(self, user_id: uuid.UUID) -> Optional[Character]:
        stmt = select(CharacterModel).where(CharacterModel.user_id == user_id)
        result = await self._session.execute(stmt)
        m = result.scalar_one_or_none()
        return self._to_entity(m) if m else None

    async def save(self, character: Character) -> None:
        self._session.add(self._to_model(character))
        await self._session.flush()

    async def update(self, character: Character) -> None:
        m = await self._session.get(CharacterModel, character.id)
        if m is None:
            raise ValueError(f"Character {character.id} not found.")
        for attr in (
            "name", "hp", "current_streak", "longest_streak",
            "total_study_minutes", "life_shields", "rituals_used",
            "ghosting_days", "has_flow_state_buff", "is_permanently_dead", "is_in_penance",
            "weekly_consistency_multiplier", "consecutive_below_average_days",
            "updated_at",
        ):
            setattr(m, attr, getattr(character, attr))
        await self._session.flush()
