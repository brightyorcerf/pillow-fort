"""
SQLAlchemy implementation of IUserRepository.

Maps between the domain User entity and the UserModel ORM object,
keeping the domain free of persistence concerns (DIP).
"""

from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth_domain.domain.entities.user import User
from auth_domain.domain.interfaces.user_repository import IUserRepository
from auth_domain.domain.value_objects import Email, HashedPassword, OAuthProvider
from auth_domain.infrastructure.persistence.models.user_model import UserModel


class SqlAlchemyUserRepository(IUserRepository):

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # ── Mapping helpers ────────────────────────────────────────────────

    @staticmethod
    def _to_entity(model: UserModel) -> User:
        return User(
            id=model.id,
            email=Email(model.email),
            hashed_password=(
                HashedPassword(model.hashed_password)
                if model.hashed_password
                else None
            ),
            username=model.username,
            roles=list(model.roles),
            is_email_verified=model.is_email_verified,
            is_active=model.is_active,
            failed_login_attempts=model.failed_login_attempts,
            locked_until=model.locked_until,
            oauth_provider=(
                OAuthProvider(model.oauth_provider) if model.oauth_provider else None
            ),
            oauth_provider_id=model.oauth_provider_id,
            email_verification_token=model.email_verification_token,
            password_reset_token=model.password_reset_token,
            password_reset_expires=model.password_reset_expires,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def _to_model(entity: User) -> UserModel:
        return UserModel(
            id=entity.id,
            email=str(entity.email),
            hashed_password=entity.hashed_password.value if entity.hashed_password else None,
            username=entity.username,
            roles=entity.roles,
            is_email_verified=entity.is_email_verified,
            is_active=entity.is_active,
            failed_login_attempts=entity.failed_login_attempts,
            locked_until=entity.locked_until,
            oauth_provider=entity.oauth_provider.value if entity.oauth_provider else None,
            oauth_provider_id=entity.oauth_provider_id,
            email_verification_token=entity.email_verification_token,
            password_reset_token=entity.password_reset_token,
            password_reset_expires=entity.password_reset_expires,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    # ── Interface implementation ───────────────────────────────────────

    async def find_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        result = await self._session.get(UserModel, user_id)
        return self._to_entity(result) if result else None

    async def find_by_email(self, email: Email) -> Optional[User]:
        stmt = select(UserModel).where(UserModel.email == str(email))
        result = await self._session.execute(stmt)
        row = result.scalar_one_or_none()
        return self._to_entity(row) if row else None

    async def find_by_oauth(
        self, provider: str, provider_id: str
    ) -> Optional[User]:
        stmt = select(UserModel).where(
            UserModel.oauth_provider == provider,
            UserModel.oauth_provider_id == provider_id,
        )
        result = await self._session.execute(stmt)
        row = result.scalar_one_or_none()
        return self._to_entity(row) if row else None

    async def save(self, user: User) -> None:
        model = self._to_model(user)
        self._session.add(model)
        await self._session.flush()

    async def update(self, user: User) -> None:
        model = await self._session.get(UserModel, user.id)
        if model is None:
            raise ValueError(f"User {user.id} not found for update.")
        model.email = str(user.email)
        model.hashed_password = user.hashed_password.value if user.hashed_password else None
        model.username = user.username
        model.roles = user.roles
        model.is_email_verified = user.is_email_verified
        model.is_active = user.is_active
        model.failed_login_attempts = user.failed_login_attempts
        model.locked_until = user.locked_until
        model.oauth_provider = user.oauth_provider.value if user.oauth_provider else None
        model.oauth_provider_id = user.oauth_provider_id
        model.email_verification_token = user.email_verification_token
        model.password_reset_token = user.password_reset_token
        model.password_reset_expires = user.password_reset_expires
        model.updated_at = user.updated_at
        await self._session.flush()

    async def exists_by_email(self, email: Email) -> bool:
        stmt = select(UserModel.id).where(UserModel.email == str(email)).limit(1)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None
