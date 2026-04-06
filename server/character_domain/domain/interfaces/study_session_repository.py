"""Repository interface for StudySession entity."""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from typing import Optional

from character_domain.domain.entities.study_session import StudySession


class IStudySessionRepository(ABC):

    @abstractmethod
    async def find_by_id(self, session_id: uuid.UUID) -> Optional[StudySession]:
        ...

    @abstractmethod
    async def find_active_for_character(
        self, character_id: uuid.UUID
    ) -> Optional[StudySession]:
        """Find an in-progress session."""
        ...

    @abstractmethod
    async def save(self, session: StudySession) -> None:
        ...

    @abstractmethod
    async def update(self, session: StudySession) -> None:
        ...

    @abstractmethod
    async def get_longest_session_minutes(self, character_id: uuid.UUID) -> int:
        """Longest single session ever logged (for PVR ceiling)."""
        ...
