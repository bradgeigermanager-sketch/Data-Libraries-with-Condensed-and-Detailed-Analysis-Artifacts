"""
MODULE: connection.py
LOCATION: backend/db/connection.py
NOTATION: PostgreSQL connection manager for the immutable logic graph.
USE: Provides a clean, reusable interface for acquiring DB connections.
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor


class DatabaseConnection:
    """
    NOTATION: DB Connection Wrapper.
    USE: Centralized access point for all repository modules.
    """

    def __init__(self):
        self.db_url = os.getenv("DATABASE_URL")

        if not self.db_url:
            raise RuntimeError("DATABASE_URL environment variable is not set.")

    def get_connection(self):
        """
        NOTATION: Connection Factory.
        USE: Returns a new PostgreSQL connection with RealDictCursor.
        """
        return psycopg2.connect(
            self.db_url,
            cursor_factory=RealDictCursor
        )

    def execute(self, query: str, params=None, fetchone=False, fetchall=False):
        """
        NOTATION: Convenience Executor.
        USE: Simplifies repository operations while preserving immutability rules.
        """
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params or [])

                if fetchone:
                    return cur.fetchone()

                if fetchall:
                    return cur.fetchall()

                conn.commit()
                return None
