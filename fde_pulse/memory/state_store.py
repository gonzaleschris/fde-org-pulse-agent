"""Multi-week persistent state and memory store."""
import sqlite3
import json
from pathlib import Path
from typing import Optional, Dict, Any, List, Union
from ..models.schemas import WeeklyStateSnapshot, ExecutiveReport

class StateStore:
    """Persistent SQLite & JSON memory store for tracking historical FDE chat intelligence."""

    def __init__(self, db_path: Optional[Union[Path, str]] = None):
        if db_path == ":memory:":
            self.db_path = ":memory:"
            self._mem_conn = sqlite3.connect(":memory:")
        else:
            self.db_path = Path(db_path) if db_path else (Path(__file__).resolve().parent.parent.parent / "data" / "fde_pulse_memory.db")
            if isinstance(self.db_path, Path):
                self.db_path.parent.mkdir(parents=True, exist_ok=True)
            self._mem_conn = None
        self._init_db()

    def _get_connection(self):
        if self._mem_conn is not None:
            return self._mem_conn
        conn = sqlite3.connect(str(self.db_path))
        conn.execute("PRAGMA journal_mode=MEMORY")
        return conn

    def _init_db(self):
        """Initializes database tables."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS weekly_snapshots (
                week_identifier TEXT PRIMARY KEY,
                generated_at TEXT,
                total_message_volume INTEGER,
                wins_count INTEGER,
                raw_json TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reports (
                week_identifier TEXT PRIMARY KEY,
                generated_at TEXT,
                markdown_content TEXT,
                raw_json TEXT
            )
        """)
        conn.commit()
        if self._mem_conn is None:
            conn.close()

    def save_weekly_snapshot(self, snapshot: WeeklyStateSnapshot):
        """Saves a weekly snapshot into the persistent store."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO weekly_snapshots 
            (week_identifier, generated_at, total_message_volume, wins_count, raw_json)
            VALUES (?, ?, ?, ?, ?)
        """, (
            snapshot.week_identifier,
            snapshot.generated_at,
            snapshot.total_message_volume,
            snapshot.wins_count,
            snapshot.model_dump_json()
        ))
        conn.commit()
        if self._mem_conn is None:
            conn.close()

    def get_weekly_snapshot(self, week_identifier: str) -> Optional[WeeklyStateSnapshot]:
        """Retrieves a historical weekly snapshot."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT raw_json FROM weekly_snapshots WHERE week_identifier = ?",
            (week_identifier,)
        )
        row = cursor.fetchone()
        if self._mem_conn is None:
            conn.close()
        if row:
            return WeeklyStateSnapshot.model_validate_json(row[0])
        return None

    def save_report(self, report: ExecutiveReport, markdown_text: str):
        """Persists the rendered executive report."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO reports
            (week_identifier, generated_at, markdown_content, raw_json)
            VALUES (?, ?, ?, ?)
        """, (
            report.week_identifier,
            report.generated_at,
            markdown_text,
            report.model_dump_json()
        ))
        conn.commit()
        if self._mem_conn is None:
            conn.close()

    def compute_week_over_week_delta(self, current_snapshot: WeeklyStateSnapshot, previous_week_id: str) -> Dict[str, Any]:
        """Computes trend deltas between current week and previous week."""
        prev = self.get_weekly_snapshot(previous_week_id)
        if not prev:
            return {
                "Historical Baseline": "No prior week snapshot available. Setting baseline for future trend comparison.",
                "Volume Trend": "Baseline established."
            }

        vol_delta = current_snapshot.total_message_volume - prev.total_message_volume
        vol_pct = (vol_delta / prev.total_message_volume * 100) if prev.total_message_volume > 0 else 0
        wins_delta = current_snapshot.wins_count - prev.wins_count

        return {
            "Message Activity Delta": f"{'+' if vol_delta >= 0 else ''}{vol_delta} messages ({vol_pct:+.1f}%) vs {previous_week_id}",
            "Customer Wins Velocity": f"{current_snapshot.wins_count} wins this week ({'+' if wins_delta >= 0 else ''}{wins_delta} vs {previous_week_id})",
            "Trending Topic Continuity": f"{len(current_snapshot.top_topics)} active primary tracks tracked in memory.",
            "Active Risk Status": f"{len(current_snapshot.active_risks)} open friction items monitored by leadership."
        }
