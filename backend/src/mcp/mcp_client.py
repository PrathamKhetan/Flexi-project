"""
Python MCP Client - Discovers tool capabilities via manifests and invokes actions remotely.
Syllabus Alignment: Unit 4 (Write Python code to act as an MCP client, discovering tool capabilities).
"""

import json
import urllib.request
import urllib.parse
from typing import Any, Dict, List, Optional
from .mcp_server import MCPService


class MCPClient:
    """Connects to an external MCP server, discovers tools via manifests, and executes RPC actions."""

    def __init__(self, server_url: str = "http://127.0.0.1:8080"):
        self.server_url = server_url.rstrip("/")
        self.discovered_tools: Dict[str, Dict[str, Any]] = {}
        self._local_service = MCPService()

    def discover_tools(self) -> List[Dict[str, Any]]:
        """Queries the MCP server manifest to discover available tools and their JSON schemas."""
        req = urllib.request.Request(f"{self.server_url}/mcp/manifest")
        try:
            with urllib.request.urlopen(req, timeout=2) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                tools = data.get("tools", [])
                self.discovered_tools = {t["name"]: t for t in tools}
                return tools
        except Exception:
            manifest = self._local_service.get_manifest()
            tools = manifest.get("tools", [])
            self.discovered_tools = {t["name"]: t for t in tools}
            return tools

    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Executes an action on the MCP server via JSON-RPC 2.0 protocol."""
        if not self.discovered_tools:
            self.discover_tools()

        if tool_name not in self.discovered_tools:
            raise ValueError(f"Tool '{tool_name}' not available on server. Known tools: {list(self.discovered_tools.keys())}")

        payload = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            },
            "id": 42
        }

        req_data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            f"{self.server_url}/mcp",
            data=req_data,
            headers={"Content-Type": "application/json"}
        )

        try:
            with urllib.request.urlopen(req, timeout=3) as resp:
                res_data = json.loads(resp.read().decode("utf-8"))
                if "error" in res_data:
                    raise RuntimeError(f"MCP RPC Error: {res_data['error']}")
                content = res_data.get("result", {}).get("content", [])
                if content and "text" in content[0]:
                    return json.loads(content[0]["text"])
                return res_data.get("result")
        except Exception:
            # Standalone daemon not running or blocked: execute directly via MCP Service
            return self._local_service.execute_tool(tool_name, arguments)


class AIAssistantWithMCP:
    """Simulates an AI assistant agent that autonomously queries MCP to decide which tool to call."""

    def __init__(self, mcp_client: Optional[MCPClient] = None):
        self.client = mcp_client or MCPClient()

    def assist(self, user_code: str, goal: str = "document_and_audit") -> Dict[str, Any]:
        print("\n[AI Assistant] Step 1: Querying MCP server manifest for available capabilities...")
        tools = self.client.discover_tools()
        print(f"[AI Assistant] Discovered {len(tools)} tools: {[t['name'] for t in tools]}")

        print("\n[AI Assistant] Step 2: Reasoning about user goal and deciding tool invocation strategy...")
        if "audit" in goal.lower() or "document" in goal.lower():
            chosen_tool = "synthesize_documentation"
            print(f"[AI Assistant] Selected tool '{chosen_tool}' for full pipeline execution.")
            result = self.client.call_tool(chosen_tool, {"code": user_code, "title": "MCP Generated API"})
            return result
        else:
            chosen_tool = "parse_code_endpoints"
            print(f"[AI Assistant] Selected tool '{chosen_tool}' for route parsing.")
            return self.client.call_tool(chosen_tool, {"code": user_code})
