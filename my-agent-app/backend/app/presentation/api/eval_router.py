from fastapi import APIRouter, Depends, HTTPException
from starlette.concurrency import run_in_threadpool

from app.infrastructure.ai_services.judge_service import LLMJudgeService
from app.observability.schemas import AgentRequestTrace, JudgeEvaluationResult
from app.observability.trace_store import AsyncJsonlTraceStore
from app.presentation.api.dependencies import get_judge_service, get_trace_store
from app.presentation.schemas.evaluation import JudgeTraceRequest

router = APIRouter(prefix="/api/evals", tags=["Evaluation"])


@router.get("/traces/{trace_id}", response_model=AgentRequestTrace)
async def get_trace(
    trace_id: str,
    trace_store: AsyncJsonlTraceStore = Depends(get_trace_store),
) -> AgentRequestTrace:
    trace = await run_in_threadpool(trace_store.get_trace, trace_id)
    if trace is None:
        raise HTTPException(status_code=404, detail="Trace not found.")
    return trace


@router.get(
    "/sessions/{session_id}/latest-trace",
    response_model=AgentRequestTrace,
)
async def latest_trace_for_session(
    session_id: str,
    trace_store: AsyncJsonlTraceStore = Depends(get_trace_store),
) -> AgentRequestTrace:
    trace = await run_in_threadpool(trace_store.latest_trace_for_session, session_id)
    if trace is None:
        raise HTTPException(status_code=404, detail="No trace found for session.")
    return trace


@router.post("/judge", response_model=JudgeEvaluationResult)
async def judge_trace(
    payload: JudgeTraceRequest,
    judge_service: LLMJudgeService = Depends(get_judge_service),
) -> JudgeEvaluationResult:
    try:
        return await run_in_threadpool(
            judge_service.evaluate_trace,
            payload.trace_id,
            payload.reference_data,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
