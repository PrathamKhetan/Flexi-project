"""
Code Snippet & Postman Collection Generator Tool.
Generates runnable cURL, Python (requests), and JavaScript (fetch) snippets,
and packages endpoints into Postman Collection v2.1.0 JSON format.
Syllabus Alignment: Unit 1 & Unit 5 (Structured JSON parsing & API automation).
"""

import json
from typing import Any, Dict, List


class CurlGeneratorTool:
    """Generates multi-language client call snippets and Postman Collections."""

    def generate_snippets(self, endpoint: Dict[str, Any], base_url: str = "https://api.example.com") -> Dict[str, str]:
        path = endpoint.get("path", "/")
        method = endpoint.get("method", "GET").upper()
        params = endpoint.get("parameters", [])
        request_body = endpoint.get("request_body")
        auth_required = endpoint.get("auth_required", False)

        # Substitute sample path variables
        sample_path = path
        query_params = []
        for p in params:
            name = p.get("name", "")
            if p.get("in") == "path":
                sample_path = sample_path.replace(f"{{{name}}}", "123")
            elif p.get("in") == "query":
                query_params.append(f"{name}=example")

        full_url = f"{base_url}{sample_path}"
        if query_params:
            full_url += "?" + "&".join(query_params)

        headers = ["-H 'Content-Type: application/json'"]
        if auth_required:
            headers.append("-H 'Authorization: Bearer <YOUR_ACCESS_TOKEN>'")

        # 1. cURL
        curl_cmd = f"curl -X {method} '{full_url}' \\\n  " + " \\\n  ".join(headers)
        if request_body and method in ("POST", "PUT", "PATCH"):
            sample_payload = {"name": "sample_item", "quantity": 1}
            curl_cmd += f" \\\n  -d '{json.dumps(sample_payload)}'"

        # 2. Python Requests
        py_code = [
            "import requests",
            "",
            f"url = '{full_url}'",
            "headers = {",
            "    'Content-Type': 'application/json',",
        ]
        if auth_required:
            py_code.append("    'Authorization': 'Bearer <YOUR_ACCESS_TOKEN>',")
        py_code.append("}")

        if request_body and method in ("POST", "PUT", "PATCH"):
            py_code.append("payload = {'name': 'sample_item', 'quantity': 1}")
            py_code.append(f"response = requests.{method.lower()}(url, json=payload, headers=headers)")
        else:
            py_code.append(f"response = requests.{method.lower()}(url, headers=headers)")
        py_code.append("print(response.status_code)")
        py_code.append("print(response.json())")

        # 3. JavaScript Fetch
        js_code = [
            f"const response = await fetch('{full_url}', {{",
            f"  method: '{method}',",
            "  headers: {",
            "    'Content-Type': 'application/json',",
        ]
        if auth_required:
            js_code.append("    'Authorization': 'Bearer <YOUR_ACCESS_TOKEN>',")
        js_code.append("  },")
        if request_body and method in ("POST", "PUT", "PATCH"):
            js_code.append("  body: JSON.stringify({ name: 'sample_item', quantity: 1 }),")
        js_code.append("});")
        js_code.append("const data = await response.json();")
        js_code.append("console.log(data);")

        return {
            "curl": curl_cmd,
            "python": "\n".join(py_code),
            "javascript": "\n".join(js_code)
        }

    def generate_postman_collection(self, title: str, endpoints: List[Dict[str, Any]], base_url: str = "https://api.example.com") -> Dict[str, Any]:
        """Generates Postman Collection v2.1.0 JSON format."""
        items = []
        for ep in endpoints:
            path = ep.get("path", "/")
            method = ep.get("method", "GET").upper()
            summary = ep.get("summary", f"{method} {path}")
            description = ep.get("description", "")
            auth_required = ep.get("auth_required", False)

            path_segments = [seg for seg in path.strip("/").split("/") if seg]

            headers = [{"key": "Content-Type", "value": "application/json"}]
            if auth_required:
                headers.append({"key": "Authorization", "value": "Bearer {{access_token}}"})

            request_obj = {
                "method": method,
                "header": headers,
                "url": {
                    "raw": f"{{{{baseUrl}}}}/{'/'.join(path_segments)}",
                    "host": ["{{baseUrl}}"],
                    "path": path_segments
                },
                "description": description
            }

            if ep.get("request_body") and method in ("POST", "PUT", "PATCH"):
                request_obj["body"] = {
                    "mode": "raw",
                    "raw": json.dumps({"example_field": "sample_value"}, indent=2)
                }

            items.append({
                "name": summary,
                "request": request_obj,
                "response": []
            })

        return {
            "info": {
                "_postman_id": "auto-generated-collection-id",
                "name": f"{title} Postman Collection",
                "description": "Generated by Automated API Documentation Assistant",
                "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
            },
            "variable": [
                {"key": "baseUrl", "value": base_url, "type": "string"},
                {"key": "access_token", "value": "your_test_token_here", "type": "string"}
            ],
            "item": items
        }
