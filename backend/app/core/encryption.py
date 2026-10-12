"""
StandBharat Database Credential Encryption Module
Phase 38B: Dedicated DB Encryption Key & Backward-Compatible Migration

Provides authenticated symmetric encryption (Fernet / AES-128-CBC + HMAC-SHA256)
for integration credentials and sensitive tokens at rest.
Uses dedicated DB_ENCRYPTION_KEY with backward-compatible fallback to legacy SECRET_KEY.
Fails closed on missing or invalid keys and never leaks secrets or ciphertext.
"""

import base64
import logging
from typing import Optional, List
from cryptography.fernet import Fernet, MultiFernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from app.core.config import settings

logger = logging.getLogger(__name__)

# Cryptographic salt constants
LEGACY_KDF_SALT = b"standbharat_salt"
DB_KDF_SALT = b"StandBharat_DB_Encryption_Salt_2026_v1"


class EncryptionError(Exception):
    """Base exception for credential encryption failures."""
    pass


class EncryptionKeyMissingError(EncryptionError):
    """Raised when no valid encryption key is configured."""
    pass


class DecryptionError(EncryptionError):
    """Raised when ciphertext cannot be decrypted due to invalid token or wrong key."""
    pass


def derive_fernet_key(key_str: str, salt: bytes = DB_KDF_SALT) -> bytes:
    """
    Validates or derives a 32-byte URL-safe base64-encoded key suitable for Fernet.
    If the key is already 44 chars (valid Fernet key format), it is used directly.
    Otherwise, PBKDF2-HMAC-SHA256 is used to derive a strong key deterministically.
    """
    if not key_str or not key_str.strip():
        raise EncryptionKeyMissingError("Encryption key string cannot be empty.")
    
    clean_key = key_str.strip()
    try:
        if len(clean_key) == 44:
            decoded = base64.urlsafe_b64decode(clean_key.encode('utf-8'))
            if len(decoded) == 32:
                return clean_key.encode('utf-8')
    except Exception:
        pass

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    derived = kdf.derive(clean_key.encode('utf-8'))
    return base64.urlsafe_b64encode(derived)


def derive_legacy_fernet_key(secret_key: str) -> bytes:
    """Derives a Fernet key from SECRET_KEY using the legacy PBKDF2 salt and configuration."""
    if not secret_key or not secret_key.strip():
        raise EncryptionKeyMissingError("Legacy SECRET_KEY cannot be empty.")
    return derive_fernet_key(secret_key, salt=LEGACY_KDF_SALT)


def get_primary_fernet(db_key: Optional[str] = None) -> Optional[Fernet]:
    """Returns the primary Fernet instance derived from DB_ENCRYPTION_KEY, or None if not set."""
    key = db_key if db_key is not None else settings.DB_ENCRYPTION_KEY
    if key and key.strip():
        derived = derive_fernet_key(key, salt=DB_KDF_SALT)
        return Fernet(derived)
    return None


def get_legacy_fernet(secret_key: Optional[str] = None) -> Optional[Fernet]:
    """Returns the legacy Fernet instance derived from SECRET_KEY, or None if not set."""
    key = secret_key if secret_key is not None else settings.SECRET_KEY
    if key and key.strip():
        derived = derive_legacy_fernet_key(key)
        return Fernet(derived)
    return None


def get_encryption_engine(
    db_key: Optional[str] = None,
    secret_key: Optional[str] = None,
    allow_fallback: Optional[bool] = None
) -> MultiFernet:
    """
    Constructs a MultiFernet engine.
    - If DB_ENCRYPTION_KEY is provided, it is the primary key (first in list).
    - If fallback is allowed and SECRET_KEY is provided, it is added as secondary decryption key.
    - If DB_ENCRYPTION_KEY is not provided, but fallback is allowed, legacy key is used as primary.
    - Fails closed with EncryptionKeyMissingError if no valid keys exist.
    """
    fernets: List[Fernet] = []
    
    # 1. Primary dedicated key
    primary = get_primary_fernet(db_key=db_key)
    if primary:
        fernets.append(primary)
        
    # 2. Legacy fallback key
    use_fallback = (
        allow_fallback if allow_fallback is not None 
        else getattr(settings, "DB_ENCRYPTION_FALLBACK_TO_SECRET_KEY", True)
    )
    
    if use_fallback:
        legacy = get_legacy_fernet(secret_key=secret_key)
        if legacy:
            if not fernets:
                # Fallback becomes primary when DB_ENCRYPTION_KEY is not yet configured
                fernets.append(legacy)
            else:
                # Append legacy as secondary only if distinct from primary
                if fernets[0]._signing_key != legacy._signing_key:
                    fernets.append(legacy)

    if not fernets:
        raise EncryptionKeyMissingError(
            "Database encryption key is not configured. Configure DB_ENCRYPTION_KEY or enable SECRET_KEY fallback."
        )

    return MultiFernet(fernets)


def _get_fernet() -> MultiFernet:
    """Backward-compatible internal getter returning the MultiFernet encryption engine."""
    return get_encryption_engine()


def encrypt(data: Optional[str], engine: Optional[MultiFernet] = None) -> Optional[str]:
    """
    Encrypts plaintext string to a Fernet token.
    Always encrypts using the primary key of the engine (DB_ENCRYPTION_KEY if configured).
    """
    if not data:
        return data
    eng = engine or get_encryption_engine()
    return eng.encrypt(data.encode('utf-8')).decode('utf-8')


def decrypt(data: Optional[str], engine: Optional[MultiFernet] = None) -> Optional[str]:
    """
    Decrypts a Fernet token to plaintext string.
    Supports primary DB_ENCRYPTION_KEY and legacy fallback key via MultiFernet.
    Fails closed: raises DecryptionError on wrong key or corrupted ciphertext.
    Never returns empty string or placeholder credentials on failure.
    """
    if not data:
        return data
    eng = engine or get_encryption_engine()
    try:
        return eng.decrypt(data.encode('utf-8')).decode('utf-8')
    except InvalidToken:
        raise DecryptionError(
            "Failed to decrypt credentials: token invalid, corrupted ciphertext, or incorrect encryption key."
        ) from None
    except Exception as e:
        if isinstance(e, EncryptionError):
            raise
        raise DecryptionError(
            "Failed to decrypt credentials: unauthenticated or corrupted payload."
        ) from None


def re_encrypt(data: Optional[str], engine: Optional[MultiFernet] = None) -> Optional[str]:
    """
    Decrypts ciphertext (using primary or legacy fallback) and re-encrypts it
    strictly under the primary DB_ENCRYPTION_KEY.
    Fails closed if the token cannot be decrypted or if DB_ENCRYPTION_KEY is unset.
    """
    if not data:
        return data
    
    # 1. Decrypt existing ciphertext
    plaintext = decrypt(data, engine=engine)
    
    # 2. Determine primary Fernet
    eng = engine or get_encryption_engine()
    primary = eng._fernets[0]
    
    # Verify that the primary key is indeed the dedicated key when configured
    if not settings.DB_ENCRYPTION_KEY and engine is None:
        raise EncryptionKeyMissingError(
            "Cannot migrate to new key: DB_ENCRYPTION_KEY is not configured in settings."
        )
        
    return primary.encrypt(plaintext.encode('utf-8')).decode('utf-8')


def is_encrypted_with_primary_key(data: Optional[str], engine: Optional[MultiFernet] = None) -> bool:
    """Checks whether a ciphertext token can be decrypted by the primary key."""
    if not data:
        return False
    eng = engine or get_encryption_engine()
    primary = eng._fernets[0]
    try:
        primary.decrypt(data.encode('utf-8'))
        return True
    except Exception:
        return False


def is_encrypted_with_legacy_key(data: Optional[str], secret_key: Optional[str] = None) -> bool:
    """Checks whether a ciphertext token can be decrypted by the legacy SECRET_KEY."""
    if not data:
        return False
    legacy = get_legacy_fernet(secret_key=secret_key)
    if not legacy:
        return False
    try:
        legacy.decrypt(data.encode('utf-8'))
        return True
    except Exception:
        return False


def get_token_key_source(data: Optional[str], engine: Optional[MultiFernet] = None) -> str:
    """
    Inspects a ciphertext token and returns its key version:
    - 'primary': decryptable by primary DB_ENCRYPTION_KEY
    - 'legacy': decryptable only by legacy SECRET_KEY
    Raises DecryptionError if unreadable by either key.
    """
    if not data:
        return "empty"
    eng = engine or get_encryption_engine()
    primary = eng._fernets[0]
    try:
        primary.decrypt(data.encode('utf-8'))
        return "primary"
    except Exception:
        pass
    
    if len(eng._fernets) > 1:
        for secondary in eng._fernets[1:]:
            try:
                secondary.decrypt(data.encode('utf-8'))
                return "legacy"
            except Exception:
                pass

    raise DecryptionError("Token cannot be decrypted by either primary or legacy keys.")
