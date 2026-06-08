"""
MODULE: job_repository.py
LOCATION: backend/db/job_repository.py
NOTATION: Ingestion Job Repository
USE: Append-only storage for ingestion job metadata.
"""

from uuid import UUID, uuid4
from datetime import datetime
from typing import Dict, Any, List, Optional


class JobRepository:
    """
    NOTATION: Job Repository.
    USE: Stores ingestion job metadata in an append-only structure.

    STORAGE MODEL:
        jobs: Dict[str, Dict]
            {
                job_id: {
                    "job_id": str,
                    "started_at": str,
                    "completed_at": str | None,
                    "status": "running" | "completed" | "failed",
                    "created_artifacts": [...],
                    "resolver_hits": [...],
                    "resolver_misses": [...],
                    "logs": [...],
                }
            }
    """

    def __init__(self):
        self.jobs: Dict[str, Dict[str, Any]] = {}

    # ------------------------------------------------------------
    # JOB CREATION
    # ------------------------------------------------------------

    def record_job_start(self) -> str:
        """
        NOTATION: Job Start.
        USE: Creates a new job record with a unique ID.
        """
        job_id = str(uuid4())
        self.jobs[job_id] = {
            "job_id": job_id,
            "started_at": datetime.utcnow().isoformat(),
            "completed_at": None,
            "status": "running",
            "created_artifacts": [],
            "resolver_hits": [],
            "resolver_misses": [],
            "logs": [],
        }
        return job_id

    # ------------------------------------------------------------
    # JOB UPDATES (APPEND-ONLY)
    # ------------------------------------------------------------

    def record_job_update(
        self,
        job_id: UUID,
        *,
        created_artifact: Optional[Dict[str, Any]] = None,
        resolver_hit: Optional[Dict[str, Any]] = None,
        resolver_miss: Optional[Dict[str, Any]] = None,
        log: Optional[str] = None,
    ):
        """
        NOTATION: Job Update.
        USE: Appends new information to the job record.
        """
        jid = str(job_id)
        job = self.jobs.get(jid)
        if not job:
            return

        if created_artifact:
            job["created_artifacts"].append(created_artifact)

        if resolver_hit:
            job["resolver_hits"].append(resolver_hit)

        if resolver_miss:
            job["resolver_misses"].append(resolver_miss)

        if log:
            job["logs"].append({
                "timestamp": datetime.utcnow().isoformat(),
                "message": log,
            })

    # ------------------------------------------------------------
    # JOB COMPLETION
    # ------------------------------------------------------------

    def record_job_complete(self, job_id: UUID, status: str = "completed"):
        """
        NOTATION: Job Completion.
        USE: Marks a job as completed or failed.
        """
        jid = str(job_id)
        job = self.jobs.get(jid)
        if not job:
            return

        job["completed_at"] = datetime.utcnow().isoformat()
        job["status"] = status

    # ------------------------------------------------------------
    # JOB RETRIEVAL
    # ------------------------------------------------------------

    def list_jobs(self) -> List[Dict[str, Any]]:
        """
        NOTATION: Job List.
        USE: Returns all jobs sorted by start time (descending).
        """
        return sorted(
            self.jobs.values(),
            key=lambda j: j["started_at"],
            reverse=True,
        )

    def get_job(self, job_id: UUID) -> Optional[Dict[str, Any]]:
        """
        NOTATION: Job Detail.
        USE: Returns a single job record.
        """
        return self.jobs.get(str(job_id))

    def get_latest_job(self) -> Optional[Dict[str, Any]]:
        """
        NOTATION: Latest Job.
        USE: Returns the most recently started job.
        """
        jobs = self.list_jobs()
        return jobs[0] if jobs else None
