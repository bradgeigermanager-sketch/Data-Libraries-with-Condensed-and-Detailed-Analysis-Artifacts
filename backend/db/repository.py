"""
MODULE: repository.py
LOCATION: backend/db/repository.py
NOTATION: Data access layer for the immutable logic graph.
USE: Provides append-only writes and safe reads for artifacts and relationships.
"""

from typing import Optional, List
from uuid import UUID, uuid4

from backend.db.connection import DatabaseConnection
from backend.logic_core.models import LogicArtifact, LogicRelationship


class LogicRepository:
    """
    NOTATION: Repository Layer.
    USE: Centralized DB operations for artifacts and relationships.
    """

    def __init__(self, db: DatabaseConnection):
        self.db = db

    # ------------------------------------------------------------
    # ARTIFACT OPERATIONS
    # ------------------------------------------------------------

    def insert_artifact(self, artifact: LogicArtifact) -> UUID:
        """
        NOTATION: Append-only artifact insert.
        USE: Creates a new immutable LogicArtifact row.
        """
        query = """
            INSERT INTO LogicArtifact (
                artifact_id, title, condensed_logic, verbose_desc,
                foundational_data, artifact_category, syntax_language,
                created_at, updated_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        params = (
            str(artifact.artifact_id),
            artifact.title,
            artifact.condensed_logic,
            artifact.verbose_desc,
            artifact.foundational_data,
            artifact.artifact_category,
            artifact.syntax_language,
            artifact.created_at,
            artifact.updated_at,
        )

        self.db.execute(query, params)
        return artifact.artifact_id

    def get_artifact(self, artifact_id: UUID) -> Optional[dict]:
        """
        NOTATION: Artifact retrieval.
        USE: Returns a dict row for rendering or ingestion.
        """
        query = """
            SELECT *
            FROM LogicArtifact
            WHERE artifact_id = %s
            LIMIT 1
        """
        return self.db.execute(query, [str(artifact_id)], fetchone=True)

    def find_artifact_by_title(self, title: str) -> Optional[dict]:
        """
        NOTATION: Resolver lookup.
        USE: Supports autocomplete + duplicate prevention.
        """
        query = """
            SELECT *
            FROM LogicArtifact
            WHERE LOWER(title) = LOWER(%s)
            LIMIT 1
        """
        return self.db.execute(query, [title], fetchone=True)

    def list_artifacts(self, category: Optional[str] = None) -> List[dict]:
        """
        NOTATION: Directory listing.
        USE: Feeds browse.html with filtered artifact lists.
        """
        if category:
            query = """
                SELECT artifact_id, title, artifact_category
                FROM LogicArtifact
                WHERE artifact_category = %s
                ORDER BY title ASC
            """
            return self.db.execute(query, [category], fetchall=True)

        query = """
            SELECT artifact_id, title, artifact_category
            FROM LogicArtifact
            ORDER BY title ASC
        """
        return self.db.execute(query, fetchall=True)

    # ------------------------------------------------------------
    # RELATIONSHIP OPERATIONS
    # ------------------------------------------------------------

    def insert_relationship(self, rel: LogicRelationship) -> UUID:
        """
        NOTATION: Append-only relationship insert.
        USE: Creates a new immutable directed edge.
        """
        query = """
            INSERT INTO LogicRelationship (
                relationship_id, source_id, target_id, relationship_type, created_at
            )
            VALUES (%s, %s, %s, %s, %s)
        """

        params = (
            str(rel.relationship_id),
            str(rel.source_id),
            str(rel.target_id),
            rel.relationship_type,
            rel.created_at,
        )

        self.db.execute(query, params)
        return rel.relationship_id

    def get_relationships_for_artifact(self, artifact_id: UUID) -> List[dict]:
        """
        NOTATION: Graph traversal.
        USE: Returns all edges where artifact is source or target.
        """
        query = """
            SELECT *
            FROM LogicRelationship
            WHERE source_id = %s OR target_id = %s
        """
        return self.db.execute(
            query,
            [str(artifact_id), str(artifact_id)],
            fetchall=True
        )

    # ------------------------------------------------------------
    # UTILITY OPERATIONS
    # ------------------------------------------------------------

    def artifact_exists(self, title: str) -> bool:
        """
        NOTATION: Duplicate prevention.
        USE: Supports resolver + ingestion safety.
        """
        return self.find_artifact_by_title(title) is not None

    def resolve_title_to_uuid(self, title: str) -> Optional[UUID]:
        """
        NOTATION: Resolver bridge.
        USE: Maps human-readable titles to canonical UUIDs.
        """
        row = self.find_artifact_by_title(title)
        if row:
            return UUID(row["artifact_id"])
        return None
