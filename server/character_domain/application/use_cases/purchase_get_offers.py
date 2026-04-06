"""Get all active special offers available to the player."""

from __future__ import annotations

from character_domain.application.dtos import PriceResponse, SpecialOfferResponse
from character_domain.domain.services.purchase_manager import PurchaseManager


class PurchaseGetOffersUseCase:

    def __init__(self, purchase_manager: PurchaseManager) -> None:
        self._pm = purchase_manager

    async def execute(self, player_level: int = 0) -> list[SpecialOfferResponse]:
        offers = await self._pm.get_active_offers(player_level)
        return [
            SpecialOfferResponse(
                id=o.id,
                title=o.title,
                description=o.description,
                bundled_item_ids=o.bundled_item_ids,
                price=PriceResponse(
                    currency=o.price.currency.value,
                    original_amount=o.price.original_amount,
                    discounted_amount=o.price.discounted_amount,
                    effective_amount=o.price.effective_amount,
                    is_on_sale=o.price.is_on_sale,
                    discount_percent=o.price.discount_percent,
                ),
                required_level=o.required_level,
                is_active=o.is_active,
                expires_at=o.expires_at,
                image_url=o.image_url,
                discount_percent=o.discount_percent,
                created_at=o.created_at,
            )
            for o in offers
        ]
