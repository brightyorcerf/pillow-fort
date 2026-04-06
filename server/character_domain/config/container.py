"""
Dependency Injection container for the character domain.

Follows the same Composition Root / per-request factory pattern as the
auth domain: singletons are created once at startup; use cases that need
a DB session are built per-request via factory methods.

The Anubis domain service is instantiated per-request alongside its
HPLog repository and notification service.
"""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

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
from character_domain.domain.services.anubis import Anubis
from character_domain.domain.services.reaper import Reaper
from character_domain.domain.services.purchase_manager import PurchaseManager
from character_domain.infrastructure.external.log_notification_service import (
    LogNotificationService,
)
from character_domain.infrastructure.external.eulogy_service_impl import (
    SqlAlchemyEulogyService,
)
from character_domain.infrastructure.persistence.repositories import (
    SqlAlchemyCharacterRepository,
    SqlAlchemyCovenantRepository,
    SqlAlchemyDeathRecordRepository,
    SqlAlchemyHPLogRepository,
    SqlAlchemyPenanceStreakRepository,
    SqlAlchemyPhoenixFeatherRepository,
    SqlAlchemyRevivalAttemptRepository,
    SqlAlchemyStudySessionRepository,
    SqlAlchemyWalletRepository,
    SqlAlchemyVaultRepository,
    SqlAlchemyStoreItemRepository,
    SqlAlchemySpecialOfferRepository,
    SqlAlchemyTransactionRepository,
    SqlAlchemyInventoryRepository,
)


class CharacterContainer:
    """
    Lightweight DI container for the character bounded context.

    Singleton dependencies (event publisher, notification service)
    are injected from the auth domain's container or created once
    at startup. Use cases that need a DB session are built
    per-request via factory methods.
    """

    def __init__(self, event_publisher) -> None:
        self.event_publisher = event_publisher
        self.notification_service = LogNotificationService()

    # ── Per-request factory methods ───────────────────────────────────

    def _repos(self, session: AsyncSession):
        return (
            SqlAlchemyCharacterRepository(session),
            SqlAlchemyCovenantRepository(session),
            SqlAlchemyStudySessionRepository(session),
        )

    def _hp_log_repo(self, session: AsyncSession) -> SqlAlchemyHPLogRepository:
        return SqlAlchemyHPLogRepository(session)

    def _anubis(self, session: AsyncSession) -> Anubis:
        return Anubis(
            hp_log_repo=self._hp_log_repo(session),
            notification_service=self.notification_service,
        )

    def create_character_use_case(self, session: AsyncSession) -> CreateCharacterUseCase:
        char_repo, *_ = self._repos(session)
        _, _, _, feather_repo = self._reaper_repos(session)
        return CreateCharacterUseCase(
            char_repo=char_repo,
            event_publisher=self.event_publisher,
            feather_repo=feather_repo,
        )

    def get_character_status_use_case(self, session: AsyncSession) -> GetCharacterStatusUseCase:
        char_repo, *_ = self._repos(session)
        return GetCharacterStatusUseCase(char_repo=char_repo)

    def character_repo(self, session: AsyncSession) -> SqlAlchemyCharacterRepository:
        """Exposed for the dependency that resolves character_id from user_id."""
        return SqlAlchemyCharacterRepository(session)

    def set_covenant_use_case(self, session: AsyncSession) -> SetCovenantUseCase:
        char_repo, cov_repo, *_ = self._repos(session)
        return SetCovenantUseCase(
            char_repo=char_repo,
            covenant_repo=cov_repo,
        )

    def validate_goal_use_case(self, session: AsyncSession) -> ValidateGoalUseCase:
        _, cov_repo, *_ = self._repos(session)
        return ValidateGoalUseCase(
            covenant_repo=cov_repo,
        )

    def start_session_use_case(self, session: AsyncSession) -> StartSessionUseCase:
        char_repo, cov_repo, sess_repo = self._repos(session)
        return StartSessionUseCase(
            char_repo=char_repo,
            covenant_repo=cov_repo,
            session_repo=sess_repo,
            event_publisher=self.event_publisher,
        )

    def complete_session_use_case(self, session: AsyncSession) -> CompleteSessionUseCase:
        char_repo, cov_repo, sess_repo = self._repos(session)
        return CompleteSessionUseCase(
            char_repo=char_repo,
            session_repo=sess_repo,
            covenant_repo=cov_repo,
            event_publisher=self.event_publisher,
            anubis=self._anubis(session),
            reaper=self._reaper(session),
        )

    def session_check_in_use_case(self, session: AsyncSession) -> SessionCheckInUseCase:
        _, _, sess_repo = self._repos(session)
        return SessionCheckInUseCase(session_repo=sess_repo)

    def get_pvr_use_case(self, session: AsyncSession) -> GetPvrUseCase:
        char_repo, cov_repo, sess_repo = self._repos(session)
        return GetPvrUseCase(
            covenant_repo=cov_repo,
            session_repo=sess_repo,
            char_repo=char_repo,
        )

    # (start_ritual_use_case and advance_ritual_use_case removed — rituals no longer exist)

    def revive_character_use_case(self, session: AsyncSession) -> ReviveCharacterUseCase:
        char_repo, *_ = self._repos(session)
        return ReviveCharacterUseCase(
            char_repo=char_repo,
            event_publisher=self.event_publisher,
        )

    def get_eulogy_use_case(self, session: AsyncSession) -> GetEulogyUseCase:
        char_repo, *_ = self._repos(session)
        return GetEulogyUseCase(char_repo=char_repo)

    # ── Anubis use case factories ────────────────────────────────────

    def get_hp_timeline_use_case(self, session: AsyncSession) -> GetHPTimelineUseCase:
        return GetHPTimelineUseCase(anubis=self._anubis(session))

    def get_hp_summary_use_case(self, session: AsyncSession) -> GetHPSummaryUseCase:
        return GetHPSummaryUseCase(anubis=self._anubis(session))

    def anubis_validate_goal_use_case(self, session: AsyncSession) -> AnubisValidateGoalUseCase:
        char_repo, cov_repo, sess_repo, _ = self._repos(session)
        return AnubisValidateGoalUseCase(
            anubis=self._anubis(session),
            char_repo=char_repo,
            covenant_repo=cov_repo,
            session_repo=sess_repo,
        )

    def apply_session_hp_use_case(self, session: AsyncSession) -> ApplySessionHPUseCase:
        char_repo, _, sess_repo, _ = self._repos(session)
        return ApplySessionHPUseCase(
            anubis=self._anubis(session),
            char_repo=char_repo,
            session_repo=sess_repo,
        )

    def apply_bonus_task_hp_use_case(self, session: AsyncSession) -> ApplyBonusTaskHPUseCase:
        char_repo, *_ = self._repos(session)
        return ApplyBonusTaskHPUseCase(
            anubis=self._anubis(session),
            char_repo=char_repo,
        )

    def apply_reflection_hp_use_case(self, session: AsyncSession) -> ApplyReflectionHPUseCase:
        char_repo, *_ = self._repos(session)
        return ApplyReflectionHPUseCase(
            anubis=self._anubis(session),
            char_repo=char_repo,
        )

    def get_weekly_consistency_use_case(self, session: AsyncSession) -> GetWeeklyConsistencyUseCase:
        char_repo, cov_repo, *_ = self._repos(session)
        return GetWeeklyConsistencyUseCase(
            anubis=self._anubis(session),
            char_repo=char_repo,
            covenant_repo=cov_repo,
        )

    def anubis_daily_evaluation_use_case(self, session: AsyncSession) -> AnubisDailyEvaluationUseCase:
        char_repo, cov_repo, *_ = self._repos(session)
        return AnubisDailyEvaluationUseCase(
            anubis=self._anubis(session),
            char_repo=char_repo,
            covenant_repo=cov_repo,
        )

    # ── Reaper helpers ──────────────────────────────────────────────────

    def _reaper_repos(self, session: AsyncSession):
        """Return all Reaper-specific repositories."""
        return (
            SqlAlchemyDeathRecordRepository(session),
            SqlAlchemyRevivalAttemptRepository(session),
            SqlAlchemyPenanceStreakRepository(session),
            SqlAlchemyPhoenixFeatherRepository(session),
        )

    def _eulogy_service(self, session: AsyncSession) -> SqlAlchemyEulogyService:
        return SqlAlchemyEulogyService(session)

    def _reaper(self, session: AsyncSession) -> Reaper:
        death_repo, revival_repo, penance_repo, feather_repo = self._reaper_repos(session)
        return Reaper(
            death_record_repo=death_repo,
            revival_attempt_repo=revival_repo,
            penance_repo=penance_repo,
            feather_repo=feather_repo,
            anubis=self._anubis(session),
            eulogy_service=self._eulogy_service(session),
            notification_service=self.notification_service,
        )

    # ── Reaper use case factories ───────────────────────────────────────

    def reaper_kill_use_case(self, session: AsyncSession) -> ReaperKillUseCase:
        char_repo, *_ = self._repos(session)
        return ReaperKillUseCase(reaper=self._reaper(session), char_repo=char_repo)

    def reaper_revival_options_use_case(self, session: AsyncSession) -> ReaperRevivalOptionsUseCase:
        char_repo, *_ = self._repos(session)
        return ReaperRevivalOptionsUseCase(reaper=self._reaper(session), char_repo=char_repo)

    def reaper_feather_revive_use_case(self, session: AsyncSession) -> ReaperFeatherReviveUseCase:
        char_repo, *_ = self._repos(session)
        return ReaperFeatherReviveUseCase(reaper=self._reaper(session), char_repo=char_repo)

    def reaper_start_penance_use_case(self, session: AsyncSession) -> ReaperStartPenanceUseCase:
        char_repo, *_ = self._repos(session)
        return ReaperStartPenanceUseCase(reaper=self._reaper(session), char_repo=char_repo)

    def reaper_penance_progress_use_case(self, session: AsyncSession) -> ReaperPenanceProgressUseCase:
        char_repo, *_ = self._repos(session)
        return ReaperPenanceProgressUseCase(reaper=self._reaper(session), char_repo=char_repo)

    def reaper_get_penance_use_case(self, session: AsyncSession) -> ReaperGetPenanceUseCase:
        return ReaperGetPenanceUseCase(reaper=self._reaper(session))

    # (ritual use case factories removed — rituals no longer exist)

    def reaper_restore_unfair_death_use_case(self, session: AsyncSession) -> ReaperRestoreUnfairDeathUseCase:
        char_repo, *_ = self._repos(session)
        death_repo, *_ = self._reaper_repos(session)
        return ReaperRestoreUnfairDeathUseCase(
            reaper=self._reaper(session),
            char_repo=char_repo,
            death_record_repo=death_repo,
        )

    def reaper_death_history_use_case(self, session: AsyncSession) -> ReaperDeathHistoryUseCase:
        return ReaperDeathHistoryUseCase(reaper=self._reaper(session))

    def reaper_revival_history_use_case(self, session: AsyncSession) -> ReaperRevivalHistoryUseCase:
        return ReaperRevivalHistoryUseCase(reaper=self._reaper(session))

    def reaper_get_eulogy_use_case(self, session: AsyncSession) -> ReaperGetEulogyUseCase:
        return ReaperGetEulogyUseCase(eulogy_service=self._eulogy_service(session))

    # ── PurchaseManager helpers ────────────────────────────────────────

    def _purchase_repos(self, session: AsyncSession):
        """Return all PurchaseManager-specific repositories."""
        return (
            SqlAlchemyWalletRepository(session),
            SqlAlchemyVaultRepository(session),
            SqlAlchemyStoreItemRepository(session),
            SqlAlchemySpecialOfferRepository(session),
            SqlAlchemyTransactionRepository(session),
            SqlAlchemyInventoryRepository(session),
        )

    def _purchase_manager(self, session: AsyncSession) -> PurchaseManager:
        wallet_repo, vault_repo, store_repo, offer_repo, txn_repo, inv_repo = (
            self._purchase_repos(session)
        )
        _, _, _, feather_repo = self._reaper_repos(session)
        return PurchaseManager(
            wallet_repo=wallet_repo,
            vault_repo=vault_repo,
            store_item_repo=store_repo,
            offer_repo=offer_repo,
            txn_repo=txn_repo,
            inventory_repo=inv_repo,
            feather_repo=feather_repo,
            notification_service=self.notification_service,
        )

    # ── Purchase use case factories ────────────────────────────────────

    def purchase_get_balances_use_case(self, session: AsyncSession) -> PurchaseGetBalancesUseCase:
        return PurchaseGetBalancesUseCase(purchase_manager=self._purchase_manager(session))

    def purchase_credit_coins_use_case(self, session: AsyncSession) -> PurchaseCreditCoinsUseCase:
        return PurchaseCreditCoinsUseCase(purchase_manager=self._purchase_manager(session))

    def purchase_credit_star_dust_use_case(self, session: AsyncSession) -> PurchaseCreditStarDustUseCase:
        return PurchaseCreditStarDustUseCase(purchase_manager=self._purchase_manager(session))

    def purchase_buy_item_use_case(self, session: AsyncSession) -> PurchaseBuyItemUseCase:
        return PurchaseBuyItemUseCase(purchase_manager=self._purchase_manager(session))

    def purchase_buy_offer_use_case(self, session: AsyncSession) -> PurchaseBuyOfferUseCase:
        return PurchaseBuyOfferUseCase(purchase_manager=self._purchase_manager(session))

    def purchase_refund_use_case(self, session: AsyncSession) -> PurchaseRefundUseCase:
        return PurchaseRefundUseCase(purchase_manager=self._purchase_manager(session))

    def purchase_feather_price_use_case(self, session: AsyncSession) -> PurchaseFeatherPriceUseCase:
        return PurchaseFeatherPriceUseCase(purchase_manager=self._purchase_manager(session))

    def purchase_add_store_item_use_case(self, session: AsyncSession) -> PurchaseAddStoreItemUseCase:
        return PurchaseAddStoreItemUseCase(purchase_manager=self._purchase_manager(session))

    def purchase_get_catalog_use_case(self, session: AsyncSession) -> PurchaseGetCatalogUseCase:
        return PurchaseGetCatalogUseCase(purchase_manager=self._purchase_manager(session))

    def purchase_get_offers_use_case(self, session: AsyncSession) -> PurchaseGetOffersUseCase:
        return PurchaseGetOffersUseCase(purchase_manager=self._purchase_manager(session))

    def purchase_get_inventory_use_case(self, session: AsyncSession) -> PurchaseGetInventoryUseCase:
        return PurchaseGetInventoryUseCase(purchase_manager=self._purchase_manager(session))

    def purchase_get_transactions_use_case(self, session: AsyncSession) -> PurchaseGetTransactionsUseCase:
        return PurchaseGetTransactionsUseCase(purchase_manager=self._purchase_manager(session))

    def purchase_get_vault_ledger_use_case(self, session: AsyncSession) -> PurchaseGetVaultLedgerUseCase:
        return PurchaseGetVaultLedgerUseCase(purchase_manager=self._purchase_manager(session))

    def purchase_death_penalty_use_case(self, session: AsyncSession) -> PurchaseDeathPenaltyUseCase:
        return PurchaseDeathPenaltyUseCase(purchase_manager=self._purchase_manager(session))

    # ── Composite Use Case factories ────────────────────────────────────────

    def get_analytics_use_case(self, session: AsyncSession) -> GetAnalyticsUseCase:
        return GetAnalyticsUseCase(
            get_pvr=self.get_pvr_use_case(session),
            get_hp_timeline=self.get_hp_timeline_use_case(session),
            get_hp_summary=self.get_hp_summary_use_case(session),
            get_weekly_consistency=self.get_weekly_consistency_use_case(session),
        )

    def get_revival_status_use_case(self, session: AsyncSession) -> GetRevivalStatusUseCase:
        return GetRevivalStatusUseCase(
            get_options=self.reaper_revival_options_use_case(session),
            get_death_history=self.reaper_death_history_use_case(session),
            get_revival_history=self.reaper_revival_history_use_case(session),
            get_eulogies=self.reaper_get_eulogy_use_case(session),
        )

    def handle_revival_use_case(self, session: AsyncSession) -> HandleRevivalUseCase:
        return HandleRevivalUseCase(
            feather_revive=self.reaper_feather_revive_use_case(session),
        )

    def get_shop_catalog_use_case(self, session: AsyncSession) -> GetShopCatalogUseCase:
        return GetShopCatalogUseCase(
            get_catalog=self.purchase_get_catalog_use_case(session),
            get_offers=self.purchase_get_offers_use_case(session),
        )

    def get_shop_me_use_case(self, session: AsyncSession) -> GetShopMeUseCase:
        return GetShopMeUseCase(
            get_balances=self.purchase_get_balances_use_case(session),
            get_inventory=self.purchase_get_inventory_use_case(session),
        )

    def get_shop_transactions_use_case(self, session: AsyncSession) -> GetShopTransactionsUseCase:
        return GetShopTransactionsUseCase(
            get_transactions=self.purchase_get_transactions_use_case(session),
            get_vault_ledger=self.purchase_get_vault_ledger_use_case(session),
        )

    def shop_purchase_use_case(self, session: AsyncSession) -> ShopPurchaseUseCase:
        return ShopPurchaseUseCase(
            buy_item=self.purchase_buy_item_use_case(session),
            buy_offer=self.purchase_buy_offer_use_case(session),
        )

    def run_daily_cron_use_case(self, session: AsyncSession) -> RunDailyCronUseCase:
        char_repo, cov_repo, *_ = self._repos(session)
        return RunDailyCronUseCase(
            anubis_daily_eval=self.anubis_daily_evaluation_use_case(session),
            char_repo=char_repo,
            covenant_repo=cov_repo,
            reaper=self._reaper(session),
        )
