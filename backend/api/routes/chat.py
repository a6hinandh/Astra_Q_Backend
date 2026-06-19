from __future__ import annotations

from typing import Any, List, Literal, Optional

from fastapi import APIRouter
from pydantic import BaseModel

from backend.api.router_logic import Mode, decide_mode
from backend.session.firebase_session import append_message, get_history
from tools import get_default_registry

router = APIRouter()


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    user_id: Optional[str] = None
    thread_id: Optional[str] = None
    message: str
    history: List[ChatMessage] = []


class Source(BaseModel):
    source: str
    content_preview: str
    page: Optional[int] = None
    cypher: Optional[str] = None
    rows: Optional[Any] = None


class ChatResponse(BaseModel):
    answer: str
    sources: List[Source]
    mode: Mode


class HistoryItem(BaseModel):
    role: str
    content: str
    timestamp: Optional[Any] = None


@router.post("/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest) -> ChatResponse:
    # 1) Derive IDs with defaults
    user_id = payload.user_id or "anonymous"
    thread_id = payload.thread_id or "default"

    # 2) Save current user message to Firebase
    append_message(user_id, thread_id, "user", payload.message)

    # 3) Load stored history from Firebase
    stored_history = get_history(user_id, thread_id)
    # Each item: {"role": "user"|"assistant", "content": "..."}

    # 4) Build history_for_llm = all stored messages
    history_for_llm = stored_history

    # 5) Decide mode on current message
    mode = decide_mode(payload.message)

    # 6) Run tools via registry
    registry = get_default_registry()
    kg_result = None
    rag_result = None

    if mode in (Mode.KG, Mode.BOTH):
        try:
            kg_result = registry.run_tool("knowledge_graph", payload.message, history=history_for_llm)
        except Exception:
            kg_result = None

    if mode in (Mode.RAG, Mode.BOTH):
        try:
            rag_result = registry.run_tool("vector_search", payload.message, history=history_for_llm)
        except Exception:
            rag_result = None

    # 7) Fusion logic — extract from ToolResult
    # KG only
    if mode == Mode.KG and kg_result and kg_result.success:
        answer = kg_result.metadata.get("answer", "")
        append_message(user_id, thread_id, "assistant", answer)

        return ChatResponse(
            answer=answer,
            sources=[
                Source(
                    source="KG",
                    content_preview="",
                    cypher=kg_result.metadata.get("cypher"),
                    rows=kg_result.metadata.get("rows"),
                )
            ],
            mode=mode,
        )

    # RAG only
    if mode == Mode.RAG and rag_result and rag_result.success:
        answer = rag_result.metadata.get("answer", "")
        append_message(user_id, thread_id, "assistant", answer)

        sources = [
            Source(
                source=ev.source,
                content_preview=ev.content,
                page=ev.metadata.get("page"),
            )
            for ev in rag_result.evidence
        ]

        return ChatResponse(
            answer=answer,
            sources=sources,
            mode=mode,
        )

    # BOTH: concatenate answers + sources
    combined_answer_parts: List[str] = []
    combined_sources: List[Source] = []

    if kg_result and kg_result.success:
        combined_answer_parts.append(kg_result.metadata.get("answer", ""))
        combined_sources.append(
            Source(
                source="KG",
                content_preview="",
                cypher=kg_result.metadata.get("cypher"),
                rows=kg_result.metadata.get("rows"),
            )
        )

    if rag_result and rag_result.success:
        combined_answer_parts.append(rag_result.metadata.get("answer", ""))
        combined_sources.extend(
            [
                Source(
                    source=ev.source,
                    content_preview=ev.content,
                    page=ev.metadata.get("page"),
                )
                for ev in rag_result.evidence
            ]
        )

    final_answer = "\n\n".join(part for part in combined_answer_parts if part)

    append_message(user_id, thread_id, "assistant", final_answer)

    return ChatResponse(
        answer=final_answer,
        sources=combined_sources,
        mode=mode,
    )


@router.get("/thread/{thread_id}", response_model=List[HistoryItem])
async def get_thread_history(thread_id: str, user_id: str) -> List[HistoryItem]:
    """
    Return all messages for a given user/thread, ordered by timestamp ascending.
    Used by the frontend to reopen an existing thread.
    """
    stored_history = get_history(user_id, thread_id)
    # stored_history items: {"id", "role", "content", "timestamp"}

    return [
        HistoryItem(
            role=item["role"],
            content=item["content"],
            timestamp=item.get("timestamp"),
        )
        for item in stored_history
    ]
