"""
Character domain use-case dependency factories.

Each function is a FastAPI dependency that lazily constructs a single
use case with a request-scoped DB session.  Only the use case needed
by the matched route is ever instantiated.
"""

from __future__ import annotations

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from auth_domain.presentation.dependencies.db_dependencies import (
    get_char_container,
    get_db_session,
)
from character_domain.application.use_cases import (
    AnubisDailyEvaluationUseCase,
    AnubisValidateGoalUseCase,
    ApplyBonusTaskHPUseCase,
    ApplyReflectionHPUseCase,
    ApplySessionHPUseCase,
    CompleteSessionUseCase,
    CreateCharacterUseCase,
    GetCharacterStatusUseCase,
    GetEulogyUseCase,
    GetHPSummaryUseCase,
    GetHPTimelineUseCase,
    GetPvrUseCase,
    GetWeeklyConsistencyUseCase,
    ReviveCharacterUseCase,
    SessionCheckInUseCase,
    SetCovenantUseCase,
    StartSessionUseCase,
    ValidateGoalUseCase,
    # Reaper use cases
    ReaperKillUseCase,
    ReaperRevivalOptionsUseCase,
    ReaperFeatherReviveUseCase,
    ReaperStartPenanceUseCase,
    ReaperPenanceProgressUseCase,
    ReaperGetPenanceUseCase,
    ReaperRestoreUnfairDeathUseCase,
    ReaperDeathHistoryUseCase,
    ReaperRevivalHistoryUseCase,
    ReaperGetEulogyUseCase,
    # Purchase use cases
    PurchaseGetBalancesUseCase,
    PurchaseCreditCoinsUseCase,
    PurchaseCreditStarDustUseCase,
    PurchaseBuyItemUseCase,
    PurchaseBuyOfferUseCase,
    PurchaseRefundUseCase,
    PurchaseFeatherPriceUseCase,
    PurchaseAddStoreItemUseCase,
    PurchaseGetCatalogUseCase,
    PurchaseGetOffersUseCase,
    PurchaseGetInventoryUseCase,
    PurchaseGetVaultLedgerUseCase,
    PurchaseDeathPenaltyUseCase,
)
from character_domain.application.use_cases.get_analytics import GetAnalyticsUseCase
from character_domain.application.use_cases.get_revival_status import GetRevivalStatusUseCase
from character_domain.application.use_cases.handle_revival import HandleRevivalUseCase
from character_domain.application.use_cases.get_shop_catalog import GetShopCatalogUseCase
from character_domain.application.use_cases.get_shop_me import GetShopMeUseCase
from character_domain.application.use_cases.get_shop_transactions import GetShopTransactionsUseCase
from character_domain.application.use_cases.shop_purchase import ShopPurchaseUseCase
from character_domain.application.use_cases.run_daily_cron import RunDailyCronUseCase
from character_domain.config.container import CharacterContainer


# ── Character lifecycle ──────────────────────────────────────────────

async def get_create_character_use_case(
    session: AsyncSession = Depends(get_db_session),
    container: CharacterContainer = Depends(get_char_container),
) -> CreateCharacterUseCase:
    return container.create_character_use_case(session)


async def get_character_status_use_case(
    session: AsyncSession = Depends(get_db_session),
    container: CharacterContainer = Depends(get_char_container),
) -> GetCharacterStatusUseCase:
    return container.get_character_status_use_case(session)


async def get_set_covenant_use_case(
    session: AsyncSession = Depends(get_db_session),
    container: CharacterContainer = Depends(get_char_container),
) -> SetCovenantUseCase:
    return container.set_covenant_use_case(session)


async def get_validate_goal_use_case(
    session: AsyncSession = Depends(get_db_session),
    container: CharacterContainer = Depends(get_char_container),
) -> ValidateGoalUseCase:
    return container.validate_goal_use_case(session)


async def get_start_session_use_case(
    session: AsyncSession = Depends(get_db_session),
    container: CharacterContainer = Depends(get_char_container),
) -> StartSessionUseCase:
    return container.start_session_use_case(session)


async def get_complete_session_use_case(
    session: AsyncSession = Depends(get_db_session),
    container: CharacterContainer = Depends(get_char_container),
) -> CompleteSessionUseCase:
    return container.complete_session_use_case(session)


async def get_session_check_in_use_case(
    session: AsyncSession = Depends(get_db_session),
    container: CharacterContainer = Depends(get_char_container),
) -> SessionCheckInUseCase:
    return container.session_check_in_use_case(session)


async def get_pvr_use_case(
    session: AsyncSession = Depends(get_db_session),
    container: CharacterContainer = Depends(get_char_container),
) -> GetPvrUseCase:
    return container.get_pvr_use_case(session)


# (ritual dependency factories removed — rituals no longer exist)


async def get_reaper_restore_unfair_death_use_case(
    session: AsyncSession = Depends(get_db_session),
    container: CharacterContainer = Depends(get_char_container),
) -> ReaperRestoreUnfairDeathUseCase:
    return container.reaper_restore_unfair_death_use_case(session)


async def get_reaper_death_history_use_case(
    session: AsyncSession = Depends(get_db_session),
    container: CharacterContainer = Depends(get_char_container),
) -> ReaperDeathHistoryUseCase:
    return container.reaper_death_history_use_case(session)


async def get_reaper_revival_history_use_case(
    session: AsyncSession = Depends(get_db_session),
    container: CharacterContainer = Depends(get_char_container),
) -> ReaperRevivalHistoryUseCase:
    return container.reaper_revival_history_use_case(session)


async def get_reaper_get_eulogy_use_case(
    session: AsyncSession = Depends(get_db_session),
    container: CharacterContainer = Depends(get_char_container),
) -> ReaperGetEulogyUseCase:
    return container.reaper_get_eulogy_use_case(session)


# ── Purchase use cases ──────────────────────────────────────────────

async def get_purchase_get_balances_use_case(
    session: AsyncSession = Depends(get_db_session),
    container: CharacterContainer = Depends(get_char_container),
) -> PurchaseGetBalancesUseCase:
    return container.purchase_get_balances_use_case(session)


async def get_purchase_credit_coins_use_case(
    session: AsyncSession = Depends(get_db_session),
    container: CharacterContainer = Depends(get_char_container),
) -> PurchaseCreditCoinsUseCase:
    return container.purchase_credit_coins_use_case(session)


async def get_purchase_credit_star_dust_use_case(
    session: AsyncSession = Depends(get_db_session),
    container: CharacterContainer = Depends(get_char_container),
) -> PurchaseCreditStarDustUseCase:
    return container.purchase_credit_star_dust_use_case(session)


async def get_purchase_buy_item_use_case(
    session: AsyncSession = Depends(get_db_session),
    container: CharacterContainer = Depends(get_char_container),
) -> PurchaseBuyItemUseCase:
    return container.purchase_buy_item_use_case(session)


async def get_purchase_buy_offer_use_case(
    session: AsyncSession = Depends(get_db_session),
    container: CharacterContainer = Depends(get_char_container),
) -> PurchaseBuyOfferUseCase:
    return container.purchase_buy_offer_use_case(session)


async def get_purchase_refund_use_case(
    session: AsyncSession = Depends(get_db_session),
    container: CharacterContainer = Depends(get_char_container),
) -> PurchaseRefundUseCase:
    return container.purchase_refund_use_case(session)


async def get_purchase_feather_price_use_case(
    session: AsyncSession = Depends(get_db_session),
    container: CharacterContainer = Depends(get_char_container),
) -> PurchaseFeatherPriceUseCase:
    return container.purchase_feather_price_use_case(session)


async def get_purchase_add_store_item_use_case(
    session: AsyncSession = Depends(get_db_session),
    container: CharacterContainer = Depends(get_char_container),
) -> PurchaseAddStoreItemUseCase:
    return container.purchase_add_store_item_use_case(session)


async def get_purchase_get_catalog_use_case(
    session: AsyncSession = Depends(get_db_session),
    container: CharacterContainer = Depends(get_char_container),
) -> PurchaseGetCatalogUseCase:
    return container.purchase_get_catalog_use_case(session)


async def get_purchase_get_offers_use_case(
    session: AsyncSession = Depends(get_db_session),
    container: CharacterContainer = Depends(get_char_container),
) -> PurchaseGetOffersUseCase:
    return container.purchase_get_offers_use_case(session)


async def get_purchase_get_inventory_use_case(
    session: AsyncSession = Depends(get_db_session),
    container: CharacterContainer = Depends(get_char_container),
) -> PurchaseGetInventoryUseCase:
    return container.purchase_get_inventory_use_case(session)


async def get_purchase_get_transactions_use_case(
    session: AsyncSession = Depends(get_db_session),
    container: CharacterContainer = Depends(get_char_container),
) -> PurchaseGetTransactionsUseCase:
    return container.purchase_get_transactions_use_case(session)


async def get_purchase_get_vault_ledger_use_case(
    session: AsyncSession = Depends(get_db_session),
    container: CharacterContainer = Depends(get_char_container),
) -> PurchaseGetVaultLedgerUseCase:
    return container.purchase_get_vault_ledger_use_case(session)


async def get_purchase_death_penalty_use_case(
    session: AsyncSession = Depends(get_db_session),
    container: CharacterContainer = Depends(get_char_container),
) -> PurchaseDeathPenaltyUseCase:
    return container.purchase_death_penalty_use_case(session)


# ── Composite dependencies ──────────────────────────────────────────

async def get_analytics_use_case(
    session: AsyncSession = Depends(get_db_session),
    container: CharacterContainer = Depends(get_char_container),
) -> GetAnalyticsUseCase:
    return container.get_analytics_use_case(session)


async def get_revival_status_use_case(
    session: AsyncSession = Depends(get_db_session),
    container: CharacterContainer = Depends(get_char_container),
) -> GetRevivalStatusUseCase:
    return container.get_revival_status_use_case(session)


async def get_handle_revival_use_case(
    session: AsyncSession = Depends(get_db_session),
    container: CharacterContainer = Depends(get_char_container),
) -> HandleRevivalUseCase:
    return container.handle_revival_use_case(session)


async def get_shop_catalog_use_case(
    session: AsyncSession = Depends(get_db_session),
    container: CharacterContainer = Depends(get_char_container),
) -> GetShopCatalogUseCase:
    return container.get_shop_catalog_use_case(session)


async def get_shop_me_use_case(
    session: AsyncSession = Depends(get_db_session),
    container: CharacterContainer = Depends(get_char_container),
) -> GetShopMeUseCase:
    return container.get_shop_me_use_case(session)


async def get_shop_transactions_use_case(
    session: AsyncSession = Depends(get_db_session),
    container: CharacterContainer = Depends(get_char_container),
) -> GetShopTransactionsUseCase:
    return container.get_shop_transactions_use_case(session)


async def get_shop_purchase_use_case(
    session: AsyncSession = Depends(get_db_session),
    container: CharacterContainer = Depends(get_char_container),
) -> ShopPurchaseUseCase:
    return container.shop_purchase_use_case(session)


async def get_run_daily_cron_use_case(
    session: AsyncSession = Depends(get_db_session),
    container: CharacterContainer = Depends(get_char_container),
) -> RunDailyCronUseCase:
    return container.run_daily_cron_use_case(session)
