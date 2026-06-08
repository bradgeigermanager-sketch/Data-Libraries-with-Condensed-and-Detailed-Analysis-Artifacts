"""
MODULE: auth_gateway.py
LOCATION: backend/api/auth_gateway.py
USE: Username/password login → session cookie with role.
"""

from fastapi import APIRouter, Response, HTTPException, status
from pydantic import BaseModel

from backend.security.session import (
    create_session_cookie,
    SESSION_COOKIE_NAME,
)
from backend.security.rbac import ROLES

router = APIRouter(prefix="/auth", tags=["auth"])


# Static user → role map (explicit)
USERS = {
    "admin": {"password": "adminpass", "role": "admin"},
    "operator": {"password": "operatorpass", "role": "operator"},
    "reader": {"password": "readerpass", "role": "reader"},
}


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/login")
def login(payload: LoginRequest, response: Response):
    user = USERS.get(payload.username)
    if not user or user["password"] != payload.password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    role = user["role"]
    if role not in ROLES:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="User role not configured")

    cookie_value = create_session_cookie(role)
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=cookie_value,
        httponly=True,
        secure=False,  # set True behind HTTPS in prod
        samesite="Lax",
        path="/",
    )
    return {"role": role}


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(SESSION_COOKIE_NAME, path="/")
    return {"status": "logged_out"}
