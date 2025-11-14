"""SQLite storage helpers for EduXplain."""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any, Dict

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "eduxplain.db"


def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_payload TEXT NOT NULL,
                prediction TEXT NOT NULL,
                probability REAL NOT NULL,
                reasons TEXT NOT NULL,
                recommendation TEXT NOT NULL,
                counterfactual TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()


def save_prediction(student_payload: Dict[str, Any], result: Dict[str, Any]) -> None:
    init_db()
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            INSERT INTO predictions (
                student_payload, prediction, probability, reasons, recommendation, counterfactual
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                json.dumps(student_payload),
                result["prediction"],
                float(result["probability"]),
                json.dumps(result.get("reasons", [])),
                result.get("recommendation", ""),
                json.dumps(result.get("counterfactual_example", {})),
            ),
        )
        conn.commit()
