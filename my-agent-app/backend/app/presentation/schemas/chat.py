from pydantic import BaseModel, Field

class ChatMessageRequest(BaseModel):
    session_id: str = Field(..., description="Session identifier returned by session init")
    message: str = Field(..., min_length=1, description="Latest user message")
