import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Optional

DB_PATH = Path("mappings.db")


@contextmanager
def get_connection() -> Generator[sqlite3.Connection, None, None]:
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute("PRAGMA journal_mode=WAL;")
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS message_map (
                group_message_id INTEGER PRIMARY KEY,
                user_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_message_map_user_id
            ON message_map (user_id)
            """
        )


def save_mapping(group_message_id: int, user_id: int) -> None:
    with get_connection() as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO message_map (group_message_id, user_id)
            VALUES (?, ?)
            """,
            (group_message_id, user_id),
        )


def get_user_id(group_message_id: int) -> Optional[int]:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT user_id FROM message_map WHERE group_message_id = ?",
            (group_message_id,),
        ).fetchone()
    return int(row[0]) if row else None
