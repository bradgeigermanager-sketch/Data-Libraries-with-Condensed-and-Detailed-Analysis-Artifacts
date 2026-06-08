"""
MODULE: resolver.py
LOCATION: backend/ingestion/resolver.py
NOTATION: Artifact Resolver
USE: Maps human-readable titles to canonical artifact UUIDs.
"""

from typing import Optional
from uuid import UUID

from backend.db.repository import LogicRepository


class ArtifactResolver:
    """
    NOTATION: Resolver.
    USE: Provides deterministic resolution of titles → artifact UUIDs.

    Supports:
        - exact title match
        - optional fuzzy match hook
        - alias resolution (future extension)
    """

    def __init__(self, repository: LogicRepository):
        self.repo = repository

    # ------------------------------------------------------------
    # PUBLIC API
    # ------------------------------------------------------------

    def resolve(self, title: str) -> Optional[UUID]:
        """
        NOTATION: Primary Resolver.
        USE: Returns UUID if artifact exists, else None.
        """
        # 1. Exact match
        row = self.repo.find_artifact_by_title(title)
        if row:
            return UUID(row["artifact_id"])

        # 2. Alias match (future extension)
        alias_hit = self._resolve_alias(title)
        if alias_hit:
            return alias_hit

        # 3. Fuzzy match (optional)
        fuzzy_hit = self._resolve_fuzzy(title)
        if fuzzy_hit:
            return fuzzy_hit

        return None

    # ------------------------------------------------------------
    # INTERNAL HOOKS
    # ------------------------------------------------------------

    def _resolve_alias(self, title: str) -> Optional[UUID]:
        """
        NOTATION: Alias Resolver.
        USE: Placeholder for alias tables or metadata-based resolution.
        """
        return None  # reserved for future alias system

    def _resolve_fuzzy(self, title: str) -> Optional[UUID]:
        """
        NOTATION: Fuzzy Resolver.
        USE: Optional hook for approximate matching (disabled by default).
        """
        return None  # reserved for optional fuzzy matching
