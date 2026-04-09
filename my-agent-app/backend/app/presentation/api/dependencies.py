"""Dependency injection container for the presentation layer.

All infrastructure singletons are constructed here and injected into
:class:`~app.application.use_cases.chat_handler.AgentAService`.

This is the **only place** where concrete infrastructure classes are
imported — keeping the application and domain layers free of
infrastructure concerns.
"""

from __future__ import annotations


from app.application.use_cases.chat_handler import AgentAService
from app.config import settings
from app.infrastructure.ai_services.judge_service import LLMJudgeService
from app.infrastructure.repositories.booking_repo import MockBookingRepository
from app.infrastructure.ai_services.agents.specialist_agent import SpecialistAgent
from app.observability.trace_store import AsyncJsonlTraceStore
from app.infrastructure.repositories.csv_data_repo import (
    DataLoader,
    CSVDataRepository,
    KG_PATH,
)
from app.infrastructure.repositories.memory_session_repo import MemorySessionRepository

# ------------------------------------------------------------------
# Singletons — constructed once at startup
# ------------------------------------------------------------------

_session_repo = MemorySessionRepository()
_data_repo = CSVDataRepository()
_booking_repo = MockBookingRepository()
_trace_store = AsyncJsonlTraceStore(settings.observability_dir)

# SpecialistAgent (Agent B) receives its data via constructor injection.
_triage_service = SpecialistAgent(
    specialties=DataLoader.load_specialties(),
    kg_path=KG_PATH,
)
_judge_service = LLMJudgeService(_trace_store)

_chat_agent_service = AgentAService(
    session_repo=_session_repo,
    data_repo=_data_repo,
    booking_repo=_booking_repo,
    triage_service=_triage_service,
    trace_store=_trace_store,
)


def get_chat_service() -> AgentAService:
    """FastAPI dependency that returns the singleton AgentAService."""
    return _chat_agent_service


def get_trace_store() -> AsyncJsonlTraceStore:
    return _trace_store


def get_judge_service() -> LLMJudgeService:
    return _judge_service
