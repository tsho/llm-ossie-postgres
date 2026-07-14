"""Database client for PostgreSQL connections."""

import os
from typing import Optional

import psycopg2


def get_connection():
    """Create and return a PostgreSQL connection."""
    return psycopg2.connect(
        host=os.getenv("PGHOST", "localhost"),
        port=int(os.getenv("PGPORT", "5432")),
        dbname=os.getenv("PGDATABASE", "demo"),
        user=os.getenv("PGUSER", "demo"),
        password=os.getenv("PGPASSWORD", "demo"),
    )


def execute_query(sql: str) -> Optional[tuple]:
    """Execute SQL and return (columns, rows) or None on error."""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(sql)
        columns = (
            [desc[0] for desc in cur.description] if cur.description else []
        )
        rows = cur.fetchall() if cur.description else []
        cur.close()
        conn.close()
        return columns, rows
    except Exception as e:
        return None, str(e)
