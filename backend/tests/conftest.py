import pytest
from app.models.all_models import Base
from app.db.session import engine

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    try:
        Base.metadata.create_all(bind=engine)
    except Exception:
        pass
    yield

@pytest.fixture(autouse=True)
def flush_redis():
    import redis
    from app.core.config import settings
    try:
        r = redis.from_url(settings.REDIS_URL, protocol=2, socket_timeout=0.2, socket_connect_timeout=0.2)
        r.flushdb()
    except Exception:
        pass
