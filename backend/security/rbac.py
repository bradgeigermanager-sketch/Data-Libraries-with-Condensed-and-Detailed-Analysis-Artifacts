"""
MODULE: rbac.py
LOCATION: backend/security/rbac.py
USE: Explicit role-based access control for FastAPI routes.
"""

from fastapi import Header, HTTPException, status, Depends

# Explicit role → permission map
ROLES = {
    "admin": {
        "can_read": True,
        "can_write": True,
        "can_ingest": True,
        "can_harvest": True,
        "can_manage_jobs": True,
    },
    "reader": {
        "can_read": True,
        "can_write": False,
        "can_ingest": False,
        "can_harvest": False,
        "can_manage_jobs": False,
    },
    "operator": {
        "can_read": True,
        "can_write": True,
        "can_ingest": True,
        "can_harvest": False,
        "can_manage_jobs": True,
    },
}

ROLE_HEADER = "X-User-Role"


def require_permission(permission: str):
    """
    NOTATION: Permission Guard Factory.
    USE: Returns a dependency that enforces a specific permission.
    """

    def guard(role: str = Header(default=None, alias=ROLE_HEADER)):
        if role not in ROLES:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unknown or missing role",
            )

        perms = ROLES[role]

        if not perms.get(permission, False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{role}' lacks permission '{permission}'",
            )

        return True

    return Depends(guard)
