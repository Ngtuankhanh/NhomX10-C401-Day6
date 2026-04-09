from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.presentation.api.chat_router import router as chat_router
from app.presentation.api.dependencies import _trace_store
from app.presentation.api.eval_router import router as eval_router
from app.config import settings

app = FastAPI(
    title="Medical Booking Agent API",
    description="Backend API for the medical specialty suggestion and booking assistant.",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)
app.include_router(eval_router)

@app.get("/health", tags=["Monitoring"])
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.on_event("shutdown")
def flush_observability_buffers() -> None:
    _trace_store.close()
