"""
Auth API routes — thin controllers that delegate to use cases.

Each route does only:
  1. Extract HTTP-specific data (headers, IP, etc.)
  2. Call the appropriate use case
  3. Map domain exceptions to HTTP responses

This keeps controllers lean (SRP) and testable.
"""

from __future__ import annotations

import secrets
import uuid

from fastapi import APIRouter, Depends, HTTPException, Request, status

from auth_domain.application.dtos import (
    LoginRequest,
    OAuthCallbackRequest,
    PasswordResetConfirm,
    PasswordResetRequest,
    RefreshTokenRequest,
    RegisterRequest,
    TokenResponse,
    UserProfileResponse,
    VerifyEmailRequest,
)

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
from auth_domain.domain.exceptions import (
    AccountLockedException,
    AuthDomainException,
    EmailAlreadyVerifiedException,
    InsufficientPermissionsException,
    InvalidCredentialsException,
    OAuthException,
    TokenExpiredException,
    TokenRevokedException,
    UserAlreadyExistsException,
    UserNotFoundException,
)
from auth_domain.presentation.dependencies import get_current_user
from auth_domain.presentation.dependencies.use_case_dependencies import (
    get_confirm_password_reset_use_case,
    get_login_use_case,
    get_logout_use_case,
    get_oauth_login_use_case,
    get_profile_use_case,
    get_refresh_use_case,
    get_register_use_case,
    get_request_password_reset_use_case,
    get_verify_email_use_case,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])

# ── Exception → HTTP status mapping ───────────────────────────────────

_EXCEPTION_STATUS_MAP: dict[type, int] = {
    InvalidCredentialsException: status.HTTP_401_UNAUTHORIZED,
    TokenExpiredException: status.HTTP_401_UNAUTHORIZED,
    TokenRevokedException: status.HTTP_401_UNAUTHORIZED,
    AccountLockedException: status.HTTP_403_FORBIDDEN,
    InsufficientPermissionsException: status.HTTP_403_FORBIDDEN,
    UserNotFoundException: status.HTTP_404_NOT_FOUND,
    UserAlreadyExistsException: status.HTTP_409_CONFLICT,
    EmailAlreadyVerifiedException: status.HTTP_409_CONFLICT,
    OAuthException: status.HTTP_400_BAD_REQUEST,
}


def _handle_domain_error(exc: AuthDomainException) -> HTTPException:
    code = _EXCEPTION_STATUS_MAP.get(type(exc), status.HTTP_400_BAD_REQUEST)
    return HTTPException(status_code=code, detail=exc.detail)


def _client_ip(request: Request) -> str | None:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else None


# ── Routes ─────────────────────────────────────────────────────────────


@router.post(
    "/register",
    response_model=UserProfileResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    body: RegisterRequest,
    use_case: RegisterUserUseCase = Depends(get_register_use_case),
):
    try:
        return await use_case.execute(body)
    except AuthDomainException as e:
        raise _handle_domain_error(e)


@router.post("/login", response_model=TokenResponse)
async def login(
    body: LoginRequest,
    request: Request,
    use_case: LoginUserUseCase = Depends(get_login_use_case),
):
    try:
        return await use_case.execute(body, ip_address=_client_ip(request))
    except AuthDomainException as e:
        raise _handle_domain_error(e)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_tokens(
    body: RefreshTokenRequest,
    request: Request,
    use_case: RefreshTokensUseCase = Depends(get_refresh_use_case),
):
    try:
        return await use_case.execute(body, ip_address=_client_ip(request))
    except AuthDomainException as e:
        raise _handle_domain_error(e)


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    body: RefreshTokenRequest,
    use_case: LogoutUseCase = Depends(get_logout_use_case),
):
    try:
        return await use_case.execute(body.refresh_token)
    except AuthDomainException as e:
        raise _handle_domain_error(e)


@router.post("/verify-email")
async def verify_email(
    body: VerifyEmailRequest,
    request: Request,
    use_case: VerifyEmailUseCase = Depends(get_verify_email_use_case),
):
    """
    In a real app the verification link encodes user_id + token.
    Here we accept user_id as a query param for simplicity.
    """
    user_id = request.query_params.get("user_id")
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id query param required.")
    try:
        return await use_case.execute_with_user_id(user_id, body.token)
    except AuthDomainException as e:
        raise _handle_domain_error(e)


@router.post("/password-reset/request")
async def request_password_reset(
    body: PasswordResetRequest,
    use_case: RequestPasswordResetUseCase = Depends(get_request_password_reset_use_case),
):
    return await use_case.execute(body)


@router.post("/password-reset/confirm")
async def confirm_password_reset(
    body: PasswordResetConfirm,
    request: Request,
    use_case: ConfirmPasswordResetUseCase = Depends(get_confirm_password_reset_use_case),
):
    user_id = request.query_params.get("user_id")
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id query param required.")
    try:
        return await use_case.execute(uuid.UUID(user_id), body)
    except AuthDomainException as e:
        raise _handle_domain_error(e)


# ── OAuth routes ───────────────────────────────────────────────────────


@router.get("/oauth/{provider}/authorize")
async def oauth_authorize(
    provider: str,
    request: Request,
    use_case: OAuthLoginUseCase = Depends(get_oauth_login_use_case),
):
    """Redirect user to the OAuth provider's authorization page."""
    try:
        state = secrets.token_urlsafe(32)
        # In production, store state in a short-lived cache (Redis) for CSRF verification
        redirect_uri = str(request.url_for("oauth_callback", provider=provider))
        url = await use_case.get_authorization_url(provider, state, redirect_uri)
        return {"authorization_url": url, "state": state}
    except AuthDomainException as e:
        raise _handle_domain_error(e)


@router.post("/oauth/{provider}/callback", response_model=TokenResponse)
async def oauth_callback(
    provider: str,
    body: OAuthCallbackRequest,
    request: Request,
    use_case: OAuthLoginUseCase = Depends(get_oauth_login_use_case),
):
    try:
        redirect_uri = str(request.url_for("oauth_callback", provider=provider))
        return await use_case.execute(
            request=OAuthCallbackRequest(
                code=body.code,
                state=body.state,
                provider=provider,
            ),
            redirect_uri=redirect_uri,
            ip_address=_client_ip(request),
        )
    except AuthDomainException as e:
        raise _handle_domain_error(e)


# ── Protected route example ────────────────────────────────────────────

@router.get("/me", response_model=UserProfileResponse)
async def get_my_profile(
    current_user: dict = Depends(get_current_user),
    use_case: GetUserProfileUseCase = Depends(get_profile_use_case),
):
    try:
        return await use_case.execute(uuid.UUID(current_user["sub"]))
    except AuthDomainException as e:
        raise _handle_domain_error(e)
