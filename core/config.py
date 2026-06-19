import os
from typing import List


class Settings:
    """Centralized configuration for Vanta AI.

    Reads environment variables lazily (on access, not at class definition time).
    Safe defaults are provided for local development only.
    Importing this module does NOT trigger any external connection.
    """

    # --- Gemini ---
    @property
    def GOOGLE_API_KEY(self) -> str:
        return os.getenv("GOOGLE_API_KEY", "")

    @property
    def GEMINI_API_KEY(self) -> str:
        return os.getenv("GEMINI_API_KEY", "")

    @property
    def effective_gemini_key(self) -> str:
        return self.GOOGLE_API_KEY or self.GEMINI_API_KEY

    # --- Neo4j ---
    @property
    def NEO4J_URI(self) -> str:
        return os.getenv("NEO4J_URI", "bolt://localhost:7687")

    @property
    def NEO4J_USERNAME(self) -> str:
        return os.getenv("NEO4J_USERNAME", "neo4j")

    @property
    def NEO4J_PASSWORD(self) -> str:
        return os.getenv("NEO4J_PASSWORD", "")

    @property
    def NEO4J_DATABASE(self) -> str:
        return os.getenv("NEO4J_DATABASE", "neo4j")

    # --- Firebase ---
    @property
    def FIREBASE_SERVICE_ACCOUNT_JSON(self) -> str:
        return os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON", "")

    @property
    def GOOGLE_APPLICATION_CREDENTIALS(self) -> str:
        return os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")

    # --- CORS ---
    @property
    def CORS_ALLOWED_ORIGINS(self) -> str:
        return os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:5174")

    @property
    def cors_allowed_origins(self) -> List[str]:
        raw = self.CORS_ALLOWED_ORIGINS
        if not raw:
            return ["http://localhost:5173"]
        return [origin.strip() for origin in raw.split(",") if origin.strip()]

    # --- Paths (computed once from file location) ---
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    @property
    def config_env_path(self) -> str:
        return os.path.join(self.BASE_DIR, "config", ".env")

    @property
    def kg_env_path(self) -> str:
        return os.path.join(self.BASE_DIR, "kg_pipeline", ".env")

    @property
    def root_env_path(self) -> str:
        return os.path.join(self.BASE_DIR, ".env")

    @property
    def faiss_store_path(self) -> str:
        return os.path.join(self.BASE_DIR, "rag_pipeline", "faiss_store")


settings = Settings()
