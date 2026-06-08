"""
MODULE: graph_visualizer_api.py
LOCATION: backend/api/graph_visualizer_api.py
NOTATION: Graph Visualizer API
USE: Exposes node/edge graph structures for UI visualization.
"""

from fastapi import APIRouter, Query
from uuid import UUID

from backend.db.repository import LogicRepository
from backend.analysis.graph_visualizer import GraphVisualizer


def build_graph_visualizer_api(repository: LogicRepository):
    """
    NOTATION: API Builder.
    USE: Returns a configured FastAPI router for graph visualization endpoints.
    """

    router = APIRouter(prefix="/graph", tags=["graph"])
    visualizer = GraphVisualizer(repository)

    # ------------------------------------------------------------
    # SUBGRAPH ENDPOINT
    # ------------------------------------------------------------

    @router.get("/subgraph/{artifact_id}")
    def get_subgraph(
        artifact_id: UUID,
        depth: int = Query(default=1, ge=0, le=5),
    ):
        """
        NOTATION: Subgraph Endpoint.
        USE: Returns a depth-limited node/edge graph centered on an artifact.
        """
        graph = visualizer.build_subgraph_for_artifact(artifact_id, depth)
        return {
            "artifact_id": str(artifact_id),
            "depth": depth,
            "nodes": graph["nodes"],
            "edges": graph["edges"],
        }

    # ------------------------------------------------------------
    # FULL GRAPH ENDPOINT
    # ------------------------------------------------------------

    @router.get("/full")
    def get_full_graph(limit: int = Query(default=500, ge=10, le=5000)):
        """
        NOTATION: Full Graph Endpoint.
        USE: Returns a capped global graph snapshot for visualization.
        """
        graph = visualizer.build_full_graph(limit)
        return {
            "limit": limit,
            "nodes": graph["nodes"],
            "edges": graph["edges"],
        }

    return router
