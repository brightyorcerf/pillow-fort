"""
Apple Sign In OAuth provider — Strategy pattern implementation.

Apple uses a slightly different flow: the ID token is returned directly
after code exchange, and user info is only available on first login.
"""

from __future__ import annotations

import jwt
import httpx

from auth_domain.domain.exceptions import OAuthException
from auth_domain.domain.interfaces.oauth_provider import IOAuthProvider, OAuthUserInfo


class AppleOAuthProvider(IOAuthProvider):

    AUTHORIZATION_URL = "https://appleid.apple.com/auth/authorize"
    TOKEN_URL = "https://appleid.apple.com/auth/token"
    KEYS_URL = "https://appleid.apple.com/auth/keys"

    def __init__(
        self,
        client_id: str,          # Service ID
        team_id: str,
        key_id: str,
        private_key: str,        # .p8 file contents
    ) -> None:
        self._client_id = client_id
        self._team_id = team_id
        self._key_id = key_id
        self._private_key = private_key

    @property
    def provider_name(self) -> str:
        return "apple"

    def _generate_client_secret(self) -> str:
        """Apple requires a JWT as the client_secret, signed with your .p8 key."""
        import time

        now = int(time.time())
        payload = {
            "iss": self._team_id,
            "iat": now,
            "exp": now + 86400 * 180,  # 6 months max
            "aud": "https://appleid.apple.com",
            "sub": self._client_id,
        }
        return jwt.encode(
            payload,
            self._private_key,
            algorithm="ES256",
            headers={"kid": self._key_id},
        )

    async def get_authorization_url(self, state: str, redirect_uri: str) -> str:
        params = {
            "client_id": self._client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": "name email",
            "state": state,
            "response_mode": "form_post",
        }
        query = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{self.AUTHORIZATION_URL}?{query}"

    async def exchange_code(self, code: str, redirect_uri: str) -> OAuthUserInfo:
        client_secret = self._generate_client_secret()
        async with httpx.AsyncClient(timeout=10) as client:
            token_resp = await client.post(
                self.TOKEN_URL,
                data={
                    "code": code,
                    "client_id": self._client_id,
                    "client_secret": client_secret,
                    "redirect_uri": redirect_uri,
                    "grant_type": "authorization_code",
                },
            )
            if token_resp.status_code != 200:
                raise OAuthException(f"Apple token exchange failed: {token_resp.text}")

            tokens = token_resp.json()
            id_token = tokens.get("id_token")
            if not id_token:
                raise OAuthException("No id_token in Apple response.")

            # Fetch Apple's public keys and decode the id_token
            keys_resp = await client.get(self.KEYS_URL)
            apple_keys = keys_resp.json()

            # Decode without full verification first to get the header
            unverified = jwt.get_unverified_header(id_token)
            kid = unverified.get("kid")

            # Find the matching key
            matching_key = None
            for key in apple_keys.get("keys", []):
                if key["kid"] == kid:
                    matching_key = jwt.algorithms.RSAAlgorithm.from_jwk(key)
                    break

            if matching_key is None:
                raise OAuthException("Could not find matching Apple public key.")

            claims = jwt.decode(
                id_token,
                matching_key,
                algorithms=["RS256"],
                audience=self._client_id,
                issuer="https://appleid.apple.com",
            )

            return OAuthUserInfo(
                provider_id=claims["sub"],
                email=claims.get("email", ""),
                name=claims.get("email", "").split("@")[0],
                email_verified=claims.get("email_verified", "true") == "true",
            )
