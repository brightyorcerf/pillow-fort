"""Get the store catalog grouped by category."""

from __future__ import annotations

from character_domain.application.dtos import PriceResponse, StoreCatalogResponse, StoreItemResponse
from character_domain.domain.services.purchase_manager import PurchaseManager


class PurchaseGetCatalogUseCase:

    def __init__(self, purchase_manager: PurchaseManager) -> None:
        self._pm = purchase_manager

    async def execute(self, player_level: int = 0) -> StoreCatalogResponse:
        catalog = await self._pm.get_store_catalog(player_level)
        response_categories: dict[str, list[StoreItemResponse]] = {}
        total = 0
        for cat_name, items in catalog.items():
            response_categories[cat_name] = [
                StoreItemResponse(
                    id=item.id,
                    name=item.name,
                    description=item.description,
                    item_type=item.item_type.value,
                    category=item.category.value,
                    price=PriceResponse(
                        currency=item.price.currency.value,
                        original_amount=item.price.original_amount,
                        discounted_amount=item.price.discounted_amount,
                        effective_amount=item.price.effective_amount,
                        is_on_sale=item.price.is_on_sale,
                        discount_percent=item.price.discount_percent,
                    ),
                    required_level=item.required_level,
                    is_active=item.is_active,
                    max_per_user=item.max_per_user,
                    image_url=item.image_url,
                    metadata=item.metadata,
                    created_at=item.created_at,
                    updated_at=item.updated_at,
                )
                for item in items
            ]
            total += len(items)
        return StoreCatalogResponse(categories=response_categories, total_items=total)
