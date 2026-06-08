"""
MODULE: test_rbac.py
LOCATION: tests/security/test_rbac.py
NOTATION: RBAC Test Suite
USE: Validates explicit role → permission enforcement.
"""

import pytest
from fastapi.testclient import TestClient

from main import app
from backend.security.rbac import ROLES, ROLE_HEADER

client = TestClient(app)


# ------------------------------------------------------------
# HELPERS
# ------------------------------------------------------------

def authed_get(url: str, role: str):
    return client.get(url, headers={ROLE_HEADER: role})

def authed_post(url: str, role: str, json=None):
    return client.post(url, headers={ROLE_HEADER: role}, json=json or {})


# ------------------------------------------------------------
# ROLE EXISTENCE
# ------------------------------------------------------------

def test_roles_are_explicit():
    assert "admin" in ROLES
    assert "reader" in ROLES
    assert "operator" in ROLES

    # No implicit roles
    assert "superuser" not in ROLES
    assert "guest" not in ROLES


# ------------------------------------------------------------
# PERMISSION: READ
# ------------------------------------------------------------

@pytest.mark.parametrize("role,allowed", [
    ("admin", True),
    ("operator", True),
    ("reader", True),
])
def test_read_permission(role, allowed):
    resp = authed_get("/browse/artifacts", role)
    if allowed:
        assert resp.status_code == 200
    else:
        assert resp.status_code in (401, 403)


# ------------------------------------------------------------
# PERMISSION: WRITE (admin + operator)
# ------------------------------------------------------------

@pytest.mark.parametrize("role,allowed", [
    ("admin", True),
    ("operator", True),
    ("reader", False),
])
def test_write_permission(role, allowed):
    resp = authed_post("/admin/update", role, json={"foo": "bar"})
    if allowed:
        assert resp.status_code == 200
    else:
        assert resp.status_code == 403


# ------------------------------------------------------------
# PERMISSION: INGEST (admin + operator)
# ------------------------------------------------------------

@pytest.mark.parametrize("role,allowed", [
    ("admin", True),
    ("operator", True),
    ("reader", False),
])
def test_ingest_permission(role, allowed):
    resp = authed_post("/admin/ingest", role, json={"payload": "x"})
    if allowed:
        assert resp.status_code == 200
    else:
        assert resp.status_code == 403


# ------------------------------------------------------------
# PERMISSION: HARVEST (admin only)
# ------------------------------------------------------------

@pytest.mark.parametrize("role,allowed", [
    ("admin", True),
    ("operator", False),
    ("reader", False),
])
def test_harvest_permission(role, allowed):
    resp = authed_post("/admin/harvest/category", role, json={"category": "test"})
    if allowed:
        assert resp.status_code == 200
    else:
        assert resp.status_code == 403


# ------------------------------------------------------------
# PERMISSION: MANAGE JOBS (admin + operator)
# ------------------------------------------------------------

@pytest.mark.parametrize("role,allowed", [
    ("admin", True),
    ("operator", True),
    ("reader", False),
])
def test_manage_jobs_permission(role, allowed):
    resp = authed_get("/admin/jobs", role)
    if allowed:
        assert resp.status_code == 200
    else:
        assert resp.status_code == 403


# ------------------------------------------------------------
# UNKNOWN ROLE
# ------------------------------------------------------------

def test_unknown_role_rejected():
    resp = authed_get("/browse/artifacts", "unknown_role")
    assert resp.status_code == 401
    assert "Unknown or missing role" in resp.text


# ------------------------------------------------------------
# MISSING ROLE
# ------------------------------------------------------------

def test_missing_role_header_rejected():
    resp = client.get("/browse/artifacts")
    assert resp.status_code == 401
