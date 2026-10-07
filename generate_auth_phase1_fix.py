import os
from pathlib import Path

BASE_DIR = Path("backend/app")

# Just rewrite main.py completely to avoid appending issues
main_content = """from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.api import api_router

app = FastAPI(title=settings.PROJECT_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")

@app.get("/")
def root():
    return {"message": "StandBharat API running"}
"""
with open(BASE_DIR / "main.py", "w") as f:
    f.write(main_content)

print("Backend main.py updated.")
