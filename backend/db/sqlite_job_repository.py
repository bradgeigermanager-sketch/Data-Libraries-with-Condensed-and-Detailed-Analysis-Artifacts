"""
MODULE: sqlite_job_repository.py
LOCATION: backend/db/sqlite_job_repository.py
NOTATION: SQLite-backed Ingestion Job Repository
USE: Append-only persistent storage for ingestion job metadata.
"""

import sqlite3
from uuid import UUID, uuid4
from datetime import datetime
from typing import Dict, Any, List, Optional


class SQLiteJobRepository:
    """
    NOTATION: SQLite Job Repository.
    USE: Persistent append-only ingestion job storage.

    TABLES:
        ingestion_jobs:
            job_id TEXT PRIMARY KEY
            started_at TEXT
            completed_at TEXT
            status TEXT

        ingestion_job_events:
            event_id TEXT PRIMARY KEY
            job_id TEXT
            timestamp TEXT
            event_type TEXT
            payload TEXT (JSON)
    """

    def __init__(self, db_path: str = "jobs.db"):
        self.db_path = db_path
        self._init_db()

    # ------------------------------------------------------------
    # INTERNAL: DB INIT
    # ------------------------------------------------------------

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS ingestion_jobs (
                job_id TEXT PRIMARY KEY,
                started_at TEXT NOT NULL,
                completed_at TEXT,
                status TEXT NOT NULL
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS ingestion_job_events (
                event_id TEXT PRIMARY KEY,
                job_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                event_type TEXT NOT NULL,
                payload TEXT,
                FOREIGN KEY(job_id) REFERENCES ingestion_jobs(job_id)
            )
        """)

        conn.commit()
        conn.close()

    # ------------------------------------------------------------
    # JOB CREATION
    # ------------------------------------------------------------

    def record_job_start(self) -> str:
        job_id = str(uuid4())
        started_at = datetime.utcnow().isoformat()

        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO ingestion_jobs (job_id, started_at, status)
            VALUES (?, ?, ?)
        """, (job_id, started_at, "running"))

        conn.commit()
        conn.close()

        return job_id

    # ------------------------------------------------------------
    # JOB EVENTS (APPEND-ONLY)
    # ------------------------------------------------------------

    def _record_event(self, job_id: str, event_type: str, payload: Optional[str]):
        event_id = str(uuid4())
        timestamp = datetime.utcnow().isoformat()

        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO ingestion_job_events (event_id, job_id, timestamp, event_type, payload)
            VALUES (?, ?, ?, ?, ?)
        """, (event_id, job_id, timestamp, event_type, payload))

        conn.commit()
        conn.close()

    def record_job_update(
        self,
        job_id: UUID,
        *,
        created_artifact: Optional[Dict[str, Any]] = None,
        resolver_hit: Optional[Dict[str, Any]] = None,
        resolver_miss: Optional[Dict[str, Any]] = None,
        log: Optional[str] = None,
    ):
        jid = str(job_id)

        if created_artifact:
            self._record_event(jid, "created_artifact", str(created_artifact))

        if resolver_hit:
            self._record_event(jid, "resolver_hit", str(resolver_hit))

        if resolver_miss:
            self._record_event(jid, "resolver_miss", str(resolver_miss))

        if log:
            self._record_event(jid, "log", log)

    # ------------------------------------------------------------
    # JOB COMPLETION
    # ------------------------------------------------------------

    def record_job_complete(self, job_id: UUID, status: str = "completed"):
        jid = str(job_id)
        completed_at = datetime.utcnow().isoformat()

        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute("""
            UPDATE ingestion_jobs
            SET completed_at = ?, status = ?
            WHERE job_id = ?
        """, (completed_at, status, jid))

        conn.commit()
        conn.close()

    # ------------------------------------------------------------
    # JOB RETRIEVAL
    # ------------------------------------------------------------

    def list_jobs(self) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute("""
            SELECT job_id, started_at, completed_at, status
            FROM ingestion_jobs
            ORDER BY started_at DESC
        """)

        rows = cur.fetchall()
        conn.close()

        return [
            {
                "job_id": r[0],
                "started_at": r[1],
                "completed_at": r[2],
                "status": r[3],
            }
            for r in rows
        ]

    def get_job(self, job_id: UUID) -> Optional[Dict[str, Any]]:
        jid = str(job_id)

        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute("""
            SELECT job_id, started_at, completed_at, status
            FROM ingestion_jobs
            WHERE job_id = ?
        """, (jid,))
        job_row = cur.fetchone()

        if not job_row:
            conn.close()
            return None

        cur.execute("""
            SELECT timestamp, event_type, payload
            FROM ingestion_job_events
            WHERE job_id = ?
            ORDER BY timestamp ASC
        """, (jid,))
        events = cur.fetchall()

        conn.close()

        return {
            "job_id": job_row[0],
            "started_at": job_row[1],
            "completed_at": job_row[2],
            "status": job_row[3],
            "events": [
                {
                    "timestamp": e[0],
                    "event_type": e[1],
                    "payload": e[2],
                }
                for e in events
            ]
        }

    def get_latest_job(self) -> Optional[Dict[str, Any]]:
        jobs = self.list_jobs()
        return jobs[0] if jobs else None
