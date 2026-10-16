from datetime import datetime, timedelta
from typing import Optional, Any, Union
from jose import jwt  # type: ignore
import bcrypt
from app.core.config import settings

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        pw_bytes = plain_password.encode('utf-8')[:72]
        hash_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(pw_bytes, hash_bytes)
    except Exception:
        return False

def get_password_hash(password: str) -> str:
    pw_bytes = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pw_bytes, salt).decode('utf-8')

def create_access_token(subject: Union[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

import re

def sanitize_error_message(message: Optional[str]) -> Optional[str]:
    """
    Sanitizes error messages to prevent leaking credentials, bearer tokens,
    API keys, passwords, client secrets, or sensitive URL query parameters.
    """
    if not message:
        return message
    msg = message
    # Redact URL basic auth: https://user:pass@host
    msg = re.sub(r'://([^:]+):([^@]+)@', r'://\1:[REDACTED]@', msg)
    # Redact Authorization header / Bearer token
    msg = re.sub(r'(bearer\s+)[a-zA-Z0-9_\-\.]{10,}', r'\1[REDACTED]', msg, flags=re.IGNORECASE)
    # Redact JSON / query param fields for secrets
    msg = re.sub(r'((?:access_token|refresh_token|client_secret|api_key|apikey|password|pgpassword|backup_encryption_key|db_encryption_key|encryption_key|secret|code)["\':=\s]+)[a-zA-Z0-9_\-\.]{8,}', r'\1[REDACTED]', msg, flags=re.IGNORECASE)
    # Redact URL query strings for tokens
    msg = re.sub(r'([?&](?:access_token|code|client_secret|refresh_token|token|pgpassword|key)=)[^&\s"\']+', r'\1[REDACTED]', msg, flags=re.IGNORECASE)
    # Redact 44-character base64 Fernet keys
    msg = re.sub(r'\b[A-Za-z0-9_-]{43}=\b', r'[REDACTED_ENCRYPTION_KEY]', msg)
    return msg

