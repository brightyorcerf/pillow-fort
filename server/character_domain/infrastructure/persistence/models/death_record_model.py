"""SQLAlchemy ORM model for the death_records table."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from auth_domain.infrastructure.persistence.models.base import Base


class DeathRecordModel(Base):
    __tablename__ = "death_records"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    character_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, index=True
    )
    cause: Mapped[str] = mapped_column(String(64), nullable=False)
    hp_at_death: Mapped[int] = mapped_column(Integer, nullable=False)
    total_hours_in_life: Mapped[float] = mapped_column(Float, nullable=False)
    consecutive_ghost_days_at_death: Mapped[int] = mapped_column(Integer, nullable=False)
    rituals_used_at_death: Mapped[int] = mapped_column(Integer, nullable=False)
    longest_streak_at_death: Mapped[int] = mapped_column(Integer, nullable=False)
    eulogy_generated: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_permanent: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    promises_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    died_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
