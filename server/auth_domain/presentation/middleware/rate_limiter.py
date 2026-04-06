"""
In-memory sliding window rate limiter middleware.

Security: prevents brute-force attacks on login, registration, and
password reset endpoints. In production, use Redis for distributed limiting.

Follows the Middleware / Chain of Responsibility pattern.
"""

from __future__ import annotations

import time
from collections import defaultdict
from typing import Callable

from fastapi import Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Configurable per-path rate limits with sliding window.

    Usage:
        app.add_middleware(
            RateLimitMiddleware,
            rate_limits={
                "/auth/login": (5, 60),       # 5 requests per 60 seconds
                "/auth/register": (3, 60),
                "/auth/password-reset/request": (3, 300),
            },
            default_limit=(60, 60),            # 60 req/min for everything else
        )
    """

    def __init__(
        self,
        app,
        rate_limits: dict[str, tuple[int, int]] | None = None,
        default_limit: tuple[int, int] = (60, 60),
    ) -> None:
        super().__init__(app)
        self._rate_limits = rate_limits or {}
        self._default_limit = default_limit
        # {(ip, path): [timestamps]}
        self._requests: dict[tuple[str, str], list[float]] = defaultdict(list)

    def _get_client_ip(self, request: Request) -> str:
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    def _get_limit(self, path: str) -> tuple[int, int]:
        for prefix, limit in self._rate_limits.items():
            if path.startswith(prefix):
                return limit
        return self._default_limit

    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> Response:
        ip = self._get_client_ip(request)
        path = request.url.path
        max_requests, window_seconds = self._get_limit(path)

        key = (ip, path)
        now = time.time()
        cutoff = now - window_seconds

        # Slide the window
        self._requests[key] = [
            ts for ts in self._requests[key] if ts > cutoff
        ]

        if len(self._requests[key]) >= max_requests:
            retry_after = int(self._requests[key][0] + window_seconds - now) + 1
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"detail": "Too many requests. Please try again later."},
                headers={"Retry-After": str(retry_after)},
            )

        self._requests[key].append(now)
        return await call_next(request)
