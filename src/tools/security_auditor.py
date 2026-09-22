"""
Security Auditor Tool - OWASP API Security Top 10 Evaluation & Guardrails.
Syllabus Alignment: Unit 2 (Guardrails for security/boundaries) & Unit 4 (Auditing metrics).
"""

import re
from typing import Any, Dict, List


class SecurityAuditorTool:
    """Scans API endpoints and specifications for OWASP API Security vulnerabilities and risks."""

    def audit(self, endpoints: List[Dict[str, Any]], spec: Dict[str, Any] = None) -> Dict[str, Any]:
        findings = []
        passed_checks = []

        total_checks = 0

        for ep in endpoints:
            path = ep.get("path", "")
            method = ep.get("method", "GET").upper()
            auth_req = ep.get("auth_required", False)
            params = ep.get("parameters", [])
            param_names = [p.get("name", "").lower() for p in params]

            # Check 1: OWASP API1 - Broken Object Level Authorization (BOLA)
            total_checks += 1
            if re.search(r"\{[a-zA-Z0-9_]*(id|uuid|key|account)[a-zA-Z0-9_]*\}", path, re.I):
                if not auth_req:
                    findings.append({
                        "id": "API1:2023-BOLA",
                        "severity": "HIGH",
                        "endpoint": f"{method} {path}",
                        "title": "Unauthenticated Resource Identifier Access (BOLA)",
                        "description": f"Endpoint '{method} {path}' operates on a specific object identifier without requiring authentication/authorization.",
                        "remediation": "Enforce object-level access control and require Bearer/JWT token verification."
                    })
                else:
                    passed_checks.append(f"API1: Auth enforced on resource {method} {path}")

            # Check 2: OWASP API2 - Broken Authentication on Mutating Endpoints
            total_checks += 1
            if method in ("POST", "PUT", "DELETE", "PATCH") and not auth_req:
                # Exclude login, register, and public token endpoints
                if not re.search(r"login|register|signup|token|public|health", path, re.I):
                    findings.append({
                        "id": "API2:2023-BROKEN-AUTH",
                        "severity": "CRITICAL",
                        "endpoint": f"{method} {path}",
                        "title": "Unauthenticated State Modification",
                        "description": f"Mutating endpoint '{method} {path}' accepts write operations without security authentication requirements.",
                        "remediation": "Add security schemes (e.g. OAuth2, HTTP Bearer) to ensure only authorized callers can alter state."
                    })
                else:
                    passed_checks.append(f"API2: Public endpoint permitted for auth flow {method} {path}")

            # Check 3: OWASP API4 - Unrestricted Resource Consumption (Missing Pagination)
            total_checks += 1
            if method == "GET" and not re.search(r"\{", path):
                # Collection endpoint (e.g., /items, /users), exclude single health probes
                if not re.search(r"health|ping|status|metrics|info|favicon", path, re.I):
                    has_pagination = any(p in param_names for p in ("limit", "offset", "page", "size", "per_page", "cursor"))
                    if not has_pagination:
                        findings.append({
                            "id": "API4:2023-RESOURCE-CONSUMPTION",
                            "severity": "MEDIUM",
                            "endpoint": f"{method} {path}",
                            "title": "Unbounded List Query (Missing Pagination)",
                            "description": f"Collection endpoint '{method} {path}' does not document limit or pagination parameters, risking Denial of Service (DoS).",
                            "remediation": "Add 'limit' and 'offset' or cursor query parameters with standard upper limits (e.g., max 100)."
                        })
                    else:
                        passed_checks.append(f"API4: Pagination controls verified for {method} {path}")
                else:
                    passed_checks.append(f"API4: Single status/probe endpoint {method} {path}")

            # Check 4: Sensitive Data in URL Path / Query (OWASP API3)
            total_checks += 1
            sensitive_keywords = ["password", "token", "secret", "apikey", "api_key", "ssn", "creditcard"]
            found_sensitive = [p for p in param_names if any(s in p for s in sensitive_keywords)]
            if found_sensitive:
                findings.append({
                    "id": "API3:2023-EXPOSURE",
                    "severity": "HIGH",
                    "endpoint": f"{method} {path}",
                    "title": "Sensitive Credential In URL Query/Path",
                    "description": f"Parameter(s) {found_sensitive} appear in URL path or query string, which get logged in web proxies and server logs.",
                    "remediation": "Transmit sensitive credentials strictly in the Authorization header or HTTPS request body."
                })
            else:
                passed_checks.append(f"API3: No sensitive credentials in URL for {method} {path}")

        # Spec-level checks
        if spec:
            servers = spec.get("servers", [])
            for s in servers:
                url = s.get("url", "")
                if url.startswith("http://") and not "localhost" in url:
                    findings.append({
                        "id": "API8:2023-MISCONFIG",
                        "severity": "HIGH",
                        "endpoint": "Server Configuration",
                        "title": "Insecure HTTP Transport Protocol",
                        "description": f"Server URL '{url}' uses unencrypted HTTP. Production APIs must enforce HTTPS.",
                        "remediation": "Update server URL to HTTPS and configure HSTS."
                    })

        # Calculate OWASP Compliance Score (0 to 100)
        critical_count = sum(1 for f in findings if f["severity"] == "CRITICAL")
        high_count = sum(1 for f in findings if f["severity"] == "HIGH")
        medium_count = sum(1 for f in findings if f["severity"] == "MEDIUM")

        deduction = (critical_count * 25.0) + (high_count * 15.0) + (medium_count * 8.0)
        security_score = max(0.0, round(100.0 - deduction, 1))

        return {
            "security_score": security_score,
            "status": "PASSED" if security_score >= 80.0 else "ATTENTION_REQUIRED",
            "findings_count": len(findings),
            "critical_count": critical_count,
            "high_count": high_count,
            "medium_count": medium_count,
            "findings": findings,
            "passed_checks": passed_checks[:10]
        }
