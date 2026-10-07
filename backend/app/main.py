from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.api import api_router

app = FastAPI(title=settings.PROJECT_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")

@app.get("/")
def root():
    return {"message": "StandBharat API running"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/health/db")
def health_db():
    from app.db.session import engine
    from sqlalchemy import text
    try:
        with engine.connect() as conn:
            version = conn.execute(text("SELECT version();")).scalar()
            return {"status": "ok", "version": version}
    except Exception as e:
        return {"status": "error", "detail": str(e)}

@app.get("/health/redis")
def health_redis():
    import redis
    try:
        r = redis.from_url(settings.REDIS_URL, protocol=2)
        r.ping()
        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}
