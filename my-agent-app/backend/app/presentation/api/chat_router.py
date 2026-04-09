from fastapi import APIRouter, HTTPException, Depends
from app.presentation.schemas.chat import ChatMessageRequest
from app.presentation.api.dependencies import get_chat_service
from app.application.use_cases.chat_handler import AgentAService

router = APIRouter(prefix="/api/chat", tags=["Chat"])

@router.post("/session")
async def create_chat_session(chat_service: AgentAService = Depends(get_chat_service)) -> dict:
    return chat_service.create_session()

@router.post("/message")
async def chat_message(payload: ChatMessageRequest, chat_service: AgentAService = Depends(get_chat_service)) -> dict:
    if not payload.message.strip():
        raise HTTPException(status_code=400, detail="Message must not be empty.")
    return chat_service.send_user_message(payload.session_id, payload.message)
