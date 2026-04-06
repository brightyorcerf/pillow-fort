"""SQLAlchemy ORM model for the characters table."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from auth_domain.infrastructure.persistence.models.base import Base


class CharacterModel(Base):
    __tablename__ = "characters"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), unique=True, nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    hp: Mapped[int] = mapped_column(Integer, nullable=False, default=100)
    current_streak: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    longest_streak: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_study_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    life_shields: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    rituals_used: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    ghosting_days: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    has_flow_state_buff: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_permanently_dead: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_in_penance: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    weekly_consistency_multiplier: Mapped[float] = mapped_column(
        Float, nullable=False, default=1.0
    )
    consecutive_below_average_days: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )
