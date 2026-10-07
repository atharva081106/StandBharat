import os
from pathlib import Path

BASE_DIR = Path("backend")

dirs = [
    "app/api",
    "app/api/endpoints",
    "app/core",
    "app/db",
    "app/models",
    "app/schemas",
    "app/services",
    "app/agents",
    "app/ai",
    "app/orchestration",
    "app/workers",
    "app/integrations",
    "app/storage",
    "tests/api",
    "tests/crud",
    "tests/workers",
    "tests/e2e",
]

for d in dirs:
    os.makedirs(BASE_DIR / d, exist_ok=True)
    # create __init__.py
    with open(BASE_DIR / d / "__init__.py", "w") as f:
        pass

# app/core/config.py
with open(BASE_DIR / "app/core/config.py", "w") as f:
    f.write('''from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "StandBharat API"
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    DATABASE_URL: str = "postgresql://standbharat_user:standbharat_password@localhost:5432/standbharat_db"
    REDIS_URL: str = "redis://localhost:6379/0"

    class Config:
        env_file = "../.env"

settings = Settings()
''')

# app/db/session.py
with open(BASE_DIR / "app/db/session.py", "w") as f:
    f.write('''from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
''')

# app/db/base_class.py
with open(BASE_DIR / "app/db/base_class.py", "w") as f:
    f.write('''from typing import Any
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy import Column, DateTime
from sqlalchemy.sql import func

@as_declarative()
class Base:
    id: Any
    __name__: str
    
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()
        
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
''')

# app/db/base.py
with open(BASE_DIR / "app/db/base.py", "w") as f:
    f.write('''from app.db.base_class import Base
# import all models here so Alembic can see them
# from app.models.user import User
# from app.models.workspace import Workspace
''')

# app/main.py
with open(BASE_DIR / "app/main.py", "w") as f:
    f.write('''from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

app = FastAPI(title=settings.PROJECT_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "StandBharat API running"}
''')

print("Backend base files created.")
