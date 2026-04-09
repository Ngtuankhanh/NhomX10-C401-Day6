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
from app.observability.trace_runtime import (
    AgentRunResult,
    TraceCollector,
    reset_current_trace_collector,
    set_current_trace_collector,
)
from .prompts import Prompts

# ---------------------------------------------------------------------------
# LLM & graph construction
# ---------------------------------------------------------------------------

_llm = ChatOpenAI(
    model=settings.agent_model,
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
    update_booking_field_tool,
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
    update_booking_field_tool,
]

_system_prompt = Prompts.MAIN_ORCHESTRATOR
_fallback_response = (
    "Hiện tại tôi chưa thể xử lý trọn vẹn yêu cầu này. "
    "Bạn hãy mô tả lại triệu chứng hoặc nhu cầu đặt lịch tại Vinmec, tôi sẽ hỗ trợ tiếp."
)


# Khởi tạo bộ nhớ cho Agent
_memory = MemorySaver()

# Tạo agent graph (LangGraph) sử dụng create_react_agent chuẩn
agent_graph = create_react_agent(
    _llm, tools=_tools, prompt=_system_prompt, checkpointer=_memory
)


def run_agent(
    user_input: str,
    thread_id: str = "default-thread",
    conversation_state_before: str | None = None,
) -> AgentRunResult:
    """Invoke the ReAct agent graph synchronously and return the final text.

    Parameters
    ----------
    user_input:
        The raw user message to forward to the agent.
    thread_id:
        The ID for maintaining conversation state.

    Returns
    -------
    AgentRunResult
        The agent's final response text plus a structured execution trace.
    """
    collector = TraceCollector(
        session_id=thread_id,
        raw_prompt=user_input,
        system_prompt_version=Prompts.MAIN_ORCHESTRATOR_VERSION,
        conversation_state_before=conversation_state_before,
    )
    trace_token = set_current_trace_collector(collector)

    try:
        config = {
            "configurable": {"thread_id": thread_id},
            "callbacks": [collector.callback_handler],
        }
        result = agent_graph.invoke(
            {"messages": [HumanMessage(content=user_input)]},
            config=config,
        )

        # Lấy tin nhắn cuối cùng (thường là AIMessage chứa câu trả lời cuối)
        messages = result.get("messages", [])
        if messages:
            last_message = messages[-1]
            # AIMessage có thuộc tính .content
            if hasattr(last_message, "content"):
                content = str(last_message.content).strip()
                return AgentRunResult(
                    content=content, trace=collector.finalize(content)
                )
            # Trường hợp fallback nếu là dict
            if isinstance(last_message, dict):
                content = str(last_message.get("content", "")).strip()
                return AgentRunResult(
                    content=content, trace=collector.finalize(content)
                )

        return AgentRunResult(
            content=_fallback_response,
            trace=collector.finalize(_fallback_response),
        )

    except Exception as e:
        collector.record_error(str(e))
        return AgentRunResult(
            content=_fallback_response,
            trace=collector.finalize(_fallback_response),
        )
    finally:
        reset_current_trace_collector(trace_token)
