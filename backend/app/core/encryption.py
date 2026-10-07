import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from app.core.config import settings

def _get_fernet() -> Fernet:
    # Use PBKDF2 to derive a 32-byte url-safe base64 key from the SECRET_KEY
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=b"standbharat_salt", # Fixed salt for deterministic key derivation
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(settings.SECRET_KEY.encode()))
    return Fernet(key)

def encrypt(data: str) -> str:
    if not data:
        return data
    f = _get_fernet()
    return f.encrypt(data.encode()).decode()

def decrypt(data: str) -> str:
    if not data:
        return data
    f = _get_fernet()
    return f.decrypt(data.encode()).decode()
