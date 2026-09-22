"""
Web Studio Backend Server for Automated API Documentation Assistant.
Syllabus Alignment: Unit 3 (Connect to UI, Visualize Agentic workflow) & Unit 4 (MCP service).
"""

import json
import os
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse, parse_qs

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.agents.supervisor import SupervisorAgent
from src.workflow.graph import DocumentationGraph
from src.workflow.visualizer import WorkflowVisualizer
from src.evaluation.metrics import PredictiveModelEvaluator
from src.memory.sqlite_memory import SQLiteAgentMemory

STATIC_DIR = Path(__file__).resolve().parent / "static"
SAMPLES_DIR = PROJECT_ROOT / "samples"


class StudioServerHandler(SimpleHTTPRequestHandler):
    """Handles static web UI assets and REST API endpoints for the agentic assistant."""

    supervisor = SupervisorAgent()
    memory = SQLiteAgentMemory()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        if path == "/":
            self._serve_file(STATIC_DIR / "index.html", "text/html")
        elif path.startswith("/static/"):
            filename = path.replace("/static/", "")
            file_path = STATIC_DIR / filename
            mime = "text/css" if filename.endswith(".css") else ("application/javascript" if filename.endswith(".js") else "text/html")
            self._serve_file(file_path, mime)
        elif path == "/api/sample":
            name = query.get("name", ["fastapi"])[0]
            self._handle_sample(name)
        elif path == "/api/sessions":
            sessions = self.memory.list_sessions(limit=15)
            self._send_json({"status": "success", "sessions": sessions})
        elif path == "/api/ml_analytics":
            ml_results = PredictiveModelEvaluator.run_sample_api_prediction()
            self._send_json(ml_results)
        elif path == "/api/graph_svg":
            svg = WorkflowVisualizer.to_svg()
            self._send_bytes(svg.encode("utf-8"), "image/svg+xml")
        else:
            self.send_error(404, "Page or resource not found")

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/api/generate":
            content_len = int(self.headers.get("Content-Length", 0))
            raw_body = self.rfile.read(content_len).decode("utf-8")
            try:
                body = json.loads(raw_body)
            except Exception:
                self._send_json({"status": "error", "message": "Malformed JSON payload"}, status=400)
                return

            code = body.get("code", "")
            title = body.get("title", "API Service")
            framework = body.get("framework", "auto")
            version = body.get("version", "1.0.0")
            model_provider = body.get("model_provider", "auto")

            try:
                # Orchestrate multi-agent execution pipeline
                supervisor = SupervisorAgent(model_provider=model_provider)
                state = supervisor.run_pipeline(
                    code_content=code,
                    api_title=title,
                    api_version=version,
                    framework=framework
                )

                response_data = {
                    "status": "success",
                    "session_id": state.get("session_id"),
                    "api_title": title,
                    "framework": state.get("framework"),
                    "endpoints": state.get("endpoints", []),
                    "openapi_spec": state.get("openapi_spec", {}),
                    "audit_report": state.get("audit_report", {}),
                    "documentation_markdown": state.get("documentation_markdown", ""),
                    "postman_collection": state.get("postman_collection", {}),
                    "execution_log": state.get("execution_log", []),
                    "total_execution_time_ms": state.get("total_execution_time_ms", 0)
                }
                self._send_json(response_data)

            except Exception as e:
                import traceback
                traceback.print_exc()
                self._send_json({"status": "error", "message": str(e)}, status=500)
        else:
            self.send_error(404, "Endpoint not found")

    def _handle_sample(self, name: str):
        mapping = {
            "fastapi": ("fastapi_ecommerce.py", "CloudCommerce API", "fastapi"),
            "flask": ("flask_user_service.py", "User Accounts API", "flask"),
            "express": ("express_payment_api.js", "Payments Gateway API", "express")
        }
        filename, title, framework = mapping.get(name, mapping["fastapi"])
        sample_path = SAMPLES_DIR / filename
        if sample_path.exists():
            with open(sample_path, "r", encoding="utf-8") as f:
                code_content = f.read()
            self._send_json({"code": code_content, "title": title, "framework": framework})
        else:
            self._send_json({"code": "# Sample code", "title": title, "framework": framework})

    def _serve_file(self, file_path: Path, mime_type: str):
        if not file_path.exists():
            self.send_error(404, "File not found")
            return
        with open(file_path, "rb") as f:
            content = f.read()
        self._send_bytes(content, mime_type)

    def _send_bytes(self, content: bytes, mime_type: str):
        self.send_response(200)
        self.send_header("Content-Type", mime_type)
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(content)

    def _send_json(self, data: Any, status: int = 200):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)


def run_studio_server(port: int = 7860):
    server = HTTPServer(("0.0.0.0", port), StudioServerHandler)
    print(f"\n========================================================")
    print(f"⚡ Automated API Documentation Assistant - Web Studio")
    print(f"👉 Local URL: http://127.0.0.1:{port}")
    print(f"========================================================\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStudio server stopped.")
        server.server_close()


if __name__ == "__main__":
    run_studio_server()
