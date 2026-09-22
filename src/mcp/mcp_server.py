"""
Model Context Protocol (MCP) Server for Automated API Documentation.
Syllabus Alignment: Unit 4 (Components of MCP, Build and expose tool as an MCP service, Deploy apps as MCP servers).
"""

import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from typing import Any, Dict
from ..tools.ast_parser_tool import ASTParserTool
from ..tools.security_auditor import SecurityAuditorTool
from ..agents.spec_generator import SpecGeneratorAgent
from ..agents.supervisor import SupervisorAgent

MANIFEST_PATH = Path(__file__).resolve().parent / "mcp_manifest.json"


class MCPService:
    """Core logic for executing MCP-registered tools."""

    def __init__(self):
        self.parser_tool = ASTParserTool()
        self.security_tool = SecurityAuditorTool()
        self.spec_generator = SpecGeneratorAgent()
        self.supervisor = SupervisorAgent()

    def get_manifest(self) -> Dict[str, Any]:
        with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    def execute_tool(self, tool_name: str, args: Dict[str, Any]) -> Any:
        if tool_name == "parse_code_endpoints":
            code = args.get("code", "")
            framework = args.get("framework", "auto")
            parsed = self.parser_tool.parse(code, framework=framework)
            return [p.to_dict() for p in parsed]

        elif tool_name == "generate_openapi_spec":
            endpoints = args.get("endpoints", [])
            title = args.get("title", "REST API")
            version = args.get("version", "1.0.0")
            state = {
                "endpoints": endpoints,
                "api_title": title,
                "api_version": version,
                "execution_log": []
            }
            res_state = self.spec_generator.execute(state)
            return res_state.get("openapi_spec", {})

        elif tool_name == "audit_api_security":
            endpoints = args.get("endpoints", [])
            return self.security_tool.audit(endpoints)

        elif tool_name == "synthesize_documentation":
            code = args.get("code", "")
            title = args.get("title", "API Service")
            framework = args.get("framework", "auto")
            state = self.supervisor.run_pipeline(code_content=code, api_title=title, framework=framework)
            return {
                "openapi_spec": state.get("openapi_spec"),
                "quality_score": state.get("audit_report", {}).get("overall_quality_score"),
                "markdown_doc": state.get("documentation_markdown"),
                "postman_collection": state.get("postman_collection")
            }
        else:
            raise ValueError(f"Unknown tool: {tool_name}")


class MCPHandler(BaseHTTPRequestHandler):
    """Handles JSON-RPC 2.0 and MCP REST requests."""

    service = MCPService()

    def do_GET(self):
        if self.path in ("/mcp/manifest", "/manifest.json", "/"):
            self._send_json(self.service.get_manifest())
        else:
            self.send_error(404, "Endpoint not found")

    def do_POST(self):
        content_len = int(self.headers.get("Content-Length", 0))
        post_body = self.rfile.read(content_len).decode("utf-8")
        try:
            req_data = json.loads(post_body)
        except Exception:
            self._send_error_response(-32700, "Parse error: Invalid JSON")
            return

        # Check for JSON-RPC 2.0 format
        method = req_data.get("method")
        params = req_data.get("params", {})
        rpc_id = req_data.get("id", 1)

        if method == "tools/list":
            manifest = self.service.get_manifest()
            self._send_json({"jsonrpc": "2.0", "result": manifest.get("tools", []), "id": rpc_id})
        elif method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            try:
                result = self.service.execute_tool(tool_name, arguments)
                self._send_json({"jsonrpc": "2.0", "result": {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}, "id": rpc_id})
            except Exception as e:
                self._send_error_response(-32603, f"Internal error during execution: {str(e)}", rpc_id)
        else:
            # Direct REST fallback
            tool_name = req_data.get("action") or req_data.get("tool")
            args = req_data.get("args", {})
            if tool_name:
                try:
                    result = self.service.execute_tool(tool_name, args)
                    self._send_json({"status": "success", "result": result})
                except Exception as e:
                    self._send_json({"status": "error", "message": str(e)}, status=500)
            else:
                self._send_error_response(-32601, f"Method '{method}' not found", rpc_id)

    def _send_json(self, data: Any, status: int = 200):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def _send_error_response(self, code: int, message: str, rpc_id: Any = None):
        self._send_json({
            "jsonrpc": "2.0",
            "error": {"code": code, "message": message},
            "id": rpc_id
        }, status=400)


class MCPServer:
    """Manages the lifecycle of the Model Context Protocol Server."""

    def __init__(self, host: str = "127.0.0.1", port: int = 8080):
        self.host = host
        self.port = port
        self.httpd = None

    def start(self):
        self.httpd = HTTPServer((self.host, self.port), MCPHandler)
        print(f"[MCP Server] Running at http://{self.host}:{self.port}")
        try:
            self.httpd.serve_forever()
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        if self.httpd:
            self.httpd.server_close()
            print("[MCP Server] Stopped.")


if __name__ == "__main__":
    server = MCPServer(port=8080)
    server.start()
