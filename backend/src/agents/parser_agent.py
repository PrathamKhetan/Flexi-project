"""
Parser Agent - Extracts AST structure, routes, schemas, and endpoint metadata.
Syllabus Alignment: Unit 2 (Specialist Agents, Code analysis) & Unit 4 (Custom Tool: Python code).
"""

import time
from typing import Any, Dict
from .base_agent import BaseAgent
from ..tools.ast_parser_tool import ASTParserTool


class ParserAgent(BaseAgent):
    """Specialist agent responsible for code inspection and AST decomposition."""

    def __init__(self, model_provider: str = "auto"):
        super().__init__(
            name="ParserAgent",
            role="AST & Code Inspection Specialist",
            goal="Dissect codebases to extract all routes, parameters, data models, typing annotations, and authentication hooks.",
            backstory="A compiler and AST engineer who parses source code with static analysis and regex fallback.",
            tools=[ASTParserTool()],
            model_provider=model_provider
        )
        self.parser_tool = ASTParserTool()

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        start_time = time.time()
        code = state.get("input_code", "")
        framework = state.get("framework", "fastapi")

        # Parse endpoints
        endpoints = self.parser_tool.parse(code, framework=framework)
        endpoint_dicts = [ep.to_dict() for ep in endpoints]

        execution_time_ms = round((time.time() - start_time) * 1000, 2)
        state["endpoints"] = endpoint_dicts
        state["current_step"] = "parsing_completed"
        state["execution_log"].append({
            "agent": self.name,
            "action": "ast_code_parsing",
            "thought": f"Extracted {len(endpoint_dicts)} endpoints using static AST analysis and pattern matching.",
            "endpoints_summary": [f"{ep['method']} {ep['path']}" for ep in endpoint_dicts],
            "execution_time_ms": execution_time_ms
        })

        return state
