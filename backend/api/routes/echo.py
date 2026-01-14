from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional, Any

from backend.session.firebase_session import append_message, get_history

router = APIRouter()

class EchoRequest(BaseModel):
    user_id: Optional[str] = None
    thread_id: Optional[str] = None
    message: str

class EchoMessage(BaseModel):
    id: str
    role: str
    content: str
    timestamp: Optional[Any] = None

class EchoResponse(BaseModel):
    user_id: str
    thread_id: str
    messages: List[EchoMessage]

@router.post("/echo", response_model=EchoResponse)
async def echo(payload: EchoRequest) -> EchoResponse:
    user_id = payload.user_id or "anonymous"
    thread_id = payload.thread_id or "test_thread"

    # 1) write the new message
    append_message(user_id, thread_id, "user", payload.message)

    # 2) read full history
    raw_history = get_history(user_id, thread_id)

    messages = [
        EchoMessage(
            id=m["id"],
            role=m["role"],
            content=m["content"],
            timestamp=m["timestamp"],
        )
        for m in raw_history
    ]

    return EchoResponse(
        user_id=user_id,
        thread_id=thread_id,
        messages=messages,
    )
