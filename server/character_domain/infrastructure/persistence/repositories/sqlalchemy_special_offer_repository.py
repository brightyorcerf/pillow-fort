"""SQLAlchemy implementation of ISpecialOfferRepository."""

from __future__ import annotations

import json
import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from character_domain.domain.entities.special_offer import SpecialOffer
from character_domain.domain.interfaces.special_offer_repository import ISpecialOfferRepository
from character_domain.domain.value_objects.purchase_enums import CurrencyType
from character_domain.infrastructure.persistence.models.special_offer_model import SpecialOfferModel


class SqlAlchemySpecialOfferRepository(ISpecialOfferRepository):

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @staticmethod
    def _to_entity(m: SpecialOfferModel) -> SpecialOffer:
        bundled_ids: list[uuid.UUID] = []
        if m.bundled_item_ids_json:
            try:
                bundled_ids = [uuid.UUID(s) for s in json.loads(m.bundled_item_ids_json)]
            except (json.JSONDecodeError, TypeError, ValueError):
                bundled_ids = []
        return SpecialOffer(
            id=m.id,
            title=m.title,
            description=m.description,
            bundled_item_ids=bundled_ids,
            bundle_currency=CurrencyType(m.bundle_currency),
            bundle_price=m.bundle_price,
            original_total=m.original_total,
            required_level=m.required_level,
            is_active=m.is_active,
            expires_at=m.expires_at,
            image_url=m.image_url,
            created_at=m.created_at,
        )

    @staticmethod
    def _to_model(e: SpecialOffer) -> SpecialOfferModel:
        bundled_json = json.dumps([str(uid) for uid in e.bundled_item_ids])
        return SpecialOfferModel(
            id=e.id,
            title=e.title,
            description=e.description,
            bundled_item_ids_json=bundled_json,
            bundle_currency=e.price.currency.value,
            bundle_price=e.price.effective_amount,
            original_total=e.price.original_amount,
            required_level=e.required_level,
            is_active=e.is_active,
            expires_at=e.expires_at,
            image_url=e.image_url,
            created_at=e.created_at,
        )

    async def save(self, offer: SpecialOffer) -> None:
        self._session.add(self._to_model(offer))
        await self._session.flush()

    async def update(self, offer: SpecialOffer) -> None:
        m = await self._session.get(SpecialOfferModel, offer.id)
        if m is None:
            raise ValueError(f"SpecialOffer {offer.id} not found.")
        m.title = offer.title
        m.description = offer.description
        m.bundled_item_ids_json = json.dumps([str(uid) for uid in offer.bundled_item_ids])
        m.bundle_currency = offer.price.currency.value
        m.bundle_price = offer.price.effective_amount
        m.original_total = offer.price.original_amount
        m.required_level = offer.required_level
        m.is_active = offer.is_active
        m.expires_at = offer.expires_at
        m.image_url = offer.image_url
        await self._session.flush()

    async def find_by_id(self, offer_id: uuid.UUID) -> Optional[SpecialOffer]:
        m = await self._session.get(SpecialOfferModel, offer_id)
        return self._to_entity(m) if m else None

    async def find_all_active(self) -> list[SpecialOffer]:
        stmt = (
            select(SpecialOfferModel)
            .where(SpecialOfferModel.is_active.is_(True))
            .order_by(SpecialOfferModel.created_at.desc())
        )
        result = await self._session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]

    async def find_available_for_level(self, player_level: int) -> list[SpecialOffer]:
        stmt = (
            select(SpecialOfferModel)
            .where(
                SpecialOfferModel.is_active.is_(True),
                SpecialOfferModel.required_level <= player_level,
            )
            .order_by(SpecialOfferModel.created_at.desc())
        )
        result = await self._session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]
