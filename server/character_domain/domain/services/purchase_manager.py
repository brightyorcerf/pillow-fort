"""
PurchaseManager — The Single Authority Over All Purchases and Currency.

Orchestrates:
  - Dual-currency management (Coins via Wallet, Star Dust via Vault)
  - Store item purchases (validate → debit → grant → record)
  - Special offer / bundle purchases
  - Phoenix Feather dynamic pricing
  - Transaction lifecycle (purchase → complete → optional refund)
  - Inventory management (grant items, track ownership)
  - Vault ledger (immutable audit trail for Star Dust)

Design principles:
  - Single Responsibility: PurchaseManager owns purchases. Period.
  - Open/Closed: new item types added via ItemType enum.
  - Dependency Inversion: depends on repository/service interfaces.
  - No Loot Boxes: PRD §5.3 — users always know what they're buying.

PRD references: §3.3 (Dual Economy), §3.2.5 (Vault Security),
                §5.1 (Monetization), §5.3 (Fair Play Rules).
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

from character_domain.domain.entities.owned_item import OwnedItem
from character_domain.domain.entities.phoenix_feather import PhoenixFeather
from character_domain.domain.entities.special_offer import SpecialOffer
from character_domain.domain.entities.store_item import StoreItem
from character_domain.domain.entities.transaction import Transaction
from character_domain.domain.entities.vault_ledger import VaultLedger
from character_domain.domain.entities.vault_wallet import VaultWallet
from character_domain.domain.entities.wallet import Wallet
from character_domain.domain.exceptions import (
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
from character_domain.domain.interfaces.inventory_repository import IInventoryRepository
from character_domain.domain.interfaces.notification_service import (
    INotificationService,
    NotificationType,
)
from character_domain.domain.interfaces.phoenix_feather_repository import (
    IPhoenixFeatherRepository,
)
from character_domain.domain.interfaces.special_offer_repository import (
    ISpecialOfferRepository,
)
from character_domain.domain.interfaces.store_item_repository import IStoreItemRepository
from character_domain.domain.interfaces.transaction_repository import ITransactionRepository
from character_domain.domain.interfaces.vault_repository import IVaultRepository
from character_domain.domain.interfaces.wallet_repository import IWalletRepository
from character_domain.domain.value_objects.purchase_enums import (
    CurrencyType,
    ItemType,
    TransactionStatus,
    VaultLedgerReason,
)


# ── Result types ────────────────────────────────────────────────────


@dataclass(frozen=True)
class ValidationResult:
    valid: bool
    reason: str | None = None


@dataclass(frozen=True)
class PurchaseResult:
    success: bool
    transaction_id: uuid.UUID | None = None
    owned_item_id: uuid.UUID | None = None
    reason: str | None = None


# ── Dynamic Feather Pricing ─────────────────────────────────────────

FEATHER_BASE_PRICE_STARDUST = 99       # ~$0.99 worth of Star Dust
FEATHER_PRICE_INCREMENT = 100           # +$1.00 per death in 30-day window
FEATHER_MAX_PRICE_STARDUST = 499       # Cap at ~$4.99
FEATHER_PRICE_WINDOW_DAYS = 30


class PurchaseManager:
    """
    Domain service — sole arbiter of purchases, currency, and inventory.

    Injected dependencies (ports):
      - wallet_repo: coin wallet persistence
      - vault_repo: Star Dust vault + ledger persistence
      - store_item_repo: catalog management
      - offer_repo: special offer management
      - txn_repo: transaction records
      - inventory_repo: owned items
      - feather_repo: Phoenix Feather inventory
      - notification_service: purchase notifications
    """

    def __init__(
        self,
        wallet_repo: IWalletRepository,
        vault_repo: IVaultRepository,
        store_item_repo: IStoreItemRepository,
        offer_repo: ISpecialOfferRepository,
        txn_repo: ITransactionRepository,
        inventory_repo: IInventoryRepository,
        feather_repo: IPhoenixFeatherRepository,
        notification_service: INotificationService,
    ) -> None:
        self._wallet_repo = wallet_repo
        self._vault_repo = vault_repo
        self._store_item_repo = store_item_repo
        self._offer_repo = offer_repo
        self._txn_repo = txn_repo
        self._inventory_repo = inventory_repo
        self._feather_repo = feather_repo
        self._notification_service = notification_service

    # ═════════════════════════════════════════════════════════════════
    #  1. WALLET & VAULT MANAGEMENT
    # ═════════════════════════════════════════════════════════════════

    async def get_or_create_wallet(self, user_id: uuid.UUID) -> Wallet:
        """Get the user's coin wallet, creating one if it doesn't exist."""
        wallet = await self._wallet_repo.find_by_user(user_id)
        if wallet is None:
            wallet = Wallet.create(user_id)
            await self._wallet_repo.save(wallet)
        return wallet

    async def get_or_create_vault(self, user_id: uuid.UUID) -> VaultWallet:
        """Get the user's Star Dust vault, creating one if it doesn't exist."""
        vault = await self._vault_repo.find_wallet_by_user(user_id)
        if vault is None:
            vault = VaultWallet.create(user_id)
            await self._vault_repo.save_wallet(vault)
        return vault

    async def credit_coins(
        self, user_id: uuid.UUID, amount: int, reason: str = "Study reward"
    ) -> Wallet:
        """Award coins for studying, streaks, etc."""
        wallet = await self.get_or_create_wallet(user_id)
        wallet.credit_coins(amount)
        await self._wallet_repo.update(wallet)
        return wallet

    async def credit_star_dust(
        self,
        user_id: uuid.UUID,
        amount: int,
        reason: VaultLedgerReason = VaultLedgerReason.PURCHASE,
        description: str = "Star Dust top-up",
        reference_id: uuid.UUID | None = None,
    ) -> VaultWallet:
        """Add Star Dust (real-money purchase or refund/gift)."""
        vault = await self.get_or_create_vault(user_id)
        is_purchase = reason == VaultLedgerReason.PURCHASE
        vault.credit(amount, is_purchase=is_purchase)
        await self._vault_repo.update_wallet(vault)

        # Immutable ledger entry
        entry = VaultLedger.create(
            vault_id=vault.id,
            user_id=user_id,
            delta=amount,
            reason=reason,
            description=description,
            balance_after=vault.star_dust_balance,
            reference_id=reference_id,
        )
        await self._vault_repo.save_ledger_entry(entry)

        return vault

    async def get_balances(
        self, user_id: uuid.UUID
    ) -> dict:
        """Get both currency balances for a user."""
        wallet = await self.get_or_create_wallet(user_id)
        vault = await self.get_or_create_vault(user_id)
        return {
            "coins": wallet.coin_balance,
            "star_dust": vault.star_dust_balance,
            "total_coins_earned": wallet.total_coins_earned,
            "total_coins_spent": wallet.total_coins_spent,
            "total_star_dust_purchased": vault.total_star_dust_purchased,
            "total_star_dust_spent": vault.total_star_dust_spent,
        }

    # ═════════════════════════════════════════════════════════════════
    #  2. PURCHASE VALIDATION
    # ═════════════════════════════════════════════════════════════════

    async def validate_purchase(
        self,
        user_id: uuid.UUID,
        item: StoreItem,
        player_level: int = 0,
    ) -> ValidationResult:
        """
        Pre-purchase validation. Checks:
          1. Item is active
          2. Player meets level requirement
          3. Player hasn't exceeded per-user purchase limit
          4. Player can afford the item
        """
        if not item.is_active:
            return ValidationResult(valid=False, reason="Item is not currently available.")

        if not item.is_unlocked(player_level):
            return ValidationResult(
                valid=False,
                reason=f"Requires level {item.required_level}.",
            )

        # Per-user limit check
        if item.max_per_user is not None:
            owned_count = await self._txn_repo.count_completed_for_item(
                user_id, item.id
            )
            if owned_count >= item.max_per_user:
                return ValidationResult(
                    valid=False,
                    reason=f"Purchase limit reached ({item.max_per_user}).",
                )

        # Affordability check
        effective_price = item.price.effective_amount
        if item.price.currency == CurrencyType.COINS:
            wallet = await self.get_or_create_wallet(user_id)
            if not wallet.can_afford_coins(effective_price):
                return ValidationResult(
                    valid=False,
                    reason=f"Not enough coins. Need {effective_price}, have {wallet.coin_balance}.",
                )
        else:
            vault = await self.get_or_create_vault(user_id)
            if not vault.can_afford(effective_price):
                return ValidationResult(
                    valid=False,
                    reason=f"Not enough Star Dust. Need {effective_price}, have {vault.star_dust_balance}.",
                )

        return ValidationResult(valid=True)

    # ═════════════════════════════════════════════════════════════════
    #  3. PURCHASE PROCESSING
    # ═════════════════════════════════════════════════════════════════

    async def purchase_item(
        self,
        user_id: uuid.UUID,
        item_id: uuid.UUID,
        player_level: int = 0,
    ) -> PurchaseResult:
        """
        Execute a store item purchase:
          1. Find and validate item
          2. Debit currency
          3. Create transaction record
          4. Grant item to inventory
          5. Handle special item types (Phoenix Feather, etc.)
          6. Notify user
        """
        item = await self._store_item_repo.find_by_id(item_id)
        if item is None:
            raise StoreItemNotFoundException()

        validation = await self.validate_purchase(user_id, item, player_level)
        if not validation.valid:
            return PurchaseResult(success=False, reason=validation.reason)

        effective_price = item.price.effective_amount

        # Create pending transaction
        txn = Transaction.create_for_item(
            user_id=user_id,
            item_id=item.id,
            item_name=item.name,
            currency=item.price.currency,
            amount_paid=effective_price,
        )
        await self._txn_repo.save(txn)

        try:
            # Debit currency
            if item.price.currency == CurrencyType.COINS:
                wallet = await self.get_or_create_wallet(user_id)
                wallet.debit_coins(effective_price)
                await self._wallet_repo.update(wallet)
            else:
                vault = await self.get_or_create_vault(user_id)
                vault.debit(effective_price)
                await self._vault_repo.update_wallet(vault)

                # Vault ledger entry
                entry = VaultLedger.create(
                    vault_id=vault.id,
                    user_id=user_id,
                    delta=-effective_price,
                    reason=VaultLedgerReason.SPENDING,
                    description=f"Purchased: {item.name}",
                    balance_after=vault.star_dust_balance,
                    reference_id=txn.id,
                )
                await self._vault_repo.save_ledger_entry(entry)

            # Grant item
            owned_item = await self._grant_item(user_id, item)

            # Handle Phoenix Feather special case
            if item.item_type == ItemType.PHOENIX_FEATHER:
                feather = PhoenixFeather.purchase(
                    user_id=user_id,
                    price_stardust=effective_price,
                )
                await self._feather_repo.save(feather)

            # Complete transaction
            txn.complete()
            await self._txn_repo.update(txn)

            await self._notification_service.send(
                user_id=user_id,
                notification_type=NotificationType.LIFE_SHIELD_EARNED,
                title="Purchase Complete!",
                body=f"You bought {item.name} for {effective_price} {item.price.currency.value}.",
                data={"item_id": str(item.id), "transaction_id": str(txn.id)},
            )

            return PurchaseResult(
                success=True,
                transaction_id=txn.id,
                owned_item_id=owned_item.id,
            )

        except Exception as e:
            txn.fail(str(e))
            await self._txn_repo.update(txn)
            return PurchaseResult(success=False, reason=str(e))

    async def purchase_offer(
        self,
        user_id: uuid.UUID,
        offer_id: uuid.UUID,
        player_level: int = 0,
    ) -> PurchaseResult:
        """
        Purchase a special offer (bundle) at the discounted price.
        Grants all bundled items to the user's inventory.
        """
        offer = await self._offer_repo.find_by_id(offer_id)
        if offer is None:
            raise OfferNotFoundException()

        if offer.is_expired():
            raise OfferExpiredException()

        if not offer.is_available(player_level):
            raise ItemLevelLockedException(offer.required_level)

        effective_price = offer.price.effective_amount

        # Affordability check
        if offer.price.currency == CurrencyType.COINS:
            wallet = await self.get_or_create_wallet(user_id)
            if not wallet.can_afford_coins(effective_price):
                raise InsufficientBalanceException()
        else:
            vault = await self.get_or_create_vault(user_id)
            if not vault.can_afford(effective_price):
                raise InsufficientBalanceException()

        # Create pending transaction
        txn = Transaction.create_for_offer(
            user_id=user_id,
            offer_id=offer.id,
            offer_title=offer.title,
            currency=offer.price.currency,
            amount_paid=effective_price,
        )
        await self._txn_repo.save(txn)

        try:
            # Debit currency
            if offer.price.currency == CurrencyType.COINS:
                wallet = await self.get_or_create_wallet(user_id)
                wallet.debit_coins(effective_price)
                await self._wallet_repo.update(wallet)
            else:
                vault = await self.get_or_create_vault(user_id)
                vault.debit(effective_price)
                await self._vault_repo.update_wallet(vault)

                entry = VaultLedger.create(
                    vault_id=vault.id,
                    user_id=user_id,
                    delta=-effective_price,
                    reason=VaultLedgerReason.SPENDING,
                    description=f"Purchased offer: {offer.title}",
                    balance_after=vault.star_dust_balance,
                    reference_id=txn.id,
                )
                await self._vault_repo.save_ledger_entry(entry)

            # Grant all bundled items
            for item_id in offer.bundled_item_ids:
                item = await self._store_item_repo.find_by_id(item_id)
                if item is not None:
                    owned = await self._grant_item(user_id, item)

                    if item.item_type == ItemType.PHOENIX_FEATHER:
                        feather = PhoenixFeather.purchase(
                            user_id=user_id,
                            price_stardust=0,  # Bundled — no individual cost
                        )
                        await self._feather_repo.save(feather)

            txn.complete()
            await self._txn_repo.update(txn)

            await self._notification_service.send(
                user_id=user_id,
                notification_type=NotificationType.LIFE_SHIELD_EARNED,
                title="Bundle Purchased!",
                body=f"You bought the '{offer.title}' bundle for {effective_price} {offer.price.currency.value}.",
                data={"offer_id": str(offer.id), "transaction_id": str(txn.id)},
            )

            return PurchaseResult(
                success=True,
                transaction_id=txn.id,
            )

        except Exception as e:
            txn.fail(str(e))
            await self._txn_repo.update(txn)
            return PurchaseResult(success=False, reason=str(e))

    # ═════════════════════════════════════════════════════════════════
    #  4. REFUND
    # ═════════════════════════════════════════════════════════════════

    async def refund_transaction(
        self, transaction_id: uuid.UUID
    ) -> Transaction:
        """
        Refund a completed transaction. Credits back the currency spent.
        """
        txn = await self._txn_repo.find_by_id(transaction_id)
        if txn is None:
            raise TransactionNotFoundException()

        if txn.status != TransactionStatus.COMPLETED:
            raise TransactionNotRefundableException()

        # Credit back
        if txn.currency == CurrencyType.COINS:
            wallet = await self._wallet_repo.find_by_user(txn.user_id)
            if wallet is None:
                raise WalletNotFoundException()
            wallet.refund_coins(txn.amount_paid)
            await self._wallet_repo.update(wallet)
        else:
            vault = await self._vault_repo.find_wallet_by_user(txn.user_id)
            if vault is None:
                raise WalletNotFoundException(detail="Vault not found.")
            vault.refund(txn.amount_paid)
            await self._vault_repo.update_wallet(vault)

            entry = VaultLedger.create(
                vault_id=vault.id,
                user_id=txn.user_id,
                delta=txn.amount_paid,
                reason=VaultLedgerReason.REFUND,
                description=f"Refund: {txn.item_name}",
                balance_after=vault.star_dust_balance,
                reference_id=txn.id,
            )
            await self._vault_repo.save_ledger_entry(entry)

        txn.refund()
        await self._txn_repo.update(txn)

        return txn

    # ═════════════════════════════════════════════════════════════════
    #  5. PHOENIX FEATHER DYNAMIC PRICING
    # ═════════════════════════════════════════════════════════════════

    async def get_feather_price(
        self, user_id: uuid.UUID, deaths_in_window: int = 0
    ) -> int:
        """
        Dynamic feather pricing per PRD §5.1:
          - Base: ~$0.99 (99 Star Dust)
          - Each death within 30-day window: +$1.00 (100 Star Dust)
          - Cap: ~$4.99 (499 Star Dust)
        """
        price = FEATHER_BASE_PRICE_STARDUST + (
            deaths_in_window * FEATHER_PRICE_INCREMENT
        )
        return min(price, FEATHER_MAX_PRICE_STARDUST)

    # ═════════════════════════════════════════════════════════════════
    #  6. STORE CATALOG MANAGEMENT (admin)
    # ═════════════════════════════════════════════════════════════════

    async def add_store_item(self, item: StoreItem) -> StoreItem:
        """Add a new item to the store catalog (admin operation)."""
        if await self._store_item_repo.exists_by_name(item.name):
            raise DuplicateStoreItemException()
        await self._store_item_repo.save(item)
        return item

    async def get_store_catalog(
        self, player_level: int = 0
    ) -> dict[str, list[StoreItem]]:
        """
        Get the full store catalog grouped by category.
        Only includes items unlocked for the player's level.
        """
        all_items = await self._store_item_repo.find_all_active()
        catalog: dict[str, list[StoreItem]] = {}
        for item in all_items:
            if item.is_unlocked(player_level):
                cat = item.category.value
                catalog.setdefault(cat, []).append(item)
        return catalog

    async def get_active_offers(
        self, player_level: int = 0
    ) -> list[SpecialOffer]:
        """Get all currently available special offers."""
        return await self._offer_repo.find_available_for_level(player_level)

    # ═════════════════════════════════════════════════════════════════
    #  7. INVENTORY QUERIES
    # ═════════════════════════════════════════════════════════════════

    async def get_inventory(self, user_id: uuid.UUID) -> list[OwnedItem]:
        """Get all items in a user's inventory."""
        return await self._inventory_repo.find_by_user(user_id)

    async def get_transaction_history(
        self, user_id: uuid.UUID, limit: int = 50
    ) -> list[Transaction]:
        """Get a user's purchase history."""
        return await self._txn_repo.find_by_user(user_id, limit)

    async def get_vault_ledger(
        self, user_id: uuid.UUID, limit: int = 50
    ) -> list[VaultLedger]:
        """Get the immutable Star Dust transaction ledger."""
        return await self._vault_repo.get_ledger_for_user(user_id, limit)

    # ═════════════════════════════════════════════════════════════════
    #  8. DEATH PENALTY (called by Reaper)
    # ═════════════════════════════════════════════════════════════════

    async def apply_death_coin_penalty(self, user_id: uuid.UUID) -> int:
        """
        On character death, 25% of coins are lost.
        Star Dust is unaffected (persists in Vault).
        Returns the amount of coins lost.
        """
        wallet = await self._wallet_repo.find_by_user(user_id)
        if wallet is None:
            return 0
        loss = wallet.apply_death_penalty()
        await self._wallet_repo.update(wallet)
        return loss

    # ── Internal helpers ────────────────────────────────────────────

    async def _grant_item(
        self, user_id: uuid.UUID, item: StoreItem
    ) -> OwnedItem:
        """
        Add an item to the user's inventory. If the item is consumable
        and already owned, increment quantity instead of creating a new record.
        """
        is_consumable = item.item_type in (
            ItemType.PHOENIX_FEATHER,
            ItemType.BANDAGE,
            ItemType.FOOD,
        )

        existing = await self._inventory_repo.find_by_user_and_item(
            user_id, item.id
        )

        if existing is not None and is_consumable:
            existing.add_quantity(1)
            await self._inventory_repo.update(existing)
            return existing

        owned = OwnedItem.create(
            user_id=user_id,
            item_id=item.id,
            item_name=item.name,
            item_type=item.item_type,
            is_consumable=is_consumable,
        )
        await self._inventory_repo.save(owned)
        return owned
