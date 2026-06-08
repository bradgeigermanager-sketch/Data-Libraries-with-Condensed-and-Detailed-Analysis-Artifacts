"""
MODULE: session.py
LOCATION: backend/security/session.py
USE: Cookie-based session with signed role token.
"""

import hmac
import hashlib
from fastapi import Request, HTTPException, status

SESSION_COOKIE_NAME = "logic_session"
SESSION_SECRET = b"CHANGE_ME_SESSION_SECRET"  # inject via env in prod


def _sign(value: str) -> str:
    sig = hmac.new(SESSION_SECRET, value.encode("utf-8"), hashlib.sha256).hexdigest()
    return f"{value}.{sig}"


def _verify(signed_value: str) -> str:
    try:
        value, sig = signed_value.rsplit(".", 1)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session token")

    expected = hmac.new(SESSION_SECRET, value.encode("utf-8"), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(sig, expected):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session signature")
    return value


def create_session_cookie(role: str) -> str:
    """
    USE: Returns signed cookie value for a given role.
    """
    return _sign(role)


def get_role_from_session(request: Request) -> str:
    """
    USE: Extracts and verifies role from session cookie.
    """
    cookie = request.cookies.get(SESSION_COOKIE_NAME)
    if not cookie:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing session")
    return _verify(cookie)
