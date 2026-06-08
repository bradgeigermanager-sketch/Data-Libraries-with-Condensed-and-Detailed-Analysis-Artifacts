"""
MODULE: main.py
LOCATION: project/main.py
NOTATION: Deployment Entrypoint
USE: Creates FastAPI app, mounts routers, serves static UIs.
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

# Backend components
from backend.db.repository import LogicRepository
from backend.db.job_repository import JobRepository
from backend.ingestion.engine import LogicIngestionEngine
from backend.harvest.harvester_orchestrator import HarvesterOrchestrator
from backend.analysis.contradiction_engine import ContradictionEngine

# API builders
from backend.api.admin_api import build_admin_api
from backend.api.browse_api import build_browse_api
from backend.api.lineage_api import build_lineage_api
from backend.api.contradiction_api import build_contradiction_api
from backend.api.search_api import build_search_api
from backend.api.graph_visualizer_api import build_graph_visualizer_api
from backend.api.ingestion_job_api import build_ingestion_job_api


def create_app() -> FastAPI:
    """
    NOTATION: App Factory.
    USE: Constructs the full FastAPI application with explicit dependencies.
    """

    app = FastAPI(title="Logic Graph System")

    # ------------------------------------------------------------
    # DEPENDENCY INSTANTIATION
    # ------------------------------------------------------------

    repository = LogicRepository()
    job_repo = JobRepository()

    ingestion_engine = LogicIngestionEngine(repository, job_repo)
    harvester = HarvesterOrchestrator(repository, ingestion_engine)
    contradiction_engine = ContradictionEngine(repository)

    # ------------------------------------------------------------
    # ROUTER MOUNTING
    # ------------------------------------------------------------

    app.include_router(build_admin_api(
        repository,
        ingestion_engine,
        harvester,
        contradiction_engine,
    ))

    app.include_router(build_browse_api(repository))
    app.include_router(build_lineage_api(repository))
    app.include_router(build_contradiction_api(repository, contradiction_engine))
    app.include_router(build_search_api(repository))
    app.include_router(build_graph_visualizer_api(repository))
    app.include_router(build_ingestion_job_api(job_repo))

    # ------------------------------------------------------------
    # STATIC FILE SERVING
    # ------------------------------------------------------------

    app.mount("/ui", StaticFiles(directory="static"), name="ui")

    return app


app = create_app()
