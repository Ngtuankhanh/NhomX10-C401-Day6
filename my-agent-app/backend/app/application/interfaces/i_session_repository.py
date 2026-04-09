from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from app.domain.entities import SessionState


class ISessionRepository(ABC):
    """Port for session persistence."""

    @abstractmethod
    def get_session(self, session_id: str) -> Optional[SessionState]:
        ...

    @abstractmethod
    def save_session(self, session: SessionState) -> None:
        ...

    @abstractmethod
    def delete_session(self, session_id: str) -> None:
        ...
