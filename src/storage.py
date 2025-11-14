"""SQLite storage helpers for EduXplain."""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, Optional

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "eduxplain.db"


def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                student_payload TEXT NOT NULL,
                prediction TEXT NOT NULL,
                probability REAL NOT NULL,
                reasons TEXT NOT NULL,
                recommendation TEXT NOT NULL,
                counterfactual TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
            """
        )
        # Check if user_id column exists, add it if it doesn't
        cursor = conn.execute("PRAGMA table_info(predictions)")
        columns = [row[1] for row in cursor.fetchall()]
        if "user_id" not in columns:
            conn.execute("ALTER TABLE predictions ADD COLUMN user_id INTEGER")
        conn.commit()


def save_prediction(student_payload: Dict[str, Any], result: Dict[str, Any], user_id: Optional[int] = None) -> None:
    init_db()
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            INSERT INTO predictions (
                user_id, student_payload, prediction, probability, reasons, recommendation, counterfactual
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                json.dumps(student_payload),
                result["prediction"],
                float(result["probability"]),
                json.dumps(result.get("reasons", [])),
                result.get("recommendation", ""),
                json.dumps(result.get("counterfactual_example", {})),
            ),
        )
        conn.commit()
