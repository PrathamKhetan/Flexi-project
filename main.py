"""
CLI Entrypoint and Demonstration Runner for Automated API Documentation Assistant.
Provides command-line execution, sample demonstration, MCP simulation, and ML analytics.
"""

import argparse
import json
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.agents.supervisor import SupervisorAgent
from src.workflow.visualizer import WorkflowVisualizer
from src.evaluation.metrics import APIDocEvaluator, PredictiveModelEvaluator
from src.mcp.mcp_client import AIAssistantWithMCP


def main():
    parser = argparse.ArgumentParser(
        description="Automated API Documentation Assistant (CA3 Mini Project - Symbiosis International University)"
    )
    parser.add_argument("--sample", choices=["fastapi", "flask", "express"], default="fastapi",
                        help="Run multi-agent generation on a pre-packaged sample API")
    parser.add_argument("--file", type=str, help="Path to custom source code file to document")
    parser.add_argument("--web", action="store_true", help="Launch interactive Web Studio UI")
    parser.add_argument("--mcp-demo", action="store_true", help="Run Model Context Protocol (MCP) tool discovery demo")
    parser.add_argument("--ml-eval", action="store_true", help="Run Unit 4 Classical ML predictive regression evaluation")
    parser.add_argument("--title", type=str, default="API Service", help="Title for the generated API documentation")
    parser.add_argument("--model", type=str, default="auto", choices=["auto", "openai", "gemini", "local"],
                        help="Model provider to use for agent reasoning")

    args = parser.parse_args()

    # Mode 1: Launch Web Studio
    if args.web:
        from web.server import run_studio_server
        run_studio_server()
        return

    # Mode 2: MCP Tool Discovery & Remote Action Demo (Unit 4)
    if args.mcp_demo:
        print("\n" + "=" * 70)
        print("⚡ MODEL CONTEXT PROTOCOL (MCP) DEMONSTRATION (UNIT 4)")
        print("=" * 70)
        sample_code = """from fastapi import FastAPI
app = FastAPI()
@app.get('/users/{user_id}')
def get_user(user_id: int):
    return {'id': user_id}
"""
        assistant = AIAssistantWithMCP()
        result = assistant.assist(sample_code, goal="document_and_audit")
        print("\n[MCP Demo Completed] Result Quality Score:", result.get("quality_score"))
        return

    # Mode 3: Classical ML Predictive Evaluation (Unit 4)
    if args.ml_eval:
        print("\n" + "=" * 70)
        print("📊 CLASSICAL ML PREDICTIVE ANALYTICS & REGRESSION EVALUATION (UNIT 4)")
        print("=" * 70)
        ml_results = PredictiveModelEvaluator.run_sample_api_prediction()
        print(f"Dataset: {ml_results['dataset']} ({ml_results['samples_count']} samples)")
        print(f"Model Type: {ml_results['model_type']}")
        print(f"Regression Formula: {ml_results['formula']}")
        print("\nEvaluation Metrics:")
        for k, v in ml_results["metrics"].items():
            print(f"  • {k.upper()}: {v}")
        return

    # Mode 4: Multi-Agent Pipeline Execution
    print("\n" + "=" * 75)
    print("🚀 AUTOMATED API DOCUMENTATION ASSISTANT - MULTI-AGENT ORCHESTRATION")
    print("   Symbiosis International University • Agentic AI & Automation (CA3 Mini Project)")
    print("=" * 75)

    print(WorkflowVisualizer.to_ascii())

    code_content = ""
    framework = "auto"
    if args.file:
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"Error: File '{args.file}' not found.")
            sys.exit(1)
        with open(file_path, "r", encoding="utf-8") as f:
            code_content = f.read()
        title = args.title or file_path.stem.replace("_", " ").title()
    else:
        sample_map = {
            "fastapi": (PROJECT_ROOT / "samples" / "fastapi_ecommerce.py", "CloudCommerce API", "fastapi"),
            "flask": (PROJECT_ROOT / "samples" / "flask_user_service.py", "User Accounts API", "flask"),
            "express": (PROJECT_ROOT / "samples" / "express_payment_api.js", "Payments Gateway API", "express")
        }
        path, title, framework = sample_map[args.sample]
        with open(path, "r", encoding="utf-8") as f:
            code_content = f.read()

    print(f"[*] Target Codebase: {title} ({framework})")
    print(f"[*] Agent Reasoning Mode: {args.model}")

    supervisor = SupervisorAgent(model_provider=args.model)
    state = supervisor.run_pipeline(
        code_content=code_content,
        api_title=title,
        framework=framework
    )

    print("\n" + "-" * 75)
    print("📋 MULTI-AGENT EXECUTION TRACE LOG (Unit 1 & Unit 2 Handoffs)")
    print("-" * 75)
    for log in state.get("execution_log", []):
        agent = log.get("agent", "Agent")
        action = log.get("action", "action")
        thought = log.get("thought", "")
        time_ms = log.get("execution_time_ms", 0)
        print(f"  [🤖 {agent:<20}] {action:<25} ({time_ms:>6.1f} ms)")
        print(f"    └─ Thought: {thought}")

    print("\n" + "-" * 75)
    print("📊 QUALITY AUDIT & OWASP API SECURITY COMPLIANCE (Unit 2 & Unit 4)")
    print("-" * 75)
    audit = state.get("audit_report", {})
    print(f"  • Schema Validity:        {'PASSED' if audit.get('is_schema_valid') else 'FAILED'}")
    print(f"  • Specification Score:    {audit.get('spec_quality_score', 0)}%")
    print(f"  • OWASP Security Score:   {audit.get('security_score', 0)}%")
    print(f"  • Overall Quality Score:  {audit.get('overall_quality_score', 0)}%")
    print(f"  • Self-Healing Cycles:    {state.get('iteration_count', 1)} iteration(s)")

    findings = audit.get("security_findings", [])
    if findings:
        print(f"\n  [!] Security Vulnerabilities Flagged ({len(findings)}):")
        for f in findings:
            print(f"      - [{f['severity']}] {f['id']}: {f['title']} on {f['endpoint']}")

    print("\n" + "-" * 75)
    print("✨ GENERATED ARTIFACTS SUMMARY")
    print("-" * 75)
    print(f"  1. OpenAPI 3.1.0 Specification: {len(state.get('openapi_spec', {}).get('paths', {}))} paths defined")
    print(f"  2. Markdown Documentation:      {len(state.get('documentation_markdown', ''))} characters")
    print(f"  3. Postman Collection v2.1.0:   {len(state.get('postman_collection', {}).get('item', []))} requests packaged")
    print(f"  4. SQLite Session ID:           {state.get('session_id')}")
    print(f"  5. Total Pipeline Latency:      {state.get('total_execution_time_ms', 0)} ms")

    print("\n" + "=" * 75)
    print("✅ EXECUTION SUCCESSFUL. Run 'python3 main.py --web' to view in interactive Web Studio UI!")
    print("=" * 75 + "\n")


if __name__ == "__main__":
    main()
