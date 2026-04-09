from __future__ import annotations

import json
import re
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from pydantic import SecretStr

from app.config import settings
from app.infrastructure.ai_services.agents.prompts import Prompts
from app.observability.schemas import (
    AgentRequestTrace,
    JudgeEvaluationResult,
    JudgeMetricEvaluation,
    JudgeReferenceData,
)
from app.observability.trace_store import AsyncJsonlTraceStore


def parse_json_from_llm(content: str | list[Any]) -> dict[str, Any]:
    text = content if isinstance(content, str) else str(content[0])
    text = text.strip()
    match = re.search(r"```(?:json)?(.*?)```", text, re.DOTALL)
    if match:
        text = match.group(1).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Judge returned invalid JSON: {text}") from exc


def build_judge_payload(
    trace: AgentRequestTrace,
    reference_data: JudgeReferenceData,
) -> dict[str, Any]:
    return {
        "raw_prompt": trace.raw_prompt,
        "candidate_output": trace.final_output,
        "system_prompt_version": trace.system_prompt_version,
        "prompt_versions_seen": trace.system_prompt_versions_seen,
        "tool_calls": [
            {
                "name": tool_call.name,
                "status": tool_call.status,
                "input_payload": tool_call.input_payload,
                "output_payload": tool_call.output_payload,
                "latency_ms": tool_call.latency_ms,
            }
            for tool_call in trace.tool_calls
        ],
        "token_usage": trace.token_usage.model_dump(),
        "reference_data": reference_data.model_dump(mode="json"),
    }


def derive_overall_verdict(
    grounding: JudgeMetricEvaluation,
    constraints: JudgeMetricEvaluation,
    instructions: JudgeMetricEvaluation,
    blocking_issues: list[str],
) -> tuple[float, str]:
    overall_score = round(
        (grounding.score + constraints.score + instructions.score) / 3,
        2,
    )
    min_score = min(grounding.score, constraints.score, instructions.score)

    if blocking_issues or min_score <= 2:
        return overall_score, "fail"
    if min_score == 3:
        return overall_score, "needs_review"
    return overall_score, "pass"


class LLMJudgeService:
    def __init__(self, trace_store: AsyncJsonlTraceStore) -> None:
        self.trace_store = trace_store
        self.model_name = settings.judge_model
        self.llm = ChatOpenAI(
            model=self.model_name,
            temperature=0,
            api_key=SecretStr(settings.openai_api_key) if settings.openai_api_key else None,
        )

    def evaluate_trace(
        self,
        trace_id: str,
        reference_data: JudgeReferenceData,
    ) -> JudgeEvaluationResult:
        if not settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY is required to run the judge pipeline.")

        trace = self.trace_store.get_trace(trace_id)
        if trace is None:
            raise ValueError(f"Trace '{trace_id}' was not found.")

        payload = build_judge_payload(trace, reference_data)
        response = self.llm.invoke(
            [
                SystemMessage(content=Prompts.JUDGE_EVALUATOR),
                HumanMessage(content=json.dumps(payload, ensure_ascii=False, indent=2)),
            ]
        )
        parsed = parse_json_from_llm(response.content)

        grounding = JudgeMetricEvaluation.model_validate(
            parsed.get("grounding_factuality", {})
        )
        constraints = JudgeMetricEvaluation.model_validate(
            parsed.get("constraint_compliance", {})
        )
        instructions = JudgeMetricEvaluation.model_validate(
            parsed.get("instruction_following", {})
        )
        blocking_issues = [str(item) for item in parsed.get("blocking_issues", [])]
        improvement_actions = [
            str(item) for item in parsed.get("improvement_actions", [])
        ]
        insufficient_reference_data = bool(
            parsed.get("insufficient_reference_data", False)
        )
        overall_score, overall_verdict = derive_overall_verdict(
            grounding,
            constraints,
            instructions,
            blocking_issues,
        )

        result = JudgeEvaluationResult(
            trace_id=trace.trace_id,
            session_id=trace.session_id,
            judge_model=self.model_name,
            judge_prompt_version=Prompts.JUDGE_EVALUATOR_VERSION,
            reference_data=reference_data,
            insufficient_reference_data=insufficient_reference_data,
            grounding_factuality=grounding,
            constraint_compliance=constraints,
            instruction_following=instructions,
            overall_score=overall_score,
            overall_verdict=overall_verdict,
            blocking_issues=blocking_issues,
            improvement_actions=improvement_actions,
        )
        self.trace_store.append_judge_result(result)
        return result
