"""
Dependency Injection container — Composition Root.

All concrete implementations are wired together here, following the
Composition Root pattern. No other module imports concrete classes
directly — they depend only on interfaces.
"""

from __future__ import annotations

from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from auth_domain.application.use_cases import (
    ConfirmPasswordResetUseCase,
    GetUserProfileUseCase,
    LoginUserUseCase,
    LogoutUseCase,
    OAuthLoginUseCase,
    RefreshTokensUseCase,
    RegisterUserUseCase,
    RequestPasswordResetUseCase,
    VerifyEmailUseCase,
)
from auth_domain.config.settings import Settings
from auth_domain.domain.interfaces import IOAuthProvider
from auth_domain.infrastructure.external import (
    AppleOAuthProvider,
    GoogleOAuthProvider,
    LogEventPublisher,
    SmtpEmailService,
)
from auth_domain.infrastructure.persistence.repositories import (
    SqlAlchemyRefreshTokenRepository,
    SqlAlchemyUserRepository,
)
from auth_domain.infrastructure.security import Argon2PasswordHasher, JWTTokenService


class Container:
    """
    Holds all wired-up dependencies. Created once at application startup.

    Per-request dependencies (those needing an AsyncSession) are built
    via factory methods, since the session is scoped to the request.
    """

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

        # ── Singletons ─────────────────────────────────────────────────
        private_key = Path(settings.jwt_private_key_path).read_text()
        public_key = Path(settings.jwt_public_key_path).read_text()

        self.password_hasher = Argon2PasswordHasher()
        self.token_service = JWTTokenService(
            private_key=private_key,
            public_key=public_key,
            algorithm=settings.jwt_algorithm,
            access_token_ttl_minutes=settings.jwt_access_token_ttl_minutes,
        )
        self.email_service = SmtpEmailService(
            host=settings.smtp_host,
            port=settings.smtp_port,
            username=settings.smtp_username,
            password=settings.smtp_password,
            from_email=settings.smtp_from_email,
            base_url=settings.base_url,
        )
        self.event_publisher = LogEventPublisher()

        # ── OAuth Providers (Strategy pattern registry) ────────────────
        self.oauth_providers: dict[str, IOAuthProvider] = {}
        if settings.google_client_id:
            self.oauth_providers["google"] = GoogleOAuthProvider(
                client_id=settings.google_client_id,
                client_secret=settings.google_client_secret,
            )
        if settings.apple_client_id:
            apple_key = Path(settings.apple_private_key_path).read_text()
            self.oauth_providers["apple"] = AppleOAuthProvider(
                client_id=settings.apple_client_id,
                team_id=settings.apple_team_id,
                key_id=settings.apple_key_id,
                private_key=apple_key,
            )

    # ── Per-request factories ──────────────────────────────────────────

    def register_use_case(self, session: AsyncSession) -> RegisterUserUseCase:
        return RegisterUserUseCase(
            user_repo=SqlAlchemyUserRepository(session),
            password_hasher=self.password_hasher,
            email_service=self.email_service,
            event_publisher=self.event_publisher,
        )

    def login_use_case(self, session: AsyncSession) -> LoginUserUseCase:
        return LoginUserUseCase(
            user_repo=SqlAlchemyUserRepository(session),
            token_service=self.token_service,
            password_hasher=self.password_hasher,
            refresh_token_repo=SqlAlchemyRefreshTokenRepository(session),
            event_publisher=self.event_publisher,
        )

    def refresh_use_case(self, session: AsyncSession) -> RefreshTokensUseCase:
        return RefreshTokensUseCase(
            user_repo=SqlAlchemyUserRepository(session),
            token_service=self.token_service,
            refresh_token_repo=SqlAlchemyRefreshTokenRepository(session),
        )

    def logout_use_case(self, session: AsyncSession) -> LogoutUseCase:
        return LogoutUseCase(
            token_service=self.token_service,
            refresh_token_repo=SqlAlchemyRefreshTokenRepository(session),
        )

    def verify_email_use_case(self, session: AsyncSession) -> VerifyEmailUseCase:
        return VerifyEmailUseCase(
            user_repo=SqlAlchemyUserRepository(session),
            event_publisher=self.event_publisher,
        )

    def request_password_reset_use_case(
        self, session: AsyncSession
    ) -> RequestPasswordResetUseCase:
        return RequestPasswordResetUseCase(
            user_repo=SqlAlchemyUserRepository(session),
            email_service=self.email_service,
        )

    def confirm_password_reset_use_case(
        self, session: AsyncSession
    ) -> ConfirmPasswordResetUseCase:
        return ConfirmPasswordResetUseCase(
            user_repo=SqlAlchemyUserRepository(session),
            password_hasher=self.password_hasher,
            refresh_token_repo=SqlAlchemyRefreshTokenRepository(session),
            event_publisher=self.event_publisher,
        )

    def oauth_login_use_case(self, session: AsyncSession) -> OAuthLoginUseCase:
        return OAuthLoginUseCase(
            user_repo=SqlAlchemyUserRepository(session),
            token_service=self.token_service,
            refresh_token_repo=SqlAlchemyRefreshTokenRepository(session),
            oauth_providers=self.oauth_providers,
        )

    def get_profile_use_case(self, session: AsyncSession) -> GetUserProfileUseCase:
        return GetUserProfileUseCase(
            user_repo=SqlAlchemyUserRepository(session),
        )
