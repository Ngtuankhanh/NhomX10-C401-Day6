from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.infrastructure.ai_services.judge_service import (  # noqa: E402
    build_judge_payload,
    derive_overall_verdict,
)
from app.observability.schemas import (  # noqa: E402
    AgentRequestTrace,
    JudgeEvaluationResult,
    JudgeMetricEvaluation,
    JudgeReferenceData,
    PromptMessageTrace,
    TokenUsage,
)
from app.observability.trace_runtime import TraceCollector  # noqa: E402
from app.observability.trace_store import AsyncJsonlTraceStore  # noqa: E402


class TraceCollectorTests(unittest.TestCase):
    def test_trace_collector_captures_required_fields(self) -> None:
        collector = TraceCollector(
            session_id="session-123",
            raw_prompt="Tôi bị đau đầu 2 ngày nay",
            system_prompt_version="main-orchestrator-v2026-04-09",
            conversation_state_before="COLLECTING_SYMPTOMS",
        )
        collector.note_prompt_version("specialist_diagnosis", "diagnosis-v2026-04-09")
        collector.start_model_call(
            run_id="llm-1",
            model_name="gpt-4o",
            system_prompt_name="main_orchestrator",
            system_prompt_version="main-orchestrator-v2026-04-09",
            prompt_messages=[PromptMessageTrace(role="system", content="sys")],
        )
        collector.end_model_call(
            run_id="llm-1",
            completion="Bạn nên khám chuyên khoa thần kinh.",
            finish_reason="stop",
            token_usage=TokenUsage(input_tokens=11, output_tokens=7, total_tokens=18),
            tool_calls=[{"name": "specialist_agent_tool"}],
        )
        collector.start_tool_call(
            run_id="tool-1",
            name="specialist_agent_tool",
            input_payload={"conversation_summary": "đau đầu 2 ngày"},
        )
        collector.end_tool_call(
            run_id="tool-1",
            output_payload='{"status":"success","specialty_name":"Nội thần kinh"}',
        )

        trace = collector.finalize(
            final_output="Mình thấy khoa Nội thần kinh đang phù hợp nhất.",
            conversation_state_after="SHOWING_SPECIALTY_RESULT",
        )

        self.assertEqual(trace.session_id, "session-123")
        self.assertEqual(trace.raw_prompt, "Tôi bị đau đầu 2 ngày nay")
        self.assertEqual(trace.system_prompt_version, "main-orchestrator-v2026-04-09")
        self.assertEqual(trace.token_usage.total_tokens, 18)
        self.assertEqual(trace.conversation_state_before, "COLLECTING_SYMPTOMS")
        self.assertEqual(trace.conversation_state_after, "SHOWING_SPECIALTY_RESULT")
        self.assertEqual(len(trace.tool_calls), 1)
        self.assertEqual(trace.tool_calls[0].name, "specialist_agent_tool")
        self.assertIn("specialist_diagnosis", trace.system_prompt_versions_seen)
        self.assertEqual(trace.model_completion, "Bạn nên khám chuyên khoa thần kinh.")


class TraceStoreTests(unittest.TestCase):
    def test_jsonl_store_persists_trace_and_evaluation(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = AsyncJsonlTraceStore(Path(temp_dir))
            trace = AgentRequestTrace(
                trace_id="trace-001",
                session_id="session-001",
                raw_prompt="đau bụng",
                system_prompt_version="main-orchestrator-v2026-04-09",
                final_output="Bạn nên khám Tiêu hóa.",
                model_completion="Bạn nên khám Tiêu hóa.",
            )
            evaluation = JudgeEvaluationResult(
                trace_id="trace-001",
                session_id="session-001",
                judge_model="gpt-4o-mini",
                judge_prompt_version="judge-evaluator-v2026-04-09",
                reference_data=JudgeReferenceData(
                    ground_truth_facts=["Đau bụng kéo dài nên ưu tiên khám Tiêu hóa."]
                ),
                grounding_factuality=JudgeMetricEvaluation(
                    score=4,
                    passed=True,
                    rationale="Bám ground truth.",
                    evidence=["Khớp với dữ kiện tham chiếu."],
                ),
                constraint_compliance=JudgeMetricEvaluation(
                    score=5,
                    passed=True,
                    rationale="Không vi phạm ràng buộc.",
                    evidence=["Không đưa thuốc hay chẩn đoán xác định."],
                ),
                instruction_following=JudgeMetricEvaluation(
                    score=4,
                    passed=True,
                    rationale="Trả lời đúng intent.",
                    evidence=["Có gợi ý chuyên khoa."],
                ),
                overall_score=4.33,
                overall_verdict="pass",
            )

            store.append_trace(trace)
            store.append_judge_result(evaluation)
            store.close()

            persisted = store.get_trace("trace-001")
            self.assertIsNotNone(persisted)
            self.assertEqual(persisted.session_id, "session-001")


class JudgeHelperTests(unittest.TestCase):
    def test_judge_helpers_include_reference_data_and_deterministic_verdict(self) -> None:
        trace = AgentRequestTrace(
            trace_id="trace-002",
            session_id="session-002",
            raw_prompt="Tôi muốn đặt lịch khám tiêu hóa",
            system_prompt_version="main-orchestrator-v2026-04-09",
            final_output="Mình có thể hỗ trợ bạn đặt lịch với khoa Tiêu hóa.",
            model_completion="Mình có thể hỗ trợ bạn đặt lịch với khoa Tiêu hóa.",
        )
        reference = JudgeReferenceData(
            ground_truth_facts=["User muốn đặt lịch khám tiêu hóa."],
            required_constraints=["Không bịa bác sĩ hoặc lịch trống."],
        )
        payload = build_judge_payload(trace, reference)
        self.assertEqual(payload["reference_data"]["ground_truth_facts"][0], "User muốn đặt lịch khám tiêu hóa.")

        overall_score, verdict = derive_overall_verdict(
            grounding=JudgeMetricEvaluation(
                score=4,
                passed=True,
                rationale="Ổn",
                evidence=[],
            ),
            constraints=JudgeMetricEvaluation(
                score=3,
                passed=True,
                rationale="Có lệch nhẹ",
                evidence=[],
            ),
            instructions=JudgeMetricEvaluation(
                score=4,
                passed=True,
                rationale="Theo yêu cầu",
                evidence=[],
            ),
            blocking_issues=[],
        )

        self.assertEqual(overall_score, 3.67)
        self.assertEqual(verdict, "needs_review")


if __name__ == "__main__":
    unittest.main()
