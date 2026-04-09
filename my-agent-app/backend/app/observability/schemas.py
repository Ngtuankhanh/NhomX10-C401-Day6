from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, Field


def utc_now_iso() -> str:
    return (
        datetime.now(timezone.utc)
        .isoformat(timespec="milliseconds")
        .replace("+00:00", "Z")
    )


class TokenUsage(BaseModel):
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0

    def add(self, other: "TokenUsage") -> None:
        self.input_tokens += other.input_tokens
        self.output_tokens += other.output_tokens
        self.total_tokens += other.total_tokens

    @classmethod
    def from_mapping(cls, payload: dict[str, Any] | None) -> "TokenUsage":
        if not payload:
            return cls()

        input_tokens = payload.get("input_tokens", payload.get("prompt_tokens", 0)) or 0
        output_tokens = (
            payload.get("output_tokens", payload.get("completion_tokens", 0)) or 0
        )
        total_tokens = payload.get("total_tokens") or (input_tokens + output_tokens)
        return cls(
            input_tokens=int(input_tokens),
            output_tokens=int(output_tokens),
            total_tokens=int(total_tokens),
        )


class PromptMessageTrace(BaseModel):
    role: str
    content: str


class ToolCallTrace(BaseModel):
    name: str
    input_payload: Any | None = None
    output_payload: str | None = None
    status: Literal["success", "error"] = "success"
    started_at: str
    ended_at: str | None = None
    latency_ms: int | None = None
    error: str | None = None


class ModelCallTrace(BaseModel):
    run_id: str
    model_name: str | None = None
    system_prompt_name: str | None = None
    system_prompt_version: str | None = None
    prompt_messages: list[PromptMessageTrace] = Field(default_factory=list)
    completion: str | None = None
    finish_reason: str | None = None
    tool_calls: list[dict[str, Any]] = Field(default_factory=list)
    token_usage: TokenUsage = Field(default_factory=TokenUsage)
    started_at: str
    ended_at: str | None = None
    latency_ms: int | None = None
    error: str | None = None


class AgentRequestTrace(BaseModel):
    trace_id: str = Field(default_factory=lambda: str(uuid4()))
    session_id: str
    raw_prompt: str
    system_prompt_version: str
    system_prompt_versions_seen: dict[str, str] = Field(default_factory=dict)
    model_completion: str | None = None
    final_output: str | None = None
    latency_ms: int | None = None
    token_usage: TokenUsage = Field(default_factory=TokenUsage)
    tool_calls: list[ToolCallTrace] = Field(default_factory=list)
    model_calls: list[ModelCallTrace] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    conversation_state_before: str | None = None
    conversation_state_after: str | None = None
    started_at: str = Field(default_factory=utc_now_iso)
    ended_at: str | None = None


class JudgeReferenceData(BaseModel):
    ground_truth_facts: list[str] = Field(default_factory=list)
    required_constraints: list[str] = Field(default_factory=list)
    required_output_format: list[str] = Field(default_factory=list)
    expected_answer: str | None = None
    forbidden_claims: list[str] = Field(default_factory=list)
    task_success_criteria: list[str] = Field(default_factory=list)
    notes: str | None = None


class JudgeMetricEvaluation(BaseModel):
    score: int = Field(ge=1, le=5)
    passed: bool
    rationale: str
    evidence: list[str] = Field(default_factory=list)


class JudgeEvaluationResult(BaseModel):
    evaluation_id: str = Field(default_factory=lambda: str(uuid4()))
    trace_id: str
    session_id: str
    judge_model: str
    judge_prompt_version: str
    reference_data: JudgeReferenceData
    insufficient_reference_data: bool = False
    grounding_factuality: JudgeMetricEvaluation
    constraint_compliance: JudgeMetricEvaluation
    instruction_following: JudgeMetricEvaluation
    overall_score: float
    overall_verdict: Literal["pass", "needs_review", "fail"]
    blocking_issues: list[str] = Field(default_factory=list)
    improvement_actions: list[str] = Field(default_factory=list)
    created_at: str = Field(default_factory=utc_now_iso)
