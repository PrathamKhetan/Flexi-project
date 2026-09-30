"""
Unit tests for SQLite persistent session memory and trace logging.
Syllabus Alignment: Unit 1 (SQLite-based session storage).
"""

import tempfile
import unittest
from pathlib import Path
from src.memory.sqlite_memory import SQLiteAgentMemory


class TestSQLiteMemory(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_memory.db"
        self.memory = SQLiteAgentMemory(db_path=self.db_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_create_and_get_session(self):
        session_id = self.memory.create_session(title="Test Session", framework="fastapi", metadata={"env": "test"})
        self.assertIsNotNone(session_id)

        session = self.memory.get_session(session_id)
        self.assertIsNotNone(session)
        self.assertEqual(session["title"], "Test Session")
        self.assertEqual(session["framework"], "fastapi")
        self.assertEqual(session["metadata"].get("env"), "test")

    def test_record_turn_and_history(self):
        session_id = self.memory.create_session(title="Turn Test")
        turn_num = self.memory.record_turn(session_id, "Document API", {"step": 1, "status": "ok"})
        self.assertEqual(turn_num, 1)

        history = self.memory.get_session_history(session_id)
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["user_query"], "Document API")
        self.assertEqual(history[0]["agent_state"]["step"], 1)

    def test_log_trace_and_retrieve(self):
        session_id = self.memory.create_session(title="Trace Test")
        self.memory.log_trace(
            session_id=session_id,
            agent_name="PlannerAgent",
            action="plan_documentation",
            thought="Identified 5 endpoints",
            execution_time_ms=12.5
        )

        traces = self.memory.get_traces(session_id)
        self.assertEqual(len(traces), 1)
        self.assertEqual(traces[0]["agent_name"], "PlannerAgent")
        self.assertEqual(traces[0]["thought"], "Identified 5 endpoints")
        self.assertEqual(traces[0]["execution_time_ms"], 12.5)

    def test_save_and_get_artifacts(self):
        session_id = self.memory.create_session(title="Artifact Test")
        v1 = self.memory.save_artifact(session_id, "openapi_json", '{"openapi": "3.1.0"}')
        self.assertEqual(v1, 1)

        v2 = self.memory.save_artifact(session_id, "openapi_json", '{"openapi": "3.1.0", "updated": true}')
        self.assertEqual(v2, 2)

        artifacts = self.memory.get_artifacts(session_id, latest_only=True)
        self.assertIn("openapi_json", artifacts)
        self.assertEqual(artifacts["openapi_json"]["version"], 2)


if __name__ == "__main__":
    unittest.main()
