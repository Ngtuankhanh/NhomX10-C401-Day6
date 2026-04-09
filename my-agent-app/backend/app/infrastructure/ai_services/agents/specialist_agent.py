"""Agent B — Specialist Classifier Agent.

Nhiệm vụ: Nhận payload triệu chứng chuẩn hóa, phân tích Knowledge Graph
và trả về gợi ý chuyên khoa cùng độ tin cậy.
Agent này KHÔNG giao tiếp trực tiếp với người dùng.
"""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any

from app.application.interfaces import ITriageService
from app.domain.entities import ClassificationResult, SpecialtyDefinition
from app.shared.text_utils import normalize_text

AMBIGUOUS_SINGLE_TOKEN_SYMPTOMS: frozenset[str] = frozenset({"ngay", "nam", "nu"})

class SpecialistAgent(ITriageService):
    """Implement của Agent B dùng Rule-based Knowledge Graph cho MVP.
    
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

        self.sorted_symptoms = sorted(
            self.symptom_to_diseases.keys(), key=lambda x: (-len(x), x)
        )
        self.sorted_body_parts = sorted(
            self.body_part_to_diseases.keys(), key=lambda x: (-len(x), x)
        )

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
            )

        # Direct specialty mention
        for s in self.specialties:
            if s.normalized_name in normalized:
                return ClassificationResult(
                    speciality_id=s.speciality_id,
                    speciality_name=s.speciality_name,
                    description=f"Bạn nhắc tới {s.speciality_name}.",
                    confidence=0.92,
                    question=None,
                    matched_symptoms=(),
                    fallback_used=False,
                )

        # Symptom matching
        matched_symptoms = [
            p
            for p in self.sorted_symptoms
            if p not in AMBIGUOUS_SINGLE_TOKEN_SYMPTOMS and p in normalized
        ]

        scores: dict[int, float] = {}
        for sym in matched_symptoms:
            for dis in self.symptom_to_diseases.get(sym, set()):
                spec = self.disease_to_specialty.get(dis)
                if spec:
                    scores[spec.speciality_id] = scores.get(spec.speciality_id, 0.0) + 1.2

        if not scores:
            return ClassificationResult(
                speciality_id=None,
                speciality_name="Chưa xác định",
                description="Vui lòng mô tả rõ hơn.",
                confidence=0.34,
                question="Bạn có thể nói rõ hơn không?",
                matched_symptoms=(),
                fallback_used=True,
            )

        top_id = max(scores, key=lambda k: scores[k])
        spec = self.specialty_by_id[top_id]

        return ClassificationResult(
            speciality_id=spec.speciality_id,
            speciality_name=spec.speciality_name,
            description=f"Dựa trên triệu chứng, bạn nên khám {spec.speciality_name}.",
            confidence=0.8,
            question=None,
            matched_symptoms=tuple(
                self.symptom_display.get(s, s) for s in matched_symptoms[:3]
            ),
            fallback_used=False,
        )

from langchain_core.tools import tool

@tool
def specialist_agent_tool(conversation_summary: str, thread_id: str = "default-thread") -> str:
    """Gọi chuyên gia y tế (Agent B) để phân tích triệu chứng và gợi ý chuyên khoa.
    
    Hãy dùng tool này khi người dùng mô tả các triệu chứng bệnh và cần biết nên khám khoa nào.
    
    Args:
        conversation_summary: Tóm tắt các triệu chứng và tình trạng mà người dùng đã mô tả.
        thread_id: ID của phiên chat (tự động lấy từ config nếu gọi trong LangGraph).
    """
    from app.presentation.api.dependencies import _triage_service, _session_repo
    from app.domain.entities import SpecialtyAssessment
    
    result = _triage_service.classify_symptoms(conversation_summary)
    
    # Đồng bộ vào Session State để FE hiển thị bảng Summary
    session = _session_repo.get_session(thread_id)
    if session:
        session.symptom_summary = conversation_summary
        session.specialty_assessment = SpecialtyAssessment(
            speciality_id=result.speciality_id,
            speciality_name=result.speciality_name,
            description=result.description,
            confidence=result.confidence,
            question=result.question,
            matched_symptoms=list(result.matched_symptoms),
            fallback_used=result.fallback_used,
            agent_b_status="completed"
        )
        # Tự động cập nhật chuyên khoa vào tiến độ đặt lịch nếu độ tin cậy cao
        if result.confidence > 0.7:
            session.booking_context.speciality_id = result.speciality_id
            session.booking_context.speciality_name = result.speciality_name
            
        _session_repo.save_session(session)
    
    return json.dumps({
        "specialty_name": result.speciality_name,
        "description": result.description,
        "confidence": result.confidence,
        "matched_symptoms": result.matched_symptoms,
        "question": result.question if result.confidence < 0.7 else None
    }, ensure_ascii=False)


