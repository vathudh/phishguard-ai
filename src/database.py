import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path


class ScanRepository:
    """Small SQLite repository; raw email content never leaves the local machine."""

    def __init__(self, database_path):
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connection(self):
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self):
        with self._connection() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS scans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TEXT NOT NULL,
                    subject TEXT,
                    sender TEXT,
                    email_preview TEXT NOT NULL,
                    verdict TEXT NOT NULL,
                    risk_score INTEGER NOT NULL,
                    model_confidence REAL NOT NULL,
                    indicators_json TEXT NOT NULL,
                    feedback TEXT CHECK(feedback IN ('phishing', 'safe'))
                )
                """
            )

    def save_scan(self, subject, sender, email_text, result):
        with self._connection() as connection:
            cursor = connection.execute(
                """
                INSERT INTO scans (
                    created_at, subject, sender, email_preview, verdict, risk_score,
                    model_confidence, indicators_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    datetime.now(UTC).isoformat(),
                    subject[:300],
                    sender[:300],
                    email_text[:500].replace("\n", " "),
                    result["verdict"],
                    result["risk_score"],
                    result["model_confidence"],
                    json.dumps(result["indicators"]),
                ),
            )
            return cursor.lastrowid

    def list_scans(self, limit=30):
        with self._connection() as connection:
            rows = connection.execute(
                """
                SELECT id, created_at, subject, sender, email_preview, verdict, risk_score,
                       model_confidence, indicators_json, feedback
                FROM scans ORDER BY id DESC LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [self._row_to_dict(row) for row in rows]

    def save_feedback(self, scan_id, feedback):
        with self._connection() as connection:
            cursor = connection.execute(
                "UPDATE scans SET feedback = ? WHERE id = ?", (feedback, scan_id)
            )
            return cursor.rowcount == 1

    def export_json(self, export_directory):
        export_directory = Path(export_directory)
        export_directory.mkdir(parents=True, exist_ok=True)
        output_path = export_directory / "phishguard_scan_history.json"
        output_path.write_text(json.dumps(self.list_scans(limit=10_000), indent=2), encoding="utf-8")
        return output_path

    @staticmethod
    def _row_to_dict(row):
        item = dict(row)
        item["indicators"] = json.loads(item.pop("indicators_json"))
        return item
