"""
MODULE: browse_api.py
LOCATION: backend/api/browse_api.py
NOTATION: Public Browse API
USE: Exposes read-only browsing endpoints for the logic graph.
"""

from fastapi import APIRouter, Query
from uuid import UUID

from backend.db.repository import LogicRepository
from backend.logic_core.versioning import resolve_lineage


def build_browse_api(repository: LogicRepository):
    """
    NOTATION: API Builder.
    USE: Returns a configured FastAPI router for browsing the logic graph.
    """

    router = APIRouter(prefix="/browse", tags=["browse"])

    # ------------------------------------------------------------
    # ARTIFACT LISTING
    # ------------------------------------------------------------

    @router.get("/artifacts")
    def list_artifacts(category: str | None = Query(default=None)):
        """
        NOTATION: Artifact Directory Endpoint.
        USE: Returns a list of artifacts, optionally filtered by category.
        """
        rows = repository.list_artifacts(category)
        return {"artifacts": rows}

    # ------------------------------------------------------------
    # ARTIFACT SUMMARY
    # ------------------------------------------------------------

    @router.get("/artifact/{artifact_id}")
    def get_artifact(artifact_id: UUID):
        """
        NOTATION: Artifact Summary Endpoint.
        USE: Returns full artifact details for browsing.
        """
        row = repository.get_artifact(artifact_id)
        return {"artifact": row}

    # ------------------------------------------------------------
    # RELATIONSHIPS
    # ------------------------------------------------------------

    @router.get("/artifact/{artifact_id}/relationships")
    def get_relationships(artifact_id: UUID):
        """
        NOTATION: Relationship Browser.
        USE: Returns all edges where artifact is source or target.
        """
        rels = repository.get_relationships_for_artifact(artifact_id)
        return {"relationships": rels}

    # ------------------------------------------------------------
    # LINEAGE
    # ------------------------------------------------------------

    @router.get("/artifact/{artifact_id}/lineage")
    def get_lineage(artifact_id: UUID):
        """
        NOTATION: Lineage Browser.
        USE: Returns supersedes + deprecated_by edges.
        """
        lineage = resolve_lineage(repository, artifact_id)
        return {"lineage": lineage}

    # ------------------------------------------------------------
    # RELATED ARTIFACTS
    # ------------------------------------------------------------

    @router.get("/artifact/{artifact_id}/related")
    def get_related_artifacts(artifact_id: UUID):
        """
        NOTATION: Related Artifact Browser.
        USE: Returns all artifacts connected via any relationship.
        """
        rels = repository.get_relationships_for_artifact(artifact_id)

        related_ids = set()
        for r in rels:
            if r["source_id"] != str(artifact_id):
                related_ids.add(r["source_id"])
            if r["target_id"] != str(artifact_id):
                related_ids.add(r["target_id"])

        related = [
            repository.get_artifact(UUID(aid))
            for aid in related_ids
        ]

        return {"related": related}

    return router
