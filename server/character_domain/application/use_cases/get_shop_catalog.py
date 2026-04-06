from __future__ import annotations

import uuid

from character_domain.application.dtos.purchase_dtos import ShopCatalogResponse
from character_domain.application.use_cases.purchase_get_catalog import PurchaseGetCatalogUseCase
from character_domain.application.use_cases.purchase_get_offers import PurchaseGetOffersUseCase


class GetShopCatalogUseCase:
    def __init__(
        self,
        get_catalog: PurchaseGetCatalogUseCase,
        get_offers: PurchaseGetOffersUseCase,
    ) -> None:
        self._get_catalog = get_catalog
        self._get_offers = get_offers

    async def execute(self) -> ShopCatalogResponse:
        catalog = await self._get_catalog.execute()
        offers = await self._get_offers.execute()

        # Unwrap lists since ShopCatalogResponse expects the nested objects
        return ShopCatalogResponse(
            items=catalog,
            offers=offers,
        )
