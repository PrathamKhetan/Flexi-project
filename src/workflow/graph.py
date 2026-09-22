"""
LangGraph StateGraph Workflow Orchestration for Automated API Documentation.
Syllabus Alignment: Unit 3 (Core Components of LangGraph, Agentic workflow in LangGraph, Conditional Edges).
"""

import time
from typing import Any, Callable, Dict, List, Optional
from .state import AgentWorkflowState
from ..agents.planner_agent import PlannerAgent
from ..agents.parser_agent import ParserAgent
from ..agents.spec_generator import SpecGeneratorAgent
from ..agents.quality_auditor import QualityAuditorAgent
from ..agents.doc_writer import DocWriterAgent
from ..memory.sqlite_memory import SQLiteAgentMemory
from ..config import MAX_SELF_HEALING_ITERATIONS


class StateGraph:
    """
    Lightweight, native implementation of LangGraph's StateGraph abstraction.
    Supports node registration, linear edges, conditional edges, and cyclical execution loops.
    """

    def __init__(self, state_schema=AgentWorkflowState):
        self.state_schema = state_schema
        self.nodes: Dict[str, Callable[[Dict[str, Any]], Dict[str, Any]]] = {}
        self.edges: Dict[str, str] = {}
        self.conditional_edges: Dict[str, Dict[str, Any]] = {}
        self.entry_point: Optional[str] = None

    def add_node(self, name: str, fn: Callable[[Dict[str, Any]], Dict[str, Any]]):
        self.nodes[name] = fn

    def set_entry_point(self, name: str):
        self.entry_point = name

    def add_edge(self, from_node: str, to_node: str):
        self.edges[from_node] = to_node

    def add_conditional_edges(self, source_node: str, condition_fn: Callable[[Dict[str, Any]], str], mapping: Dict[str, str]):
        self.conditional_edges[source_node] = {
            "condition": condition_fn,
            "mapping": mapping
        }

    def compile(self):
        return CompiledGraph(self)


class CompiledGraph:
    """Executable compiled workflow graph."""

    def __init__(self, graph: StateGraph):
        self.graph = graph

    def invoke(self, initial_state: Dict[str, Any], callback: Optional[Callable[[str, Dict[str, Any]], None]] = None) -> Dict[str, Any]:
        state = dict(initial_state)
        current_node = self.graph.entry_point

        visited_nodes = 0
        max_safety_steps = 25

        while current_node and current_node != "END" and visited_nodes < max_safety_steps:
            visited_nodes += 1
            node_fn = self.graph.nodes.get(current_node)
            if not node_fn:
                break

            # Execute node
            state = node_fn(state)
            if callback:
                callback(current_node, state)

            # Determine next node
            if current_node in self.graph.conditional_edges:
                cond_info = self.graph.conditional_edges[current_node]
                decision = cond_info["condition"](state)
                current_node = cond_info["mapping"].get(decision, "END")
            elif current_node in self.graph.edges:
                current_node = self.graph.edges[current_node]
            else:
                current_node = "END"

        return state


class DocumentationGraph:
    """Pre-configured LangGraph workflow for Automated API Documentation synthesis."""

    def __init__(self, memory: Optional[SQLiteAgentMemory] = None, model_provider: str = "auto"):
        self.memory = memory or SQLiteAgentMemory()
        self.model_provider = model_provider

        # Initialize specialist agents
        self.planner = PlannerAgent(model_provider=model_provider)
        self.parser = ParserAgent(model_provider=model_provider)
        self.spec_generator = SpecGeneratorAgent(model_provider=model_provider)
        self.quality_auditor = QualityAuditorAgent(model_provider=model_provider)
        self.doc_writer = DocWriterAgent(model_provider=model_provider)

        self.graph = self._build_graph()
        self.app = self.graph.compile()

    def _build_graph(self) -> StateGraph:
        workflow = StateGraph(state_schema=AgentWorkflowState)

        # 1. Register Nodes
        workflow.add_node("planner_node", self.planner.execute)
        workflow.add_node("parser_node", self.parser.execute)
        workflow.add_node("spec_generator_node", self.spec_generator.execute)
        workflow.add_node("quality_auditor_node", self.quality_auditor.execute)
        workflow.add_node("doc_writer_node", self.doc_writer.execute)

        # 2. Set Entry Point
        workflow.set_entry_point("planner_node")

        # 3. Define Linear Edges
        workflow.add_edge("planner_node", "parser_node")
        workflow.add_edge("parser_node", "spec_generator_node")
        workflow.add_edge("spec_generator_node", "quality_auditor_node")

        # 4. Define Conditional Edge (Reflection / Self-Healing Cycle)
        def should_revise_or_write(state: Dict[str, Any]) -> str:
            needs_revision = state.get("needs_revision", False)
            iteration = state.get("iteration_count", 0)
            if needs_revision and iteration < MAX_SELF_HEALING_ITERATIONS:
                return "revise"
            return "proceed"

        workflow.add_conditional_edges(
            "quality_auditor_node",
            should_revise_or_write,
            {
                "revise": "spec_generator_node",   # Cyclic edge back to Spec Generator
                "proceed": "doc_writer_node"        # Approved: proceed to Doc Writer
            }
        )

        workflow.add_edge("doc_writer_node", "END")

        return workflow

    def execute(self, code_content: str, api_title: str = "API Service", framework: str = "auto", session_id: Optional[str] = None) -> Dict[str, Any]:
        start_time = time.time()
        if not session_id:
            session_id = self.memory.create_session(title=f"Graph: {api_title}", framework=framework)

        initial_state: Dict[str, Any] = {
            "session_id": session_id,
            "input_code": code_content,
            "api_title": api_title,
            "api_version": "1.0.0",
            "api_description": "API Specification generated via LangGraph Multi-Agent Architecture",
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
            "current_step": "initialized",
            "execution_log": []
        }

        def node_callback(node_name: str, current_state: Dict[str, Any]):
            last_log = current_state["execution_log"][-1] if current_state.get("execution_log") else {}
            self.memory.log_trace(
                session_id=session_id,
                agent_name=node_name,
                action=last_log.get("action", node_name),
                thought=last_log.get("thought", ""),
                input_data={"node": node_name},
                output_data={"step": current_state.get("current_step")},
                execution_time_ms=last_log.get("execution_time_ms", 0)
            )

        final_state = self.app.invoke(initial_state, callback=node_callback)
        final_state["total_execution_time_ms"] = round((time.time() - start_time) * 1000, 2)
        return final_state
