from __future__ import annotations

import json
import time
from contextvars import ContextVar, Token
from dataclasses import dataclass
from typing import Any
from uuid import UUID

from langchain_core.callbacks.base import BaseCallbackHandler
from langchain_core.messages import BaseMessage
from langchain_core.outputs import LLMResult

from app.infrastructure.ai_services.agents.prompts import resolve_prompt_version
from app.observability.schemas import (
    AgentRequestTrace,
    ModelCallTrace,
    PromptMessageTrace,
    TokenUsage,
    ToolCallTrace,
    utc_now_iso,
)

_CURRENT_TRACE_COLLECTOR: ContextVar["TraceCollector | None"] = ContextVar(
    "current_trace_collector",
    default=None,
)


def get_current_trace_collector() -> "TraceCollector | None":
    return _CURRENT_TRACE_COLLECTOR.get()


def set_current_trace_collector(collector: "TraceCollector") -> Token:
    return _CURRENT_TRACE_COLLECTOR.set(collector)


def reset_current_trace_collector(token: Token) -> None:
    _CURRENT_TRACE_COLLECTOR.reset(token)


def _truncate_text(value: str | None, limit: int = 1500) -> str | None:
    if value is None:
        return None
    if len(value) <= limit:
        return value
    return f"{value[:limit]}..."


def _extract_text_content(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        chunks: list[str] = []
        for item in content:
            if isinstance(item, str):
                chunks.append(item)
                continue
            if isinstance(item, dict):
                text = item.get("text")
                if text:
                    chunks.append(str(text))
                    continue
            chunks.append(json.dumps(item, ensure_ascii=False))
        return "\n".join(chunks)
    if content is None:
        return ""
    return str(content)


def _serialize_messages(messages: list[BaseMessage]) -> list[PromptMessageTrace]:
    return [
        PromptMessageTrace(
            role=getattr(message, "type", message.__class__.__name__.lower()),
            content=_truncate_text(_extract_text_content(message.content), 4000) or "",
        )
        for message in messages
    ]


def _extract_model_name(serialized: dict[str, Any] | None, kwargs: dict[str, Any]) -> str | None:
    if isinstance(serialized, dict):
        serialized_kwargs = serialized.get("kwargs")
        if isinstance(serialized_kwargs, dict):
            for key in ("model", "model_name"):
                value = serialized_kwargs.get(key)
                if value:
                    return str(value)
        for key in ("name", "id"):
            value = serialized.get(key)
            if isinstance(value, str) and value:
                return value
    invocation_params = kwargs.get("invocation_params")
    if isinstance(invocation_params, dict):
        for key in ("model", "model_name"):
            value = invocation_params.get(key)
            if value:
                return str(value)
    return None


def _extract_token_usage(response: LLMResult, message: Any | None) -> TokenUsage:
    if message is not None:
        usage_metadata = getattr(message, "usage_metadata", None)
        if isinstance(usage_metadata, dict):
            return TokenUsage.from_mapping(usage_metadata)
        response_metadata = getattr(message, "response_metadata", None)
        if isinstance(response_metadata, dict):
            token_usage = response_metadata.get("token_usage")
            if isinstance(token_usage, dict):
                return TokenUsage.from_mapping(token_usage)

    llm_output = getattr(response, "llm_output", None)
    if isinstance(llm_output, dict):
        token_usage = llm_output.get("token_usage")
        if isinstance(token_usage, dict):
            return TokenUsage.from_mapping(token_usage)

    return TokenUsage()


def _extract_finish_reason(response: LLMResult, message: Any | None) -> str | None:
    if message is not None:
        response_metadata = getattr(message, "response_metadata", None)
        if isinstance(response_metadata, dict):
            finish_reason = response_metadata.get("finish_reason")
            if finish_reason:
                return str(finish_reason)
    llm_output = getattr(response, "llm_output", None)
    if isinstance(llm_output, dict):
        finish_reason = llm_output.get("finish_reason")
        if finish_reason:
            return str(finish_reason)
    return None


def _extract_tool_calls(message: Any | None) -> list[dict[str, Any]]:
    if message is None:
        return []
    tool_calls = getattr(message, "tool_calls", None)
    if isinstance(tool_calls, list):
        return tool_calls
    additional_kwargs = getattr(message, "additional_kwargs", None)
    if isinstance(additional_kwargs, dict):
        raw_tool_calls = additional_kwargs.get("tool_calls")
        if isinstance(raw_tool_calls, list):
            return raw_tool_calls
    return []


class StructuredTraceCallbackHandler(BaseCallbackHandler):
    raise_error = False

    def __init__(self, collector: "TraceCollector") -> None:
        self.collector = collector

    def on_chat_model_start(
        self,
        serialized: dict[str, Any],
        messages: list[list[BaseMessage]] | list[BaseMessage],
        *,
        run_id: UUID,
        **kwargs: Any,
    ) -> Any:
        batches = messages if messages and isinstance(messages[0], list) else [messages]
        first_batch = batches[0] if batches else []
        prompt_messages = _serialize_messages(first_batch)
        system_prompt = next(
            (item.content for item in prompt_messages if item.role == "system"),
            None,
        )
        prompt_name, prompt_version = resolve_prompt_version(system_prompt)
        self.collector.start_model_call(
            run_id=str(run_id),
            model_name=_extract_model_name(serialized, kwargs),
            system_prompt_name=prompt_name,
            system_prompt_version=prompt_version,
            prompt_messages=prompt_messages,
        )

    def on_llm_end(self, response: LLMResult, *, run_id: UUID, **kwargs: Any) -> Any:
        generation = None
        generations = getattr(response, "generations", None) or []
        if generations:
            first_bucket = generations[0]
            if first_bucket:
                generation = first_bucket[0]

        message = getattr(generation, "message", None)
        completion = None
        if message is not None:
            completion = _extract_text_content(getattr(message, "content", None))

        self.collector.end_model_call(
            run_id=str(run_id),
            completion=_truncate_text(completion, 4000),
            finish_reason=_extract_finish_reason(response, message),
            token_usage=_extract_token_usage(response, message),
            tool_calls=_extract_tool_calls(message),
        )

    def on_llm_error(self, error: BaseException, *, run_id: UUID, **kwargs: Any) -> Any:
        self.collector.fail_model_call(str(run_id), str(error))

    def on_tool_start(
        self,
        serialized: dict[str, Any],
        input_str: str,
        *,
        run_id: UUID,
        inputs: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> Any:
        tool_name = "unknown_tool"
        if isinstance(serialized, dict):
            tool_name = (
                serialized.get("name")
                or serialized.get("id")
                or serialized.get("lc")
                or tool_name
            )
        self.collector.start_tool_call(
            run_id=str(run_id),
            name=str(tool_name),
            input_payload=inputs if inputs is not None else _truncate_text(input_str, 2000),
        )

    def on_tool_end(self, output: Any, *, run_id: UUID, **kwargs: Any) -> Any:
        try:
            rendered_output = (
                output
                if isinstance(output, str)
                else json.dumps(output, ensure_ascii=False)
            )
        except TypeError:
            rendered_output = str(output)
        self.collector.end_tool_call(
            run_id=str(run_id),
            output_payload=_truncate_text(rendered_output, 2000),
        )

    def on_tool_error(self, error: BaseException, *, run_id: UUID, **kwargs: Any) -> Any:
        self.collector.fail_tool_call(str(run_id), str(error))


@dataclass
class AgentRunResult:
    content: str
    trace: AgentRequestTrace


class TraceCollector:
    def __init__(
        self,
        session_id: str,
        raw_prompt: str,
        system_prompt_version: str,
        conversation_state_before: str | None = None,
    ) -> None:
        self.trace = AgentRequestTrace(
            session_id=session_id,
            raw_prompt=raw_prompt,
            system_prompt_version=system_prompt_version,
            conversation_state_before=conversation_state_before,
            system_prompt_versions_seen={"main_orchestrator": system_prompt_version},
        )
        self.callback_handler = StructuredTraceCallbackHandler(self)
        self._started_at_monotonic = time.perf_counter()
        self._active_model_calls: dict[str, ModelCallTrace] = {}
        self._active_model_started: dict[str, float] = {}
        self._active_tool_calls: dict[str, ToolCallTrace] = {}
        self._active_tool_started: dict[str, float] = {}

    def note_prompt_version(self, prompt_name: str, version: str) -> None:
        self.trace.system_prompt_versions_seen[prompt_name] = version

    def start_model_call(
        self,
        run_id: str,
        model_name: str | None,
        system_prompt_name: str | None,
        system_prompt_version: str | None,
        prompt_messages: list[PromptMessageTrace],
    ) -> None:
        if system_prompt_name and system_prompt_version:
            self.note_prompt_version(system_prompt_name, system_prompt_version)
        self._active_model_calls[run_id] = ModelCallTrace(
            run_id=run_id,
            model_name=model_name,
            system_prompt_name=system_prompt_name,
            system_prompt_version=system_prompt_version,
            prompt_messages=prompt_messages,
            started_at=utc_now_iso(),
        )
        self._active_model_started[run_id] = time.perf_counter()

    def end_model_call(
        self,
        run_id: str,
        completion: str | None,
        finish_reason: str | None,
        token_usage: TokenUsage,
        tool_calls: list[dict[str, Any]],
    ) -> None:
        call = self._active_model_calls.pop(run_id, None)
        started_at = self._active_model_started.pop(run_id, None)
        if call is None:
            return

        call.completion = completion
        call.finish_reason = finish_reason
        call.token_usage = token_usage
        call.tool_calls = tool_calls
        call.ended_at = utc_now_iso()
        if started_at is not None:
            call.latency_ms = int((time.perf_counter() - started_at) * 1000)
        self.trace.model_calls.append(call)
        self.trace.token_usage.add(token_usage)
        if completion:
            self.trace.model_completion = completion

    def fail_model_call(self, run_id: str, error: str) -> None:
        call = self._active_model_calls.pop(run_id, None)
        started_at = self._active_model_started.pop(run_id, None)
        if call is None:
            return

        call.error = error
        call.ended_at = utc_now_iso()
        if started_at is not None:
            call.latency_ms = int((time.perf_counter() - started_at) * 1000)
        self.trace.model_calls.append(call)
        self.trace.errors.append(error)

    def start_tool_call(self, run_id: str, name: str, input_payload: Any | None) -> None:
        self._active_tool_calls[run_id] = ToolCallTrace(
            name=name,
            input_payload=input_payload,
            started_at=utc_now_iso(),
        )
        self._active_tool_started[run_id] = time.perf_counter()

    def end_tool_call(self, run_id: str, output_payload: str | None) -> None:
        call = self._active_tool_calls.pop(run_id, None)
        started_at = self._active_tool_started.pop(run_id, None)
        if call is None:
            return
        call.output_payload = output_payload
        call.ended_at = utc_now_iso()
        if started_at is not None:
            call.latency_ms = int((time.perf_counter() - started_at) * 1000)
        self.trace.tool_calls.append(call)

    def fail_tool_call(self, run_id: str, error: str) -> None:
        call = self._active_tool_calls.pop(run_id, None)
        started_at = self._active_tool_started.pop(run_id, None)
        if call is None:
            return
        call.status = "error"
        call.error = error
        call.ended_at = utc_now_iso()
        if started_at is not None:
            call.latency_ms = int((time.perf_counter() - started_at) * 1000)
        self.trace.tool_calls.append(call)
        self.trace.errors.append(error)

    def record_error(self, message: str) -> None:
        self.trace.errors.append(message)

    def finalize(
        self,
        final_output: str,
        conversation_state_after: str | None = None,
    ) -> AgentRequestTrace:
        self.trace.final_output = final_output
        self.trace.model_completion = self.trace.model_completion or final_output
        self.trace.conversation_state_after = conversation_state_after
        self.trace.ended_at = utc_now_iso()
        self.trace.latency_ms = int((time.perf_counter() - self._started_at_monotonic) * 1000)
        return self.trace
