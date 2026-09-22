"""
AST and Regex Code Analysis Tool for Automated Endpoint Extraction.
Supports FastAPI, Flask, Django REST Framework, and Express.js codebases.
Syllabus Alignment: Unit 1 & Unit 4 (Custom Tool, Code analysis & modeling).
"""

import ast
import re
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional


@dataclass
class ParsedEndpoint:
    path: str
    method: str
    function_name: str
    summary: str = ""
    description: str = ""
    parameters: List[Dict[str, Any]] = field(default_factory=list)
    request_body: Optional[Dict[str, Any]] = None
    responses: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    auth_required: bool = False
    tags: List[str] = field(default_factory=list)
    source_line: int = 1

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ASTParserTool:
    """Extracts REST API endpoints, schemas, parameters, and auth requirements from source code."""

    def parse(self, code_content: str, framework: str = "auto") -> List[ParsedEndpoint]:
        """Detects framework and parses endpoints accordingly."""
        if framework == "auto":
            framework = self.detect_framework(code_content)

        if framework in ("fastapi", "flask", "django"):
            return self.parse_python(code_content, framework)
        elif framework in ("express", "nodejs", "javascript"):
            return self.parse_javascript(code_content)
        else:
            # Fallback to python AST, if syntax fails fallback to regex
            try:
                return self.parse_python(code_content, "fastapi")
            except Exception:
                return self.parse_javascript(code_content)

    def detect_framework(self, code: str) -> str:
        if "from fastapi" in code or "FastAPI(" in code or "@app.get" in code or "@router." in code:
            return "fastapi"
        if "from flask" in code or "Flask(" in code or "@app.route" in code:
            return "flask"
        if "express()" in code or "require('express')" in code or "from 'express'" in code:
            return "express"
        if "rest_framework" in code or "APIView" in code:
            return "django"
        return "fastapi"

    def parse_python(self, code: str, framework: str) -> List[ParsedEndpoint]:
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            # Try regex fallback for partial Python snippets
            return self._regex_fallback_python(code)

        endpoints: List[ParsedEndpoint] = []
        pydantic_models = self._extract_pydantic_models(tree)

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                endpoint = self._inspect_python_function(node, framework, pydantic_models)
                if endpoint:
                    endpoints.append(endpoint)

        return endpoints

    def _extract_pydantic_models(self, tree: ast.AST) -> Dict[str, Dict[str, Any]]:
        models = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                fields = {}
                for item in node.body:
                    if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                        field_name = item.target.id
                        type_str = ast.unparse(item.annotation) if hasattr(ast, "unparse") else "string"
                        fields[field_name] = {
                            "type": self._map_python_type(type_str),
                            "required": item.value is None
                        }
                if fields:
                    models[node.name] = fields
        return models

    def _inspect_python_function(
        self,
        node: ast.FunctionDef,
        framework: str,
        models: Dict[str, Dict[str, Any]]
    ) -> Optional[ParsedEndpoint]:
        for decorator in node.decorator_list:
            route_info = self._extract_route_info(decorator, framework)
            if route_info:
                path, method, tags, status_code = route_info
                docstring = ast.get_docstring(node) or ""
                summary = docstring.strip().split("\n")[0] if docstring else node.name.replace("_", " ").title()
                description = docstring.strip() if docstring else f"Handler for {method} {path}"

                # Extract path, query, and body parameters
                params, request_body, auth_required = self._extract_parameters(node, path, models)

                responses = {
                    str(status_code): {
                        "description": "Successful Response",
                        "content_type": "application/json"
                    },
                    "400": {"description": "Bad Request"},
                    "422": {"description": "Validation Error"},
                    "500": {"description": "Internal Server Error"}
                }
                if auth_required:
                    responses["401"] = {"description": "Unauthorized"}
                    responses["403"] = {"description": "Forbidden"}

                # Infer response model from return annotation if present
                if node.returns and hasattr(ast, "unparse"):
                    ret_type = ast.unparse(node.returns)
                    if ret_type in models:
                        responses[str(status_code)]["schema_name"] = ret_type
                        responses[str(status_code)]["fields"] = models[ret_type]

                return ParsedEndpoint(
                    path=path,
                    method=method,
                    function_name=node.name,
                    summary=summary,
                    description=description,
                    parameters=params,
                    request_body=request_body,
                    responses=responses,
                    auth_required=auth_required,
                    tags=tags or [path.strip("/").split("/")[0].title() or "Default"],
                    source_line=node.lineno
                )
        return None

    def _extract_route_info(self, dec: ast.AST, framework: str):
        # Handles @app.get("/items", tags=["items"], status_code=201)
        if isinstance(dec, ast.Call):
            func = dec.func
            method = "GET"
            path = "/"
            tags = []
            status_code = 200

            if isinstance(func, ast.Attribute):
                attr_name = func.attr.lower()
                if attr_name in ("get", "post", "put", "delete", "patch", "options", "head"):
                    method = attr_name.upper()
                elif attr_name == "route":
                    # Flask @app.route('/items', methods=['POST'])
                    method = "GET"
                    for kw in dec.keywords:
                        if kw.arg == "methods" and isinstance(kw.value, (ast.List, ast.Tuple)):
                            for elt in kw.value.elts:
                                if isinstance(elt, ast.Constant):
                                    method = elt.value.upper()
                                    break
                else:
                    return None
            else:
                return None

            # First positional arg is usually path
            if dec.args and isinstance(dec.args[0], ast.Constant) and isinstance(dec.args[0].value, str):
                path = dec.args[0].value

            for kw in dec.keywords:
                if kw.arg == "tags" and isinstance(kw.value, ast.List):
                    tags = [e.value for e in kw.value.elts if isinstance(e, ast.Constant)]
                elif kw.arg == "status_code" and isinstance(kw.value, ast.Constant):
                    status_code = kw.value.value

            if method == "POST" and status_code == 200:
                status_code = 201

            return path, method, tags, status_code
        return None

    def _extract_parameters(
        self,
        node: ast.FunctionDef,
        path: str,
        models: Dict[str, Dict[str, Any]]
    ):
        params = []
        request_body = None
        auth_required = False

        path_params = re.findall(r"\{([a-zA-Z0-9_]+)\}", path)

        # Build dictionary of arg defaults
        defaults_map = {}
        num_args = len(node.args.args)
        num_defaults = len(node.args.defaults)
        offset = num_args - num_defaults
        for i, default_node in enumerate(node.args.defaults):
            arg_name = node.args.args[offset + i].arg
            default_str = ast.unparse(default_node) if hasattr(ast, "unparse") else ""
            defaults_map[arg_name] = default_str

        for arg in node.args.args:
            name = arg.arg
            if name in ("self", "cls", "request", "response"):
                continue

            type_hint = "string"
            if arg.annotation and hasattr(ast, "unparse"):
                type_hint = ast.unparse(arg.annotation)

            default_val = defaults_map.get(name, "")

            # Check if this parameter is an authentication dependency
            if (
                "Depends" in type_hint
                or "Depends" in default_val
                or "get_current_user" in type_hint
                or "get_current_user" in default_val
                or "auth" in name.lower()
                or "token" in name.lower()
            ):
                auth_required = True
                continue

            # Check if it's a Pydantic model (request body)
            if type_hint in models or "Create" in type_hint or "Update" in type_hint or "Schema" in type_hint or "Body" in type_hint:
                request_body = {
                    "schema_name": type_hint,
                    "content_type": "application/json",
                    "fields": models.get(type_hint, {})
                }
                continue

            # Path parameter
            if name in path_params:
                params.append({
                    "name": name,
                    "in": "path",
                    "type": self._map_python_type(type_hint),
                    "required": True,
                    "description": f"The unique identifier for {name}"
                })
            else:
                # Query parameter
                params.append({
                    "name": name,
                    "in": "query",
                    "type": self._map_python_type(type_hint),
                    "required": False,
                    "description": f"Filter or parameter: {name}"
                })

        return params, request_body, auth_required

    def _map_python_type(self, type_str: str) -> str:
        s = type_str.lower()
        if "int" in s:
            return "integer"
        if "float" in s:
            return "number"
        if "bool" in s:
            return "boolean"
        if "list" in s or "[]" in s:
            return "array"
        if "dict" in s:
            return "object"
        return "string"

    def parse_javascript(self, code: str) -> List[ParsedEndpoint]:
        """Parses Express.js / Node.js router files via regular expressions."""
        endpoints: List[ParsedEndpoint] = []
        # Pattern: app.get('/api/users', authMiddleware, (req, res) => ...)
        pattern = r"(?:app|router)\.(get|post|put|delete|patch)\s*\(\s*['\"]([^'\"]+)['\"]\s*,?(.*?)(?:function|\(.*?\)\s*=>)"
        matches = re.finditer(pattern, code, re.IGNORECASE | re.DOTALL)

        for match in matches:
            method = match.group(1).upper()
            raw_path = match.group(2)
            middlewares = match.group(3)

            # Express path parameter conversion: /users/:id -> /users/{id}
            path = re.sub(r":([a-zA-Z0-9_]+)", r"{\1}", raw_path)
            auth_required = bool(re.search(r"auth|token|jwt|protect|guard", middlewares, re.IGNORECASE))

            path_params = re.findall(r"\{([a-zA-Z0-9_]+)\}", path)
            parameters = [
                {
                    "name": p,
                    "in": "path",
                    "type": "string",
                    "required": True,
                    "description": f"Identifier for {p}"
                }
                for p in path_params
            ]

            request_body = None
            if method in ("POST", "PUT", "PATCH"):
                request_body = {
                    "content_type": "application/json",
                    "schema_name": f"{method.capitalize()}Request",
                    "fields": {"payload": {"type": "object", "required": True}}
                }

            tag = path.strip("/").split("/")[0].title() or "General"
            endpoints.append(ParsedEndpoint(
                path=path,
                method=method,
                function_name=f"handle_{method.lower()}_{path.replace('/', '_').strip('_')}",
                summary=f"{method} {path}",
                description=f"Express.js endpoint handling {method} {path}",
                parameters=parameters,
                request_body=request_body,
                responses={
                    "200" if method != "POST" else "201": {"description": "OK"},
                    "400": {"description": "Bad Request"},
                    "500": {"description": "Internal Server Error"}
                },
                auth_required=auth_required,
                tags=[tag]
            ))

        return endpoints

    def _regex_fallback_python(self, code: str) -> List[ParsedEndpoint]:
        endpoints = []
        pattern = r"@(?:app|router)\.(get|post|put|delete|patch)\s*\(\s*['\"]([^'\"]+)['\"]"
        for match in re.finditer(pattern, code, re.IGNORECASE):
            method = match.group(1).upper()
            path = match.group(2)
            endpoints.append(ParsedEndpoint(
                path=path,
                method=method,
                function_name=f"{method.lower()}_{path.replace('/', '_').strip('_')}",
                summary=f"{method} {path}",
                description=f"API Endpoint for {method} {path}",
                parameters=[],
                responses={"200": {"description": "Success"}},
                tags=["API"]
            ))
        return endpoints
