from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes.chat import router as chat_router
from backend.api.routes.trace import router as trace_router
from backend.session.firebase_session import init_firebase
from core.config import settings

app = FastAPI()

# Routers
app.include_router(chat_router, prefix="/api")
app.include_router(trace_router, prefix="/api")


# CORS — configurable via CORS_ALLOWED_ORIGINS env
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    """Initialize Firebase on first startup, not at import time."""
    try:
        init_firebase()
    except RuntimeError as e:
        print(f"[Vanta AI] Firebase not configured: {e}")
        print("[Vanta AI] Chat history persistence disabled.")


@app.get("/")
async def root():
    return {"message": "Vanta AI backend is running"}
