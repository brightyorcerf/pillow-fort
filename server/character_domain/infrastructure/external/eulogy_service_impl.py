"""
Concrete EulogyService implementation.

Generates a rich eulogy by querying the character's lifetime stats
from repositories and persists the result in the eulogies table.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from character_domain.domain.interfaces.eulogy_service import Eulogy, IEulogyService
from character_domain.infrastructure.persistence.models.character_model import CharacterModel
from character_domain.infrastructure.persistence.models.covenant_model import CovenantModel
from character_domain.infrastructure.persistence.models.eulogy_model import EulogyModel
from character_domain.domain.value_objects.rank import Rank


class SqlAlchemyEulogyService(IEulogyService):
    """
    Generates eulogies from live DB data and persists them
    as permanent records in the eulogies table.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def generate(
        self,
        character_id: uuid.UUID,
        user_id: uuid.UUID,
        death_record_id: uuid.UUID,
    ) -> Eulogy:
        # Fetch character snapshot
        char = await self._session.get(CharacterModel, character_id)
        if char is None:
            raise ValueError(f"Character {character_id} not found for eulogy.")

        # Count covenants
        total_signed_stmt = (
            select(func.count())
            .select_from(CovenantModel)
            .where(CovenantModel.character_id == character_id)
        )
        total_signed = (await self._session.execute(total_signed_stmt)).scalar_one()

        total_kept_stmt = (
            select(func.count())
            .select_from(CovenantModel)
            .where(
                CovenantModel.character_id == character_id,
                CovenantModel.status == "completed",
            )
        )
        total_kept = (await self._session.execute(total_kept_stmt)).scalar_one()

        eulogy = Eulogy(
            id=uuid.uuid4(),
            character_id=character_id,
            user_id=user_id,
            death_record_id=death_record_id,
            character_name=char.name,
            total_study_hours=round(char.total_study_minutes / 60, 1),
            longest_streak=char.longest_streak,
            rank_achieved=Rank.from_streak(char.longest_streak).value,
            life_shields_earned=char.life_shields,
            rituals_completed=char.rituals_used,
            total_covenants_signed=total_signed,
            total_covenants_kept=total_kept,
            born_at=char.created_at,
            died_at=datetime.now(timezone.utc),
        )

        # Persist
        model = EulogyModel(
            id=eulogy.id,
            character_id=eulogy.character_id,
            user_id=eulogy.user_id,
            death_record_id=eulogy.death_record_id,
            character_name=eulogy.character_name,
            total_study_hours=eulogy.total_study_hours,
            longest_streak=eulogy.longest_streak,
            rank_achieved=eulogy.rank_achieved,
            life_shields_earned=eulogy.life_shields_earned,
            rituals_completed=eulogy.rituals_completed,
            total_covenants_signed=eulogy.total_covenants_signed,
            total_covenants_kept=eulogy.total_covenants_kept,
            born_at=eulogy.born_at,
            died_at=eulogy.died_at,
            created_at=eulogy.created_at,
        )
        self._session.add(model)
        await self._session.flush()

        return eulogy

    async def find_by_character(
        self, character_id: uuid.UUID
    ) -> list[Eulogy]:
        stmt = (
            select(EulogyModel)
            .where(EulogyModel.character_id == character_id)
            .order_by(EulogyModel.created_at.desc())
        )
        result = await self._session.execute(stmt)
        return [self._to_domain(m) for m in result.scalars().all()]

    async def find_by_death_record(
        self, death_record_id: uuid.UUID
    ) -> Eulogy | None:
        stmt = select(EulogyModel).where(
            EulogyModel.death_record_id == death_record_id
        )
        result = await self._session.execute(stmt)
        m = result.scalar_one_or_none()
        return self._to_domain(m) if m else None

    @staticmethod
    def _to_domain(m: EulogyModel) -> Eulogy:
        return Eulogy(
            id=m.id,
            character_id=m.character_id,
            user_id=m.user_id,
            death_record_id=m.death_record_id,
            character_name=m.character_name,
            total_study_hours=m.total_study_hours,
            longest_streak=m.longest_streak,
            rank_achieved=m.rank_achieved,
            life_shields_earned=m.life_shields_earned,
            rituals_completed=m.rituals_completed,
            total_covenants_signed=m.total_covenants_signed,
            total_covenants_kept=m.total_covenants_kept,
            born_at=m.born_at,
            died_at=m.died_at,
            created_at=m.created_at,
        )
