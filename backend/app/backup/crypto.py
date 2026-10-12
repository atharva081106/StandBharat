"""
StandBharat Backup Cryptography Module
Provides authenticated symmetric encryption (Fernet / AES-128-CBC + HMAC-SHA256)
and cryptographic checksumming for PostgreSQL backup artifacts.
Never logs or leaks encryption keys or plaintext contents.
"""

import os
import base64
import hashlib
from typing import Optional
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

from app.core.security import sanitize_error_message

# Constant salt for deterministic key derivation from passphrases
BACKUP_KDF_SALT = b"StandBharat_PG_Backup_Salt_2026_v1"
CHUNK_SIZE = 64 * 1024  # 64 KB streaming buffer

class BackupCryptoError(Exception):
    """Raised when cryptographic operations fail."""
    pass

class BackupDecryptionError(BackupCryptoError):
    """Raised when decryption fails due to an invalid key or corrupted artifact."""
    pass


def get_fernet_key(key_str: str) -> bytes:
    """
    Validates or derives a 32-byte URL-safe base64-encoded key suitable for Fernet.
    If the key is already 44 chars (valid Fernet key format), it is used directly.
    Otherwise, PBKDF2-HMAC-SHA256 is used to derive a strong key deterministically.
    """
    if not key_str:
        raise BackupCryptoError("Encryption key cannot be empty.")
    
    clean_key = key_str.strip()
    try:
        if len(clean_key) == 44:
            decoded = base64.urlsafe_b64decode(clean_key.encode('utf-8'))
            if len(decoded) == 32:
                return clean_key.encode('utf-8')
    except Exception:
        pass

    # Deterministically derive 32 bytes from passphrase
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=BACKUP_KDF_SALT,
        iterations=100000,
        backend=default_backend()
    )
    derived = kdf.derive(clean_key.encode('utf-8'))
    return base64.urlsafe_b64encode(derived)


def compute_file_sha256(file_path: str) -> str:
    """Calculates the SHA-256 hex digest of a file in streaming chunks."""
    if not os.path.exists(file_path):
        raise BackupCryptoError(f"Target file does not exist: {file_path}")
    
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        while True:
            chunk = f.read(CHUNK_SIZE)
            if not chunk:
                break
            hasher.update(chunk)
    return hasher.hexdigest()


def encrypt_file(source_path: str, target_path: str, key_str: str) -> None:
    """
    Encrypts source_path using authenticated Fernet encryption and writes to target_path.
    Never prints or stores the key in plaintext.
    """
    try:
        fernet_key = get_fernet_key(key_str)
        fernet = Fernet(fernet_key)
        
        with open(source_path, "rb") as src_file:
            plaintext = src_file.read()
            
        ciphertext = fernet.encrypt(plaintext)
        
        tmp_target = f"{target_path}.tmp"
        with open(tmp_target, "wb") as dst_file:
            dst_file.write(ciphertext)
            
        os.replace(tmp_target, target_path)
    except Exception as e:
        if 'tmp_target' in locals() and os.path.exists(tmp_target):
            try:
                os.remove(tmp_target)
            except OSError:
                pass
        sanitized = sanitize_error_message(str(e))
        raise BackupCryptoError(f"Encryption failed: {sanitized}") from None


def decrypt_file(source_path: str, target_path: str, key_str: str) -> None:
    """
    Decrypts source_path using Fernet and writes decrypted bytes to target_path.
    Raises BackupDecryptionError if the key is incorrect or the ciphertext is tampered.
    """
    try:
        fernet_key = get_fernet_key(key_str)
        fernet = Fernet(fernet_key)
        
        with open(source_path, "rb") as src_file:
            ciphertext = src_file.read()
            
        plaintext = fernet.decrypt(ciphertext)
        
        tmp_target = f"{target_path}.tmp"
        with open(tmp_target, "wb") as dst_file:
            dst_file.write(plaintext)
            
        os.replace(tmp_target, target_path)
    except InvalidToken:
        if 'tmp_target' in locals() and os.path.exists(tmp_target):
            try:
                os.remove(tmp_target)
            except OSError:
                pass
        raise BackupDecryptionError("Decryption failed: Invalid encryption key or corrupted backup artifact.") from None
    except Exception as e:
        if 'tmp_target' in locals() and os.path.exists(tmp_target):
            try:
                os.remove(tmp_target)
            except OSError:
                pass
        sanitized = sanitize_error_message(str(e))
        raise BackupCryptoError(f"Decryption failed: {sanitized}") from None
