"""
MODULE: schema_contract_full_system.py
LOCATION: backend/db/schema_contract_full_system.py
NOTATION: Full-System SQLite Schema Contract
USE: Canonical contract for schema_validation_tool + migrations.
"""

SCHEMA_CONTRACT_FULL = {
    "tables": {
        # -----------------------------
        # LOGIC GRAPH CORE
        # -----------------------------
        "artifacts": {
            "columns": {
                "artifact_id": "TEXT",
                "title": "TEXT",
                "artifact_category": "TEXT",
                "condensed_logic": "TEXT",
                "raw_logic": "TEXT",
            }
        },
        "relationships": {
            "columns": {
                "relationship_id": "TEXT",
                "source_id": "TEXT",
                "target_id": "TEXT",
                "relationship_type": "TEXT",
            }
        },

        # -----------------------------
        # INGESTION JOBS
        # -----------------------------
        "ingestion_jobs": {
            "columns": {
                "job_id": "TEXT",
                "started_at": "TEXT",
                "completed_at": "TEXT",
                "status": "TEXT",
            }
        },
        "ingestion_job_events": {
            "columns": {
                "event_id": "TEXT",
                "job_id": "TEXT",
                "timestamp": "TEXT",
                "event_type": "TEXT",
                "payload": "TEXT",
            }
        },

        # -----------------------------
        # MIGRATIONS
        # -----------------------------
        "schema_migrations": {
            "columns": {
                "id": "TEXT",
                "applied_at": "TEXT",
            }
        },
    }
}
