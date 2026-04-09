"""Agent B — Specialist Classifier Agent.

Nhiệm vụ: Nhận payload triệu chứng chuẩn hóa, phân tích Knowledge Graph
và trả về gợi ý chuyên khoa cùng độ tin cậy.
Agent này KHÔNG giao tiếp trực tiếp với người dùng.
"""
from __future__ import annotations
import json
from pathlib import Path
import re

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from pydantic import SecretStr
from langgraph.prebuilt import ToolRuntime

from app.application.interfaces import ITriageService
from app.domain.entities import ClassificationResult, SpecialtyDefinition
from app.observability.trace_runtime import get_current_trace_collector
from app.shared.text_utils import normalize_text
from app.config import settings
from .prompts import Prompts

def parse_json_from_llm(content: str | list) -> dict:
    text = content if isinstance(content, str) else str(content[0])
    text = text.strip()
    match = re.search(r"```(?:json)?(.*?)```", text, re.DOTALL)
    if match:
        text = match.group(1).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {}


def _tool_success(**payload: object) -> str:
    return json.dumps({"status": "success", **payload}, ensure_ascii=False)


def _tool_error(code: str, message: str) -> str:
    return json.dumps(
        {"status": "error", "error": {"code": code, "message": message}},
        ensure_ascii=False,
    )


def _resolve_thread_id(runtime: ToolRuntime | None) -> str:
    if runtime is None:
        return "default-thread"

    config = getattr(runtime, "config", None) or {}
    configurable = config.get("configurable", {}) if hasattr(config, "get") else {}
    thread_id = configurable.get("thread_id")
    return str(thread_id) if thread_id else "default-thread"


def _sync_specialist_session(
    thread_id: str,
    conversation_summary: str,
    result: ClassificationResult,
    agent_b_status: str = "completed",
) -> None:
    from app.presentation.api.dependencies import _session_repo
    from app.domain.entities import SpecialtyAssessment

    session = _session_repo.get_session(thread_id)
    if not session:
        return

    session.symptom_summary = conversation_summary
    session.specialty_assessment = SpecialtyAssessment(
        speciality_id=result.speciality_id,
        speciality_name=result.speciality_name,
        description=result.description,
        confidence=result.confidence,
        question=result.question,
        matched_symptoms=list(result.matched_symptoms),
        needs_more_info=result.needs_more_info,
        warning_signs=list(result.warning_signs),
        fallback_used=result.fallback_used,
        agent_b_status=agent_b_status,
    )

    session.failure_state.last_error_code = None
    if result.warning_signs:
        session.conversation_state = "FALLBACK_SUPPORT"
        session.pending_field = None
        session.last_follow_up_question = None
    elif result.needs_more_info and result.question:
        session.conversation_state = "ASKING_FOLLOWUP"
        session.pending_field = "follow_up_answer"
        session.last_follow_up_question = result.question
    else:
        session.conversation_state = "SHOWING_SPECIALTY_RESULT"
        session.pending_field = None
        session.last_follow_up_question = None

    if result.confidence > 0.7 and result.speciality_id is not None:
        session.booking_context.speciality_id = result.speciality_id
        session.booking_context.speciality_name = result.speciality_name

    _session_repo.save_session(session)


def _mark_specialist_error(thread_id: str, error_code: str, error_message: str) -> None:
    from app.presentation.api.dependencies import _session_repo

    session = _session_repo.get_session(thread_id)
    if not session:
        return

    session.failure_state.agent_b_failures += 1
    session.failure_state.last_error_code = error_code
    session.conversation_state = "FALLBACK_SUPPORT"
    session.specialty_assessment.agent_b_status = "error"
    session.specialty_assessment.description = error_message
    _session_repo.save_session(session)


AMBIGUOUS_SINGLE_TOKEN_SYMPTOMS: frozenset[str] = frozenset({"ngay", "nam", "nu"})

class SpecialistAgent(ITriageService):
    """Implement của Agent B kết hợp LLM (gpt-4o-mini) và Knowledge Graph.
    
    Agent sử dụng 2 prompt chính từ prompt_agent.py:
    - KG_EXTRACTION: Trích xuất triệu chứng, tuổi, giới tính thành Graph.
    - DIAGNOSIS: Tổng hợp kết quả từ Graph local và đưa ra chẩn đoán, gợi ý chuyên khoa,
      kèm theo các câu hỏi follow-up.
    
    Parameters
    ----------
    specialties:
        Danh sách chuyên khoa load từ CSV.
    kg_path:
        Đường dẫn file knowledge-graph JSON.
    """

    def __init__(
        self,
        specialties: list[SpecialtyDefinition],
        kg_path: Path,
    ) -> None:
        self.specialties = specialties
        self.specialty_by_id: dict[int, SpecialtyDefinition] = {
            s.speciality_id: s for s in specialties
        }
        self.disease_to_specialty: dict[str, SpecialtyDefinition] = {
            d: s for s in specialties for d in s.diseases
        }

        self.symptom_to_diseases: dict[str, set[str]] = {}
        self.disease_to_symptoms: dict[str, set[str]] = {}
        self.body_part_to_diseases: dict[str, set[str]] = {}
        self.symptom_display: dict[str, str] = {}

        self._load_kg(kg_path)
        
        self.llm = ChatOpenAI(
            model=settings.specialist_model,
            temperature=0,
            api_key=SecretStr(settings.openai_api_key) if settings.openai_api_key else None
        )

        self.sorted_symptoms = sorted(
            self.symptom_to_diseases.keys(), key=lambda x: (-len(x), x)
        )
        self.sorted_body_parts = sorted(
            self.body_part_to_diseases.keys(), key=lambda x: (-len(x), x)
        )

    def _trace_config(self) -> dict | None:
        collector = get_current_trace_collector()
        if collector is None:
            return None
        return {"callbacks": [collector.callback_handler]}

    def _load_kg(self, kg_path: Path) -> None:
        if not kg_path.exists():
            return
        kg_data: dict = json.loads(kg_path.read_text(encoding="utf-8"))
        node_by_id: dict[str, dict] = {
            node["id"]: node for node in kg_data.get("nodes", [])
        }

        for rel in kg_data.get("relations", []):
            disease: str | None = rel.get("disease")
            if not disease:
                continue
            target: dict | None = node_by_id.get(rel.get("target", ""))
            if not target:
                continue

            label = str(target.get("label", "")).strip()
            norm_label = normalize_text(label)
            if not norm_label:
                continue

            relation_type: str = rel.get("relation", "")
            if relation_type == "HAS_SYMPTOM":
                self.symptom_to_diseases.setdefault(norm_label, set()).add(disease)
                self.disease_to_symptoms.setdefault(disease, set()).add(label)
                self.symptom_display[norm_label] = label
            elif relation_type in {"LOCATED_IN", "AFFECTS"} and target.get("type") == "BODY_PART":
                self.body_part_to_diseases.setdefault(norm_label, set()).add(disease)
                self.symptom_display[norm_label] = label

    def classify_symptoms(self, raw_text: str) -> ClassificationResult:
        normalized = normalize_text(raw_text)
        if not normalized:
            return ClassificationResult(
                speciality_id=None,
                speciality_name="Chưa xác định",
                description="Cần thêm thông tin.",
                confidence=0.2,
                question="Bạn đau ở đâu?",
                matched_symptoms=(),
                fallback_used=True,
                needs_more_info=True,
            )

        # 1. Trích xuất Knowledge Graph bằng LLM
        kg_messages = [
            SystemMessage(content=Prompts.KG_EXTRACTION),
            HumanMessage(content=f"Văn bản: {raw_text}")
        ]
        try:
            collector = get_current_trace_collector()
            if collector is not None:
                collector.note_prompt_version(
                    "specialist_kg_extraction",
                    Prompts.KG_EXTRACTION_VERSION,
                )
            kg_resp = self.llm.invoke(kg_messages, config=self._trace_config())
            kg_ext = parse_json_from_llm(kg_resp.content)
        except Exception:
            kg_ext = {"nodes": [], "context": {}}

        # 2. Gom nhóm các triệu chứng tìm thấy trong raw_text và kg_ext
        ext_labels = [n.get("label", "").lower() for n in kg_ext.get("nodes", [])]
        matched_symptoms = set()
        
        for sym in self.sorted_symptoms:
            if sym in normalized and sym not in AMBIGUOUS_SINGLE_TOKEN_SYMPTOMS:
                matched_symptoms.add(sym)
                
        for label in ext_labels:
            norm_label = normalize_text(label)
            if norm_label in self.symptom_to_diseases:
                matched_symptoms.add(norm_label)

        matched_symptoms_list = list(matched_symptoms)

        # 3. Tính điểm các bệnh liên quan
        scores: dict[str, float] = {}
        for sym in matched_symptoms_list:
            for dis in self.symptom_to_diseases.get(sym, set()):
                # Mỗi triệu chứng khớp cộng thêm 1.0 (có thể cộng thêm logic context_weight sau này)
                scores[dis] = scores.get(dis, 0.0) + 1.0

        top_diseases = []
        for dis, score in sorted(scores.items(), key=lambda x: x[1], reverse=True)[:3]:
            spec = self.disease_to_specialty.get(dis)
            top_diseases.append({
                "disease_name": dis,
                "weighted_score": score,
                "specialties_matched": [
                    {
                        "specialty_id": spec.speciality_id,
                        "specialty_name": spec.speciality_name
                    }
                ] if spec else []
            })
            
        # 4. Yêu cầu LLM chẩn đoán và chọn chuyên khoa
        user_msg = {
            "patient_input": raw_text,
            "extracted_context": kg_ext.get("context", {}),
            "matched_symptoms": matched_symptoms_list,
            "top_diseases": top_diseases
        }
        diag_messages = [
            SystemMessage(content=Prompts.DIAGNOSIS),
            HumanMessage(content=json.dumps(user_msg, ensure_ascii=False, indent=2))
        ]
        try:
            collector = get_current_trace_collector()
            if collector is not None:
                collector.note_prompt_version(
                    "specialist_diagnosis",
                    Prompts.DIAGNOSIS_VERSION,
                )
            diag_resp = self.llm.invoke(diag_messages, config=self._trace_config())
            diag_data = parse_json_from_llm(diag_resp.content)
        except Exception:
            diag_data = {}

        # 5. Fallback nếu LLM lỗi hoặc không có cấu trúc đúng
        diagnoses = diag_data.get("diagnoses", [])
        if not diagnoses:
            # Fallback về rule-based cũ nếu LLM thất bại
            if scores:
                top_dis = max(scores, key=lambda k: scores[k])
                spec = self.disease_to_specialty.get(top_dis)
                if spec:
                    return ClassificationResult(
                        speciality_id=spec.speciality_id,
                        speciality_name=spec.speciality_name,
                        description=f"Dựa trên triệu chứng, bạn nên khám {spec.speciality_name}.",
                        confidence=0.8,
                        question=None,
                        matched_symptoms=tuple(str(self.symptom_display.get(s, s)) for s in matched_symptoms_list[:3]),
                        fallback_used=True,
                    )
                    
            return ClassificationResult(
                speciality_id=None,
                speciality_name="Chưa xác định",
                description="Vui lòng mô tả rõ hơn.",
                confidence=0.34,
                question="Bạn có thể nói rõ hơn không?",
                matched_symptoms=(),
                fallback_used=True,
                needs_more_info=True,
            )

        # 6. Chuẩn bị kết quả từ LLM
        best_diag = diagnoses[0]
        sp_id = best_diag.get("specialty_id")
        # Đảm bảo logic nếu LLM trả về ID 0 là Đa khoa, ta map lại cho chuẩn DB (ví dụ ID 30)
        # Trong thiết kế hiện tại ID đa khoa là 30
        if sp_id == 0 or sp_id is None:
            sp_id = 30
        
        questions = diag_data.get("follow_up_questions", [])
        first_q = questions[0].get("question") if questions else ("Bạn có biểu hiện nào khác không?" if diag_data.get("needs_more_info") else None)
        warning_signs = tuple(str(item) for item in diag_data.get("warning_signs", [])[:3])
        needs_more_info = bool(diag_data.get("needs_more_info") or first_q)

        return ClassificationResult(
            speciality_id=sp_id,
            speciality_name=best_diag.get("specialty_name", "Đa khoa"),
            description=best_diag.get("cause") or best_diag.get("confidence_note") or "Dựa trên triệu chứng từ Knowledge Graph.",
            confidence=float(diag_data.get("overall_confidence", best_diag.get("confidence", 0.5))),
            question=first_q,
            matched_symptoms=tuple(str(self.symptom_display.get(s, s)) for s in best_diag.get("matched_symptoms", [])[:3]),
            fallback_used=False,
            needs_more_info=needs_more_info,
            warning_signs=warning_signs,
        )


from langchain_core.tools import tool

@tool
def specialist_agent_tool(conversation_summary: str, runtime: ToolRuntime) -> str:
    """Gọi chuyên gia y tế (Agent B) để phân tích triệu chứng và gợi ý chuyên khoa.
    
    Hãy dùng tool này khi người dùng mô tả các triệu chứng bệnh và cần biết nên khám khoa nào.
    
    Args:
        conversation_summary: Tóm tắt các triệu chứng và tình trạng mà người dùng đã mô tả.
    """
    from app.presentation.api.dependencies import _triage_service
    
    thread_id = _resolve_thread_id(runtime)

    try:
        result = _triage_service.classify_symptoms(conversation_summary)
        _sync_specialist_session(thread_id, conversation_summary, result)

        return _tool_success(
            specialty_id=result.speciality_id,
            specialty_name=result.speciality_name,
            description=result.description,
            confidence=result.confidence,
            matched_symptoms=list(result.matched_symptoms),
            question=result.question,
            needs_more_info=result.needs_more_info,
            warning_signs=list(result.warning_signs),
            fallback_used=result.fallback_used,
            agent_b_status="completed",
        )
    except Exception as exc:
        error_code = "SPECIALIST_TOOL_ERROR"
        _mark_specialist_error(thread_id, error_code, str(exc))
        return _tool_error(error_code, str(exc))
