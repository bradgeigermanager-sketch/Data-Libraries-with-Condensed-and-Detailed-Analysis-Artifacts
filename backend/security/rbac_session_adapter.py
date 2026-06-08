"""
MODULE: rbac_session_adapter.py
LOCATION: backend/security/rbac_session_adapter.py
USE: RBAC guard that reads role from session cookie.
"""

from fastapi import Depends, Request, HTTPException, status

from backend.security.rbac import ROLES
from backend.security.session import get_role_from_session


def require_permission_session(permission: str):
    """
    USE: Same semantics as require_permission, but role comes from session cookie.
    """

    def guard(request: Request):
        role = get_role_from_session(request)
        if role not in ROLES:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unknown role in session",
            )

        perms = ROLES[role]
        if not perms.get(permission, False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{role}' lacks permission '{permission}'",
            )
        return True

    return Depends(guard)
