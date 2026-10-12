from pydantic_settings import BaseSettings
from typing import Optional, Union, List
from pydantic import ConfigDict, field_validator, model_validator

class Settings(BaseSettings):
    PROJECT_NAME: str = "StandBharat API"
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    POSTGRES_USER: str = "standbharat_user"
    POSTGRES_PASSWORD: str = "standbharat_password"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: str = "5432"
    POSTGRES_DB: str = "standbharat_db"
    
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    REDIS_URL: str = "redis://localhost:6380/0"
    
    # OAuth configuration
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    LINKEDIN_CLIENT_ID: Optional[str] = None
    LINKEDIN_CLIENT_SECRET: Optional[str] = None
    OAUTH_REDIRECT_URI: str = "http://localhost:8000/api/integrations/oauth/callback"
    GOOGLE_REDIRECT_URI: Optional[str] = None
    FRONTEND_URL: str = "http://localhost:3000"
    
    # Environment & Deployment
    ENVIRONMENT: str = "development"
    CORS_ORIGINS: Union[List[str], str] = ["http://localhost:3000", "http://localhost:5000"]

    # Database Pooling & Connection Reliability
    DB_POOL_PRE_PING: bool = True
    DB_POOL_RECYCLE: int = 1800
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30

    # Storage & Upload Configuration
    STORAGE_BACKEND: str = "local" # "local" or "s3"
    STORAGE_LOCAL_ROOT: str = "storage/documents"
    STORAGE_MAX_UPLOAD_SIZE_BYTES: int = 25 * 1024 * 1024 # 25 MB
    S3_BUCKET_NAME: Optional[str] = None
    S3_ENDPOINT_URL: Optional[str] = None
    S3_REGION_NAME: Optional[str] = "us-east-1"
    S3_ACCESS_KEY_ID: Optional[str] = None
    S3_SECRET_ACCESS_KEY: Optional[str] = None

    # Publishing & Stale Recovery
    STALE_PUBLICATION_TIMEOUT_MINUTES: int = 60

    # Security
    SECURE_COOKIES: Optional[bool] = None

    @field_validator("CORS_ORIGINS", mode="after")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            if v.startswith("[") and v.endswith("]"):
                try:
                    import json
                    return json.loads(v)
                except Exception:
                    pass
            return [x.strip() for x in v.split(",") if x.strip()]
        return v

    @model_validator(mode="after")
    def compute_security_defaults(self):
        if self.SECURE_COOKIES is None:
            self.SECURE_COOKIES = (self.ENVIRONMENT.lower() == "production")
        if self.ENVIRONMENT.lower() == "production":
            if not self.SECRET_KEY or self.SECRET_KEY == "dev-secret-key-change-in-production" or len(self.SECRET_KEY) < 32:
                raise ValueError(
                    "CRITICAL SECURITY DEFECT: In production, SECRET_KEY must be explicitly configured "
                    "with a secure key of at least 32 characters."
                )
            if any(origin.strip() == "*" for origin in (self.CORS_ORIGINS or [])):
                raise ValueError(
                    "CRITICAL SECURITY DEFECT: In production with credentials enabled, CORS_ORIGINS must not contain wildcard '*'."
                )
        return self

    model_config = ConfigDict(env_file=(".env", "../.env"), extra="ignore")

settings = Settings()

