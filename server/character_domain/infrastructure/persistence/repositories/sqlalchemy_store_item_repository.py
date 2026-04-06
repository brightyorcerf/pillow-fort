"""SQLAlchemy implementation of IStoreItemRepository."""

from __future__ import annotations

import json
import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from character_domain.domain.entities.store_item import StoreItem
from character_domain.domain.interfaces.store_item_repository import IStoreItemRepository
from character_domain.domain.value_objects.purchase_enums import CategoryType, CurrencyType, ItemType
from character_domain.infrastructure.persistence.models.store_item_model import StoreItemModel


class SqlAlchemyStoreItemRepository(IStoreItemRepository):

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @staticmethod
    def _to_entity(m: StoreItemModel) -> StoreItem:
        metadata = {}
        if m.metadata_json:
            try:
                metadata = json.loads(m.metadata_json)
            except (json.JSONDecodeError, TypeError):
                metadata = {}
        return StoreItem(
            id=m.id,
            name=m.name,
            description=m.description,
            item_type=ItemType(m.item_type),
            category=CategoryType(m.category),
            price_currency=CurrencyType(m.price_currency),
            price_amount=m.price_amount,
            discounted_amount=m.discounted_amount,
            required_level=m.required_level,
            is_active=m.is_active,
            max_per_user=m.max_per_user,
            image_url=m.image_url,
            metadata=metadata,
            created_at=m.created_at,
            updated_at=m.updated_at,
        )

    @staticmethod
    def _to_model(e: StoreItem) -> StoreItemModel:
        metadata_json = json.dumps(e.metadata) if e.metadata else None
        return StoreItemModel(
            id=e.id,
            name=e.name,
            description=e.description,
            item_type=e.item_type.value,
            category=e.category.value,
            price_currency=e.price.currency.value,
            price_amount=e.price.original_amount,
            discounted_amount=e.price.discounted_amount,
            required_level=e.required_level,
            is_active=e.is_active,
            max_per_user=e.max_per_user,
            image_url=e.image_url,
            metadata_json=metadata_json,
            created_at=e.created_at,
            updated_at=e.updated_at,
        )

    async def save(self, item: StoreItem) -> None:
        self._session.add(self._to_model(item))
        await self._session.flush()

    async def update(self, item: StoreItem) -> None:
        m = await self._session.get(StoreItemModel, item.id)
        if m is None:
            raise ValueError(f"StoreItem {item.id} not found.")
        m.name = item.name
        m.description = item.description
        m.item_type = item.item_type.value
        m.category = item.category.value
        m.price_currency = item.price.currency.value
        m.price_amount = item.price.original_amount
        m.discounted_amount = item.price.discounted_amount
        m.required_level = item.required_level
        m.is_active = item.is_active
        m.max_per_user = item.max_per_user
        m.image_url = item.image_url
        m.metadata_json = json.dumps(item.metadata) if item.metadata else None
        m.updated_at = item.updated_at
        await self._session.flush()

    async def find_by_id(self, item_id: uuid.UUID) -> Optional[StoreItem]:
        m = await self._session.get(StoreItemModel, item_id)
        return self._to_entity(m) if m else None

    async def find_by_name(self, name: str) -> Optional[StoreItem]:
        stmt = select(StoreItemModel).where(StoreItemModel.name == name)
        result = await self._session.execute(stmt)
        m = result.scalar_one_or_none()
        return self._to_entity(m) if m else None

    async def find_active_by_category(
        self, category: CategoryType
    ) -> list[StoreItem]:
        stmt = (
            select(StoreItemModel)
            .where(
                StoreItemModel.category == category.value,
                StoreItemModel.is_active.is_(True),
            )
            .order_by(StoreItemModel.name)
        )
        result = await self._session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]

    async def find_active_by_type(self, item_type: ItemType) -> list[StoreItem]:
        stmt = (
            select(StoreItemModel)
            .where(
                StoreItemModel.item_type == item_type.value,
                StoreItemModel.is_active.is_(True),
            )
            .order_by(StoreItemModel.name)
        )
        result = await self._session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]

    async def find_all_active(self) -> list[StoreItem]:
        stmt = (
            select(StoreItemModel)
            .where(StoreItemModel.is_active.is_(True))
            .order_by(StoreItemModel.category, StoreItemModel.name)
        )
        result = await self._session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]

    async def exists_by_name(self, name: str) -> bool:
        stmt = select(StoreItemModel.id).where(StoreItemModel.name == name).limit(1)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None
