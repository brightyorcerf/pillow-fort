"""Add a new item to the store catalog (admin)."""

from __future__ import annotations

from character_domain.application.dtos import AddStoreItemRequest, StoreItemResponse, PriceResponse
from character_domain.domain.entities.store_item import StoreItem
from character_domain.domain.services.purchase_manager import PurchaseManager
from character_domain.domain.value_objects.purchase_enums import (
    CategoryType,
    CurrencyType,
    ItemType,
)


class PurchaseAddStoreItemUseCase:

    def __init__(self, purchase_manager: PurchaseManager) -> None:
        self._pm = purchase_manager

    async def execute(self, req: AddStoreItemRequest) -> StoreItemResponse:
        item = StoreItem.create(
            name=req.name,
            description=req.description,
            item_type=ItemType(req.item_type),
            category=CategoryType(req.category),
            currency=CurrencyType(req.currency),
            price_amount=req.price_amount,
            discounted_amount=req.discounted_amount,
            required_level=req.required_level,
            max_per_user=req.max_per_user,
            image_url=req.image_url,
            metadata=req.metadata,
        )
        saved = await self._pm.add_store_item(item)
        return StoreItemResponse(
            id=saved.id,
            name=saved.name,
            description=saved.description,
            item_type=saved.item_type.value,
            category=saved.category.value,
            price=PriceResponse(
                currency=saved.price.currency.value,
                original_amount=saved.price.original_amount,
                discounted_amount=saved.price.discounted_amount,
                effective_amount=saved.price.effective_amount,
                is_on_sale=saved.price.is_on_sale,
                discount_percent=saved.price.discount_percent,
            ),
            required_level=saved.required_level,
            is_active=saved.is_active,
            max_per_user=saved.max_per_user,
            image_url=saved.image_url,
            metadata=saved.metadata,
            created_at=saved.created_at,
            updated_at=saved.updated_at,
        )
