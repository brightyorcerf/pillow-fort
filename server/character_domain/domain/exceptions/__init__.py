"""Domain exceptions for the character bounded context."""


class CharacterDomainException(Exception):
    """Base for all character-domain errors."""


class CharacterNotFoundException(CharacterDomainException):
    def __init__(self, detail: str = "Character not found."):
        super().__init__(detail)
        self.detail = detail


class CharacterAlreadyDeadException(CharacterDomainException):
    def __init__(self, detail: str = "Character is dead."):
        super().__init__(detail)
        self.detail = detail


class CharacterNotDeadException(CharacterDomainException):
    def __init__(self, detail: str = "Character is not dead — cannot revive."):
        super().__init__(detail)
        self.detail = detail


class CharacterAlreadyExistsException(CharacterDomainException):
    def __init__(self, detail: str = "User already has an active character."):
        super().__init__(detail)
        self.detail = detail


class MaxRitualsExhaustedException(CharacterDomainException):
    def __init__(self):
        detail = (
            "You've used all your revivals. Your journey ends here. Start fresh?"
        )
        super().__init__(detail)
        self.detail = detail


class RitualRequiredException(CharacterDomainException):
    def __init__(self):
        detail = "HP is locked at 0. Complete a re-engagement ritual to recover."
        super().__init__(detail)
        self.detail = detail


class CovenantAlreadyExistsException(CharacterDomainException):
    def __init__(self, detail: str = "A covenant already exists for today."):
        super().__init__(detail)
        self.detail = detail


class CovenantNotSignedException(CharacterDomainException):
    def __init__(self, detail: str = "You must sign your covenant before starting a session."):
        super().__init__(detail)
        self.detail = detail


class GoalBelowMinimumException(CharacterDomainException):
    def __init__(self, minimum: int):
        detail = f"Too short to count. Minimum is {minimum} minutes."
        super().__init__(detail)
        self.detail = detail


class GoalAboveCeilingException(CharacterDomainException):
    def __init__(self, ceiling: int):
        detail = (
            f"Studying beyond {ceiling // 60} hours risks cognitive fatigue "
            f"and may reduce retention. Are you sure?"
        )
        super().__init__(detail)
        self.detail = detail


class SessionAlreadyActiveException(CharacterDomainException):
    def __init__(self, detail: str = "A study session is already in progress."):
        super().__init__(detail)
        self.detail = detail


class SessionNotFoundException(CharacterDomainException):
    def __init__(self, detail: str = "Study session not found."):
        super().__init__(detail)
        self.detail = detail


class NoActiveRitualException(CharacterDomainException):
    def __init__(self, detail: str = "No active ritual in progress."):
        super().__init__(detail)
        self.detail = detail


# ── Reaper exceptions ─────────────────────────────────────────────────


class DeathRecordNotFoundException(CharacterDomainException):
    def __init__(self, detail: str = "Death record not found."):
        super().__init__(detail)
        self.detail = detail


class NoAvailableFeatherException(CharacterDomainException):
    def __init__(self, detail: str = "No Phoenix Feather available."):
        super().__init__(detail)
        self.detail = detail


class PenanceAlreadyActiveException(CharacterDomainException):
    def __init__(self, detail: str = "A penance streak is already in progress."):
        super().__init__(detail)
        self.detail = detail


class NoPenanceActiveException(CharacterDomainException):
    def __init__(self, detail: str = "No active penance streak."):
        super().__init__(detail)
        self.detail = detail


class RevivalNotEligibleException(CharacterDomainException):
    def __init__(self, detail: str = "Character is not eligible for revival."):
        super().__init__(detail)
        self.detail = detail


class PermanentlyDeadException(CharacterDomainException):
    def __init__(self, detail: str = "Character is permanently dead. No revival possible."):
        super().__init__(detail)
        self.detail = detail


# ── Purchase exceptions ──────────────────────────────────────────────


class InsufficientBalanceException(CharacterDomainException):
    def __init__(self, detail: str = "Insufficient balance for this purchase."):
        super().__init__(detail)
        self.detail = detail


class StoreItemNotFoundException(CharacterDomainException):
    def __init__(self, detail: str = "Store item not found."):
        super().__init__(detail)
        self.detail = detail


class StoreItemInactiveException(CharacterDomainException):
    def __init__(self, detail: str = "This item is currently unavailable."):
        super().__init__(detail)
        self.detail = detail


class ItemLevelLockedException(CharacterDomainException):
    def __init__(self, required_level: int):
        detail = f"Item requires level {required_level} to purchase."
        super().__init__(detail)
        self.detail = detail


class ItemPurchaseLimitException(CharacterDomainException):
    def __init__(self, detail: str = "You have reached the purchase limit for this item."):
        super().__init__(detail)
        self.detail = detail


class OfferNotFoundException(CharacterDomainException):
    def __init__(self, detail: str = "Special offer not found."):
        super().__init__(detail)
        self.detail = detail


class OfferExpiredException(CharacterDomainException):
    def __init__(self, detail: str = "This offer has expired."):
        super().__init__(detail)
        self.detail = detail


class TransactionNotFoundException(CharacterDomainException):
    def __init__(self, detail: str = "Transaction not found."):
        super().__init__(detail)
        self.detail = detail


class TransactionNotRefundableException(CharacterDomainException):
    def __init__(self, detail: str = "This transaction cannot be refunded."):
        super().__init__(detail)
        self.detail = detail


class WalletNotFoundException(CharacterDomainException):
    def __init__(self, detail: str = "Wallet not found."):
        super().__init__(detail)
        self.detail = detail


class DuplicateStoreItemException(CharacterDomainException):
    def __init__(self, detail: str = "An item with this name already exists in the catalog."):
        super().__init__(detail)
        self.detail = detail
