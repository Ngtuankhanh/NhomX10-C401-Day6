from typing import Dict, Optional
from app.application.interfaces import ISessionRepository
from app.domain.entities import SessionState


class MemorySessionRepository(ISessionRepository):
    def __init__(self):
        self._sessions: Dict[str, SessionState] = {}

    def get_session(self, session_id: str) -> Optional[SessionState]:
        return self._sessions.get(session_id)

    def save_session(self, session: SessionState) -> None:
        self._sessions[session.session_id] = session

    def delete_session(self, session_id: str) -> None:
        if session_id in self._sessions:
            del self._sessions[session_id]
