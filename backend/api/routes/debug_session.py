# backend/api/routes/debug_session.py
from fastapi import APIRouter
from typing import Any, Dict, List

from backend.session.firebase_session import append_message, get_history

router = APIRouter()

@router.get("/debug-session")
async def debug_session() -> Dict[str, Any]:
    user_id = "debug_user"
    thread_id = "debug_thread"

    # Write two messages
    append_message(user_id, thread_id, "user", "First debug message")
    append_message(user_id, thread_id, "assistant", "Second debug reply")

    # Read history
    history: List[Dict[str, str]] = get_history(user_id, thread_id)

    return {
        "user_id": user_id,
        "thread_id": thread_id,
        "history": history,
    }
