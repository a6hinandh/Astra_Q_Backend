from __future__ import annotations

import logging
import time
from typing import Any, List, Literal, Optional

from fastapi import APIRouter
from pydantic import BaseModel

from backend.api.router_logic import Mode, decide_mode
from backend.session.firebase_session import append_message, get_history
from core.tracing import RequestTrace, TraceStatus, generate_trace_id, trace_store
from tools import get_default_registry

logger = logging.getLogger(__name__)

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
    trace_id: str = ""


class HistoryItem(BaseModel):
    role: str
    content: str
    timestamp: Optional[Any] = None


@router.post("/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest) -> ChatResponse:
    # 1) Derive IDs with defaults
    user_id = payload.user_id or "anonymous"
    thread_id = payload.thread_id or "default"

    # 2) Create trace for this request
    trace = RequestTrace(
        trace_id=generate_trace_id(),
        user_id=user_id,
        thread_id=thread_id,
        query=payload.message,
        started_at=time.time(),
    )

    # 3) Save current user message to Firebase
    append_message(user_id, thread_id, "user", payload.message)

    # 4) Load stored history from Firebase
    stored_history = get_history(user_id, thread_id)

    # 5) Decide mode on current message
    mode = decide_mode(payload.message)
    trace.selected_mode = mode.value

    # 6) Run tools via registry with tracing
    registry = get_default_registry()
    kg_result = None
    rag_result = None

    if mode in (Mode.KG, Mode.BOTH):
        try:
            kg_result = registry.run_tool("knowledge_graph", payload.message, trace=trace, history=stored_history)
        except Exception:
            kg_result = None

    if mode in (Mode.RAG, Mode.BOTH):
        try:
            rag_result = registry.run_tool("vector_search", payload.message, trace=trace, history=stored_history)
        except Exception:
            rag_result = None

    # 7) Fusion logic — extract from ToolResult
    # KG only
    if mode == Mode.KG and kg_result and kg_result.success:
        answer = kg_result.metadata.get("answer", "")
        append_message(user_id, thread_id, "assistant", answer)
        trace.finalize(answer=answer)
        trace_store.add(trace)
        logger.info("Trace %s | mode=kg | status=%s", trace.trace_id, trace.status.value)

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
            trace_id=trace.trace_id,
        )

    # RAG only
    if mode == Mode.RAG and rag_result and rag_result.success:
        answer = rag_result.metadata.get("answer", "")
        append_message(user_id, thread_id, "assistant", answer)
        trace.finalize(answer=answer)
        trace_store.add(trace)
        logger.info("Trace %s | mode=rag | status=%s", trace.trace_id, trace.status.value)

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
            trace_id=trace.trace_id,
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
    trace.finalize(answer=final_answer)
    trace_store.add(trace)
    logger.info("Trace %s | mode=both | status=%s", trace.trace_id, trace.status.value)

    return ChatResponse(
        answer=final_answer,
        sources=combined_sources,
        mode=mode,
        trace_id=trace.trace_id,
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
