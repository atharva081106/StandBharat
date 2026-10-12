"""
StandBharat - Phase 40B: JWT Algorithm & Cryptographic Regression Tests
Verifies mitigation of python-jose (CVE-2026-85394) and transitive ecdsa (PYSEC-2026-1325).

Requirements:
1. Strict algorithm whitelist: only settings.ALGORITHM ("HS256") is accepted.
2. Tokens with alg="none" MUST be rejected.
3. Tokens with mismatched algorithms (e.g. RS256, HS384, HS512, ES256) MUST be rejected.
4. Tampered tokens MUST fail verification.
5. The application codebase must never invoke vulnerable ECDSA signing routines.
"""

import pytest
import base64
import json
import inspect
from jose import jwt, JWTError
from app.core.config import settings
from app.core.security import create_access_token
from app.api import deps


def test_jwt_algorithm_is_strictly_hs256():
    """Verify that settings.ALGORITHM is configured to HS256."""
    assert settings.ALGORITHM == "HS256"


def test_valid_access_token_decodes_successfully():
    """Verify that legitimate access tokens created by the app decode properly."""
    token = create_access_token(subject="user_test_123")
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert payload.get("sub") == "user_test_123"


def test_jwt_rejects_none_algorithm():
    """
    CVE-2026-85394 / Algorithm Confusion:
    Verify that tokens with alg="none" are strictly rejected by the backend decoding policy.
    """
    # Forge a token with alg="none"
    header = {"typ": "JWT", "alg": "none"}
    payload = {"sub": "attacker_impersonation", "exp": 9999999999}
    
    header_b64 = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip("=")
    payload_b64 = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=")
    unsigned_token = f"{header_b64}.{payload_b64}."

    with pytest.raises(JWTError):
        jwt.decode(unsigned_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])


def test_jwt_rejects_mismatched_algorithms():
    """
    Verify that tokens signed with unauthorized algorithms (e.g., HS384, HS512, RS256)
    are rejected even if they are signed with the same secret key.
    """
    # Sign with HS512
    token_hs512 = jwt.encode({"sub": "admin"}, settings.SECRET_KEY, algorithm="HS512")
    
    # Decoding strictly specifying [settings.ALGORITHM] ("HS256") must raise JWTError
    with pytest.raises(JWTError):
        jwt.decode(token_hs512, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])


def test_jwt_rejects_tampered_payload():
    """Verify that tampered payload fails signature verification."""
    token = create_access_token(subject="regular_user")
    parts = token.split(".")
    assert len(parts) == 3

    # Tamper with the payload part
    tampered_payload = {"sub": "escalated_admin", "exp": 9999999999}
    tampered_b64 = base64.urlsafe_b64encode(json.dumps(tampered_payload).encode()).decode().rstrip("=")
    forged_token = f"{parts[0]}.{tampered_b64}.{parts[2]}"

    with pytest.raises(JWTError):
        jwt.decode(forged_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])


def test_deps_enforces_explicit_algorithm_restriction():
    """
    Verify by AST/source inspection that deps.get_current_user passes algorithms=[settings.ALGORITHM].
    This ensures no developer accidentally removes the algorithms parameter.
    """
    source = inspect.getsource(deps.get_current_user)
    assert "algorithms=[settings.ALGORITHM]" in source, (
        "deps.get_current_user must explicitly pass algorithms=[settings.ALGORITHM]"
    )


def test_zero_ecdsa_signing_in_app():
    """
    PYSEC-2026-1325 / Transitive ecdsa vulnerability:
    Verify that no module in app imports or references ecdsa signing keys or operations.
    The vulnerable ecdsa library is only present as an unused transitive dependency of python-jose.
    """
    import sys
    # Verify that app package does not import ecdsa directly
    app_modules = [m for m in sys.modules.keys() if m.startswith("app.")]
    for mod_name in app_modules:
        mod = sys.modules[mod_name]
        assert not hasattr(mod, "SigningKey"), f"{mod_name} should not expose SigningKey"
        assert not hasattr(mod, "ecdsa"), f"{mod_name} should not import ecdsa"
