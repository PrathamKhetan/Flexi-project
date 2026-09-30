"""
Automated API Documentation Assistant - FastAPI Application & Gradio Mount.
Compatible with Vercel Serverless, Render, Docker, and Local Execution.
Exports top-level 'app' instance of FastAPI.
"""

import json
import os
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, Response, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from src.agents.supervisor import SupervisorAgent
from src.workflow.visualizer import WorkflowVisualizer
from src.evaluation.metrics import PredictiveModelEvaluator
from src.memory.sqlite_memory import SQLiteAgentMemory
from src.mcp.mcp_server import MCPService
from src.config import SAMPLES_DIR

STATIC_DIR = PROJECT_ROOT / "web" / "static"

# Export top-level "app" FastAPI instance for Vercel
app = FastAPI(
    title="Automated API Documentation Assistant",
    description="Multi-Agent API Documentation Synthesis & Security Auditing with LangGraph, SQLite Memory & MCP",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for Web Studio UI
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Shared instances
mcp_service = MCPService()
memory = SQLiteAgentMemory()


@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serves the Interactive Glassmorphic Web Studio UI."""
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return HTMLResponse("<h1>Automated API Documentation Assistant</h1><p>API Server Running.</p>")


@app.get("/health")
@app.get("/healthz")
async def health_check():
    """Health check endpoint for Vercel / Render / Cloud monitoring."""
    return {"status": "healthy", "service": "Automated API Documentation Assistant"}


@app.get("/api/sample")
async def get_sample_code(name: str = "fastapi"):
    """Loads pre-packaged sample backend codebases."""
    mapping = {
        "fastapi": ("fastapi_ecommerce.py", "CloudCommerce API", "fastapi"),
        "flask": ("flask_user_service.py", "User Accounts API", "flask"),
        "express": ("express_payment_api.js", "Payments Gateway API", "express")
    }
    filename, title, framework = mapping.get(name, mapping["fastapi"])
    sample_path = SAMPLES_DIR / filename
    if sample_path.exists():
        with open(sample_path, "r", encoding="utf-8") as f:
            code_content = f.read()
        return {"code": code_content, "title": title, "framework": framework}
    return {"code": "# Sample code", "title": title, "framework": framework}


@app.post("/api/generate")
async def generate_documentation(request: Request):
    """Executes the LangGraph Multi-Agent documentation pipeline."""
    try:
        body = await request.json()
    except Exception:
        return JSONResponse(status_code=400, content={"status": "error", "message": "Invalid JSON body"})

    code = body.get("code", "")
    title = body.get("title", "API Service")
    framework = body.get("framework", "auto")
    version = body.get("version", "1.0.0")
    model_provider = body.get("model_provider", "auto")

    try:
        supervisor = SupervisorAgent(model_provider=model_provider)
        state = supervisor.run_pipeline(
            code_content=code,
            api_title=title,
            api_version=version,
            framework=framework
        )

        return {
            "status": "success",
            "session_id": state.get("session_id"),
            "api_title": title,
            "framework": state.get("framework"),
            "endpoints": state.get("endpoints", []),
            "openapi_spec": state.get("openapi_spec", {}),
            "audit_report": state.get("audit_report", {}),
            "documentation_markdown": state.get("documentation_markdown", ""),
            "postman_collection": state.get("postman_collection", {}),
            "execution_log": state.get("execution_log", []),
            "total_execution_time_ms": state.get("total_execution_time_ms", 0)
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})


@app.get("/api/sessions")
async def get_sessions():
    """Lists persistent SQLite agent memory sessions (Unit 1)."""
    sessions = memory.list_sessions(limit=15)
    return {"status": "success", "sessions": sessions}


@app.get("/api/ml_analytics")
async def get_ml_analytics():
    """Runs Classical ML predictive regression evaluation (Unit 4)."""
    return PredictiveModelEvaluator.run_sample_api_prediction()


@app.get("/api/graph_svg")
async def get_graph_svg():
    """Renders the SVG Agentic Workflow Graph (Unit 3)."""
    svg = WorkflowVisualizer.to_svg()
    return Response(content=svg, media_type="image/svg+xml")


@app.get("/mcp/manifest")
@app.get("/manifest.json")
async def get_mcp_manifest():
    """Model Context Protocol (MCP) tool capability manifest (Unit 4)."""
    return mcp_service.get_manifest()


@app.post("/mcp")
async def handle_mcp_request(request: Request):
    """Model Context Protocol (MCP) JSON-RPC 2.0 tool execution endpoint (Unit 4)."""
    try:
        req_data = await request.json()
    except Exception:
        return JSONResponse(status_code=400, content={"jsonrpc": "2.0", "error": {"code": -32700, "message": "Parse error: Invalid JSON"}, "id": None})

    method = req_data.get("method")
    params = req_data.get("params", {})
    rpc_id = req_data.get("id", 1)

    if method == "tools/list":
        manifest = mcp_service.get_manifest()
        return {"jsonrpc": "2.0", "result": manifest.get("tools", []), "id": rpc_id}
    elif method == "tools/call":
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        try:
            result = mcp_service.execute_tool(tool_name, arguments)
            return {"jsonrpc": "2.0", "result": {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}, "id": rpc_id}
        except Exception as e:
            return JSONResponse(status_code=400, content={"jsonrpc": "2.0", "error": {"code": -32603, "message": str(e)}, "id": rpc_id})
    else:
        tool_name = req_data.get("action") or req_data.get("tool")
        args = req_data.get("args", {})
        if tool_name:
            try:
                result = mcp_service.execute_tool(tool_name, args)
                return {"status": "success", "result": result}
            except Exception as e:
                return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})
        return JSONResponse(status_code=400, content={"jsonrpc": "2.0", "error": {"code": -32601, "message": f"Method '{method}' not found"}, "id": rpc_id})


# Optional: Mount Gradio interface at /gradio if gradio is installed (Unit 3)
try:
    import gradio as gr

    def gradio_process(code, title, framework, model_provider):
        if not code.strip():
            return "Please provide API source code.", "{}", "{}", "{}"
        supervisor = SupervisorAgent(model_provider=model_provider)
        res = supervisor.run_pipeline(code_content=code, api_title=title, framework=framework)
        return (
            res.get("documentation_markdown", ""),
            json.dumps(res.get("openapi_spec", {}), indent=2),
            json.dumps(res.get("audit_report", {}), indent=2),
            json.dumps(res.get("postman_collection", {}), indent=2),
        )

    with gr.Blocks(title="Automated API Documentation Assistant") as gradio_demo:
        gr.Markdown("## ⚡ Automated API Documentation Assistant (Gradio Interface)")
        with gr.Row():
            with gr.Column():
                g_title = gr.Textbox(label="API Title", value="CloudCommerce API")
                g_frame = gr.Dropdown(label="Framework", choices=["auto", "fastapi", "flask", "express"], value="auto")
                g_model = gr.Dropdown(label="Model", choices=["auto", "openai", "gemini", "local"], value="auto")
                g_code = gr.Textbox(label="Code", lines=10, placeholder="Paste API code here...")
                g_btn = gr.Button("Generate Documentation", variant="primary")
            with gr.Column():
                g_out_md = gr.Markdown()
                g_out_spec = gr.Code(language="json", label="OpenAPI 3.1.0")
                g_out_sec = gr.Code(language="json", label="Security Audit")
                g_out_postman = gr.Code(language="json", label="Postman Collection")

        g_btn.click(gradio_process, inputs=[g_code, g_title, g_frame, g_model], outputs=[g_out_md, g_out_spec, g_out_sec, g_out_postman])

    app = gr.mount_gradio_app(app, gradio_demo, path="/gradio")
except Exception:
    # Gradio not installed or running in lean serverless environment
    pass


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    try:
        import uvicorn
        print(f"Starting server on http://0.0.0.0:{port}")
        uvicorn.run("app:app", host="0.0.0.0", port=port, reload=False)
    except ImportError:
        from web.server import run_studio_server
        run_studio_server(port=port)
