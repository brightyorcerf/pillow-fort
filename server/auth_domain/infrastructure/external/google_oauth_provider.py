"""
Google OAuth 2.0 provider — Strategy pattern implementation.

Follows the Authorization Code Flow with PKCE recommended by Google.
"""

from __future__ import annotations

import httpx

from auth_domain.domain.exceptions import OAuthException
from auth_domain.domain.interfaces.oauth_provider import IOAuthProvider, OAuthUserInfo


class GoogleOAuthProvider(IOAuthProvider):

    AUTHORIZATION_URL = "https://accounts.google.com/o/oauth2/v2/auth"
    TOKEN_URL = "https://oauth2.googleapis.com/token"
    USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"

    def __init__(self, client_id: str, client_secret: str) -> None:
        self._client_id = client_id
        self._client_secret = client_secret

    @property
    def provider_name(self) -> str:
        return "google"

    async def get_authorization_url(self, state: str, redirect_uri: str) -> str:
        params = {
            "client_id": self._client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": "openid email profile",
            "state": state,
            "access_type": "offline",
            "prompt": "consent",
        }
        query = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{self.AUTHORIZATION_URL}?{query}"

    async def exchange_code(self, code: str, redirect_uri: str) -> OAuthUserInfo:
        async with httpx.AsyncClient(timeout=10) as client:
            # Exchange authorisation code for tokens
            token_resp = await client.post(
                self.TOKEN_URL,
                data={
                    "code": code,
                    "client_id": self._client_id,
                    "client_secret": self._client_secret,
                    "redirect_uri": redirect_uri,
                    "grant_type": "authorization_code",
                },
            )
            if token_resp.status_code != 200:
                raise OAuthException(f"Google token exchange failed: {token_resp.text}")

            tokens = token_resp.json()
            access_token = tokens.get("access_token")
            if not access_token:
                raise OAuthException("No access token in Google response.")

            # Fetch user profile
            profile_resp = await client.get(
                self.USERINFO_URL,
                headers={"Authorization": f"Bearer {access_token}"},
            )
            if profile_resp.status_code != 200:
                raise OAuthException("Failed to fetch Google user info.")

            data = profile_resp.json()
            return OAuthUserInfo(
                provider_id=data["sub"],
                email=data["email"],
                name=data.get("name", data["email"].split("@")[0]),
                picture_url=data.get("picture"),
                email_verified=data.get("email_verified", False),
            )
