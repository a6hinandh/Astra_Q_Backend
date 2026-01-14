from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes.chat import router as chat_router
from backend.api.routes.echo import router as echo_router
from backend.api.routes.debug_session import router as debug_router
from backend.session.firebase_session import init_firebase

app = FastAPI()

# Initialize Firebase once (uses env var inside)
init_firebase()

# Routers
app.include_router(chat_router, prefix="/api")
app.include_router(echo_router,prefix="/api")
app.include_router(debug_router, prefix="/api")

# CORS
origins = [
    "http://localhost:5173",
    "http://localhost:5174",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Astra-Q backend is running"}
