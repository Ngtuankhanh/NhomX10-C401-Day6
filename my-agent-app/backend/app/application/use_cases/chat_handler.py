from __future__ import annotations
from dataclasses import asdict
from uuid import uuid4
from typing import Any

from app.application.interfaces import (
    ISessionRepository,
    IDataRepository,
    IBookingRepository,
    ITriageService,
)
from app.domain.entities import SessionState, ChatMessage, StatusCode
from app.infrastructure.ai_services.agents.agent import run_agent


def booking_status_label(code: StatusCode) -> str:
    mapping = {
        "typing": "Đang chuẩn bị phản hồi...",
        "analyzing_symptoms": "Đang phân tích triệu chứng...",
        "finding_doctors": "Đang tìm bác sĩ...",
        "loading_slots": "Đang kiểm tra lịch trống...",
        "submitting_booking": "Đang gửi yêu cầu...",
        "waiting_for_otp": "Đang chờ mã OTP...",
        "confirming_booking": "Đang xác nhận...",
        "recovering_from_error": "Đang thử lại...",
        "idle": "Sẵn sàng",
    }
    return mapping.get(code, "Sẵn sàng")


class AgentAService:
    """Orchestrator Service - Cầu nối giữa API và Agent A (LangGraph).

    Đã lược bỏ toàn bộ logic cứng (if/else state machine) để chuyển sang
    kiến trúc Agentic hoàn toàn.
    """

    def __init__(
        self,
        session_repo: ISessionRepository,
        data_repo: IDataRepository,
        booking_repo: IBookingRepository,
        triage_service: ITriageService,
    ) -> None:
        self.session_repo = session_repo
        self.data_repo = data_repo
        self.booking_repo = booking_repo
        self.triage_service = triage_service

    def create_session(self) -> dict[str, Any]:
        session = SessionState(session_id=str(uuid4()))
        self.session_repo.save_session(session)

        # Agent A sẽ xử lý lời chào ban đầu thông qua run_agent hoặc trả về mặc định
        welcome_msg = "Xin chào, tôi là trợ lý Vinmec. Bạn gặp vấn đề sức khỏe gì?"
        session.messages.append(ChatMessage(role="assistant", content=welcome_msg))
        self.session_repo.save_session(session)

        return self._respond(
            session, welcome_msg, replies=["Đau đầu", "Đau bụng", "Ho kéo dài"]
        )

    def send_user_message(self, session_id: str, message: str) -> dict[str, Any]:
        session = self.session_repo.get_session(session_id) or SessionState(
            session_id=session_id
        )

        msg_text = message.strip()
        session.messages.append(ChatMessage(role="user", content=msg_text))

        # Gọi Agent A (Orchestrator) với session_id làm thread_id
        agent_response = run_agent(msg_text, thread_id=session_id)

        self.session_repo.save_session(session)
        return self._respond(session, agent_response)

    def _respond(
        self,
        session: SessionState,
        content: str,
        replies: list[str] | None = None,
        status: StatusCode = "idle",
    ) -> dict[str, Any]:
        session.quick_replies = replies or []
        session.current_status = status
        msg = ChatMessage(role="assistant", content=content)
        session.messages.append(msg)

        # Cập nhật trạng thái vào repo
        self.session_repo.save_session(session)

        return {
            "session_id": session.session_id,
            "assistant_message": asdict(msg),
            "conversation_state": session.conversation_state,
            "status": {"code": status, "label": booking_status_label(status)},
            "quick_replies": session.quick_replies,
            "snapshot": asdict(session),
        }
