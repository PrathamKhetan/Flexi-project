"""
Workflow Visualizer - Renders Mermaid diagrams, ASCII representations, and SVG diagrams for the multi-agent graph.
Syllabus Alignment: Unit 3 (Visualize Agentic workflow, Connect to UI).
"""

from typing import Any, Dict, List


class WorkflowVisualizer:
    """Generates visual graph representations for LangGraph state machine execution."""

    @staticmethod
    def to_mermaid() -> str:
        """Returns Mermaid.js flowchart string representing the agent graph."""
        return """graph TD
    Start([User Source Code]) --> Planner[PlannerAgent: Roadmap & Framework Detection]
    Planner --> Parser[ParserAgent: AST & Regex Extraction]
    Parser --> SpecGen[SpecGeneratorAgent: OpenAPI 3.1 Synthesis]
    SpecGen --> Auditor[QualityAuditorAgent: Guardrails & OWASP Security]
    
    Auditor -->|Defects Detected & Iteration < 3| SpecGen
    Auditor -->|Quality Passed & Guardrails Met| Writer[DocWriterAgent: Markdown & Postman]
    Writer --> Supervisor[Supervisor: Memory Persistence & Signoff]
    Supervisor --> Finish([Ready API Documentation])

    style Start fill:#4A90E2,stroke:#2C3E50,stroke-width:2px,color:#fff
    style Planner fill:#6C5CE7,stroke:#2C3E50,stroke-width:1px,color:#fff
    style Parser fill:#00B894,stroke:#2C3E50,stroke-width:1px,color:#fff
    style SpecGen fill:#FDCB6E,stroke:#2C3E50,stroke-width:1px,color:#333
    style Auditor fill:#FF7675,stroke:#2C3E50,stroke-width:1px,color:#fff
    style Writer fill:#0984E3,stroke:#2C3E50,stroke-width:1px,color:#fff
    style Supervisor fill:#A29BFE,stroke:#2C3E50,stroke-width:1px,color:#fff
    style Finish fill:#00CEC9,stroke:#2C3E50,stroke-width:2px,color:#fff
"""

    @staticmethod
    def to_ascii() -> str:
        """Returns clean ASCII workflow diagram for terminal execution."""
        return """
+-----------------------------------------------------------------------------+
|                      AGENTIC WORKFLOW GRAPH (LangGraph)                     |
+-----------------------------------------------------------------------------+
   [ User Codebase ]
          |
          v
   +--------------+
   | PlannerAgent |   --> Framework detection & execution roadmap
   +--------------+
          |
          v
   +--------------+
   | ParserAgent  |   --> AST endpoint extraction & typing analysis
   +--------------+
          |
          v
   +-------------------+ <--------------------------------------------+
   | SpecGeneratorAgent|                                              |
   +-------------------+                                              | (Self-Healing Loop)
          |                                                           |
          v                                                           |
   +--------------------+                                             |
   | QualityAuditorAgent| -- [If Schema Defects / Score < 85%] -------+
   +--------------------+
          | [If Passed]
          v
   +---------------+
   | DocWriterAgent|  --> Markdown guide, cURL/SDK snippets, Postman v2.1
   +---------------+
          |
          v
   +-----------------+
   | SupervisorAgent | --> SQLite persistence, versioning & memory sign-off
   +-----------------+
          |
          v
   [ Documentation Artifacts Complete ]
+-----------------------------------------------------------------------------+
"""

    @staticmethod
    def to_svg() -> str:
        """Returns clean inline SVG markup for web UI rendering."""
        return """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 950 180" width="100%" height="180">
  <defs>
    <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#6366f1;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#8b5cf6;stop-opacity:1" />
    </linearGradient>
    <marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 8 5 L 0 9 z" fill="#94a3b8" />
    </marker>
  </defs>
  <!-- Node 1: Planner -->
  <rect x="20" y="55" width="140" height="65" rx="10" fill="#1e1b4b" stroke="#6366f1" stroke-width="2"/>
  <text x="90" y="83" fill="#ffffff" font-family="sans-serif" font-size="13" font-weight="bold" text-anchor="middle">1. Planner Agent</text>
  <text x="90" y="103" fill="#a5b4fc" font-family="sans-serif" font-size="10" text-anchor="middle">Scope &amp; Roadmaps</text>
  <line x1="160" y1="87" x2="200" y2="87" stroke="#94a3b8" stroke-width="2" marker-end="url(#arrow)"/>

  <!-- Node 2: Parser -->
  <rect x="200" y="55" width="140" height="65" rx="10" fill="#064e3b" stroke="#10b981" stroke-width="2"/>
  <text x="270" y="83" fill="#ffffff" font-family="sans-serif" font-size="13" font-weight="bold" text-anchor="middle">2. Parser Agent</text>
  <text x="270" y="103" fill="#6ee7b7" font-family="sans-serif" font-size="10" text-anchor="middle">AST Route Extraction</text>
  <line x1="340" y1="87" x2="380" y2="87" stroke="#94a3b8" stroke-width="2" marker-end="url(#arrow)"/>

  <!-- Node 3: Spec Generator -->
  <rect x="380" y="55" width="150" height="65" rx="10" fill="#78350f" stroke="#f59e0b" stroke-width="2"/>
  <text x="455" y="83" fill="#ffffff" font-family="sans-serif" font-size="13" font-weight="bold" text-anchor="middle">3. Spec Generator</text>
  <text x="455" y="103" fill="#fde68a" font-family="sans-serif" font-size="10" text-anchor="middle">OpenAPI 3.1.0 JSON</text>
  <line x1="530" y1="87" x2="570" y2="87" stroke="#94a3b8" stroke-width="2" marker-end="url(#arrow)"/>

  <!-- Node 4: Quality Auditor -->
  <rect x="570" y="55" width="150" height="65" rx="10" fill="#7f1d1d" stroke="#ef4444" stroke-width="2"/>
  <text x="645" y="83" fill="#ffffff" font-family="sans-serif" font-size="13" font-weight="bold" text-anchor="middle">4. Quality Auditor</text>
  <text x="645" y="103" fill="#fca5a5" font-family="sans-serif" font-size="10" text-anchor="middle">Guardrails &amp; OWASP</text>
  <line x1="720" y1="87" x2="760" y2="87" stroke="#94a3b8" stroke-width="2" marker-end="url(#arrow)"/>

  <!-- Self-Healing Reflection Arc -->
  <path d="M 645 55 C 645 15, 455 15, 455 55" fill="none" stroke="#f43f5e" stroke-width="2" stroke-dasharray="4" marker-end="url(#arrow)"/>
  <text x="550" y="22" fill="#f43f5e" font-family="sans-serif" font-size="10" font-weight="bold" text-anchor="middle">Self-Healing Loop (if defects)</text>

  <!-- Node 5: Doc Writer -->
  <rect x="760" y="55" width="165" height="65" rx="10" fill="#0c4a6e" stroke="#0284c7" stroke-width="2"/>
  <text x="842" y="83" fill="#ffffff" font-family="sans-serif" font-size="13" font-weight="bold" text-anchor="middle">5. Doc Writer</text>
  <text x="842" y="103" fill="#bae6fd" font-family="sans-serif" font-size="10" text-anchor="middle">Markdown, SDKs &amp; Postman</text>
</svg>"""
