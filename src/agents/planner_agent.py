"""
Planner Agent - Analyzes repository structure, determines documentation roadmap, and prioritizes tasks.
Syllabus Alignment: Unit 2 (AI Agent Team Structure, Planner Agent, Task Delegation).
"""

import time
from typing import Any, Dict
from .base_agent import BaseAgent
from ..tools.ast_parser_tool import ASTParserTool


class PlannerAgent(BaseAgent):
    """Specialist agent responsible for planning documentation strategy and scope."""

    def __init__(self, model_provider: str = "auto"):
        super().__init__(
            name="PlannerAgent",
            role="Lead API Documentation Architect",
            goal="Analyze raw codebase structure, detect framework patterns, and devise an execution plan for complete documentation coverage.",
            backstory="An expert technical architect with deep mastery over REST paradigms, microservices, OpenAPI standards, and developer experience.",
            tools=[ASTParserTool()],
            model_provider=model_provider
        )
        self.parser_tool = ASTParserTool()

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        start_time = time.time()
        code = state.get("input_code", "")
        framework_override = state.get("framework", "auto")

        # 1. Detect framework
        detected_framework = self.parser_tool.detect_framework(code) if framework_override == "auto" else framework_override

        # 2. Estimate scope
        preliminary_endpoints = self.parser_tool.parse(code, framework=detected_framework)
        endpoint_count = len(preliminary_endpoints)

        # 3. Construct documentation plan
        plan = {
            "detected_framework": detected_framework,
            "estimated_endpoint_count": endpoint_count,
            "security_features_detected": any(ep.auth_required for ep in preliminary_endpoints),
            "execution_steps": [
                "Step 1: Deep AST & Schema extraction of routes, params, models.",
                "Step 2: OpenAPI 3.1.0 JSON & YAML specification synthesis.",
                "Step 3: OWASP API Security Top 10 and structural validation.",
                "Step 4: Self-healing schema repair loop if errors detected.",
                "Step 5: Multi-language SDK code snippet & Markdown portal authoring.",
                "Step 6: Postman Collection v2.1.0 packaging."
            ],
            "target_artifacts": [
                "openapi.json",
                "openapi.yaml",
                "README_API.md",
                "postman_collection.json",
                "security_audit_report.json"
            ],
            "quality_threshold": 85.0
        }

        execution_time_ms = round((time.time() - start_time) * 1000, 2)
        state["plan"] = plan
        state["framework"] = detected_framework
        state["current_step"] = "planning_completed"
        state["execution_log"].append({
            "agent": self.name,
            "action": "plan_documentation",
            "thought": f"Analyzed codebase. Framework: {detected_framework}. Found {endpoint_count} candidate endpoints. Formulated 6-stage execution plan.",
            "execution_time_ms": execution_time_ms
        })

        return state
