import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class AIConfig(BaseSettings):
    OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY", None)
    ANTHROPIC_API_KEY: str | None = os.getenv("ANTHROPIC_API_KEY", None)
    GEMINI_API_KEY: str | None = os.getenv("GEMINI_API_KEY", None)
    MISTRAL_API_KEY: str | None = os.getenv("MISTRAL_API_KEY", None)
    GROQ_API_KEY: str | None = os.getenv("GROQ_API_KEY", None)
    
    DEFAULT_PROVIDER: str = os.getenv("DEFAULT_PROVIDER", "mistral")
    DEFAULT_MODEL: str = os.getenv("DEFAULT_MODEL", "mistral-small-latest")
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

ai_config = AIConfig()
