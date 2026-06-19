"""Tests for core/tracing.py TraceStore — must pass without external services."""

from core.tracing import RequestTrace, TraceStore


def _make_trace(tid: str) -> RequestTrace:
    return RequestTrace(trace_id=tid)


def test_store_add_and_get():
    store = TraceStore(max_size=100)
    trace = _make_trace("abc")
    store.add(trace)
    assert store.get("abc") is trace


def test_store_get_missing():
    store = TraceStore()
    assert store.get("nonexistent") is None


def test_store_list_recent():
    store = TraceStore()
    for i in range(10):
        store.add(_make_trace(f"t{i}"))
    recent = store.list_recent(limit=3)
    assert len(recent) == 3
    assert recent[0].trace_id == "t7"


def test_store_list_recent_returns_all_when_under_limit():
    store = TraceStore()
    for i in range(3):
        store.add(_make_trace(f"t{i}"))
    recent = store.list_recent(limit=10)
    assert len(recent) == 3


def test_store_clear():
    store = TraceStore()
    store.add(_make_trace("a"))
    store.clear()
    assert store.get("a") is None
    assert len(store) == 0


def test_store_bounded_size():
    store = TraceStore(max_size=3)
    for i in range(10):
        store.add(_make_trace(f"t{i}"))
    assert len(store) == 3
    assert store.get("t0") is None
    assert store.get("t9") is not None


def test_store_len():
    store = TraceStore()
    assert len(store) == 0
    store.add(_make_trace("a"))
    assert len(store) == 1
    store.add(_make_trace("b"))
    assert len(store) == 2
