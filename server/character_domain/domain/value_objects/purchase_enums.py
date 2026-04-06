"""
Purchase system enumerations.

PRD §3.3 — Dual-economy model (Coins vs. Star Dust).
PRD §5.1 — Monetization & dynamic pricing.
"""

from __future__ import annotations

from enum import Enum


class CurrencyType(str, Enum):
    """Two-currency economy."""
    COINS = "coins"             # Earned via study — non-persistent across death
    STAR_DUST = "star_dust"     # Purchased with real money — persists in Vault


class ItemType(str, Enum):
    """What a store item actually is."""
    PHOENIX_FEATHER = "phoenix_feather"
    LIFE_INSURANCE = "life_insurance"       # Subscription-based shield
    ACCESSORY = "accessory"                 # Cosmetic accessories
    BACKGROUND_THEME = "background_theme"   # Legendary gear / themes
    PET = "pet"                             # Alien cat, penguin, etc.
    FOOD = "food"                           # Ice cream, pizza for the child
    BANDAGE = "bandage"                     # HP restore consumable


class CategoryType(str, Enum):
    """Store categories for browsing."""
    DAILY_NEEDS = "daily_needs"             # Food, bandages (coin-priced)
    PETS = "pets"                           # Companion creatures
    ACCESSORIES = "accessories"             # Cosmetic gear
    LEGENDARY_GEAR = "legendary_gear"       # Premium themes & backgrounds
    REVIVAL = "revival"                     # Phoenix Feathers, life insurance
    SPECIAL_OFFERS = "special_offers"       # Bundles & time-limited deals


class TransactionStatus(str, Enum):
    """Purchase transaction lifecycle."""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class VaultLedgerReason(str, Enum):
    """Reason for a vault (Star Dust) credit/debit."""
    PURCHASE = "purchase"           # Real-money top-up
    SPENDING = "spending"           # Spent on premium item
    REBIRTH_REBATE = "rebirth_rebate"  # Partial refund on character rebirth
    REFUND = "refund"               # Admin/support refund
    GIFT = "gift"                   # Promotional gift
    EXPIRED = "expired"             # Expiry deduction (if applicable)
