"""
MODULE: graph_visualizer.py
LOCATION: backend/analysis/graph_visualizer.py
NOTATION: Logic Graph Visualizer
USE: Builds UI-ready graph structures (nodes + edges) from the immutable logic graph.
"""

from typing import Dict, Any, List, Set
from uuid import UUID

from backend.db.repository import LogicRepository


class GraphVisualizer:
    """
    NOTATION: Graph Visualizer.
    USE: Produces node/edge views for UI graph components.
    """

    def __init__(self, repository: LogicRepository):
        self.repo = repository

    # ------------------------------------------------------------
    # PUBLIC API
    # ------------------------------------------------------------

    def build_subgraph_for_artifact(self, artifact_id: UUID, depth: int = 1) -> Dict[str, Any]:
        """
        NOTATION: Artifact-Centered Subgraph.
        USE: Returns nodes + edges around a focal artifact up to given depth.

        RETURNS:
            {
                "nodes": [{ "id": str, "title": str, "category": str }, ...],
                "edges": [{ "id": str, "source": str, "target": str, "type": str }, ...]
            }
        """
        visited: Set[str] = set()
        nodes: Dict[str, Dict[str, Any]] = {}
        edges: Dict[str, Dict[str, Any]] = {}

        frontier: List[UUID] = [artifact_id]
        current_depth = 0

        while frontier and current_depth <= depth:
            next_frontier: List[UUID] = []

            for aid in frontier:
                aid_str = str(aid)
                if aid_str in visited:
                    continue
                visited.add(aid_str)

                row = self.repo.get_artifact(aid)
                if not row:
                    continue

                nodes[aid_str] = {
                    "id": aid_str,
                    "title": row.get("title"),
                    "category": row.get("artifact_category"),
                }

                rels = self.repo.get_relationships_for_artifact(aid)

                for r in rels:
                    edge_id = str(r["relationship_id"])
                    source_id = r["source_id"]
                    target_id = r["target_id"]

                    edges[edge_id] = {
                        "id": edge_id,
                        "source": source_id,
                        "target": target_id,
                        "type": r["relationship_type"],
                    }

                    # enqueue neighbors
                    for neighbor in (source_id, target_id):
                        if neighbor not in visited:
                            next_frontier.append(UUID(neighbor))

            frontier = next_frontier
            current_depth += 1

        return {
            "nodes": list(nodes.values()),
            "edges": list(edges.values()),
        }

    def build_full_graph(self, limit: int = 1000) -> Dict[str, Any]:
        """
        NOTATION: Full Graph Snapshot.
        USE: Returns a capped node/edge set for global visualization.
        """
        artifacts = self.repo.list_artifacts(limit=limit)
        nodes: Dict[str, Dict[str, Any]] = {}
        edges: Dict[str, Dict[str, Any]] = {}

        for row in artifacts:
            aid = row["artifact_id"]
            nodes[aid] = {
                "id": aid,
                "title": row.get("title"),
                "category": row.get("artifact_category"),
            }

            rels = self.repo.get_relationships_for_artifact(UUID(aid))
            for r in rels:
                edge_id = str(r["relationship_id"])
                if edge_id in edges:
                    continue
                edges[edge_id] = {
                    "id": edge_id,
                    "source": r["source_id"],
                    "target": r["target_id"],
                    "type": r["relationship_type"],
                }

        return {
            "nodes": list(nodes.values()),
            "edges": list(edges.values()),
        }
