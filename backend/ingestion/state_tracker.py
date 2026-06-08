"""
MODULE: state_tracker.py
LOCATION: backend/ingestion/state_tracker.py
NOTATION: Ingestion State Tracker
USE: Tracks ingestion job lifecycle, decisions, and resulting graph changes.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional
from uuid import UUID, uuid4


@dataclass
class IngestionEvent:
    """
    NOTATION: Atomic ingestion event.
    USE: Represents a single action or decision during ingestion.
    """
    timestamp: datetime
    event_type: str
    payload: Dict[str, Any]


@dataclass
class IngestionState:
    """
    NOTATION: Ingestion Job State.
    USE: Append-only record of everything that happened during ingestion.
    """

    job_id: UUID = field(default_factory=uuid4)
    started_at: datetime = field(default_factory=datetime.utcnow)
    finished_at: Optional[datetime] = None

    # Event log
    events: List[IngestionEvent] = field(default_factory=list)

    # Outputs
    created_artifacts: List[UUID] = field(default_factory=list)
    created_relationships: List[UUID] = field(default_factory=list)
    superseded_artifacts: List[UUID] = field(default_factory=list)

    # Resolver decisions
    resolver_hits: List[Dict[str, Any]] = field(default_factory=list)
    resolver_misses: List[str] = field(default_factory=list)

    # Contradiction flags (optional future integration)
    contradictions_detected: List[Dict[str, Any]] = field(default_factory=list)

    def record_event(self, event_type: str, payload: Dict[str, Any]):
        self.events.append(
            IngestionEvent(
                timestamp=datetime.utcnow(),
                event_type=event_type,
                payload=payload,
            )
        )

    def mark_finished(self):
        self.finished_at = datetime.utcnow()


class IngestionStateTracker:
    """
    NOTATION: State Tracker.
    USE: Provides a structured, append-only record of ingestion behavior.
    """

    def __init__(self):
        self.state = IngestionState()

    # ------------------------------------------------------------
    # EVENT RECORDING
    # ------------------------------------------------------------

    def log_normalization(self, normalized: Dict[str, Any]):
        self.state.record_event("normalization", {"normalized": normalized})

    def log_extraction(self, extracted: Dict[str, Any]):
        self.state.record_event("extraction", {"extracted": extracted})

    def log_resolver_hit(self, title: str, artifact_id: UUID):
        self.state.resolver_hits.append({"title": title, "artifact_id": artifact_id})
        self.state.record_event("resolver_hit", {"title": title, "artifact_id": str(artifact_id)})

    def log_resolver_miss(self, title: str):
        self.state.resolver_misses.append(title)
        self.state.record_event("resolver_miss", {"title": title})

    def log_artifact_created(self, artifact_id: UUID):
        self.state.created_artifacts.append(artifact_id)
        self.state.record_event("artifact_created", {"artifact_id": str(artifact_id)})

    def log_relationship_created(self, relationship_id: UUID, rel_type: str):
        self.state.created_relationships.append(relationship_id)
        self.state.record_event(
            "relationship_created",
            {"relationship_id": str(relationship_id), "type": rel_type},
        )

    def log_supersedes(self, old_id: UUID, new_id: UUID):
        self.state.superseded_artifacts.append(old_id)
        self.state.record_event(
            "supersedes",
            {"old_artifact": str(old_id), "new_artifact": str(new_id)},
        )

    def log_contradiction(self, details: Dict[str, Any]):
        self.state.contradictions_detected.append(details)
        self.state.record_event("contradiction_detected", details)

    # ------------------------------------------------------------
    # FINALIZATION
    # ------------------------------------------------------------

    def finalize(self) -> IngestionState:
        self.state.mark_finished()
        return self.state
