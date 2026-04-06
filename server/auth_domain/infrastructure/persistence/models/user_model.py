"""
SQLAlchemy ORM model for the users table.

This is an *infrastructure concern* — the domain entity User is mapped
to/from this model by the repository, keeping persistence details out
of the domain.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    DateTime,
    Index,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(
        String(320), unique=True, nullable=False, index=True
    )
    hashed_password: Mapped[str | None] = mapped_column(Text, nullable=True)
    username: Mapped[str] = mapped_column(String(64), nullable=False)
    roles: Mapped[list[str]] = mapped_column(
        ARRAY(String), nullable=False, server_default="{player}"
    )
    is_email_verified: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True
    )
    failed_login_attempts: Mapped[int] = mapped_column(
        nullable=False, default=0
    )
    locked_until: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    oauth_provider: Mapped[str | None] = mapped_column(
        String(32), nullable=True
    )
    oauth_provider_id: Mapped[str | None] = mapped_column(
        String(256), nullable=True
    )
    email_verification_token: Mapped[str | None] = mapped_column(
        String(256), nullable=True
    )
    password_reset_token: Mapped[str | None] = mapped_column(
        String(256), nullable=True
    )
    password_reset_expires: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    __table_args__ = (
        Index("ix_users_oauth", "oauth_provider", "oauth_provider_id", unique=True),
    )
