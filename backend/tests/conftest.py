import pytest
from app.models.all_models import Base
from app.db.session import engine

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    # Base.metadata.drop_all(bind=engine) # Optional: don't drop so we can inspect

@pytest.fixture(autouse=True)
def flush_redis():
    import redis
    from app.core.config import settings
    try:
        r = redis.from_url(settings.REDIS_URL, protocol=2)
        r.flushdb()
    except Exception:
        pass
