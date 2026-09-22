"""
SQLite Persistent Memory and Session Storage for AI Agents.
Syllabus Alignment: Unit 1 (Persistent session storage, state management, trace logging).
"""

import json
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from ..config import SQLITE_DB_PATH


class SQLiteAgentMemory:
    """Manages persistent sessions, agent state, execution traces, and artifacts."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or SQLITE_DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # Sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    framework TEXT DEFAULT 'fastapi',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT
                )
            """)

            # Multi-turn interaction history
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS turns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    turn_number INTEGER NOT NULL,
                    user_query TEXT NOT NULL,
                    agent_state_json TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES sessions (session_id) ON DELETE CASCADE
                )
            """)

            # Step-by-step agent execution traces (Unit 1 & Unit 2 handoffs)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS agent_traces (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    agent_name TEXT NOT NULL,
                    action TEXT NOT NULL,
                    thought TEXT,
                    input_data TEXT,
                    output_data TEXT,
                    execution_time_ms REAL DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES sessions (session_id) ON DELETE CASCADE
                )
            """)

            # Generated documentation artifacts & versions
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS doc_artifacts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    artifact_type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    version INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES sessions (session_id) ON DELETE CASCADE
                )
            """)
            conn.commit()

    def create_session(self, title: str = "New Documentation Session", framework: str = "fastapi", metadata: Optional[Dict[str, Any]] = None) -> str:
        session_id = str(uuid.uuid4())
        meta_json = json.dumps(metadata or {})
        with self._get_connection() as conn:
            conn.execute(
                "INSERT INTO sessions (session_id, title, framework, metadata) VALUES (?, ?, ?, ?)",
                (session_id, title, framework, meta_json)
            )
            conn.commit()
        return session_id

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM sessions WHERE session_id = ?", (session_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return {
                "session_id": row["session_id"],
                "title": row["title"],
                "framework": row["framework"],
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
                "metadata": json.loads(row["metadata"] or "{}")
            }

    def list_sessions(self, limit: int = 20) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM sessions ORDER BY updated_at DESC LIMIT ?", (limit,))
            rows = cursor.fetchall()
            return [
                {
                    "session_id": r["session_id"],
                    "title": r["title"],
                    "framework": r["framework"],
                    "created_at": r["created_at"],
                    "updated_at": r["updated_at"],
                    "metadata": json.loads(r["metadata"] or "{}")
                }
                for r in rows
            ]

    def record_turn(self, session_id: str, user_query: str, agent_state: Dict[str, Any]) -> int:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM turns WHERE session_id = ?", (session_id,))
            turn_num = (cursor.fetchone()[0] or 0) + 1

            state_json = json.dumps(agent_state, default=str)
            cursor.execute(
                "INSERT INTO turns (session_id, turn_number, user_query, agent_state_json) VALUES (?, ?, ?, ?)",
                (session_id, turn_num, user_query, state_json)
            )
            conn.execute(
                "UPDATE sessions SET updated_at = CURRENT_TIMESTAMP WHERE session_id = ?",
                (session_id,)
            )
            conn.commit()
            return turn_num

    def get_session_history(self, session_id: str) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM turns WHERE session_id = ? ORDER BY turn_number ASC", (session_id,))
            rows = cursor.fetchall()
            return [
                {
                    "turn_number": r["turn_number"],
                    "user_query": r["user_query"],
                    "agent_state": json.loads(r["agent_state_json"]),
                    "created_at": r["created_at"]
                }
                for r in rows
            ]

    def log_trace(
        self,
        session_id: str,
        agent_name: str,
        action: str,
        thought: str = "",
        input_data: Any = None,
        output_data: Any = None,
        execution_time_ms: float = 0.0
    ):
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO agent_traces (session_id, agent_name, action, thought, input_data, output_data, execution_time_ms)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    session_id,
                    agent_name,
                    action,
                    thought,
                    json.dumps(input_data, default=str) if input_data is not None else "",
                    json.dumps(output_data, default=str) if output_data is not None else "",
                    execution_time_ms
                )
            )
            conn.commit()

    def get_traces(self, session_id: str) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM agent_traces WHERE session_id = ? ORDER BY id ASC", (session_id,))
            rows = cursor.fetchall()
            return [
                {
                    "id": r["id"],
                    "session_id": r["session_id"],
                    "agent_name": r["agent_name"],
                    "action": r["action"],
                    "thought": r["thought"],
                    "input_data": r["input_data"],
                    "output_data": r["output_data"],
                    "execution_time_ms": r["execution_time_ms"],
                    "created_at": r["created_at"]
                }
                for r in rows
            ]

    def save_artifact(self, session_id: str, artifact_type: str, content: str) -> int:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COALESCE(MAX(version), 0) + 1 FROM doc_artifacts WHERE session_id = ? AND artifact_type = ?",
                (session_id, artifact_type)
            )
            next_version = cursor.fetchone()[0]

            cursor.execute(
                "INSERT INTO doc_artifacts (session_id, artifact_type, content, version) VALUES (?, ?, ?, ?)",
                (session_id, artifact_type, content, next_version)
            )
            conn.commit()
            return next_version

    def get_artifacts(self, session_id: str, latest_only: bool = True) -> Dict[str, Any]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if latest_only:
                cursor.execute("""
                    SELECT a.* FROM doc_artifacts a
                    INNER JOIN (
                        SELECT artifact_type, MAX(version) as max_v
                        FROM doc_artifacts WHERE session_id = ?
                        GROUP BY artifact_type
                    ) b ON a.artifact_type = b.artifact_type AND a.version = b.max_v
                    WHERE a.session_id = ?
                """, (session_id, session_id))
            else:
                cursor.execute("SELECT * FROM doc_artifacts WHERE session_id = ? ORDER BY version DESC", (session_id,))

            rows = cursor.fetchall()
            result = {}
            for r in rows:
                result[r["artifact_type"]] = {
                    "content": r["content"],
                    "version": r["version"],
                    "created_at": r["created_at"]
                }
            return result
