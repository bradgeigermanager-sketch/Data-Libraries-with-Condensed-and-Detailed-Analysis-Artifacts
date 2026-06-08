"""
MODULE: schema_validation_tool.py
LOCATION: backend/db/schema_validation_tool.py
NOTATION: SQLite Schema Validation Tool
USE: Validates that the actual SQLite schema matches an explicit contract.
"""

import sqlite3
from typing import Dict, List, Any


class SchemaValidationTool:
    """
    NOTATION: Schema Validator.
    USE: Compares actual DB schema against a declared contract.

    CONTRACT MODEL:
        {
            "tables": {
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
                }
            }
        }
    """

    def __init__(self, db_path: str, contract: Dict[str, Any]):
        self.db_path = db_path
        self.contract = contract

    # ------------------------------------------------------------
    # PUBLIC: VALIDATE
    # ------------------------------------------------------------

    def validate(self) -> Dict[str, Any]:
        """
        NOTATION: Validate Schema.
        USE: Returns a structured report of mismatches.
        """
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        report = {
            "tables_missing": [],
            "tables_extra": [],
            "columns_missing": {},
            "columns_extra": {},
            "type_mismatches": {},
        }

        # actual tables
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        actual_tables = {row[0] for row in cur.fetchall()}

        contract_tables = set(self.contract.get("tables", {}).keys())

        # table-level comparison
        report["tables_missing"] = sorted(contract_tables - actual_tables)
        report["tables_extra"] = sorted(actual_tables - contract_tables)

        # column-level comparison
        for table in contract_tables:
            expected_cols = self.contract["tables"][table]["columns"]

            if table not in actual_tables:
                continue

            cur.execute(f"PRAGMA table_info({table})")
            actual_info = cur.fetchall()

            actual_cols = {row[1]: row[2] for row in actual_info}

            missing = []
            extra = []
            type_mismatch = []

            for col_name, col_type in expected_cols.items():
                if col_name not in actual_cols:
                    missing.append(col_name)
                else:
                    actual_type = actual_cols[col_name]
                    if actual_type.upper() != col_type.upper():
                        type_mismatch.append({
                            "column": col_name,
                            "expected": col_type,
                            "actual": actual_type,
                        })

            for col_name in actual_cols.keys():
                if col_name not in expected_cols:
                    extra.append(col_name)

            if missing:
                report["columns_missing"][table] = missing
            if extra:
                report["columns_extra"][table] = extra
            if type_mismatch:
                report["type_mismatches"][table] = type_mismatch

        conn.close()
        return report
