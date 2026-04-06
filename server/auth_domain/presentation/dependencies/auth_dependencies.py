"""
FastAPI dependency injection for authentication and authorisation.

Uses the Dependency Injection pattern native to FastAPI.
"""

from __future__ import annotations

import uuid
from typing import Callable

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from auth_domain.domain.exceptions import (
    InsufficientPermissionsException,
    InvalidCredentialsException,
    TokenExpiredException,
)
from auth_domain.domain.interfaces.token_service import ITokenService

_bearer_scheme = HTTPBearer(auto_error=True)


def _get_token_service(request: Request) -> ITokenService:
    """Resolve the token service from the app state (set during startup)."""
    return request.app.state.token_service


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
    token_service: ITokenService = Depends(_get_token_service),
) -> dict:
    """
    Dependency that validates the Bearer JWT and returns the token payload.

    Returns dict with keys: sub (user_id), roles, iat, exp, iss, jti.
    """
    try:
        payload = token_service.decode_access_token(credentials.credentials)
    except TokenExpiredException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token has expired.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except InvalidCredentialsException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )

    return payload


def require_roles(*required_roles: str) -> Callable:
    """
    Factory that returns a dependency checking RBAC roles.

    Usage:
        @router.get("/admin", dependencies=[Depends(require_roles("admin"))])
    """

    async def _check(
        current_user: dict = Depends(get_current_user),
    ) -> dict:
        user_roles = set(current_user.get("roles", []))
        if not user_roles.intersection(required_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions.",
            )
        return current_user

    return _check
