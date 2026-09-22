"""
Agentic State Schema for LangGraph Workflow.
Syllabus Alignment: Unit 3 (Core Components of LangGraph, State management).
"""

from typing import Any, Dict, List, Optional, TypedDict


class AgentWorkflowState(TypedDict, total=False):
    """Represents the shared memory state passing across nodes in the LangGraph graph."""
    session_id: str
    input_code: str
    framework: str
    api_title: str
    api_version: str
    api_description: str

    # Agent outputs
    plan: Dict[str, Any]
    endpoints: List[Dict[str, Any]]
    openapi_spec: Dict[str, Any]
    audit_report: Dict[str, Any]
    audit_feedback: List[str]

    # Handoff and loop flags
    needs_revision: bool
    iteration_count: int
    current_step: str

    # Final outputs
    documentation_markdown: str
    postman_collection: Dict[str, Any]
    execution_log: List[Dict[str, Any]]
    total_execution_time_ms: float
