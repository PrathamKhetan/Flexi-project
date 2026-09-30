"""
Quality & Security Auditor Agent - Enforces guardrails, validates OpenAPI schemas, and audits OWASP API Security.
Syllabus Alignment: Unit 2 (Implement guardrails for boundaries) & Unit 4 (Evaluation metrics & validation).
"""

import time
from typing import Any, Dict
from .base_agent import BaseAgent
from ..tools.openapi_validator import OpenAPIValidatorTool
from ..tools.security_auditor import SecurityAuditorTool
from ..config import MAX_SELF_HEALING_ITERATIONS, MIN_ACCEPTABLE_QUALITY_SCORE


class QualityAuditorAgent(BaseAgent):
    """Specialist agent responsible for automated guardrail compliance and security auditing."""

    def __init__(self, model_provider: str = "auto"):
        super().__init__(
            name="QualityAuditorAgent",
            role="API Security & Compliance Auditor",
            goal="Enforce strict structural schema guardrails and OWASP API Security Top 10 compliance on generated API documentation.",
            backstory="A cyber-security auditor and QA lead focused on zero-defect API specifications and vulnerability prevention.",
            tools=[OpenAPIValidatorTool(), SecurityAuditorTool()],
            model_provider=model_provider
        )
        self.validator_tool = OpenAPIValidatorTool()
        self.security_tool = SecurityAuditorTool()

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        start_time = time.time()
        spec = state.get("openapi_spec", {})
        endpoints = state.get("endpoints", [])
        iteration = state.get("iteration_count", 0)

        # 1. Structural Schema Validation Guardrail
        is_valid, spec_score, errors, warnings = self.validator_tool.validate(spec)

        # 2. OWASP API Security Audit
        sec_report = self.security_tool.audit(endpoints, spec)
        sec_score = sec_report.get("security_score", 100.0)

        # Overall Quality Score
        combined_score = round((spec_score * 0.6) + (sec_score * 0.4), 1)

        # Decision Logic: Check if revision is required
        needs_revision = False
        reasons_for_revision = []

        if not is_valid and iteration < MAX_SELF_HEALING_ITERATIONS:
            needs_revision = True
            reasons_for_revision.extend(errors)

        if combined_score < MIN_ACCEPTABLE_QUALITY_SCORE and iteration < MAX_SELF_HEALING_ITERATIONS and errors:
            needs_revision = True
            reasons_for_revision.extend(errors)

        execution_time_ms = round((time.time() - start_time) * 1000, 2)

        audit_summary = {
            "is_schema_valid": is_valid,
            "spec_quality_score": spec_score,
            "security_score": sec_score,
            "overall_quality_score": combined_score,
            "errors": errors,
            "warnings": warnings,
            "security_findings_count": sec_report.get("findings_count", 0),
            "security_findings": sec_report.get("findings", []),
            "needs_revision": needs_revision,
            "iteration": iteration
        }

        state["audit_report"] = audit_summary
        state["audit_feedback"] = reasons_for_revision
        state["needs_revision"] = needs_revision
        state["iteration_count"] = iteration + 1
        state["current_step"] = "audit_completed"

        state["execution_log"].append({
            "agent": self.name,
            "action": "audit_and_validate",
            "thought": f"Evaluated specification. Schema valid: {is_valid}, Spec Score: {spec_score}%, Security Score: {sec_score}%, Overall: {combined_score}%. Needs revision: {needs_revision}.",
            "needs_revision": needs_revision,
            "errors_detected": len(errors),
            "warnings_detected": len(warnings),
            "execution_time_ms": execution_time_ms
        })

        return state
