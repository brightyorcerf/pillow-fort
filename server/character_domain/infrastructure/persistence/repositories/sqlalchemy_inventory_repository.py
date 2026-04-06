"""SQLAlchemy implementation of IInventoryRepository."""

from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from character_domain.domain.entities.owned_item import OwnedItem
from character_domain.domain.interfaces.inventory_repository import IInventoryRepository
from character_domain.domain.value_objects.purchase_enums import ItemType
from character_domain.infrastructure.persistence.models.owned_item_model import OwnedItemModel


class SqlAlchemyInventoryRepository(IInventoryRepository):

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @staticmethod
    def _to_entity(m: OwnedItemModel) -> OwnedItem:
        return OwnedItem(
            id=m.id,
            user_id=m.user_id,
            item_id=m.item_id,
            item_name=m.item_name,
            item_type=ItemType(m.item_type),
            quantity=m.quantity,
            is_consumable=m.is_consumable,
            is_equipped=m.is_equipped,
            acquired_at=m.acquired_at,
        )

    @staticmethod
    def _to_model(e: OwnedItem) -> OwnedItemModel:
        return OwnedItemModel(
            id=e.id,
            user_id=e.user_id,
            item_id=e.item_id,
            item_name=e.item_name,
            item_type=e.item_type.value,
            quantity=e.quantity,
            is_consumable=e.is_consumable,
            is_equipped=e.is_equipped,
            acquired_at=e.acquired_at,
        )

    async def save(self, item: OwnedItem) -> None:
        self._session.add(self._to_model(item))
        await self._session.flush()

    async def update(self, item: OwnedItem) -> None:
        m = await self._session.get(OwnedItemModel, item.id)
        if m is None:
            raise ValueError(f"OwnedItem {item.id} not found.")
        m.item_name = item.item_name
        m.item_type = item.item_type.value
        m.quantity = item.quantity
        m.is_consumable = item.is_consumable
        m.is_equipped = item.is_equipped
        await self._session.flush()

    async def find_by_id(self, owned_id: uuid.UUID) -> Optional[OwnedItem]:
        m = await self._session.get(OwnedItemModel, owned_id)
        return self._to_entity(m) if m else None

    async def find_by_user(self, user_id: uuid.UUID) -> list[OwnedItem]:
        stmt = (
            select(OwnedItemModel)
            .where(OwnedItemModel.user_id == user_id)
            .order_by(OwnedItemModel.acquired_at.desc())
        )
        result = await self._session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]

    async def find_by_user_and_item(
        self, user_id: uuid.UUID, item_id: uuid.UUID
    ) -> Optional[OwnedItem]:
        stmt = select(OwnedItemModel).where(
            OwnedItemModel.user_id == user_id,
            OwnedItemModel.item_id == item_id,
        )
        result = await self._session.execute(stmt)
        m = result.scalar_one_or_none()
        return self._to_entity(m) if m else None

    async def find_by_user_and_type(
        self, user_id: uuid.UUID, item_type: ItemType
    ) -> list[OwnedItem]:
        stmt = (
            select(OwnedItemModel)
            .where(
                OwnedItemModel.user_id == user_id,
                OwnedItemModel.item_type == item_type.value,
            )
            .order_by(OwnedItemModel.acquired_at.desc())
        )
        result = await self._session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]

    async def count_by_user_and_item(
        self, user_id: uuid.UUID, item_id: uuid.UUID
    ) -> int:
        stmt = (
            select(func.count())
            .select_from(OwnedItemModel)
            .where(
                OwnedItemModel.user_id == user_id,
                OwnedItemModel.item_id == item_id,
            )
        )
        result = await self._session.execute(stmt)
        return result.scalar_one()
