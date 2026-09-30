"""
System Configuration for Automated API Documentation Assistant.
Handles paths, environment settings, multi-model LLM configurations (OpenAI / Gemini),
and SQLite database settings.
"""

import os
from pathlib import Path

# Base Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = PROJECT_ROOT / "src"
SAMPLES_DIR = PROJECT_ROOT / "samples"
DOCS_DIR = PROJECT_ROOT / "docs"
WEB_DIR = PROJECT_ROOT / "web"

# Database & Runtime Data Settings (Unit 1: SQLite Persistent Memory)
# In serverless environments (Vercel, AWS Lambda), filesystem is read-only except /tmp
if os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
    DATA_DIR = Path("/tmp/flexi_data")
else:
    DATA_DIR = PROJECT_ROOT / "data"

try:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
except OSError:
    DATA_DIR = Path("/tmp/flexi_data")
    DATA_DIR.mkdir(parents=True, exist_ok=True)

try:
    SAMPLES_DIR.mkdir(parents=True, exist_ok=True)
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
except OSError:
    pass

SQLITE_DB_PATH = DATA_DIR / "agent_memory.db"

# LLM Providers Configuration (Unit 3: Multi-Model AI Agents)
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

DEFAULT_OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o")
DEFAULT_GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-1.5-pro")

# Execution Mode: 'gemini', 'openai', 'auto', or 'local_heuristic'
# In local_heuristic mode, an intelligent AST-grounded engine generates 100% compliant docs
# without needing API tokens or network access.
AGENT_EXECUTION_MODE = os.environ.get("AGENT_MODE", "auto")

# Agent Guardrails & Limits (Unit 2: Guardrails & Handoffs)
MAX_SELF_HEALING_ITERATIONS = 3
MIN_ACCEPTABLE_QUALITY_SCORE = 85.0
OWASP_STRICT_MODE = True

# Server Settings
DEFAULT_PORT = int(os.environ.get("PORT", 7860))
HOST = os.environ.get("HOST", "127.0.0.1")
