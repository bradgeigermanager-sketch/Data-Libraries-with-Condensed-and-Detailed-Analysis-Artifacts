"""
MODULE: sqlite_migration_tool.py
LOCATION: backend/db/sqlite_migration_tool.py
NOTATION: SQLite Migration Tool
USE: Deterministic, append-only schema migration system for SQLite.
"""

import sqlite3
from typing import Callable, List, Dict


class SQLiteMigrationTool:
    """
    NOTATION: Migration Tool.
    USE: Applies ordered, append-only schema migrations to a SQLite database.

    MIGRATION MODEL:
        migrations: List[Dict]
            [
                {
                    "id": "0001_init_jobs",
                    "apply": callable(conn),
                },
                ...
            ]

    SCHEMA VERSION TABLE:
        schema_migrations:
            id TEXT PRIMARY KEY
            applied_at TEXT
    """

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.migrations: List[Dict] = []
        self._ensure_version_table()

    # ------------------------------------------------------------
    # INTERNAL: VERSION TABLE
    # ------------------------------------------------------------

    def _ensure_version_table(self):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                id TEXT PRIMARY KEY,
                applied_at TEXT NOT NULL
            )
        """)

        conn.commit()
        conn.close()

    # ------------------------------------------------------------
    # MIGRATION REGISTRATION
    # ------------------------------------------------------------

    def register(self, migration_id: str, apply_fn: Callable[[sqlite3.Connection], None]):
        """
        NOTATION: Register Migration.
        USE: Adds a migration to the ordered list.
        """
        self.migrations.append({
            "id": migration_id,
            "apply": apply_fn,
        })

    # ------------------------------------------------------------
    # MIGRATION RUNNER
    # ------------------------------------------------------------

    def apply_all(self):
        """
        NOTATION: Apply All Migrations.
        USE: Applies all migrations that have not yet been applied.
        """
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute("SELECT id FROM schema_migrations")
        applied = {row[0] for row in cur.fetchall()}

        for m in self.migrations:
            mid = m["id"]
            if mid in applied:
                continue  # already applied

            print(f"Applying migration: {mid}")
            m["apply"](conn)

            cur.execute("""
                INSERT INTO schema_migrations (id, applied_at)
                VALUES (?, datetime('now'))
            """, (mid,))

            conn.commit()

        conn.close()
