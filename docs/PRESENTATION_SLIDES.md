# Automated API Documentation Assistant
## Presentation Slides Deck (CA3 Mini Project Defense)

**Course**: Agentic AI & Automation (Level 3, 3 Credits)  
**Institution**: Symbiosis Institute of Technology, Symbiosis International (Deemed University)  
**Department**: Computer Science & Engineering  

---

### Slide 1: Title Slide
- **Title**: Automated API Documentation Assistant
- **Subtitle**: Multi-Agent Orchestration via LangGraph, SQLite Memory, OWASP Guardrails & Model Context Protocol (MCP)
- **Course**: Agentic AI & Automation (CA3 Mini Project - 30 Marks &rarr; 20 Marks)
- **Institution**: Symbiosis International (Deemed University)
- **Presenter**: Student Candidate
- **Academic Year**: 2026–2027

---

### Slide 2: Problem Statement & Motivation
- **Documentation Drift**: Backend APIs evolve continuously; manual API docs quickly become outdated, broken, or inaccurate.
- **Developer Overhead**: Writing OpenAPI specifications and multi-language SDK snippets takes valuable engineering hours.
- **Security Gaps**: Standard tools fail to detect critical OWASP API vulnerabilities (e.g., BOLA, broken auth, lack of pagination).
- **Goal**: An autonomous, self-healing multi-agent AI assistant that extracts endpoints, validates schemas, audits security, and publishes documentation automatically.

---

### Slide 3: Syllabus & Course Outcome (CO) Mapping
- **Unit 1 (CO1)**: Single Agent with persistent SQLite session storage, state management, and FunctionTool search.
- **Unit 2 (CO2)**: Multi-Agent Team with Supervisor Manager function, specialist agents, handoffs, and guardrails.
- **Unit 3 (CO3)**: LangGraph StateGraph orchestration, multi-model compatibility (GPT-4o & Gemini), and interactive Web UI.
- **Unit 4 (CO4)**: Model Context Protocol (MCP) server/client architecture and Classical ML regression metrics (\(R^2\), MAE, MSE).
- **Unit 5 (CO5)**: n8n automated CI/CD pipeline with structured JSON parsing, Google Sheets logging, and email alerts.

---

### Slide 4: Multi-Agent Team Structure (Unit 2)
- **SupervisorAgent (Manager)**: Triages user requests, initializes SQLite sessions, coordinates handoffs, and manages quality sign-offs.
- **PlannerAgent**: Analyzes codebase, detects framework (FastAPI/Flask/Express), and creates execution roadmaps.
- **ParserAgent**: Deconstructs source code into Abstract Syntax Trees (AST) to reliably extract endpoints and models.
- **SpecGeneratorAgent**: Synthesizes OpenAPI 3.1.0 specifications and resolves JSON schemas.
- **QualityAuditorAgent**: Evaluates structural guardrails and audits OWASP API Security Top 10 vulnerabilities.
- **DocWriterAgent**: Generates Markdown developer guides, cURL/Python/JS code samples, and Postman collections.

---

### Slide 5: LangGraph State Machine & Self-Healing Loop (Unit 3)
- **State Definition**: Typed state dictionary (`AgentWorkflowState`) passing across nodes.
- **Linear Handoffs**: `Planner` &rarr; `Parser` &rarr; `SpecGenerator` &rarr; `QualityAuditor`.
- **Cyclic Reflection (Self-Healing)**:
  - If `QualityAuditor` detects schema defects (e.g. missing path variables) and iteration < 3:
    - Automatically routes back to `SpecGenerator` with targeted repair feedback!
  - Once validated:
    - Routes forward to `DocWriter` &rarr; `Supervisor` &rarr; `END`.

---

### Slide 6: Persistent SQLite Memory (Unit 1)
- **Relational Tables**:
  1. `sessions`: Tracks session metadata, title, and framework configurations.
  2. `turns`: Maintains multi-turn conversation queries and state snapshots.
  3. `agent_traces`: Records granular execution telemetry (agent, action, thought, execution time in ms).
  4. `doc_artifacts`: Stores versioned snapshots of OpenAPI specs, Markdown docs, and Postman collections.
- **ACID Reliability**: Retains full state and history across server restarts.

---

### Slide 7: Guardrails & OWASP API Security Audit
- **Structural Guardrails**:
  - Enforces OpenAPI 3.1.0 root metadata and operation structures.
  - Asserts that all `{var}` path tokens match explicit `in: "path"` parameters.
- **OWASP API Security Top 10 Checks**:
  - **API1: BOLA**: Flags unauthenticated access on resource identifier paths.
  - **API2: Broken Auth**: Rejects unauthenticated mutating endpoints (POST, PUT, DELETE).
  - **API4: Resource Consumption**: Flags unpaginated list collections.
  - **API3: Sensitive Data**: Flags credentials or secrets passed in query parameters.

---

### Slide 8: Model Context Protocol (MCP) Architecture (Unit 4)
- **Open Protocol Standard**: Implements Anthropic's Model Context Protocol (JSON-RPC 2.0).
- **MCP Manifest (`mcp_manifest.json`)**: Formally declares tool capabilities, input schemas, and metadata.
- **MCP Server (`mcp_server.py`)**: Exposes `tools/list` and `tools/call` over HTTP.
- **Python MCP Client (`mcp_client.py`)**: Enables external AI agents to dynamically discover available tools and execute actions remotely.

---

### Slide 9: Classical ML Regression & Evaluation Metrics (Unit 4)
- **Predictive Modeling**: Trained an Ordinary Least Squares (OLS) Linear Regression model predicting documentation latency from API parameter complexity:
  $$\text{Latency(ms)} = 12.09 \times (\text{Params}) + 16.61$$
- **Model Evaluation Metrics**:
  - **\(R^2\) Score**: **0.9996** (near-perfect fit)
  - **MAE (Mean Absolute Error)**: **2.2747 ms**
  - **MSE (Mean Squared Error)**: **6.4461 ms\(^2\)**
  - **RMSE**: **2.5389 ms**

---

### Slide 10: n8n Automation & CI/CD Pipeline (Unit 5)
- **Importable Workflow (`n8n_workflow.json`)**:
  1. **Webhook Trigger**: Catches GitHub repository push events.
  2. **HTTP Node**: Invokes Automated API Documentation Assistant MCP service.
  3. **Structured Output Parser**: Extracts structured JSON specification attributes.
  4. **Google Sheets Node**: Appends audit rows and quality metrics.
  5. **Gmail / Slack Node**: Dispatches release alerts to engineering leads.

---

### Slide 11: Experimental Results & Benchmarks
- **FastAPI E-Commerce API**: 6 endpoints, 100% schema score, 85% security score, 9.25 ms latency.
- **Flask Microservice**: 4 endpoints, 100% schema score, 59% security score, 7.12 ms latency.
- **Express.js API**: 4 endpoints, 100% schema score, 92% security score, 5.71 ms latency.
- **Test Suite**: 11 automated unit/integration tests running with 100% pass rate in 0.027 seconds.

---

### Slide 12: Conclusion & Viva Takeaways
- **Key Achievements**:
  - Complete, working implementation covering all 5 syllabus units.
  - Multi-agent LangGraph workflow with self-healing cyclic loops.
  - Persistent SQLite session memory and trace logging.
  - Standard MCP server/client and n8n pipeline.
  - Dual Web UI (Interactive Studio + Gradio Connector).
- **GitHub Repository**: Complete codebase, unit tests, academic report (.docx), and presentation slides ready for evaluation.
