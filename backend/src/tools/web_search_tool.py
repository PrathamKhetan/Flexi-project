"""
Web Search & Documentation Lookup Tool.
Syllabus Alignment: Unit 1 (Wrap external search function as a FunctionTool, real-time search integration).
"""

import json
import os
import urllib.request
import urllib.parse
from typing import Any, Dict, List, Optional


class WebSearchTool:
    """Provides web search and standard API reference lookup for AI agents."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("TAVILY_API_KEY", "")

    def search(self, query: str, max_results: int = 3) -> List[Dict[str, Any]]:
        """
        Executes real-time search. Uses Tavily API if key is present;
        otherwise provides authoritative offline developer standard reference docs.
        """
        if self.api_key:
            try:
                return self._search_tavily(query, max_results)
            except Exception as e:
                pass  # Fallback to local knowledge base

        return self._search_offline_kb(query, max_results)

    def _search_tavily(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        url = "https://api.tavily.com/search"
        payload = json.dumps({
            "api_key": self.api_key,
            "query": query,
            "search_depth": "basic",
            "max_results": max_results
        }).encode("utf-8")

        req = urllib.request.Request(
            url,
            data=payload,
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            results = []
            for r in res_data.get("results", []):
                results.append({
                    "title": r.get("title", ""),
                    "url": r.get("url", ""),
                    "content": r.get("content", "")
                })
            return results

    def _search_offline_kb(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Offline developer reference database for API standards and best practices."""
        kb = [
            {
                "title": "OpenAPI 3.1.0 Specification Standards",
                "url": "https://spec.openapis.org/oas/v3.1.0",
                "content": "OpenAPI 3.1.0 aligns with JSON Schema draft 2020-12. Root elements must include openapi, info, paths, components, and servers. Every operation must provide summary and responses."
            },
            {
                "title": "OWASP API Security Top 10 Guidelines",
                "url": "https://owasp.org/www-project-api-security/",
                "content": "Key vulnerabilities: API1: Broken Object Level Auth (BOLA); API2: Broken Auth; API3: Broken Object Property Level Auth; API4: Unrestricted Resource Consumption; API8: Security Misconfiguration."
            },
            {
                "title": "FastAPI Response Models & Pydantic Schema Best Practices",
                "url": "https://fastapi.tiangolo.com/tutorial/response-model/",
                "content": "FastAPI uses Pydantic to filter and serialize outputs. Specify response_model and status_code to ensure proper OpenAPI schema generation."
            },
            {
                "title": "REST API Status Code Conventions",
                "url": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status",
                "content": "200 OK for successful reads, 201 Created for resource creation, 204 No Content for deletion, 400 Bad Request for client errors, 401 Unauthorized, 403 Forbidden, 422 Unprocessable Entity."
            }
        ]
        q = query.lower()
        matched = [doc for doc in kb if any(w in doc["title"].lower() or w in doc["content"].lower() for w in q.split())]
        return (matched or kb)[:max_results]

    def to_function_tool(self) -> Dict[str, Any]:
        """Exposes tool metadata in OpenAI / FunctionTool format (Unit 1)."""
        return {
            "type": "function",
            "function": {
                "name": "web_search",
                "description": "Searches online and developer reference documentation for API design patterns and OpenAPI standards.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query string"
                        },
                        "max_results": {
                            "type": "integer",
                            "description": "Maximum number of search results to return"
                        }
                    },
                    "required": ["query"]
                }
            }
        }
