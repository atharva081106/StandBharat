import logging
from contextlib import asynccontextmanager
from typing import Any, Callable, cast

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.api import api_router
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.core.limiter import limiter

from fastapi.responses import JSONResponse
from app.core.security import sanitize_error_message

logger = logging.getLogger(__name__)

is_prod = settings.ENVIRONMENT.lower() == "production"

@asynccontextmanager
async def lifespan(_app: FastAPI):
    logger.info("Running StandBharat startup diagnostics...")
    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        logger.warning("Google OAuth configuration is incomplete! GA4/GSC integrations will not function. Please configure GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET.")
    else:
        logger.info("Google OAuth configuration is present.")
        
    if not settings.LINKEDIN_CLIENT_ID or not settings.LINKEDIN_CLIENT_SECRET:
        logger.warning("LinkedIn OAuth configuration is incomplete! LinkedIn publishing will not function. Please configure LINKEDIN_CLIENT_ID and LINKEDIN_CLIENT_SECRET.")
    else:
        logger.info("LinkedIn OAuth configuration is present.")

    try:
        from app.db.session import SessionLocal
        from app.db.seed import ensure_demo_user
        db = SessionLocal()
        ensure_demo_user(db)
        db.close()
    except Exception as e:
        logger.warning(f"Could not auto-seed demo user: {e}")

    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, cast(Callable[..., Any], _rate_limit_exceeded_handler))

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
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
        logger.error(f"Health DB check failed: {e}")
        error_detail = "Database service unavailable" if is_prod else (sanitize_error_message(str(e)) or "Unknown error")
        return JSONResponse(status_code=503, content={"status": "error", "detail": error_detail})

@app.get("/health/redis")
def health_redis():
    import redis
    try:
        r = redis.from_url(settings.REDIS_URL, protocol=2)
        r.ping()
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Health Redis check failed: {e}")
        error_detail = "Cache service unavailable" if is_prod else (sanitize_error_message(str(e)) or "Unknown error")
        return JSONResponse(status_code=503, content={"status": "error", "detail": error_detail})
