"""
MODULE: engine.py
LOCATION: backend/ingestion/engine.py
NOTATION: LogicIngestionEngine for the immutable logic graph.
USE: Normalizes raw sources into LogicArtifacts + LogicRelationships.
"""

from typing import Dict, Any, Optional
from uuid import UUID

from backend.logic_core.models import LogicArtifact, LogicRelationship
from backend.logic_core.versioning import create_new_version, build_supersedes_edge
from backend.logic_core.relationships import require_valid_relationship
from backend.db.repository import LogicRepository


class LogicIngestionEngine:
    """
    NOTATION: Ingestion Orchestrator.
    USE: Converts raw text + metadata into immutable graph nodes.
    """

    def __init__(self, repository: LogicRepository, resolver):
        """
        PARAMETERS:
            repository: LogicRepository instance
            resolver: callable(title: str) -> Optional[UUID]
        """
        self.repo = repository
        self.resolver = resolver

    # ------------------------------------------------------------
    # PUBLIC ENTRYPOINT
    # ------------------------------------------------------------

    def process_source(self, raw_text: str, source_meta: Dict[str, Any]) -> UUID:
        """
        NOTATION: Source Processor.
        USE: Main entrypoint for ingestion (admin UI, Wikipedia, etc.).

        STEPS:
            1. Extract logical content (condensed, verbose, foundational).
            2. Resolve existing artifact (by title) if present.
            3. If exists → create new version + supersedes edge.
               If not → insert new artifact.
        """
        extracted = self._extract_logical_nodes(raw_text, source_meta)

        title = extracted["title"]
        condensed = extracted["condensed_logic"]
        verbose = extracted["verbose_desc"]
        foundational = extracted.get("foundational_data", {})
        category = extracted.get("artifact_category", "logic_node")
        syntax = extracted.get("syntax_language", "text")

        existing_id = self.resolver(title)

        if existing_id:
            # Versioning path
            old_row = self.repo.get_artifact(existing_id)
            old_artifact = LogicArtifact(
                artifact_id=existing_id,
                title=old_row["title"],
                condensed_logic=old_row["condensed_logic"],
                verbose_desc=old_row["verbose_desc"],
                foundational_data=old_row["foundational_data"] or {},
                artifact_category=old_row["artifact_category"],
                syntax_language=old_row["syntax_language"],
                created_at=old_row["created_at"],
                updated_at=old_row["updated_at"],
            )

            overrides = {
                "condensed_logic": condensed,
                "verbose_desc": verbose,
                "foundational_data": foundational,
                "artifact_category": category,
                "syntax_language": syntax,
            }

            new_artifact = create_new_version(old_artifact, overrides)
            self.repo.insert_artifact(new_artifact)

            supersedes_edge = build_supersedes_edge(
                old_id=old_artifact.artifact_id,
                new_id=new_artifact.artifact_id,
            )
            self.repo.insert_relationship(supersedes_edge)

            return new_artifact.artifact_id

        # New artifact path
        artifact = LogicArtifact(
            title=title,
            condensed_logic=condensed,
            verbose_desc=verbose,
            foundational_data=foundational,
            artifact_category=category,
            syntax_language=syntax,
        )

        self.repo.insert_artifact(artifact)
        return artifact.artifact_id

    # ------------------------------------------------------------
    # INTERNAL EXTRACTION HOOK
    # ------------------------------------------------------------

    def _extract_logical_nodes(
        self, raw_text: str, source_meta: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        NOTATION: Extraction Hook.
        USE: Default minimal extractor; override/extend for richer pipelines.

        EXPECTED RETURN:
            {
                "title": str,
                "condensed_logic": str,
                "verbose_desc": str,
                "foundational_data": dict,
                "artifact_category": str,
                "syntax_language": str,
            }
        """
        title = source_meta.get("page_title") or source_meta.get("title") or "Untitled"

        return {
            "title": title,
            "condensed_logic": raw_text.strip()[:280],
            "verbose_desc": raw_text.strip(),
            "foundational_data": {
                "source": source_meta,
            },
            "artifact_category": source_meta.get("artifact_category", "logic_node"),
            "syntax_language": source_meta.get("syntax_language", "text"),
        }

    # ------------------------------------------------------------
    # OPTIONAL: RELATIONSHIP INGESTION
    # ------------------------------------------------------------

    def attach_relationship(
        self,
        source_id: UUID,
        target_id: UUID,
        relationship_type: str,
    ) -> UUID:
        """
        NOTATION: Relationship Attacher.
        USE: Safely appends a new typed edge between two artifacts.
        """
        require_valid_relationship(relationship_type)

        rel = LogicRelationship(
            source_id=source_id,
            target_id=target_id,
            relationship_type=relationship_type,
        )

        return self.repo.insert_relationship(rel)
