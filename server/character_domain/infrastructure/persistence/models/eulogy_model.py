"""SQLAlchemy ORM model for the eulogies table."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from auth_domain.infrastructure.persistence.models.base import Base


class EulogyModel(Base):
    __tablename__ = "eulogies"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    character_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, index=True
    )
    death_record_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, unique=True
    )
    character_name: Mapped[str] = mapped_column(String(64), nullable=False)
    total_study_hours: Mapped[float] = mapped_column(Float, nullable=False)
    longest_streak: Mapped[int] = mapped_column(Integer, nullable=False)
    rank_achieved: Mapped[str] = mapped_column(String(32), nullable=False)
    life_shields_earned: Mapped[int] = mapped_column(Integer, nullable=False)
    rituals_completed: Mapped[int] = mapped_column(Integer, nullable=False)
    total_covenants_signed: Mapped[int] = mapped_column(Integer, nullable=False)
    total_covenants_kept: Mapped[int] = mapped_column(Integer, nullable=False)
    born_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    died_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
