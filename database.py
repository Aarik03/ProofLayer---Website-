from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

DB_PATH = Path("prooflayer.db")


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS verifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                verification_id TEXT UNIQUE NOT NULL,
                type TEXT NOT NULL,
                score REAL NOT NULL,
                risk_level TEXT NOT NULL,
                hash TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                metadata TEXT
            )
            """
        )
        conn.commit()


def insert_verification(
    *,
    verification_id: str,
    content_type: str,
    score: float,
    risk_level: str,
    content_hash: str,
    timestamp: str,
    metadata: dict[str, Any],
) -> None:
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO verifications (
                verification_id,
                type,
                score,
                risk_level,
                hash,
                timestamp,
                metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                verification_id,
                content_type,
                score,
                risk_level,
                content_hash,
                timestamp,
                json.dumps(metadata),
            ),
        )
        conn.commit()


def _row_to_record(row: sqlite3.Row) -> dict[str, Any]:
    metadata_value = row["metadata"]
    parsed_metadata: dict[str, Any] = {}
    if metadata_value:
        try:
            parsed_metadata = json.loads(metadata_value)
        except json.JSONDecodeError:
            parsed_metadata = {"raw": metadata_value}

    return {
        "id": row["id"],
        "verification_id": row["verification_id"],
        "type": row["type"],
        "score": float(row["score"]),
        "risk_level": row["risk_level"],
        "hash": row["hash"],
        "timestamp": row["timestamp"],
        "metadata": parsed_metadata,
    }


def get_verification_by_id(verification_id: str) -> dict[str, Any] | None:
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT id, verification_id, type, score, risk_level, hash, timestamp, metadata
            FROM verifications
            WHERE verification_id = ?
            """,
            (verification_id,),
        ).fetchone()

    if row is None:
        return None
    return _row_to_record(row)


def get_dashboard_stats() -> dict[str, Any]:
    with get_connection() as conn:
        total_scans = conn.execute("SELECT COUNT(*) FROM verifications").fetchone()[0]

        risk_rows = conn.execute(
            """
            SELECT risk_level, COUNT(*) AS count
            FROM verifications
            GROUP BY risk_level
            """
        ).fetchall()

        risk_counts = {"High": 0, "Medium": 0, "Low": 0}
        for row in risk_rows:
            risk = str(row["risk_level"])
            count = int(row["count"])
            risk_counts[risk] = count

        recent_rows = conn.execute(
            """
            SELECT id, verification_id, type, score, risk_level, hash, timestamp, metadata
            FROM verifications
            ORDER BY id DESC
            LIMIT 5
            """
        ).fetchall()

    return {
        "total_scans": int(total_scans),
        "risk_counts": risk_counts,
        "last_5_scans": [_row_to_record(row) for row in recent_rows],
    }


def db_health() -> dict[str, Any]:
    with get_connection() as conn:
        cursor = conn.execute("SELECT 1")
        value = cursor.fetchone()[0]
    return {"ok": value == 1, "db_path": str(DB_PATH.resolve())}
