"""OAuth provider enum value object."""

from enum import Enum


class OAuthProvider(str, Enum):
    GOOGLE = "google"
    APPLE = "apple"
