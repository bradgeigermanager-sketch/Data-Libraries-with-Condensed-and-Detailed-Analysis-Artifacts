"""
MODULE: auth.py
LOCATION: backend/security/auth.py
USE: Simple API-key based authentication for FastAPI routes.
"""

from fastapi import Header, HTTPException, status, Depends

# Deterministic, explicit key. In production, inject via env.
API_KEY = "CHANGE_ME_SUPERCONSOLE_KEY"
API_KEY_HEADER_NAME = "X-API-Key"


def verify_api_key(x_api_key: str = Header(default=None, alias=API_KEY_HEADER_NAME)):
    """
    NOTATION: API Key Guard.
    USE: Rejects requests without the correct API key.
    """
    if x_api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )
    return True


AuthDependency = Depends(verify_api_key)
