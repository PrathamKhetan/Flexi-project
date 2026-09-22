"""
Webhook Listener & CI/CD Automation Handler.
Simulates and handles incoming GitHub/GitLab push webhooks to trigger automatic API doc updates.
Syllabus Alignment: Unit 5 (Build agentic workflows, automation process).
"""

import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Any, Callable, Dict, Optional
from ..agents.supervisor import SupervisorAgent


class WebhookHandler(BaseHTTPRequestHandler):
    """Processes incoming CI/CD and GitHub push webhooks."""

    supervisor = SupervisorAgent()

    def do_POST(self):
        content_len = int(self.headers.get("Content-Length", 0))
        payload_raw = self.rfile.read(content_len).decode("utf-8")
        try:
            event_data = json.loads(payload_raw)
        except Exception:
            event_data = {}

        # Extract repo details and code
        repo_name = event_data.get("repository", {}).get("name", "Incoming Repository")
        code_diff = event_data.get("code", "")
        if not code_diff and "commits" in event_data:
            code_diff = event_data["commits"][0].get("modified_code", "")

        if not code_diff:
            code_diff = """from fastapi import FastAPI
app = FastAPI()
@app.get('/health')
def health():
    return {'status': 'ok'}
"""

        # Run pipeline
        result_state = self.supervisor.run_pipeline(
            code_content=code_diff,
            api_title=repo_name,
            framework="auto"
        )

        response_body = {
            "status": "success",
            "message": f"Documentation generated for {repo_name}",
            "endpoints_documented": len(result_state.get("endpoints", [])),
            "quality_score": result_state.get("audit_report", {}).get("overall_quality_score", 0),
            "openapi_title": result_state.get("openapi_spec", {}).get("info", {}).get("title")
        }

        resp_bytes = json.dumps(response_body).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(resp_bytes)))
        self.end_headers()
        self.wfile.write(resp_bytes)


class WebhookAutomationServer:
    """Runs a webhook server listening for automated CI/CD push triggers."""

    def __init__(self, port: int = 9000):
        self.port = port
        self.httpd = None

    def start(self):
        self.httpd = HTTPServer(("127.0.0.1", self.port), WebhookHandler)
        print(f"[Webhook Automation Server] Listening on http://127.0.0.1:{self.port}/webhook")
        try:
            self.httpd.serve_forever()
        except KeyboardInterrupt:
            if self.httpd:
                self.httpd.server_close()
