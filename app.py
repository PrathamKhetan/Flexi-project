"""
Gradio UI Connector & Application Entrypoint.
Syllabus Alignment: Unit 3 (Connect to UI (Gradio), Visualize Agentic workflow).
"""

import json
import os
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.agents.supervisor import SupervisorAgent
from src.workflow.visualizer import WorkflowVisualizer
from src.evaluation.metrics import PredictiveModelEvaluator


def build_gradio_app():
    """Constructs Gradio Blocks UI if gradio is installed."""
    try:
        import gradio as gr
    except ImportError:
        print("[Notice] Gradio package is not installed. Launching built-in Web Studio UI instead...")
        from web.server import run_studio_server
        run_studio_server(port=7860)
        return

    supervisor = SupervisorAgent()

    def process_api_documentation(code, title, framework, model_provider):
        if not code.strip():
            return "Please provide API source code.", "{}", "{}", "No execution trace."

        state = supervisor.run_pipeline(
            code_content=code,
            api_title=title,
            framework=framework
        )

        md_doc = state.get("documentation_markdown", "")
        openapi_str = json.dumps(state.get("openapi_spec", {}), indent=2)
        security_str = json.dumps(state.get("audit_report", {}), indent=2)
        postman_str = json.dumps(state.get("postman_collection", {}), indent=2)

        traces = []
        for l in state.get("execution_log", []):
            traces.append(f"[{l.get('agent')}] {l.get('action')}: {l.get('thought')} ({l.get('execution_time_ms', 0)}ms)")
        trace_str = "\n".join(traces)

        return md_doc, openapi_str, security_str, postman_str, trace_str

    with gr.Blocks(title="Automated API Documentation Assistant", theme=gr.themes.Soft()) as demo:
        gr.Markdown("""
        # ⚡ Automated API Documentation Assistant
        ### Symbiosis International University • Agentic AI & Automation (CA3 Mini Project)
        *Multi-Agent Orchestration with LangGraph, SQLite Memory, OWASP Guardrails & MCP Integration.*
        """)

        with gr.Row():
            with gr.Column(scale=1):
                api_title_input = gr.Textbox(label="API Service Name", value="CloudCommerce API")
                framework_select = gr.Dropdown(
                    label="Framework",
                    choices=["auto", "fastapi", "flask", "express"],
                    value="auto"
                )
                model_select = gr.Dropdown(
                    label="Model Engine",
                    choices=["auto", "openai", "gemini", "local"],
                    value="auto"
                )
                code_input = gr.Textbox(
                    label="API Source Code",
                    lines=14,
                    placeholder="Paste FastAPI, Flask, or Express route code here..."
                )
                btn_run = gr.Button("🚀 Generate Documentation via Agent Team", variant="primary")

            with gr.Column(scale=2):
                with gr.Tabs():
                    with gr.TabItem("📖 Developer Guide"):
                        output_md = gr.Markdown("Documentation will appear here.")
                    with gr.TabItem("🌐 OpenAPI 3.1.0 Spec"):
                        output_openapi = gr.Code(language="json", label="openapi.json")
                    with gr.TabItem("🛡️ OWASP Security Audit"):
                        output_security = gr.Code(language="json", label="Audit Findings & Guardrails")
                    with gr.TabItem("📦 Postman v2.1"):
                        output_postman = gr.Code(language="json", label="postman_collection.json")
                    with gr.TabItem("🔍 Agent Handoff Traces"):
                        output_traces = gr.Textbox(label="Step-by-Step Multi-Agent Execution Log", lines=12)

        btn_run.click(
            fn=process_api_documentation,
            inputs=[code_input, api_title_input, framework_select, model_select],
            outputs=[output_md, output_openapi, output_security, output_postman, output_traces]
        )

    demo.launch(server_name="0.0.0.0", server_port=7860)


if __name__ == "__main__":
    build_gradio_app()
