from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Literal, Optional, Any

from rag_pipeline.retrieve import run_rag_pipeline
from kg_pipeline.kg_nl_demo import ask_kg
from backend.api.router_logic import decide_mode, Mode
from backend.session.firebase_session import append_message, get_history

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

    kg_result = None
    rag_result = None

    # 6) Call KG/RAG with history
    if mode in (Mode.KG, Mode.BOTH):
        try:
            kg_result = ask_kg(payload.message, history=history_for_llm)
        except Exception:
            kg_result = None  # ignore KG errors for junk / out-of-schema questions

    if mode in (Mode.RAG, Mode.BOTH):
        rag_result = run_rag_pipeline(payload.message, history=history_for_llm)

    # 7) Fusion logic
    # KG only
    if mode == Mode.KG and kg_result:
        answer = kg_result["answer"]
        # Save assistant message
        append_message(user_id, thread_id, "assistant", answer)

        return ChatResponse(
            answer=answer,
            sources=[
                Source(
                    source="KG",
                    content_preview="",
                    cypher=kg_result.get("cypher"),
                    rows=kg_result.get("rows"),
                )
            ],
            mode=mode,
        )

    # RAG only
    if mode == Mode.RAG and rag_result:
        answer = rag_result["answer"]
        append_message(user_id, thread_id, "assistant", answer)

        sources = [
            Source(
                source=s.get("source", ""),
                content_preview=s.get("content_preview", ""),
                page=s.get("page"),
            )
            for s in rag_result.get("sources", [])
        ]

        return ChatResponse(
            answer=answer,
            sources=sources,
            mode=mode,
        )

    # BOTH: concatenate answers + sources
    combined_answer_parts: List[str] = []
    combined_sources: List[Source] = []

    if kg_result:
        combined_answer_parts.append(kg_result["answer"])
        combined_sources.append(
            Source(
                source="KG",
                content_preview="",
                cypher=kg_result.get("cypher"),
                rows=kg_result.get("rows"),
            )
        )

    if rag_result:
        combined_answer_parts.append(rag_result["answer"])
        combined_sources.extend(
            [
                Source(
                    source=s.get("source", ""),
                    content_preview=s.get("content_preview", ""),
                    page=s.get("page"),
                )
                for s in rag_result.get("sources", [])
            ]
        )

    final_answer = "\n\n".join(part for part in combined_answer_parts if part)

    # Save final assistant message
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
