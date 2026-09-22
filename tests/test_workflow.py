"""
Integration tests for the LangGraph multi-agent workflow and self-healing cycles.
Syllabus Alignment: Unit 2 (Handoffs) & Unit 3 (LangGraph Agentic workflow).
"""

import tempfile
import unittest
from pathlib import Path
from src.agents.supervisor import SupervisorAgent
from src.workflow.graph import DocumentationGraph
from src.memory.sqlite_memory import SQLiteAgentMemory


class TestWorkflowIntegration(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_workflow.db"
        self.memory = SQLiteAgentMemory(db_path=self.db_path)
        self.supervisor = SupervisorAgent(memory=self.memory)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_supervisor_pipeline_execution(self):
        code = """
from fastapi import FastAPI
app = FastAPI()

@app.get("/status")
def get_status():
    '''Check system status.'''
    return {"status": "ok"}
"""
        state = self.supervisor.run_pipeline(
            code_content=code,
            api_title="Status Service",
            framework="fastapi"
        )

        self.assertEqual(state["current_step"], "completed")
        self.assertEqual(len(state["endpoints"]), 1)
        self.assertIn("/status", state["openapi_spec"]["paths"])
        self.assertIn("Developer API Documentation", state["documentation_markdown"])
        self.assertIn("Status Service Postman Collection", state["postman_collection"]["info"]["name"])
        self.assertGreater(state["total_execution_time_ms"], 0)

        # Verify SQLite Persistence
        artifacts = self.memory.get_artifacts(state["session_id"])
        self.assertIn("openapi_json", artifacts)
        self.assertIn("markdown_doc", artifacts)
        self.assertIn("postman_json", artifacts)


if __name__ == "__main__":
    unittest.main()
