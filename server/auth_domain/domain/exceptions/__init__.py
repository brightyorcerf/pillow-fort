"""
Domain-specific exceptions.

Each exception maps to a single business rule violation so upper layers
can translate them to appropriate HTTP status codes.
"""


class AuthDomainException(Exception):
    """Base for all auth-domain errors."""


class InvalidCredentialsException(AuthDomainException):
    """Wrong email/password or invalid token."""

    def __init__(self, detail: str = "Invalid credentials."):
        super().__init__(detail)
        self.detail = detail


class AccountLockedException(AuthDomainException):
    """Account temporarily or permanently locked."""

    def __init__(self, detail: str = "Account is locked."):
        super().__init__(detail)
        self.detail = detail


class EmailAlreadyVerifiedException(AuthDomainException):
    def __init__(self):
        super().__init__("Email is already verified.")
        self.detail = "Email is already verified."


class UserAlreadyExistsException(AuthDomainException):
    def __init__(self, detail: str = "A user with this email already exists."):
        super().__init__(detail)
        self.detail = detail


class UserNotFoundException(AuthDomainException):
    def __init__(self, detail: str = "User not found."):
        super().__init__(detail)
        self.detail = detail


class TokenExpiredException(AuthDomainException):
    def __init__(self, detail: str = "Token has expired."):
        super().__init__(detail)
        self.detail = detail


class TokenRevokedException(AuthDomainException):
    def __init__(self, detail: str = "Token has been revoked."):
        super().__init__(detail)
        self.detail = detail


class InsufficientPermissionsException(AuthDomainException):
    def __init__(self, detail: str = "Insufficient permissions."):
        super().__init__(detail)
        self.detail = detail


class OAuthException(AuthDomainException):
    def __init__(self, detail: str = "OAuth authentication failed."):
        super().__init__(detail)
        self.detail = detail
