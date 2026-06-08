"""
MODULE: lineage_api.py
LOCATION: backend/api/lineage_api.py
NOTATION: Lineage API
USE: Exposes version lineage, supersedes chains, and ancestry graphs.
"""

from fastapi import APIRouter
from uuid import UUID

from backend.db.repository import LogicRepository
from backend.logic_core.versioning import resolve_lineage


def build_lineage_api(repository: LogicRepository):
    """
    NOTATION: API Builder.
    USE: Returns a configured FastAPI router for lineage inspection.
    """

    router = APIRouter(prefix="/lineage", tags=["lineage"])

    # ------------------------------------------------------------
    # BASIC LINEAGE
    # ------------------------------------------------------------

    @router.get("/{artifact_id}")
    def get_lineage(artifact_id: UUID):
        """
        NOTATION: Lineage Endpoint.
        USE: Returns supersedes + deprecated_by edges for an artifact.
        """
        lineage = resolve_lineage(repository, artifact_id)
        return {"artifact_id": str(artifact_id), "lineage": lineage}

    # ------------------------------------------------------------
    # ANCESTRY CHAIN
    # ------------------------------------------------------------

    @router.get("/{artifact_id}/ancestors")
    def get_ancestors(artifact_id: UUID):
        """
        NOTATION: Ancestor Chain Endpoint.
        USE: Walks backwards through supersedes edges to find all ancestors.
        """
        ancestors = []
        current = artifact_id

        while True:
            lineage = resolve_lineage(repository, current)
            supersedes = lineage.get("supersedes", [])

            if not supersedes:
                break

            # Each supersedes edge: new_version → old_version
            old_id = supersedes[0]["target_id"]
            ancestors.append(old_id)
            current = UUID(old_id)

        return {"artifact_id": str(artifact_id), "ancestors": ancestors}

    # ------------------------------------------------------------
    # DESCENDANT CHAIN
    # ------------------------------------------------------------

    @router.get("/{artifact_id}/descendants")
    def get_descendants(artifact_id: UUID):
        """
        NOTATION: Descendant Chain Endpoint.
        USE: Walks forward through supersedes edges to find all descendants.
        """
        descendants = []
        queue = [artifact_id]

        while queue:
            current = queue.pop(0)
            lineage = resolve_lineage(repository, current)
            deprecated_by = lineage.get("deprecated_by", [])

            for edge in deprecated_by:
                new_id = edge["target_id"]
                descendants.append(new_id)
                queue.append(UUID(new_id))

        return {"artifact_id": str(artifact_id), "descendants": descendants}

    # ------------------------------------------------------------
    # FULL LINEAGE GRAPH
    # ------------------------------------------------------------

    @router.get("/{artifact_id}/graph")
    def get_lineage_graph(artifact_id: UUID):
        """
        NOTATION: Full Lineage Graph Endpoint.
        USE: Returns ancestors + descendants in a single structure.
        """
        ancestors = get_ancestors(artifact_id)["ancestors"]
        descendants = get_descendants(artifact_id)["descendants"]

        return {
            "artifact_id": str(artifact_id),
            "ancestors": ancestors,
            "descendants": descendants,
        }

    return router
