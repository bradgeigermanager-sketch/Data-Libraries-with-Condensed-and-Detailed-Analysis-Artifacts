"""
MODULE: versioning.py
LOCATION: backend/logic_core/versioning.py
NOTATION: Versioning logic for the immutable logic graph.
USE: Creates new artifact versions and manages supersedes lineage.
"""

from dataclasses import dataclass
from uuid import UUID, uuid4
from datetime import datetime

from backend.logic_core.models import LogicArtifact, LogicRelationship
from backend.logic_core.relationships import require_valid_relationship


# ------------------------------------------------------------
# VERSIONING CONSTANTS
# ------------------------------------------------------------

VERSIONING_EDGE = "supersedes"
DEPRECATION_EDGE = "deprecated_by"


# ------------------------------------------------------------
# VERSION CREATION
# ------------------------------------------------------------

def create_new_version(old_artifact: LogicArtifact, overrides: dict) -> LogicArtifact:
    """
    NOTATION: Version Constructor.
    USE: Creates a new immutable LogicArtifact that supersedes the old one.

    PARAMETERS:
        old_artifact: the previous immutable version
        overrides: dict of fields to replace in the new version
    """

    # Build new artifact fields
    new_fields = {
        "artifact_id": uuid4(),
        "title": overrides.get("title", old_artifact.title),
        "condensed_logic": overrides.get("condensed_logic", old_artifact.condensed_logic),
        "verbose_desc": overrides.get("verbose_desc", old_artifact.verbose_desc),
        "foundational_data": overrides.get("foundational_data", old_artifact.foundational_data),
        "artifact_category": overrides.get("artifact_category", old_artifact.artifact_category),
        "syntax_language": overrides.get("syntax_language", old_artifact.syntax_language),
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }

    return LogicArtifact(**new_fields)


# ------------------------------------------------------------
# VERSIONING RELATIONSHIPS
# ------------------------------------------------------------

def build_supersedes_edge(old_id: UUID, new_id: UUID) -> LogicRelationship:
    """
    NOTATION: Supersedes Edge Builder.
    USE: Creates the directed edge new_version → old_version.
    """
    require_valid_relationship(VERSIONING_EDGE)

    return LogicRelationship(
        relationship_id=uuid4(),
        source_id=new_id,
        target_id=old_id,
        relationship_type=VERSIONING_EDGE,
    )


def build_deprecation_edge(old_id: UUID, new_id: UUID) -> LogicRelationship:
    """
    NOTATION: Deprecation Edge Builder.
    USE: Creates the directed edge old_version → new_version.
    """
    require_valid_relationship(DEPRECATION_EDGE)

    return LogicRelationship(
        relationship_id=uuid4(),
        source_id=old_id,
        target_id=new_id,
        relationship_type=DEPRECATION_EDGE,
    )


# ------------------------------------------------------------
# LINEAGE RESOLUTION
# ------------------------------------------------------------

def resolve_lineage(repository, artifact_id: UUID):
    """
    NOTATION: Lineage Resolver.
    USE: Returns all ancestors and descendants of an artifact.

    PARAMETERS:
        repository: LogicRepository instance
        artifact_id: UUID of the artifact to trace
    """

    edges = repository.get_relationships_for_artifact(artifact_id)

    supersedes = []
    deprecated_by = []

    for edge in edges:
        if edge["relationship_type"] == VERSIONING_EDGE:
            supersedes.append(edge)
        elif edge["relationship_type"] == DEPRECATION_EDGE:
            deprecated_by.append(edge)

    return {
        "supersedes": supersedes,
        "deprecated_by": deprecated_by,
    }
