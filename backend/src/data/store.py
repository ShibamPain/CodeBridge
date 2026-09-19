"""
Persistent store for history and review queue, backed by SQLite.

Replaces the old in-memory lists/dicts. Data now survives server restarts
and uvicorn --reload cycles, so review_ids stay valid until you actually
resolve them, and history isn't lost between test runs.

The DB file lives at backend/src/data/codebridge.db (auto-created on first
run). It's gitignored — see .gitignore's *.db entry — since it's local
runtime state, not source code.
"""
import json
import sqlite3
from pathlib import Path
from typing import Optional

_DB_PATH = Path(__file__).parent / "codebridge.db"


def _get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Create tables if they don't exist. Call once at app startup."""
    conn = _get_connection()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS history (
                id TEXT PRIMARY KEY,
                query_text TEXT NOT NULL,
                result_json TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS review_queue (
                review_id TEXT PRIMARY KEY,
                query_text TEXT NOT NULL,
                suggested_json TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


# --- History ---

def add_history_entry(entry: dict) -> None:
    conn = _get_connection()
    try:
        conn.execute(
            "INSERT INTO history (id, query_text, result_json, timestamp) VALUES (?, ?, ?, ?)",
            (entry["id"], entry["query_text"], json.dumps(entry["result"]), entry["timestamp"]),
        )
        conn.commit()
    finally:
        conn.close()


def get_history(limit: int = 50) -> list[dict]:
    conn = _get_connection()
    try:
        rows = conn.execute(
            "SELECT id, query_text, result_json, timestamp FROM history ORDER BY timestamp DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [
            {
                "id": row["id"],
                "query_text": row["query_text"],
                "result": json.loads(row["result_json"]),
                "timestamp": row["timestamp"],
            }
            for row in rows
        ]
    finally:
        conn.close()


# --- Review queue ---

def add_review_item(item: dict) -> None:
    conn = _get_connection()
    try:
        conn.execute(
            "INSERT INTO review_queue (review_id, query_text, suggested_json, created_at) VALUES (?, ?, ?, ?)",
            (item["review_id"], item["query_text"], json.dumps(item["suggested"]), item["created_at"]),
        )
        conn.commit()
    finally:
        conn.close()


def get_review_queue() -> list[dict]:
    conn = _get_connection()
    try:
        rows = conn.execute(
            "SELECT review_id, query_text, suggested_json, created_at FROM review_queue ORDER BY created_at DESC"
        ).fetchall()
        return [
            {
                "review_id": row["review_id"],
                "query_text": row["query_text"],
                "suggested": json.loads(row["suggested_json"]),
                "created_at": row["created_at"],
            }
            for row in rows
        ]
    finally:
        conn.close()


def get_review_item(review_id: str) -> Optional[dict]:
    conn = _get_connection()
    try:
        row = conn.execute(
            "SELECT review_id, query_text, suggested_json, created_at FROM review_queue WHERE review_id = ?",
            (review_id,),
        ).fetchone()
        if row is None:
            return None
        return {
            "review_id": row["review_id"],
            "query_text": row["query_text"],
            "suggested": json.loads(row["suggested_json"]),
            "created_at": row["created_at"],
        }
    finally:
        conn.close()


def delete_review_item(review_id: str) -> None:
    conn = _get_connection()
    try:
        conn.execute("DELETE FROM review_queue WHERE review_id = ?", (review_id,))
        conn.commit()
    finally:
        conn.close()