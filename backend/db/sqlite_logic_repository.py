"""
MODULE: sqlite_logic_repository.py
LOCATION: backend/db/sqlite_logic_repository.py
NOTATION: SQLite-backed Logic Repository
USE: Persistent storage and query layer for artifacts + relationships.
"""

import sqlite3
from uuid import UUID
from typing import Dict, Any, List, Optional


class SQLiteLogicRepository:
    """
    NOTATION: Logic Repository (SQLite).
    USE: Stores artifacts and relationships, exposes query/search/browse APIs.

    TABLES (canonical):

        artifacts:
            artifact_id TEXT PRIMARY KEY
            title TEXT
            artifact_category TEXT
            condensed_logic TEXT
            raw_logic TEXT

        relationships:
            relationship_id TEXT PRIMARY KEY
            source_id TEXT NOT NULL
            target_id TEXT NOT NULL
            relationship_type TEXT NOT NULL
    """

    def __init__(self, db_path: str = "logic.db"):
        self.db_path = db_path
        self._init_db()

    # ------------------------------------------------------------
    # INTERNAL: DB INIT
    # ------------------------------------------------------------

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS artifacts (
                artifact_id TEXT PRIMARY KEY,
                title TEXT,
                artifact_category TEXT,
                condensed_logic TEXT,
                raw_logic TEXT
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS relationships (
                relationship_id TEXT PRIMARY KEY,
                source_id TEXT NOT NULL,
                target_id TEXT NOT NULL,
                relationship_type TEXT NOT NULL
            )
        """)

        conn.commit()
        conn.close()

    # ------------------------------------------------------------
    # ARTIFACT CRUD
    # ------------------------------------------------------------

    def upsert_artifact(self, row: Dict[str, Any]) -> None:
        """
        USE: Insert or replace an artifact.
        row:
            {
                "artifact_id": str,
                "title": str,
                "artifact_category": str,
                "condensed_logic": str,
                "raw_logic": str,
            }
        """
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO artifacts (artifact_id, title, artifact_category, condensed_logic, raw_logic)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(artifact_id) DO UPDATE SET
                title=excluded.title,
                artifact_category=excluded.artifact_category,
                condensed_logic=excluded.condensed_logic,
                raw_logic=excluded.raw_logic
        """, (
            row["artifact_id"],
            row.get("title"),
            row.get("artifact_category"),
            row.get("condensed_logic"),
            row.get("raw_logic"),
        ))

        conn.commit()
        conn.close()

    def get_artifact(self, artifact_id: UUID) -> Optional[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute("""
            SELECT artifact_id, title, artifact_category, condensed_logic, raw_logic
            FROM artifacts
            WHERE artifact_id = ?
        """, (str(artifact_id),))

        row = cur.fetchone()
        conn.close()

        if not row:
            return None

        return {
            "artifact_id": row[0],
            "title": row[1],
            "artifact_category": row[2],
            "condensed_logic": row[3],
            "raw_logic": row[4],
        }

    def list_artifacts(self, limit: int = 1000) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute("""
            SELECT artifact_id, title, artifact_category, condensed_logic, raw_logic
            FROM artifacts
            ORDER BY artifact_id
            LIMIT ?
        """, (limit,))

        rows = cur.fetchall()
        conn.close()

        return [
            {
                "artifact_id": r[0],
                "title": r[1],
                "artifact_category": r[2],
                "condensed_logic": r[3],
                "raw_logic": r[4],
            }
            for r in rows
        ]

    # ------------------------------------------------------------
    # RELATIONSHIPS
    # ------------------------------------------------------------

    def upsert_relationship(self, row: Dict[str, Any]) -> None:
        """
        USE: Insert or replace a relationship.
        row:
            {
                "relationship_id": str,
                "source_id": str,
                "target_id": str,
                "relationship_type": str,
            }
        """
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO relationships (relationship_id, source_id, target_id, relationship_type)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(relationship_id) DO UPDATE SET
                source_id=excluded.source_id,
                target_id=excluded.target_id,
                relationship_type=excluded.relationship_type
        """, (
            row["relationship_id"],
            row["source_id"],
            row["target_id"],
            row["relationship_type"],
        ))

        conn.commit()
        conn.close()

    def get_relationships_for_artifact(self, artifact_id: UUID) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute("""
            SELECT relationship_id, source_id, target_id, relationship_type
            FROM relationships
            WHERE source_id = ? OR target_id = ?
        """, (str(artifact_id), str(artifact_id)))

        rows = cur.fetchall()
        conn.close()

        return [
            {
                "relationship_id": r[0],
                "source_id": r[1],
                "target_id": r[2],
                "relationship_type": r[3],
            }
            for r in rows
        ]

    # ------------------------------------------------------------
    # SEARCH
    # ------------------------------------------------------------

    def search_text(self, q: str, limit: int = 50) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        pattern = f"%{q}%"
        cur.execute("""
            SELECT artifact_id, title, artifact_category, condensed_logic
            FROM artifacts
            WHERE condensed_logic LIKE ? OR raw_logic LIKE ?
            ORDER BY artifact_id
            LIMIT ?
        """, (pattern, pattern, limit))

        rows = cur.fetchall()
        conn.close()

        return [
            {
                "artifact_id": r[0],
                "title": r[1],
                "artifact_category": r[2],
                "condensed_logic": r[3],
            }
            for r in rows
        ]

    def search_title(self, q: str, limit: int = 50) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        pattern = f"%{q}%"
        cur.execute("""
            SELECT artifact_id, title, artifact_category, condensed_logic
            FROM artifacts
            WHERE title LIKE ?
            ORDER BY artifact_id
            LIMIT ?
        """, (pattern, limit))

        rows = cur.fetchall()
        conn.close()

        return [
            {
                "artifact_id": r[0],
                "title": r[1],
                "artifact_category": r[2],
                "condensed_logic": r[3],
            }
            for r in rows
        ]

    def search_field(self, field: str, value: str, limit: int = 50) -> List[Dict[str, Any]]:
        if field not in {"artifact_category", "title"}:
            return []

        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute(f"""
            SELECT artifact_id, title, artifact_category, condensed_logic
            FROM artifacts
            WHERE {field} = ?
            ORDER BY artifact_id
            LIMIT ?
        """, (value, limit))

        rows = cur.fetchall()
        conn.close()

        return [
            {
                "artifact_id": r[0],
                "title": r[1],
                "artifact_category": r[2],
                "condensed_logic": r[3],
            }
            for r in rows
        ]

    # ------------------------------------------------------------
    # BROWSE / CATEGORY
    # ------------------------------------------------------------

    def list_artifacts_by_category(self, category: Optional[str], limit: int = 200) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        if category:
            cur.execute("""
                SELECT artifact_id, title, artifact_category, condensed_logic
                FROM artifacts
                WHERE artifact_category = ?
                ORDER BY artifact_id
                LIMIT ?
            """, (category, limit))
        else:
            cur.execute("""
                SELECT artifact_id, title, artifact_category, condensed_logic
                FROM artifacts
                ORDER BY artifact_id
                LIMIT ?
            """, (limit,))

        rows = cur.fetchall()
        conn.close()

        return [
            {
                "artifact_id": r[0],
                "title": r[1],
                "artifact_category": r[2],
                "condensed_logic": r[3],
            }
            for r in rows
        ]

    # ------------------------------------------------------------
    # LINEAGE HELPERS (simple)
    # ------------------------------------------------------------

    def get_parents(self, artifact_id: UUID) -> List[str]:
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute("""
            SELECT source_id
            FROM relationships
            WHERE target_id = ? AND relationship_type = 'derives_from'
        """, (str(artifact_id),))

        rows = cur.fetchall()
        conn.close()
        return [r[0] for r in rows]

    def get_children(self, artifact_id: UUID) -> List[str]:
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute("""
            SELECT target_id
            FROM relationships
            WHERE source_id = ? AND relationship_type = 'derives_from'
        """, (str(artifact_id),))

        rows = cur.fetchall()
        conn.close()
        return [r[0] for r in rows]
