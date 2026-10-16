from slowapi import Limiter
from slowapi.util import get_remote_address
from starlette.requests import Request
from app.core.config import settings

def get_client_id(request: Request) -> str:
    """
    Returns user ID if authenticated, else remote IP address.
    Does not trust spoofable headers (uses request.client.host instead of get_remote_address
    unless behind a trusted proxy, but here we strictly use request.client.host).
    """
    # Check for authentication token in cookies
    token = request.cookies.get("access_token")
    if not token:
        # Check header
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            
    if token:
        # Decode token to get user id (we'll just use the token string itself as a hash for limiting
        # to avoid hitting DB or importing JWT decode logic here if it's too expensive, 
        # but decoding JWT is also fast)
        from jose import jwt  # type: ignore
        from app.core.config import settings
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            user_id: str = payload.get("sub")
            if user_id:
                return f"user:{user_id}"
        except Exception:
            pass

    # Fallback to IP address (ignoring proxy headers like X-Forwarded-For)
    # request.client.host gives the real connecting IP. If behind a proxy, 
    # we would need the proxy to be configured correctly in Uvicorn (--proxy-headers).
    return f"ip:{request.client.host if request.client else '127.0.0.1'}"

limiter = Limiter(
    key_func=get_client_id,
    storage_uri=settings.REDIS_URL,
    default_limits=["100/minute"],
)
