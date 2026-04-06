"""
SMTP email service implementation.

In production you'd swap this for an async provider (SendGrid, SES, etc.)
via the IEmailService interface — no change to domain or application layer.
"""

from __future__ import annotations

import aiosmtplib
from email.mime.text import MIMEText

from auth_domain.domain.interfaces.email_service import IEmailService


class SmtpEmailService(IEmailService):

    def __init__(
        self,
        host: str,
        port: int,
        username: str,
        password: str,
        from_email: str,
        use_tls: bool = True,
        base_url: str = "https://yourgame.com",
    ) -> None:
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._from_email = from_email
        self._use_tls = use_tls
        self._base_url = base_url

    async def _send(self, to: str, subject: str, body: str) -> None:
        message = MIMEText(body, "html")
        message["From"] = self._from_email
        message["To"] = to
        message["Subject"] = subject

        await aiosmtplib.send(
            message,
            hostname=self._host,
            port=self._port,
            username=self._username,
            password=self._password,
            use_tls=self._use_tls,
        )

    async def send_verification_email(self, to: str, token: str) -> None:
        link = f"{self._base_url}/auth/verify-email?token={token}"
        body = f"""
        <h2>Verify your email</h2>
        <p>Click the link below to verify your email address:</p>
        <a href="{link}">{link}</a>
        <p>This link expires in 24 hours.</p>
        """
        await self._send(to, "Verify your email address", body)

    async def send_password_reset_email(self, to: str, token: str) -> None:
        link = f"{self._base_url}/auth/reset-password?token={token}"
        body = f"""
        <h2>Reset your password</h2>
        <p>Click the link below to reset your password:</p>
        <a href="{link}">{link}</a>
        <p>This link expires in 1 hour. If you didn't request this, ignore this email.</p>
        """
        await self._send(to, "Password reset request", body)
