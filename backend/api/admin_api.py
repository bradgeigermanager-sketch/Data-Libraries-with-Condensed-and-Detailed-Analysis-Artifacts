"""
MODULE: admin_api.py
LOCATION: backend/api/admin_api.py
NOTATION: Administrative API Layer
USE: Exposes ingestion, harvesting, lineage, and contradiction endpoints.
"""

from fastapi import APIRouter
from uuid import UUID

from backend.ingestion.engine import LogicIngestionEngine
from backend.harvest.harvester_orchestrator import HarvesterOrchestrator
from backend.analysis.contradiction_engine import ContradictionEngine
from backend.db.repository import LogicRepository
from backend.logic_core.versioning import resolve_lineage


def build_admin_api(
    repository: LogicRepository,
    ingestion_engine: LogicIngestionEngine,
    harvester: HarvesterOrchestrator,
    contradiction_engine: ContradictionEngine,
):
    """
    NOTATION: API Builder.
    USE: Returns a configured FastAPI router for admin operations.
    """

    router = APIRouter(prefix="/admin", tags=["admin"])

    # ------------------------------------------------------------
    # INGESTION ENDPOINTS
    # ------------------------------------------------------------

    @router.post("/ingest")
    def ingest_source(payload: dict):
        """
        NOTATION: Manual Ingestion Endpoint.
        USE: Allows admin UI to ingest arbitrary text + metadata.
        """
        raw_text = payload.get("raw_text", "")
        meta = payload.get("metadata", {})

        artifact_id = ingestion_engine.process_source(raw_text, meta)

        return {"status": "ok", "artifact_id": str(artifact_id)}

    # ------------------------------------------------------------
    # HARVESTING ENDPOINTS
    # ------------------------------------------------------------

    @router.post("/harvest/category")
    def harvest_category(payload: dict):
        """
        NOTATION: Category Harvest Endpoint.
        USE: Triggers a single-category Wikipedia harvest.
        """
        category = payload["category"]
        max_pages = payload.get("max_pages", 50)

        tracker = harvester.harvest_single_category(category, max_pages)

        return {
            "status": "ok",
            "category": category,
            "created_artifacts": len(tracker.state.created_artifacts),
            "resolver_hits": len(tracker.state.resolver_hits),
            "resolver_misses": len(tracker.state.resolver_misses),
        }

    @router.post("/harvest/batch")
    def harvest_batch(payload: dict):
        """
        NOTATION: Batch Harvest Endpoint.
        USE: Runs a multi-category harvesting job.
        """
        categories = payload["categories"]
        max_pages = payload.get("max_pages", 50)
        job_name = payload.get("job_name", "unnamed_job")

        summary = harvester.run_batch_job(job_name, categories, max_pages)

        return {"status": "ok", "summary": summary}

    # ------------------------------------------------------------
    # ARTIFACT INSPECTION
    # ------------------------------------------------------------

    @router.get("/artifact/{artifact_id}")
    def get_artifact(artifact_id: UUID):
        """
        NOTATION: Artifact Inspection Endpoint.
        USE: Returns full artifact row for admin UI.
        """
        row = repository.get_artifact(artifact_id)
        return {"artifact": row}

    @router.get("/artifact/{artifact_id}/lineage")
    def get_lineage(artifact_id: UUID):
        """
        NOTATION: Lineage Inspection Endpoint.
        USE: Returns supersedes + deprecated_by edges.
        """
        lineage = resolve_lineage(repository, artifact_id)
        return {"lineage": lineage}

    # ------------------------------------------------------------
    # CONTRADICTION ANALYSIS
    # ------------------------------------------------------------

    @router.get("/artifact/{artifact_id}/contradictions")
    def get_artifact_contradictions(artifact_id: UUID):
        """
        NOTATION: Artifact Contradiction Endpoint.
        USE: Returns contradictions for a single artifact.
        """
        contradictions = contradiction_engine.analyze_artifact(artifact_id)
        return {"contradictions": contradictions}

    @router.get("/contradictions/all")
    def get_all_contradictions():
        """
        NOTATION: Full Graph Contradiction Endpoint.
        USE: Returns all contradictions in the system.
        """
        contradictions = contradiction_engine.analyze_all()
        return {"contradictions": contradictions}

    return router
