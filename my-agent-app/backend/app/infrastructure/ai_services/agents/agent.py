"""LangGraph ReAct agent — infrastructure wrapper for the language model.

This module owns the LangGraph graph construction and exposes a single
:func:`run_agent` coroutine that the application layer can call via the
:class:`~app.application.interfaces.ITriageService` interface (or a dedicated
AI-agent interface if added later).
"""

from __future__ import annotations

from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage
from pydantic import SecretStr

from app.config import settings

# ---------------------------------------------------------------------------
# LLM & graph construction
# ---------------------------------------------------------------------------

_llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0,
    api_key=SecretStr(settings.openai_api_key) if settings.openai_api_key else None,
)

from .specialist_agent import specialist_agent_tool  # noqa: E402
from ..tools.booking_tools import (  # noqa: E402
    list_facilities_tool,
    search_doctors_tool,
    get_doctor_slots_tool,
    get_specialties_tool,
    suggest_hospital_by_location_tool,
    create_booking_tool,
    confirm_booking_tool,
    update_booking_field_tool
)

# Extend this list to add LangChain tools to the ReAct agent
_tools: list = [
    specialist_agent_tool,
    list_facilities_tool,
    search_doctors_tool,
    get_doctor_slots_tool,
    get_specialties_tool,
    suggest_hospital_by_location_tool,
    create_booking_tool,
    confirm_booking_tool,
    update_booking_field_tool
]

# System prompt guiding Agent A behaviors (Spec 0.11)
_system_prompt = (
    "Bạn là Trợ lý Y tế Vinmec (Agent A - Orchestrator). Nhiệm vụ của bạn là hỗ trợ khách hàng từ khi họ mô tả triệu chứng cho đến khi hoàn tất đặt lịch khám.\n\n"
    "Quy trình của bạn:\n"
    "1. Giao tiếp thân thiện với khách hàng.\n"
    "2. Khi khách hàng nói về vấn đề sức khỏe, hãy hỏi xem họ có muốn hỗ trợ tìm chuyên khoa và đặt lịch khám tại Vinmec không.\n"
    "3. Nếu họ đồng ý, hãy hỏi thêm các thông tin cần thiết về triệu chứng (như vị trí, thời gian, mức độ).\n"
    "4. Khi đã đủ thông tin, hãy sử dụng tool 'specialist_agent_tool' để hỏi Agent B về chuyên khoa phù hợp.\n"
    "5. Sau khi có chuyên khoa, hãy tiếp tục hỏi các thông tin còn thiếu để đặt lịch (cơ sở, bác sĩ, thời gian, tên, SĐT).\n"
    "6. QUAN TRỌNG: Ngay khi thu thập hoặc khách hàng xác nhận một thông tin nào đó (Cơ sở, Bác sĩ, Ngày khám, Giờ khám, Họ tên, SĐT...), bạn MUST sử dụng tool 'update_booking_field_tool' để đồng bộ dữ liệu lên giao diện người dùng (Side Panel).\n"
    "7. BƯỚC XÁC NHẬN: Trước khi gọi 'create_booking_tool', bạn phải liệt kê lại toàn bộ thông tin đã thu thập được và hỏi khách hàng: 'Bạn có xác nhận đặt lịch khám với các thông tin trên không?'. Chỉ khi khách hàng đồng ý, bạn mới tiến hành gọi tool 'create_booking_tool'.\n"
    "8. Cuối cùng, thực hiện xác nhận OTP bằng 'confirm_booking_tool' sau khi người dùng cung cấp mã.\n\n"
    "Lưu ý: Luôn chuyên nghiệp, không tự ý chẩn đoán bệnh, chỉ gợi ý dựa trên kết quả từ Expert (Agent B)."
)



# Khởi tạo bộ nhớ cho Agent
_memory = MemorySaver()

# Tạo agent graph (LangGraph) sử dụng create_react_agent chuẩn
agent_graph = create_react_agent(
    _llm, 
    tools=_tools, 
    prompt=_system_prompt,
    checkpointer=_memory
)


def run_agent(user_input: str, thread_id: str = "default-thread") -> str:
    """Invoke the ReAct agent graph synchronously and return the final text.

    Parameters
    ----------
    user_input:
        The raw user message to forward to the agent.
    thread_id:
        The ID for maintaining conversation state.

    Returns
    -------
    str
        The agent's final response text, or an empty string on failure.
    """
    try:
        config = {"configurable": {"thread_id": thread_id}}
        result = agent_graph.invoke({"messages": [HumanMessage(content=user_input)]}, config=config)

        # Lấy tin nhắn cuối cùng (thường là AIMessage chứa câu trả lời cuối)
        messages = result.get("messages", [])
        if messages:
            last_message = messages[-1]
            # AIMessage có thuộc tính .content
            if hasattr(last_message, "content"):
                return str(last_message.content).strip()
            # Trường hợp fallback nếu là dict
            if isinstance(last_message, dict):
                return str(last_message.get("content", "")).strip()

        return ""

    except Exception as e:
        # Nên log lỗi ở production
        print(f"Agent invocation error: {e}")
        return ""
