"""SQLAlchemy implementation of ITransactionRepository."""

from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from character_domain.domain.entities.transaction import Transaction
from character_domain.domain.interfaces.transaction_repository import ITransactionRepository
from character_domain.domain.value_objects.purchase_enums import CurrencyType, TransactionStatus
from character_domain.infrastructure.persistence.models.transaction_model import TransactionModel


class SqlAlchemyTransactionRepository(ITransactionRepository):

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @staticmethod
    def _to_entity(m: TransactionModel) -> Transaction:
        return Transaction(
            id=m.id,
            user_id=m.user_id,
            item_id=m.item_id,
            offer_id=m.offer_id,
            item_name=m.item_name,
            currency=CurrencyType(m.currency),
            amount_paid=m.amount_paid,
            status=TransactionStatus(m.status),
            fail_reason=m.fail_reason,
            refunded_at=m.refunded_at,
            created_at=m.created_at,
        )

    @staticmethod
    def _to_model(e: Transaction) -> TransactionModel:
        return TransactionModel(
            id=e.id,
            user_id=e.user_id,
            item_id=e.item_id,
            offer_id=e.offer_id,
            item_name=e.item_name,
            currency=e.currency.value,
            amount_paid=e.amount_paid,
            status=e.status.value,
            fail_reason=e.fail_reason,
            refunded_at=e.refunded_at,
            created_at=e.created_at,
        )

    async def save(self, txn: Transaction) -> None:
        self._session.add(self._to_model(txn))
        await self._session.flush()

    async def update(self, txn: Transaction) -> None:
        m = await self._session.get(TransactionModel, txn.id)
        if m is None:
            raise ValueError(f"Transaction {txn.id} not found.")
        m.item_id = txn.item_id
        m.offer_id = txn.offer_id
        m.item_name = txn.item_name
        m.currency = txn.currency.value
        m.amount_paid = txn.amount_paid
        m.status = txn.status.value
        m.fail_reason = txn.fail_reason
        m.refunded_at = txn.refunded_at
        await self._session.flush()

    async def find_by_id(self, txn_id: uuid.UUID) -> Optional[Transaction]:
        m = await self._session.get(TransactionModel, txn_id)
        return self._to_entity(m) if m else None

    async def find_by_user(
        self, user_id: uuid.UUID, limit: int = 50
    ) -> list[Transaction]:
        stmt = (
            select(TransactionModel)
            .where(TransactionModel.user_id == user_id)
            .order_by(TransactionModel.created_at.desc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]

    async def count_completed_for_item(
        self, user_id: uuid.UUID, item_id: uuid.UUID
    ) -> int:
        stmt = (
            select(func.count())
            .select_from(TransactionModel)
            .where(
                TransactionModel.user_id == user_id,
                TransactionModel.item_id == item_id,
                TransactionModel.status == TransactionStatus.COMPLETED.value,
            )
        )
        result = await self._session.execute(stmt)
        return result.scalar_one()
