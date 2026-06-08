"""
MODULE: contradiction_api.py
LOCATION: backend/api/contradiction_api.py
NOTATION: Contradiction API
USE: Exposes contradiction analysis endpoints for the logic graph.
"""

from fastapi import APIRouter
from uuid import UUID

from backend.analysis.contradiction_engine import ContradictionEngine
from backend.db.repository import LogicRepository


def build_contradiction_api(
    repository: LogicRepository,
    contradiction_engine: ContradictionEngine,
):
    """
    NOTATION: API Builder.
    USE: Returns a configured FastAPI router for contradiction inspection.
    """

    router = APIRouter(prefix="/contradictions", tags=["contradictions"])

    # ------------------------------------------------------------
    # ARTIFACT-LEVEL CONTRADICTIONS
    # ------------------------------------------------------------

    @router.get("/artifact/{artifact_id}")
    def get_artifact_contradictions(artifact_id: UUID):
        """
        NOTATION: Artifact Contradiction Endpoint.
        USE: Returns contradictions for a single artifact.
        """
        contradictions = contradiction_engine.analyze_artifact(artifact_id)
        return {
            "artifact_id": str(artifact_id),
            "contradictions": contradictions,
        }

    # ------------------------------------------------------------
    # FULL GRAPH CONTRADICTIONS
    # ------------------------------------------------------------

    @router.get("/all")
    def get_all_contradictions():
        """
        NOTATION: Full Graph Contradiction Endpoint.
        USE: Returns all contradictions in the system.
        """
        contradictions = contradiction_engine.analyze_all()
        return {"contradictions": contradictions}

    # ------------------------------------------------------------
    # SUMMARY VIEW
    # ------------------------------------------------------------

    @router.get("/summary")
    def get_contradiction_summary():
        """
        NOTATION: Contradiction Summary Endpoint.
        USE: Returns counts grouped by contradiction type.
        """
        all_contradictions = contradiction_engine.analyze_all()

        summary = {}
        for c in all_contradictions:
            ctype = c["type"]
            summary.setdefault(ctype, 0)
            summary[ctype] += 1

        return {
            "total": len(all_contradictions),
            "by_type": summary,
        }

    # ------------------------------------------------------------
    # DETAIL VIEW
    # ------------------------------------------------------------

    @router.get("/detail/{relationship_id}")
    def get_contradiction_detail(relationship_id: UUID):
        """
        NOTATION: Contradiction Detail Endpoint.
        USE: Returns the contradiction record for a specific relationship.
        """

        # Full scan (safe for append-only graph)
        all_contradictions = contradiction_engine.analyze_all()

        for c in all_contradictions:
            if c.get("relationship_id") == str(relationship_id):
                return {"contradiction": c}

        return {"contradiction": None}

    return router
