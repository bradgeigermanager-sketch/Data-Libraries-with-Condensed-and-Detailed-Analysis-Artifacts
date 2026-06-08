"""
MODULE: contradiction_engine.py
LOCATION: backend/analysis/contradiction_engine.py
NOTATION: Contradiction Detection Engine
USE: Identifies logical contradictions between artifacts in the immutable graph.
"""

from typing import Dict, Any, List, Optional
from uuid import UUID

from backend.db.repository import LogicRepository
from backend.logic_core.relationships import is_logical
from backend.logic_core.versioning import VERSIONING_EDGE


class ContradictionEngine:
    """
    NOTATION: Contradiction Engine.
    USE: Detects contradictions between artifacts using semantic edges + lineage.
    """

    def __init__(self, repository: LogicRepository):
        self.repo = repository

    # ------------------------------------------------------------
    # PUBLIC API
    # ------------------------------------------------------------

    def analyze_artifact(self, artifact_id: UUID) -> List[Dict[str, Any]]:
        """
        NOTATION: Artifact Contradiction Analyzer.
        USE: Returns a list of contradiction reports for a given artifact.
        """

        relationships = self.repo.get_relationships_for_artifact(artifact_id)
        contradictions = []

        for rel in relationships:
            if rel["relationship_type"] == "contradicts":
                contradictions.append(
                    self._build_contradiction_record(
                        artifact_id,
                        rel["source_id"],
                        rel["target_id"],
                        rel,
                    )
                )

        # Also detect implicit contradictions via lineage
        lineage_contradictions = self._detect_lineage_conflicts(artifact_id)
        contradictions.extend(lineage_contradictions)

        return contradictions

    def analyze_all(self) -> List[Dict[str, Any]]:
        """
        NOTATION: Full Graph Contradiction Scan.
        USE: Scans all artifacts for contradictions.
        """

        artifacts = self.repo.list_artifacts()
        results = []

        for row in artifacts:
            artifact_id = UUID(row["artifact_id"])
            contradictions = self.analyze_artifact(artifact_id)
            results.extend(contradictions)

        return results

    # ------------------------------------------------------------
    # INTERNAL CONTRADICTION BUILDERS
    # ------------------------------------------------------------

    def _build_contradiction_record(
        self,
        focal_id: UUID,
        source_id: UUID,
        target_id: UUID,
        relationship_row: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        NOTATION: Contradiction Record Builder.
        USE: Produces a structured contradiction report.
        """

        return {
            "type": "direct_contradiction",
            "focal_artifact": str(focal_id),
            "source_artifact": str(source_id),
            "target_artifact": str(target_id),
            "relationship_id": str(relationship_row["relationship_id"]),
            "relationship_type": relationship_row["relationship_type"],
        }

    # ------------------------------------------------------------
    # LINEAGE-BASED CONTRADICTIONS
    # ------------------------------------------------------------

    def _detect_lineage_conflicts(self, artifact_id: UUID) -> List[Dict[str, Any]]:
        """
        NOTATION: Lineage Conflict Detector.
        USE: Detects contradictions between versions of the same artifact.
        """

        relationships = self.repo.get_relationships_for_artifact(artifact_id)
        supersedes_edges = [
            r for r in relationships if r["relationship_type"] == VERSIONING_EDGE
        ]

        contradictions = []

        for edge in supersedes_edges:
            old_id = UUID(edge["target_id"])
            new_id = UUID(edge["source_id"])

            # Check if old and new contradict each other
            if self._artifacts_contradict(old_id, new_id):
                contradictions.append(
                    {
                        "type": "lineage_contradiction",
                        "old_version": str(old_id),
                        "new_version": str(new_id),
                        "supersedes_edge": str(edge["relationship_id"]),
                    }
                )

        return contradictions

    def _artifacts_contradict(self, a: UUID, b: UUID) -> bool:
        """
        NOTATION: Artifact Contradiction Checker.
        USE: Determines if two artifacts contradict each other.
        """

        rels_a = self.repo.get_relationships_for_artifact(a)
        rels_b = self.repo.get_relationships_for_artifact(b)

        # If either explicitly contradicts the other
        for rel in rels_a + rels_b:
            if rel["relationship_type"] == "contradicts":
                if rel["source_id"] == str(a) and rel["target_id"] == str(b):
                    return True
                if rel["source_id"] == str(b) and rel["target_id"] == str(a):
                    return True

        return False
