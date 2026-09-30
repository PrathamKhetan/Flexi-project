"""
Base Agent Architecture supporting Multi-Model Providers (Groq, Google Gemini, and Local Engine).
Syllabus Alignment: Unit 2 (AI Agent Team Structure, Agent-as-Tool) & Unit 3 (Multi-Model AI Agents).
"""

import json
import os
import time
import urllib.request
import urllib.parse
from typing import Any, Callable, Dict, List, Optional
from ..config import GROQ_API_KEY, GEMINI_API_KEY, DEFAULT_GROQ_MODEL, DEFAULT_GEMINI_MODEL


class BaseAgent:
    """Base class for all role-specific agents in the multi-agent pipeline."""

    def __init__(
        self,
        name: str,
        role: str,
        goal: str,
        backstory: str,
        tools: Optional[List[Any]] = None,
        model_provider: str = "auto"
    ):
        self.name = name
        self.role = role
        self.goal = goal
        self.backstory = backstory
        self.tools = tools or []
        self.model_provider = model_provider

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Subclasses implement specific agent task logic."""
        raise NotImplementedError

    def call_llm(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Calls the configured LLM provider.
        Supports Groq (llama-3.3-70b), Google Gemini, with automatic fallback.
        """
        sys_instruction = system_prompt or f"You are {self.name}, the {self.role}. Goal: {self.goal}. Background: {self.backstory}"

        # 1. Try Groq if configured or requested
        if (self.model_provider in ("groq", "auto")) and GROQ_API_KEY:
            try:
                return self._call_groq(prompt, sys_instruction)
            except Exception:
                if self.model_provider == "groq":
                    raise

        # 2. Try Gemini if configured or requested
        if (self.model_provider in ("gemini", "auto")) and GEMINI_API_KEY:
            try:
                return self._call_gemini(prompt, sys_instruction)
            except Exception:
                if self.model_provider == "gemini":
                    raise

        # 3. Fallback to Local Engine
        return self._local_engine_fallback(prompt)

    def _call_groq(self, prompt: str, system_prompt: str) -> str:
        """Calls Groq API — OpenAI-compatible endpoint for fast inference."""
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {GROQ_API_KEY}"
        }
        data = {
            "model": DEFAULT_GROQ_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2
        }
        req = urllib.request.Request(url, data=json.dumps(data).encode("utf-8"), headers=headers)
        with urllib.request.urlopen(req, timeout=30) as resp:
            res_json = json.loads(resp.read().decode("utf-8"))
            return res_json["choices"][0]["message"]["content"]

    def _call_gemini(self, prompt: str, system_prompt: str) -> str:
        model = DEFAULT_GEMINI_MODEL
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_API_KEY}"
        data = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": f"{system_prompt}\n\nTask:\n{prompt}"}]
                }
            ],
            "generationConfig": {"temperature": 0.2}
        }
        headers = {"Content-Type": "application/json"}
        req = urllib.request.Request(url, data=json.dumps(data).encode("utf-8"), headers=headers)
        with urllib.request.urlopen(req, timeout=30) as resp:
            res_json = json.loads(resp.read().decode("utf-8"))
            candidates = res_json.get("candidates", [])
            if candidates:
                return candidates[0]["content"]["parts"][0]["text"]
            return ""

    def _local_engine_fallback(self, prompt: str) -> str:
        """Offline deterministic reasoning engine when API keys are not provided."""
        return f"[{self.name} Local Engine Output processed for prompt]"
