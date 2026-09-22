"""
Supervisor Agent - Manager Function coordinating specialist agent handoffs and enforcing execution boundaries.
Syllabus Alignment: Unit 2 (AI Agent Team Structure, Manager Function Responsibilities, Handoff mechanisms).
"""

import json
import time
from typing import Any, Dict, Optional
from .base_agent import BaseAgent
from .planner_agent import PlannerAgent
from .parser_agent import ParserAgent
from .spec_generator import SpecGeneratorAgent
from .quality_auditor import QualityAuditorAgent
from .doc_writer import DocWriterAgent
from ..memory.sqlite_memory import SQLiteAgentMemory
from ..config import MAX_SELF_HEALING_ITERATIONS


class SupervisorAgent(BaseAgent):
    """Manager Function directing the multi-agent API documentation pipeline."""

    def __init__(self, memory: Optional[SQLiteAgentMemory] = None, model_provider: str = "auto"):
        super().__init__(
            name="SupervisorAgent",
            role="Engineering Manager & Multi-Agent Orchestrator",
            goal="Oversee documentation synthesis, route tasks to specialist agents, monitor guardrails, and enforce quality sign-off.",
            backstory="A seasoned principal engineering manager ensuring seamless team collaboration, SLA adherence, and verified outputs.",
            tools=[],
            model_provider=model_provider
        )
        self.memory = memory or SQLiteAgentMemory()
        self.planner = PlannerAgent(model_provider=model_provider)
        self.parser = ParserAgent(model_provider=model_provider)
        self.spec_gen = SpecGeneratorAgent(model_provider=model_provider)
        self.auditor = QualityAuditorAgent(model_provider=model_provider)
        self.writer = DocWriterAgent(model_provider=model_provider)

    def run_pipeline(
        self,
        code_content: str,
        api_title: str = "API Service",
        api_version: str = "1.0.0",
        framework: str = "auto",
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes the multi-agent pipeline with handoffs, guardrails, and self-healing cycles.
        """
        start_total = time.time()

        # 1. Initialize Persistent Session (Unit 1)
        if not session_id:
            session_id = self.memory.create_session(
                title=f"DocGen: {api_title}",
                framework=framework,
                metadata={"api_version": api_version}
            )

        # 2. Build Initial Workflow State
        state: Dict[str, Any] = {
            "session_id": session_id,
            "input_code": code_content,
            "api_title": api_title,
            "api_version": api_version,
            "framework": framework,
            "plan": {},
            "endpoints": [],
            "openapi_spec": {},
            "audit_report": {},
            "audit_feedback": [],
            "needs_revision": False,
            "iteration_count": 0,
            "documentation_markdown": "",
            "postman_collection": {},
            "current_step": "started",
            "execution_log": []
        }

        self._record_trace(session_id, "Manager initiated documentation run.")

        # --- Handoff 1: Supervisor -> PlannerAgent ---
        state = self.planner.execute(state)
        self._record_agent_trace(session_id, self.planner.name, state)

        # --- Handoff 2: PlannerAgent -> ParserAgent ---
        state = self.parser.execute(state)
        self._record_agent_trace(session_id, self.parser.name, state)

        # --- Handoff 3: ParserAgent -> SpecGeneratorAgent ---
        state = self.spec_gen.execute(state)
        self._record_agent_trace(session_id, self.spec_gen.name, state)

        # --- Handoff 4: SpecGeneratorAgent -> QualityAuditorAgent (Guardrail evaluation) ---
        state = self.auditor.execute(state)
        self._record_agent_trace(session_id, self.auditor.name, state)

        # --- Self-Healing Reflection Loop (Unit 2 & 3) ---
        while state.get("needs_revision") and state.get("iteration_count", 0) < MAX_SELF_HEALING_ITERATIONS:
            self._record_trace(
                session_id,
                f"Manager detected schema defects. Routing back to SpecGenerator for revision iteration {state['iteration_count']}."
            )
            state = self.spec_gen.execute(state)
            self._record_agent_trace(session_id, self.spec_gen.name, state)

            state = self.auditor.execute(state)
            self._record_agent_trace(session_id, self.auditor.name, state)

        # --- Handoff 5: QualityAuditorAgent -> DocWriterAgent ---
        state = self.writer.execute(state)
        self._record_agent_trace(session_id, self.writer.name, state)

        # Final Executive Summary
        total_time_ms = round((time.time() - start_total) * 1000, 2)
        state["total_execution_time_ms"] = total_time_ms
        state["current_step"] = "completed"

        # Save Artifacts to Persistent SQLite Memory
        self.memory.save_artifact(session_id, "openapi_json", json.dumps(state["openapi_spec"], indent=2))
        self.memory.save_artifact(session_id, "markdown_doc", state["documentation_markdown"])
        self.memory.save_artifact(session_id, "postman_json", json.dumps(state["postman_collection"], indent=2))
        self.memory.save_artifact(session_id, "security_report", json.dumps(state["audit_report"], indent=2))

        # Record conversation turn
        self.memory.record_turn(
            session_id=session_id,
            user_query=f"Generate documentation for {api_title} ({framework})",
            agent_state={
                "endpoints_count": len(state["endpoints"]),
                "quality_score": state["audit_report"].get("overall_quality_score", 0),
                "iterations": state["iteration_count"],
                "total_time_ms": total_time_ms
            }
        )

        return state

    def _record_trace(self, session_id: str, action: str, thought: str = ""):
        self.memory.log_trace(
            session_id=session_id,
            agent_name=self.name,
            action=action,
            thought=thought
        )

    def _record_agent_trace(self, session_id: str, agent_name: str, state: Dict[str, Any]):
        last_log = state["execution_log"][-1] if state.get("execution_log") else {}
        self.memory.log_trace(
            session_id=session_id,
            agent_name=agent_name,
            action=last_log.get("action", "step"),
            thought=last_log.get("thought", ""),
            input_data={"step": state.get("current_step")},
            output_data={"status": "ok"},
            execution_time_ms=last_log.get("execution_time_ms", 0)
        )
