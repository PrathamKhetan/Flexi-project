# Syllabus & Course Outcome (CO) Mapping Matrix

**Course**: Agentic AI & Automation (3 Credits, Level 3)  
**Institution**: Symbiosis International (Deemed University), Faculty of Engineering  
**Project Topic**: Automated API Documentation Assistant  
**Evaluation**: CA3 Mini Project (30 Marks scaled to 20 Marks)

---

## 1. Unit-by-Unit Syllabus Alignment

| Syllabus Unit | Key Unit Topics from Course Outline | Implementation in Project | Source Code Reference |
| :--- | :--- | :--- | :--- |
| **Unit 1** | • Introduction to AI Agent<br>• SQLite-based session storage for persistent memory<br>• Manage agent state & multi-turn queries<br>• FunctionTool integration & search capabilities | Persistent SQLite database for multi-turn sessions, conversation turns, step-by-step trace logging, and versioned artifact storage.<br>Extensible tool interfaces wrapped in FunctionTool schemas. | [`src/memory/sqlite_memory.py`](file:///Users/pratham/Desktop/flexi/src/memory/sqlite_memory.py)<br>[`src/tools/web_search_tool.py`](file:///Users/pratham/Desktop/flexi/src/tools/web_search_tool.py) |
| **Unit 2** | • AI Agent Team Structure & Manager Function<br>• Specialist agents (Planner, Writer, Search Agent)<br>• Triage user queries & delegate tasks<br>• Guardrails for boundaries<br>• Handoff mechanisms (Planner &rarr; Writer)<br>• Agent-as-Tool Design | Modular specialist agents orchestrated by a Supervisor Manager function.<br>Deterministic handoffs: `PlannerAgent` &rarr; `ParserAgent` &rarr; `SpecGeneratorAgent` &rarr; `QualityAuditorAgent` &rarr; `DocWriterAgent`.<br>Strict schema and security guardrails. | [`src/agents/supervisor.py`](file:///Users/pratham/Desktop/flexi/src/agents/supervisor.py)<br>[`src/agents/planner_agent.py`](file:///Users/pratham/Desktop/flexi/src/agents/planner_agent.py)<br>[`src/agents/quality_auditor.py`](file:///Users/pratham/Desktop/flexi/src/agents/quality_auditor.py)<br>[`src/agents/doc_writer.py`](file:///Users/pratham/Desktop/flexi/src/agents/doc_writer.py) |
| **Unit 3** | • Multi-Model AI Agents (Gemini & OpenAI GPT-4o)<br>• LangGraph Core Components (StateGraph, nodes, edges)<br>• Agentic workflow in LangGraph<br>• Connect to UI (Gradio)<br>• Visualize Agentic workflow<br>• Define Custom Tool | Unified multi-model LLM abstraction supporting OpenAI (`gpt-4o`) and Google Gemini (`gemini-1.5-pro`) with local AST engine fallback.<br>LangGraph `StateGraph` with cyclical reflection/self-healing loop.<br>Interactive Gradio connector and Web Studio UI with dynamic SVG/Mermaid workflow visualizer. | [`src/workflow/graph.py`](file:///Users/pratham/Desktop/flexi/src/workflow/graph.py)<br>[`src/agents/base_agent.py`](file:///Users/pratham/Desktop/flexi/src/agents/base_agent.py)<br>[`src/workflow/visualizer.py`](file:///Users/pratham/Desktop/flexi/src/workflow/visualizer.py)<br>[`app.py`](file:///Users/pratham/Desktop/flexi/app.py)<br>[`web/server.py`](file:///Users/pratham/Desktop/flexi/web/server.py) |
| **Unit 4** | • CrewAI role-playing paradigm<br>• Custom Tool: Python code analysis<br>• Scikit-Learn Classical ML: Train linear regression & predict metrics<br>• Handle missing values & EDA<br>• Evaluate model performance (R², MAE, MSE)<br>• Components of Model Context Protocol (MCP)<br>• Deploy as MCP server & Python MCP client with manifest discovery | Custom Python AST inspection tools.<br>Predictive regression module with mean imputation and calculation of \(R^2\), MAE, MSE, and RMSE.<br>Standard Model Context Protocol (MCP) JSON-RPC 2.0 server (`mcp_server.py`), tool capability manifest (`mcp_manifest.json`), and client (`mcp_client.py`). | [`src/tools/ast_parser_tool.py`](file:///Users/pratham/Desktop/flexi/src/tools/ast_parser_tool.py)<br>[`src/evaluation/metrics.py`](file:///Users/pratham/Desktop/flexi/src/evaluation/metrics.py)<br>[`src/mcp/mcp_server.py`](file:///Users/pratham/Desktop/flexi/src/mcp/mcp_server.py)<br>[`src/mcp/mcp_client.py`](file:///Users/pratham/Desktop/flexi/src/mcp/mcp_client.py) |
| **Unit 5** | • Build Agentic Workflows using n8n<br>• Structured output parsing (JSON)<br>• Store results systematically<br>• Connect external services (Google Sheets, Gmail, Webhooks, custom APIs) | Complete importable n8n workflow pipeline JSON.<br>Webhook receiver connecting CI/CD Git push events to automated multi-agent doc generation, structured JSON response parsing, Google Sheets logging, and notifications. | [`src/automation/n8n_workflow.json`](file:///Users/pratham/Desktop/flexi/src/automation/n8n_workflow.json)<br>[`src/automation/webhook_handler.py`](file:///Users/pratham/Desktop/flexi/src/automation/webhook_handler.py) |

---

## 2. Course Outcomes (CO) Attainment Matrix

- **CO1: Implement single AI agents using memory, tracing, and tool integration**:  
  Attained via `SQLiteAgentMemory`, recording agent actions, execution durations, thoughts, and input/output payloads in persistent tables, coupled with `WebSearchTool` and `ASTParserTool`.
- **CO2: Develop multi-agent workflows with role-based agents, task delegation, guardrails, and handoffs**:  
  Attained via 5 specialized agents (`Planner`, `Parser`, `SpecGenerator`, `QualityAuditor`, `DocWriter`) supervised by `SupervisorAgent` with OWASP and OpenAPI structural guardrails.
- **CO3: Build agentic applications using LangGraph with multi-model agents, custom tools, and workflow visualization**:  
  Attained via `StateGraph` compilation, conditional self-healing edges, OpenAI/Gemini/Local LLM engines, and interactive visual graph generation.
- **CO4: Implement AI workflows using MCP by integrating predictive analytics, external tools, and MCP-compatible services**:  
  Attained via MCP server and client implementation obeying JSON-RPC 2.0 specifications, alongside classical regression predictive modeling with \(R^2\), MAE, and MSE evaluations.
- **CO5: Create automation workflows in n8n by integrating AI services for task automation and structured data handling**:  
  Attained via `n8n_workflow.json` providing automated webhook triggering, structured OpenAPI JSON extraction, Google Sheets auditing, and email alerts.
