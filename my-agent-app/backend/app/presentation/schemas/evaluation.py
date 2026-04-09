from pydantic import BaseModel, Field

from app.observability.schemas import JudgeReferenceData


class JudgeTraceRequest(BaseModel):
    trace_id: str = Field(..., description="Structured trace identifier to evaluate.")
    reference_data: JudgeReferenceData
