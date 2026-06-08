"""
MODULE: relationships.py
LOCATION: backend/logic_core/relationships.py
NOTATION: Canonical relationship types and validation logic.
USE: Provides a unified vocabulary for all graph edges.
"""

from dataclasses import dataclass
from typing import Set


# ------------------------------------------------------------
# RELATIONSHIP TYPE REGISTRY
# ------------------------------------------------------------

# Core semantic relationships
LOGICAL_RELATIONSHIPS: Set[str] = {
    "implies",
    "extends",
    "contradicts",
    "equivalent_to",
}

# Structural / system relationships
SYSTEM_RELATIONSHIPS: Set[str] = {
    "relates_to",
    "references",
    "derived_from",
}

# Versioning lineage
VERSIONING_RELATIONSHIPS: Set[str] = {
    "supersedes",
    "deprecated_by",
}

# Template / code relationships
TEMPLATE_RELATIONSHIPS: Set[str] = {
    "implements",
    "instantiates",
}

# Full canonical set
ALL_RELATIONSHIPS: Set[str] = (
    LOGICAL_RELATIONSHIPS
    | SYSTEM_RELATIONSHIPS
    | VERSIONING_RELATIONSHIPS
    | TEMPLATE_RELATIONSHIPS
)


# ------------------------------------------------------------
# VALIDATION LOGIC
# ------------------------------------------------------------

def is_valid_relationship(rel_type: str) -> bool:
    """
    NOTATION: Relationship Validator.
    USE: Ensures ingestion + UI only create valid edge types.
    """
    return rel_type in ALL_RELATIONSHIPS


def require_valid_relationship(rel_type: str):
    """
    NOTATION: Strict Validator.
    USE: Raises an error if an invalid relationship is used.
    """
    if rel_type not in ALL_RELATIONSHIPS:
        raise ValueError(
            f"Invalid relationship type '{rel_type}'. "
            f"Must be one of: {sorted(ALL_RELATIONSHIPS)}"
        )


# ------------------------------------------------------------
# RELATIONSHIP CATEGORY HELPERS
# ------------------------------------------------------------

def is_logical(rel_type: str) -> bool:
    return rel_type in LOGICAL_RELATIONSHIPS


def is_versioning(rel_type: str) -> bool:
    return rel_type in VERSIONING_RELATIONSHIPS


def is_template_binding(rel_type: str) -> bool:
    return rel_type in TEMPLATE_RELATIONSHIPS


def is_structural(rel_type: str) -> bool:
    return rel_type in SYSTEM_RELATIONSHIPS
