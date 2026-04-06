"""SQLAlchemy implementation of IWalletRepository."""

from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from character_domain.domain.entities.wallet import Wallet
from character_domain.domain.interfaces.wallet_repository import IWalletRepository
from character_domain.infrastructure.persistence.models.wallet_model import WalletModel


class SqlAlchemyWalletRepository(IWalletRepository):

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @staticmethod
    def _to_entity(m: WalletModel) -> Wallet:
        return Wallet(
            id=m.id,
            user_id=m.user_id,
            coin_balance=m.coin_balance,
            total_coins_earned=m.total_coins_earned,
            total_coins_spent=m.total_coins_spent,
            created_at=m.created_at,
            updated_at=m.updated_at,
        )

    @staticmethod
    def _to_model(e: Wallet) -> WalletModel:
        return WalletModel(
            id=e.id,
            user_id=e.user_id,
            coin_balance=e.coin_balance,
            total_coins_earned=e.total_coins_earned,
            total_coins_spent=e.total_coins_spent,
            created_at=e.created_at,
            updated_at=e.updated_at,
        )

    async def save(self, wallet: Wallet) -> None:
        self._session.add(self._to_model(wallet))
        await self._session.flush()

    async def update(self, wallet: Wallet) -> None:
        m = await self._session.get(WalletModel, wallet.id)
        if m is None:
            raise ValueError(f"Wallet {wallet.id} not found.")
        m.coin_balance = wallet.coin_balance
        m.total_coins_earned = wallet.total_coins_earned
        m.total_coins_spent = wallet.total_coins_spent
        m.updated_at = wallet.updated_at
        await self._session.flush()

    async def find_by_user(self, user_id: uuid.UUID) -> Optional[Wallet]:
        stmt = select(WalletModel).where(WalletModel.user_id == user_id)
        result = await self._session.execute(stmt)
        m = result.scalar_one_or_none()
        return self._to_entity(m) if m else None

    async def find_by_id(self, wallet_id: uuid.UUID) -> Optional[Wallet]:
        m = await self._session.get(WalletModel, wallet_id)
        return self._to_entity(m) if m else None
