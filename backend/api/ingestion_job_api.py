"""
MODULE: ingestion_job_api.py
LOCATION: backend/api/ingestion_job_api.py
NOTATION: Ingestion Job API
USE: Exposes ingestion job history, job details, and latest job state.
"""

from fastapi import APIRouter
from uuid import UUID

from backend.db.job_repository import JobRepository


def build_ingestion_job_api(job_repo: JobRepository):
    """
    NOTATION: API Builder.
    USE: Returns a configured FastAPI router for ingestion job inspection.
    """

    router = APIRouter(prefix="/admin", tags=["ingestion-jobs"])

    # ------------------------------------------------------------
    # JOB HISTORY
    # ------------------------------------------------------------

    @router.get("/jobs")
    def list_jobs():
        """
        NOTATION: Job History Endpoint.
        USE: Returns all ingestion jobs sorted by start time.
        """
        jobs = job_repo.list_jobs()
        return {"jobs": jobs}

    # ------------------------------------------------------------
    # JOB DETAIL
    # ------------------------------------------------------------

    @router.get("/job/{job_id}")
    def get_job(job_id: UUID):
        """
        NOTATION: Job Detail Endpoint.
        USE: Returns full job state including:
            - created artifacts
            - resolver hits/misses
            - normalization/extraction logs
            - timestamps
        """
        job = job_repo.get_job(job_id)
        return {"job": job}

    # ------------------------------------------------------------
    # LATEST JOB
    # ------------------------------------------------------------

    @router.get("/job/latest")
    def get_latest_job():
        """
        NOTATION: Latest Job Endpoint.
        USE: Returns the most recent ingestion job.
        """
        job = job_repo.get_latest_job()
        return {"job": job}

    return router
