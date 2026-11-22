import base64
import hashlib
import hmac
import json
import secrets
import time
from typing import Any, Dict, Optional
from backend.app.core.config import settings

def hash_password(password: str) -> str:
    # shortcut: PBKDF2-HMAC-SHA256 with random salt, upgrade to argon2/bcrypt in prod cluster
    salt = secrets.token_hex(16)
    key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000)
    return f"{salt}:{key.hex()}"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        salt, expected_key = hashed_password.split(":")
        key = hashlib.pbkdf2_hmac("sha256", plain_password.encode("utf-8"), salt.encode("utf-8"), 100000)
        return hmac.compare_digest(key.hex(), expected_key)
    except Exception:
        return False

def _b64encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")

def _b64decode(s: str) -> bytes:
    padding = "=" * ((4 - len(s) % 4) % 4)
    return base64.urlsafe_b64decode(s + padding)

def create_access_token(data: Dict[str, Any], expires_delta: Optional[int] = None) -> str:
    # shortcut: zero-dependency standard HS256 JWT, replace with python-jose if needed
    header = {"alg": "HS256", "typ": "JWT"}
    expire = int(time.time()) + (expires_delta or settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60)
    payload = {**data, "exp": expire}

    seg_header = _b64encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    seg_payload = _b64encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    signing_input = f"{seg_header}.{seg_payload}".encode("utf-8")

    signature = hmac.new(settings.SECRET_KEY.encode("utf-8"), signing_input, hashlib.sha256).digest()
    seg_sig = _b64encode(signature)
    return f"{seg_header}.{seg_payload}.{seg_sig}"

def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None
        seg_header, seg_payload, seg_sig = parts
        signing_input = f"{seg_header}.{seg_payload}".encode("utf-8")
        expected_sig = hmac.new(settings.SECRET_KEY.encode("utf-8"), signing_input, hashlib.sha256).digest()
        actual_sig = _b64decode(seg_sig)
        if not hmac.compare_digest(actual_sig, expected_sig):
            return None
        payload = json.loads(_b64decode(seg_payload).decode("utf-8"))
        if payload.get("exp", 0) < int(time.time()):
            return None
        return payload
    except Exception:
        return None
