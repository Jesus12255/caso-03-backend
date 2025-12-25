from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "FastAPI Enterprise Backend"
    API_V1_STR: str = "/api/v1"
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    LOG_LEVEL: str = "INFO"

    LLM_API_KEY: str = "AIzaSyBubJog4BJoN2PwkBtyg7P5c_iivYZoHts" 
    # LLM_BASE_URL no longer needed for Gemini by default, but kept or refactored if needed.
    # LLM_BASE_URL: str = "https://generativelanguage.googleapis.com" 
    LLM_MODEL_NAME: str = "gemini-2.5-flash"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore"
    )

settings = Settings()
