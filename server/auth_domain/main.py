"""
Application entry point — FastAPI application factory.

Wires together both bounded contexts (auth + character), the middleware
stack, and routes. Each domain has its own DI container following the
Composition Root pattern.

Use cases are NOT eagerly instantiated per request.  Instead, each route
declares its own ``Depends()`` chain that lazily constructs only the use
case it needs, with a request-scoped DB session provided via ``yield``.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from auth_domain.config.settings import Settings
from auth_domain.config.container import Container as AuthContainer
from auth_domain.infrastructure.persistence.database import (
    get_session_factory,
    init_engine,
    shutdown_engine,
)
from auth_domain.presentation.middleware import (
    RateLimitMiddleware,
    SecurityHeadersMiddleware,
    configure_cors,
)
from auth_domain.presentation.routes import auth_router
from character_domain.config.container import CharacterContainer
from character_domain.presentation.routes import character_router, internal_router, purchase_router

logger = logging.getLogger("app")


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # Startup
        logger.info("Initialising database engine…")
        init_engine(settings.database_url, echo=settings.debug)

        auth_container = AuthContainer(settings)
        char_container = CharacterContainer(
            event_publisher=auth_container.event_publisher,
        )

        # Store singletons on app state for dependency injection
        app.state.auth_container = auth_container
        app.state.char_container = char_container
        app.state.token_service = auth_container.token_service
        app.state.session_factory = get_session_factory()

        yield

        # Shutdown
        await shutdown_engine()
        logger.info("Database engine shut down.")

    app = FastAPI(
        title="Productivity App — Gamified Study Companion",
        version="1.0.0",
        description=(
            "Backend API for the gamified productivity app. "
            "Four bounded contexts: auth (registration, JWT, OAuth), "
            "character (Mini-Me lifecycle, covenants, sessions, rituals), "
            "Anubis (the single authority over all HP changes), "
            "Reaper (the single authority over death and all revival paths), "
            "and PurchaseManager (the single authority over all purchases and currency)."
        ),
        lifespan=lifespan,
    )

    # ── Middleware stack (order matters — outermost first) ──────────────
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(
        RateLimitMiddleware,
        rate_limits={
            "/auth/login": (5, 60),
            "/auth/register": (3, 60),
            "/auth/password-reset/request": (3, 300),
            "/characters": (30, 60),
            "/characters/me/sessions": (10, 60),
            "/characters/me/revival": (20, 60),
            "/internal/cron/daily": (1, 60),
            "/shop/me/purchase": (10, 60),
            "/shop/me": (30, 60),
            "/shop/catalog": (30, 60),
            "/shop/me/transactions": (30, 60),
            "/shop/admin/items": (5, 60),
            "/shop/admin/refund": (5, 60),
            "/shop/internal/death-penalty": (3, 60),
        },
        default_limit=(60, 60),
    )
    configure_cors(app, settings.allowed_origins)

    # ── Routes ─────────────────────────────────────────────────────────
    app.include_router(auth_router, prefix="/api/v1")
    app.include_router(character_router, prefix="/api/v1")
    app.include_router(internal_router, prefix="/api/v1")
    app.include_router(purchase_router, prefix="/api/v1")

    return app


# For `uvicorn auth_domain.main:app`
app = create_app()
