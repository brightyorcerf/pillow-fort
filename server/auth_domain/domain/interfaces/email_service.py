"""Email service interface for transactional emails."""

from abc import ABC, abstractmethod


class IEmailService(ABC):

    @abstractmethod
    async def send_verification_email(self, to: str, token: str) -> None:
        ...

    @abstractmethod
    async def send_password_reset_email(self, to: str, token: str) -> None:
        ...
