"""Repository interface for VaultWallet and VaultLedger (Star Dust)."""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from typing import Optional

from character_domain.domain.entities.vault_ledger import VaultLedger
from character_domain.domain.entities.vault_wallet import VaultWallet


class IVaultRepository(ABC):

    @abstractmethod
    async def save_wallet(self, wallet: VaultWallet) -> None: ...

    @abstractmethod
    async def update_wallet(self, wallet: VaultWallet) -> None: ...

    @abstractmethod
    async def find_wallet_by_user(self, user_id: uuid.UUID) -> Optional[VaultWallet]: ...

    @abstractmethod
    async def find_wallet_by_id(self, vault_id: uuid.UUID) -> Optional[VaultWallet]: ...

    @abstractmethod
    async def save_ledger_entry(self, entry: VaultLedger) -> None: ...

    @abstractmethod
    async def get_ledger_for_user(
        self, user_id: uuid.UUID, limit: int = 50
    ) -> list[VaultLedger]: ...

    @abstractmethod
    async def get_ledger_for_vault(
        self, vault_id: uuid.UUID, limit: int = 50
    ) -> list[VaultLedger]: ...
