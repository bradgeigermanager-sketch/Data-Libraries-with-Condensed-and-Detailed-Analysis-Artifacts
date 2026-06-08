"""
MODULE: search_api.py
LOCATION: backend/api/search_api.py
NOTATION: Search API
USE: Exposes full-text, title, and multi-field search for the logic graph.
"""

from fastapi import APIRouter, Query
from uuid import UUID

from backend.db.repository import LogicRepository


def build_search_api(repository: LogicRepository):
    """
    NOTATION: API Builder.
    USE: Returns a configured FastAPI router for search operations.
    """

    router = APIRouter(prefix="/search", tags=["search"])

    # ------------------------------------------------------------
    # TITLE SEARCH
    # ------------------------------------------------------------

    @router.get("/title")
    def search_by_title(q: str = Query(..., description="Title search query")):
        """
        NOTATION: Title Search Endpoint.
        USE: Returns artifacts whose titles match the query.
        """
        rows = repository.search_by_title(q)
        return {"query": q, "results": rows}

    # ------------------------------------------------------------
    # FULL-TEXT SEARCH
    # ------------------------------------------------------------

    @router.get("/text")
    def search_by_text(q: str = Query(..., description="Full-text search query")):
        """
        NOTATION: Full-Text Search Endpoint.
        USE: Searches condensed_logic + verbose_desc fields.
        """
        rows = repository.search_full_text(q)
        return {"query": q, "results": rows}

    # ------------------------------------------------------------
    # TAG / FIELD SEARCH
    # ------------------------------------------------------------

    @router.get("/field")
    def search_by_field(
        field: str = Query(..., description="Field name"),
        value: str = Query(..., description="Field value"),
    ):
        """
        NOTATION: Field Search Endpoint.
        USE: Searches artifacts by a specific field (e.g., category).
        """
        rows = repository.search_by_field(field, value)
        return {"field": field, "value": value, "results": rows}

    # ------------------------------------------------------------
    # MULTI-CRITERIA SEARCH
    # ------------------------------------------------------------

    @router.post("/multi")
    def multi_criteria_search(payload: dict):
        """
        NOTATION: Multi-Criteria Search Endpoint.
        USE: Allows compound search queries across multiple fields.
        """
        criteria = payload.get("criteria", {})
        rows = repository.search_multi(criteria)
        return {"criteria": criteria, "results": rows}

    # ------------------------------------------------------------
    # FUZZY SEARCH (optional)
    # ------------------------------------------------------------

    @router.get("/fuzzy")
    def fuzzy_search(q: str = Query(..., description="Fuzzy search query")):
        """
        NOTATION: Fuzzy Search Endpoint.
        USE: Optional fuzzy matching for approximate queries.
        """
        rows = repository.search_fuzzy(q)
        return {"query": q, "results": rows}

    # ------------------------------------------------------------
    # ARTIFACT PREVIEW
    # ------------------------------------------------------------

    @router.get("/preview/{artifact_id}")
    def preview_artifact(artifact_id: UUID):
        """
        NOTATION: Artifact Preview Endpoint.
        USE: Returns a lightweight preview for search result cards.
        """
        row = repository.get_artifact(artifact_id)

        if not row:
            return {"artifact": None}

        preview = {
            "artifact_id": row["artifact_id"],
            "title": row["title"],
            "condensed_logic": row["condensed_logic"],
            "artifact_category": row["artifact_category"],
        }

        return {"preview": preview}

    return router
