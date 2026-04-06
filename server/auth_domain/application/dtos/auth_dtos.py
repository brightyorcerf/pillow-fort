"""
Application-layer DTOs — Pydantic models for input validation and output serialisation.

These sit between the presentation layer (HTTP) and the use cases.
The domain layer never imports from here (DIP).
"""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    username: str = Field(..., min_length=3, max_length=64)

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter.")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter.")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit.")
        if not any(c in "!@#$%^&*()-_=+[]{}|;:',.<>?/`~" for c in v):
            raise ValueError("Password must contain at least one special character.")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    device_fingerprint: str | None = None


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8, max_length=128)

    @field_validator("new_password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter.")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter.")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit.")
        if not any(c in "!@#$%^&*()-_=+[]{}|;:',.<>?/`~" for c in v):
            raise ValueError("Password must contain at least one special character.")
        return v


class VerifyEmailRequest(BaseModel):
    token: str


class OAuthCallbackRequest(BaseModel):
    code: str
    state: str
    provider: str


class UserProfileResponse(BaseModel):
    id: uuid.UUID
    email: str
    username: str
    roles: list[str]
    is_email_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True
