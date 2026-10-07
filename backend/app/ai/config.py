import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class AIConfig(BaseSettings):
    OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY", None)
    ANTHROPIC_API_KEY: str | None = os.getenv("ANTHROPIC_API_KEY", None)
    GEMINI_API_KEY: str | None = os.getenv("GEMINI_API_KEY", None)
    
    DEFAULT_PROVIDER: str = "openai"
    DEFAULT_MODEL: str = "gpt-4o"
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

ai_config = AIConfig()
