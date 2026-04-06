"""
Application settings — loaded from environment variables.

Uses pydantic-settings for validation and type coercion.
Secrets should NEVER be committed; use .env files or a vault.
"""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # ── Database ───────────────────────────────────────────────────────
    database_url: str

    # ── JWT ────────────────────────────────────────────────────────────
    jwt_private_key_path: str
    jwt_public_key_path: str
    jwt_algorithm: str = "RS256"
    jwt_access_token_ttl_minutes: int = 15

    # ── OAuth — Google ─────────────────────────────────────────────────
    google_client_id: str = ""
    google_client_secret: str = ""

    # ── OAuth — Apple ──────────────────────────────────────────────────
    apple_client_id: str = ""
    apple_team_id: str = ""
    apple_key_id: str = ""
    apple_private_key_path: str = ""

    # ── Email (SMTP) ───────────────────────────────────────────────────
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_from_email: str = "noreply@yourgame.com"

    # ── App ────────────────────────────────────────────────────────────
    base_url: str = "https://yourgame.com"
    allowed_origins: list[str] = ["http://localhost:3000"]
    debug: bool = False
