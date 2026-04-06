"""SQLAlchemy implementation of IVaultRepository."""

from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from character_domain.domain.entities.vault_ledger import VaultLedger
from character_domain.domain.entities.vault_wallet import VaultWallet
from character_domain.domain.interfaces.vault_repository import IVaultRepository
from character_domain.domain.value_objects.purchase_enums import VaultLedgerReason
from character_domain.infrastructure.persistence.models.vault_ledger_model import (
    VaultLedgerModel,
)
from character_domain.infrastructure.persistence.models.vault_wallet_model import (
    VaultWalletModel,
)


class SqlAlchemyVaultRepository(IVaultRepository):

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # ── VaultWallet mapping ────────────────────────────────────────────

    @staticmethod
    def _wallet_to_entity(m: VaultWalletModel) -> VaultWallet:
        return VaultWallet(
            id=m.id,
            user_id=m.user_id,
            star_dust_balance=m.star_dust_balance,
            total_star_dust_purchased=m.total_star_dust_purchased,
            total_star_dust_spent=m.total_star_dust_spent,
            created_at=m.created_at,
            updated_at=m.updated_at,
        )

    @staticmethod
    def _wallet_to_model(e: VaultWallet) -> VaultWalletModel:
        return VaultWalletModel(
            id=e.id,
            user_id=e.user_id,
            star_dust_balance=e.star_dust_balance,
            total_star_dust_purchased=e.total_star_dust_purchased,
            total_star_dust_spent=e.total_star_dust_spent,
            created_at=e.created_at,
            updated_at=e.updated_at,
        )

    # ── VaultLedger mapping ────────────────────────────────────────────

    @staticmethod
    def _ledger_to_entity(m: VaultLedgerModel) -> VaultLedger:
        return VaultLedger(
            id=m.id,
            vault_id=m.vault_id,
            user_id=m.user_id,
            delta=m.delta,
            reason=VaultLedgerReason(m.reason),
            description=m.description,
            balance_after=m.balance_after,
            reference_id=m.reference_id,
            created_at=m.created_at,
        )

    @staticmethod
    def _ledger_to_model(e: VaultLedger) -> VaultLedgerModel:
        return VaultLedgerModel(
            id=e.id,
            vault_id=e.vault_id,
            user_id=e.user_id,
            delta=e.delta,
            reason=e.reason.value,
            description=e.description,
            balance_after=e.balance_after,
            reference_id=e.reference_id,
            created_at=e.created_at,
        )

    # ── Wallet operations ──────────────────────────────────────────────

    async def save_wallet(self, wallet: VaultWallet) -> None:
        self._session.add(self._wallet_to_model(wallet))
        await self._session.flush()

    async def update_wallet(self, wallet: VaultWallet) -> None:
        m = await self._session.get(VaultWalletModel, wallet.id)
        if m is None:
            raise ValueError(f"VaultWallet {wallet.id} not found.")
        m.star_dust_balance = wallet.star_dust_balance
        m.total_star_dust_purchased = wallet.total_star_dust_purchased
        m.total_star_dust_spent = wallet.total_star_dust_spent
        m.updated_at = wallet.updated_at
        await self._session.flush()

    async def find_wallet_by_user(
        self, user_id: uuid.UUID
    ) -> Optional[VaultWallet]:
        stmt = select(VaultWalletModel).where(VaultWalletModel.user_id == user_id)
        result = await self._session.execute(stmt)
        m = result.scalar_one_or_none()
        return self._wallet_to_entity(m) if m else None

    async def find_wallet_by_id(
        self, vault_id: uuid.UUID
    ) -> Optional[VaultWallet]:
        m = await self._session.get(VaultWalletModel, vault_id)
        return self._wallet_to_entity(m) if m else None

    # ── Ledger operations ──────────────────────────────────────────────

    async def save_ledger_entry(self, entry: VaultLedger) -> None:
        self._session.add(self._ledger_to_model(entry))
        await self._session.flush()

    async def get_ledger_for_user(
        self, user_id: uuid.UUID, limit: int = 50
    ) -> list[VaultLedger]:
        stmt = (
            select(VaultLedgerModel)
            .where(VaultLedgerModel.user_id == user_id)
            .order_by(VaultLedgerModel.created_at.desc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return [self._ledger_to_entity(m) for m in result.scalars().all()]

    async def get_ledger_for_vault(
        self, vault_id: uuid.UUID, limit: int = 50
    ) -> list[VaultLedger]:
        stmt = (
            select(VaultLedgerModel)
            .where(VaultLedgerModel.vault_id == vault_id)
            .order_by(VaultLedgerModel.created_at.desc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return [self._ledger_to_entity(m) for m in result.scalars().all()]
