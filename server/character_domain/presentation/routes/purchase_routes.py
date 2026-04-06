"""
PurchaseManager API routes — Shop, Wallet, Inventory endpoints.
"""

from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status

from character_domain.application.dtos import (
    AddStoreItemRequest,
    CreditCoinsRequest,
    CreditStarDustRequest,
    DeathPenaltyRequest,
    DeathPenaltyResponse,
    FeatherPriceResponse,
    StoreItemResponse,
    TransactionResponse,
    VaultWalletResponse,
    WalletResponse,
    ShopCatalogResponse,
    ShopMeResponse,
    ShopTransactionsResponse,
    ShopPurchaseRequest,
)
from character_domain.application.use_cases import (
    PurchaseAddStoreItemUseCase,
    PurchaseCreditCoinsUseCase,
    PurchaseCreditStarDustUseCase,
    PurchaseDeathPenaltyUseCase,
    PurchaseFeatherPriceUseCase,
    PurchaseRefundUseCase,
    GetShopCatalogUseCase,
    GetShopMeUseCase,
    GetShopTransactionsUseCase,
    ShopPurchaseUseCase,
)
from character_domain.domain.exceptions import (
    CharacterDomainException,
    DuplicateStoreItemException,
    InsufficientBalanceException,
    ItemLevelLockedException,
    ItemPurchaseLimitException,
    OfferExpiredException,
    OfferNotFoundException,
    StoreItemInactiveException,
    StoreItemNotFoundException,
    TransactionNotFoundException,
    TransactionNotRefundableException,
    WalletNotFoundException,
)
from character_domain.presentation.dependencies.character_dependencies import (
    get_current_user_id,
)
from character_domain.presentation.dependencies.use_case_dependencies import (
    get_purchase_add_store_item_use_case,
    get_purchase_credit_coins_use_case,
    get_purchase_credit_star_dust_use_case,
    get_purchase_death_penalty_use_case,
    get_purchase_feather_price_use_case,
    get_purchase_refund_use_case,
    get_shop_catalog_use_case,
    get_shop_me_use_case,
    get_shop_transactions_use_case,
    get_shop_purchase_use_case,
)

router = APIRouter(prefix="/shop", tags=["Shop — Purchases & Economy"])


# ── Exception → HTTP status mapping ──────────────────────────────────

_EXCEPTION_STATUS_MAP: dict[type, int] = {
    StoreItemNotFoundException: status.HTTP_404_NOT_FOUND,
    OfferNotFoundException: status.HTTP_404_NOT_FOUND,
    TransactionNotFoundException: status.HTTP_404_NOT_FOUND,
    WalletNotFoundException: status.HTTP_404_NOT_FOUND,
    StoreItemInactiveException: status.HTTP_422_UNPROCESSABLE_ENTITY,
    ItemLevelLockedException: status.HTTP_422_UNPROCESSABLE_ENTITY,
    ItemPurchaseLimitException: status.HTTP_422_UNPROCESSABLE_ENTITY,
    InsufficientBalanceException: status.HTTP_422_UNPROCESSABLE_ENTITY,
    OfferExpiredException: status.HTTP_422_UNPROCESSABLE_ENTITY,
    TransactionNotRefundableException: status.HTTP_422_UNPROCESSABLE_ENTITY,
    DuplicateStoreItemException: status.HTTP_409_CONFLICT,
}


def _handle(exc: CharacterDomainException) -> HTTPException:
    code = _EXCEPTION_STATUS_MAP.get(type(exc), status.HTTP_400_BAD_REQUEST)
    return HTTPException(status_code=code, detail=exc.detail)


# ═════════════════════════════════════════════════════════════════════
#  MAIN USER SHOP ENDPOINTS
# ═════════════════════════════════════════════════════════════════════


@router.get(
    "/catalog",
    response_model=ShopCatalogResponse,
    summary="Get unified store catalog",
)
async def get_catalog(
    use_case: GetShopCatalogUseCase = Depends(get_shop_catalog_use_case),
):
    """Returns the full store catalog including standard items and special offers."""
    try:
        return await use_case.execute()
    except CharacterDomainException as e:
        raise _handle(e)


@router.get(
    "/me",
    response_model=ShopMeResponse,
    summary="Get user shop state",
)
async def get_shop_me(
    user_id: uuid.UUID = Depends(get_current_user_id),
    use_case: GetShopMeUseCase = Depends(get_shop_me_use_case),
):
    """Returns the user's balances (Coins, Star Dust) and inventory."""
    try:
        return await use_case.execute(user_id)
    except CharacterDomainException as e:
        raise _handle(e)


@router.post(
    "/me/purchase",
    summary="Purchase item or offer",
    status_code=status.HTTP_201_CREATED,
)
async def purchase(
    body: ShopPurchaseRequest,
    user_id: uuid.UUID = Depends(get_current_user_id),
    use_case: ShopPurchaseUseCase = Depends(get_shop_purchase_use_case),
) -> dict[str, Any]:
    """Unified endpoint to purchase a store item or special offer."""
    try:
        return await use_case.execute(user_id, body)
    except CharacterDomainException as e:
        raise _handle(e)


@router.get(
    "/me/transactions",
    response_model=ShopTransactionsResponse,
    summary="Get full transaction history",
)
async def get_transactions(
    user_id: uuid.UUID = Depends(get_current_user_id),
    use_case: GetShopTransactionsUseCase = Depends(get_shop_transactions_use_case),
):
    """Returns combined transaction history and Star Dust vault ledger."""
    try:
        return await use_case.execute(user_id)
    except CharacterDomainException as e:
        raise _handle(e)


@router.get(
    "/me/feather-price",
    response_model=FeatherPriceResponse,
    summary="Get Phoenix Feather price",
)
async def get_feather_price(
    user_id: uuid.UUID = Depends(get_current_user_id),
    deaths_in_window: int = Query(default=0, ge=0),
    use_case: PurchaseFeatherPriceUseCase = Depends(get_purchase_feather_price_use_case),
):
    """Returns the dynamic Phoenix Feather price based on recent deaths."""
    try:
        return await use_case.execute(user_id, deaths_in_window)
    except CharacterDomainException as e:
        raise _handle(e)


# ═════════════════════════════════════════════════════════════════════
#  ADMIN / INTERNAL WALLET COMMANDS
# ═════════════════════════════════════════════════════════════════════


@router.post(
    "/me/coins/credit",
    response_model=WalletResponse,
    summary="Credit coins",
    status_code=status.HTTP_200_OK,
)
async def credit_coins(
    body: CreditCoinsRequest,
    user_id: uuid.UUID = Depends(get_current_user_id),
    use_case: PurchaseCreditCoinsUseCase = Depends(get_purchase_credit_coins_use_case),
):
    try:
        return await use_case.execute(user_id, body.amount, body.reason)
    except CharacterDomainException as e:
        raise _handle(e)


@router.post(
    "/me/stardust/credit",
    response_model=VaultWalletResponse,
    summary="Credit Star Dust",
    status_code=status.HTTP_200_OK,
)
async def credit_star_dust(
    body: CreditStarDustRequest,
    user_id: uuid.UUID = Depends(get_current_user_id),
    use_case: PurchaseCreditStarDustUseCase = Depends(get_purchase_credit_star_dust_use_case),
):
    try:
        return await use_case.execute(
            user_id, body.amount, body.reason, body.description
        )
    except CharacterDomainException as e:
        raise _handle(e)


@router.post(
    "/admin/items",
    response_model=StoreItemResponse,
    summary="Add store item (admin)",
    status_code=status.HTTP_201_CREATED,
)
async def add_store_item(
    body: AddStoreItemRequest,
    use_case: PurchaseAddStoreItemUseCase = Depends(get_purchase_add_store_item_use_case),
):
    try:
        return await use_case.execute(body)
    except CharacterDomainException as e:
        raise _handle(e)


@router.post(
    "/admin/refund/{transaction_id}",
    response_model=TransactionResponse,
    summary="Refund a transaction (admin)",
)
async def refund_transaction(
    transaction_id: uuid.UUID,
    use_case: PurchaseRefundUseCase = Depends(get_purchase_refund_use_case),
):
    try:
        return await use_case.execute(transaction_id)
    except CharacterDomainException as e:
        raise _handle(e)


@router.post(
    "/internal/death-penalty",
    response_model=DeathPenaltyResponse,
    summary="Apply death coin penalty (internal)",
)
async def apply_death_penalty(
    body: DeathPenaltyRequest,
    use_case: PurchaseDeathPenaltyUseCase = Depends(get_purchase_death_penalty_use_case),
):
    try:
        return await use_case.execute(body.user_id)
    except CharacterDomainException as e:
        raise _handle(e)
