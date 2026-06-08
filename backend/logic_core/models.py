"""
MODULE: models.py
LOCATION: backend/logic_core/models.py
NOTATION: Domain models for the immutable logic graph.
USE: Pure Python representations of LogicArtifact and LogicRelationship.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from uuid import UUID, uuid4
from datetime import datetime


# ------------------------------------------------------------
# LogicArtifact (Atomic Node)
# ------------------------------------------------------------

@dataclass(frozen=True)
class LogicArtifact:
    """
    NOTATION: Atomic logic node.
    USE: Represents a single immutable artifact in the logic graph.
    """

    artifact_id: UUID = field(default_factory=uuid4)

    # Human-readable identifier
    title: str = ""

    # Core representations
    condensed_logic: str = ""
    verbose_desc: str = ""
    foundational_data: Dict = field(default_factory=dict)

    # Polymorphic classification
    artifact_category: str = "logic_node"   # logic_node | machine_map | fillable_schema
    syntax_language: str = "text"           # text | python | json | sql | html | ...

    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


# ------------------------------------------------------------
# LogicRelationship (Directed Edge)
# ------------------------------------------------------------

@dataclass(frozen=True)
class LogicRelationship:
    """
    NOTATION: Directed relationship edge.
    USE: Connects two LogicArtifact nodes with a typed semantic relationship.
    """

    relationship_id: UUID = field(default_factory=uuid4)

    # Directed endpoints
    source_id: UUID = None
    target_id: UUID = None

    # Relationship classification
    relationship_type: str = ""  # implies | extends | contradicts | supersedes | implements | relates_to

    # Metadata (optional)
    created_at: datetime = field(default_factory=datetime.utcnow)
