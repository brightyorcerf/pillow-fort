"""Application-layer DTOs for the PurchaseManager domain service endpoints."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# ── Wallet / Vault ────────────────────────────────────────────────────


class BalancesResponse(BaseModel):
    coins: int
    star_dust: int
    total_coins_earned: int
    total_coins_spent: int
    total_star_dust_purchased: int
    total_star_dust_spent: int


class CreditCoinsRequest(BaseModel):
    amount: int = Field(gt=0, description="Number of coins to credit")
    reason: str = Field(default="Study reward", max_length=128)


class CreditStarDustRequest(BaseModel):
    amount: int = Field(gt=0, description="Star Dust to credit")
    reason: str = Field(default="PURCHASE", max_length=32)
    description: str = Field(default="Star Dust top-up", max_length=256)


class WalletResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    coin_balance: int
    total_coins_earned: int
    total_coins_spent: int
    created_at: datetime
    updated_at: datetime


class VaultWalletResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    star_dust_balance: int
    total_star_dust_purchased: int
    total_star_dust_spent: int
    created_at: datetime
    updated_at: datetime


# ── Store Catalog ─────────────────────────────────────────────────────


class PriceResponse(BaseModel):
    currency: str
    original_amount: int
    discounted_amount: Optional[int] = None
    effective_amount: int
    is_on_sale: bool
    discount_percent: int


class StoreItemResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: str
    item_type: str
    category: str
    price: PriceResponse
    required_level: int
    is_active: bool
    max_per_user: Optional[int] = None
    image_url: Optional[str] = None
    metadata: dict = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime


class StoreCatalogResponse(BaseModel):
    categories: dict[str, list[StoreItemResponse]]
    total_items: int


class AddStoreItemRequest(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    description: str = Field(min_length=1, max_length=512)
    item_type: str = Field(description="One of: PHOENIX_FEATHER, LIFE_INSURANCE, ACCESSORY, BACKGROUND_THEME, PET, FOOD, BANDAGE")
    category: str = Field(description="One of: DAILY_NEEDS, PETS, ACCESSORIES, LEGENDARY_GEAR, REVIVAL, SPECIAL_OFFERS")
    currency: str = Field(description="COINS or STAR_DUST")
    price_amount: int = Field(gt=0)
    discounted_amount: Optional[int] = Field(default=None, ge=0)
    required_level: int = Field(default=0, ge=0)
    max_per_user: Optional[int] = Field(default=None, ge=1)
    image_url: Optional[str] = None
    metadata: dict = Field(default_factory=dict)


# ── Special Offers ────────────────────────────────────────────────────


class SpecialOfferResponse(BaseModel):
    id: uuid.UUID
    title: str
    description: str
    bundled_item_ids: list[uuid.UUID]
    price: PriceResponse
    required_level: int
    is_active: bool
    expires_at: Optional[datetime] = None
    image_url: Optional[str] = None
    discount_percent: int
    created_at: datetime


# ── Purchase ──────────────────────────────────────────────────────────


class PurchaseItemRequest(BaseModel):
    item_id: uuid.UUID
    player_level: int = Field(default=0, ge=0)


class PurchaseOfferRequest(BaseModel):
    offer_id: uuid.UUID
    player_level: int = Field(default=0, ge=0)


class PurchaseResultResponse(BaseModel):
    success: bool
    transaction_id: Optional[uuid.UUID] = None
    owned_item_id: Optional[uuid.UUID] = None
    reason: Optional[str] = None


# ── Transaction ───────────────────────────────────────────────────────


class TransactionResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    item_id: Optional[uuid.UUID] = None
    offer_id: Optional[uuid.UUID] = None
    item_name: str
    currency: str
    amount_paid: int
    status: str
    fail_reason: Optional[str] = None
    refunded_at: Optional[datetime] = None
    created_at: datetime


class TransactionHistoryResponse(BaseModel):
    user_id: uuid.UUID
    transactions: list[TransactionResponse]
    total: int


# ── Vault Ledger ──────────────────────────────────────────────────────


class VaultLedgerEntryResponse(BaseModel):
    id: uuid.UUID
    vault_id: uuid.UUID
    user_id: uuid.UUID
    delta: int
    reason: str
    description: str
    balance_after: int
    reference_id: Optional[uuid.UUID] = None
    created_at: datetime


class VaultLedgerResponse(BaseModel):
    user_id: uuid.UUID
    entries: list[VaultLedgerEntryResponse]
    total: int


# ── Inventory ─────────────────────────────────────────────────────────


class OwnedItemResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    item_id: uuid.UUID
    item_name: str
    item_type: str
    quantity: int
    is_consumable: bool
    is_equipped: bool
    acquired_at: datetime


class InventoryResponse(BaseModel):
    user_id: uuid.UUID
    items: list[OwnedItemResponse]
    total: int


# ── Feather Pricing ──────────────────────────────────────────────────


class FeatherPriceResponse(BaseModel):
    price_star_dust: int
    deaths_in_window: int
    base_price: int
    max_price: int


# ── Death Penalty ────────────────────────────────────────────────────


class DeathPenaltyRequest(BaseModel):
    user_id: uuid.UUID


class DeathPenaltyResponse(BaseModel):
    user_id: uuid.UUID
    coins_lost: int


# ── Shop Composite DTOs ───────────────────────────────────────────────

from typing import Literal

class ShopCatalogResponse(BaseModel):
    items: StoreCatalogResponse
    offers: list[SpecialOfferResponse]


class ShopMeResponse(BaseModel):
    balances: BalancesResponse
    inventory: InventoryResponse


class ShopPurchaseRequest(BaseModel):
    type: Literal["item", "offer"] = Field(..., description="Type of purchase")
    target_id: uuid.UUID = Field(..., description="ID of the item or offer")
    player_level: int = Field(default=0, ge=0)


class ShopTransactionsResponse(BaseModel):
    transactions: TransactionHistoryResponse
    vault_ledger: VaultLedgerResponse
