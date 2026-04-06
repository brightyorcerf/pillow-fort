"""SQLAlchemy ORM model for the vault_wallets table."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Integer, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from auth_domain.infrastructure.persistence.models.base import Base


class VaultWalletModel(Base):
    __tablename__ = "vault_wallets"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), unique=True, nullable=False, index=True
    )
    star_dust_balance: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_star_dust_purchased: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_star_dust_spent: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    def __repr__(self) -> str:
        return f"<VaultWalletModel user_id={self.user_id} star_dust={self.star_dust_balance}>"
