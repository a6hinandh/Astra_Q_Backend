from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException

from core.tracing import trace_store

router = APIRouter()


@router.get("/trace/{trace_id}")
async def get_trace(trace_id: str) -> dict[str, Any]:
    trace = trace_store.get(trace_id)
    if trace is None:
        raise HTTPException(status_code=404, detail=f"Trace '{trace_id}' not found.")
    return trace.to_dict()


@router.get("/traces/recent")
async def list_recent_traces(limit: int = 20) -> list[dict[str, Any]]:
    capped = min(limit, 100)
    return [t.to_dict() for t in trace_store.list_recent(limit=capped)]
