"""
Unit tests for OpenAPI structural validation and OWASP API security guardrails.
Syllabus Alignment: Unit 2 (Implement guardrails for boundaries) & Unit 4 (Evaluation).
"""

import unittest
from src.tools.openapi_validator import OpenAPIValidatorTool
from src.tools.security_auditor import SecurityAuditorTool


class TestGuardrails(unittest.TestCase):

    def setUp(self):
        self.validator = OpenAPIValidatorTool()
        self.auditor = SecurityAuditorTool()

    def test_openapi_validator_success(self):
        valid_spec = {
            "openapi": "3.1.0",
            "info": {"title": "Test API", "version": "1.0.0", "description": "Docs"},
            "paths": {
                "/items": {
                    "get": {
                        "summary": "List items",
                        "responses": {"200": {"description": "OK"}}
                    }
                }
            }
        }
        is_valid, score, errors, warnings = self.validator.validate(valid_spec)
        self.assertTrue(is_valid)
        self.assertGreaterEqual(score, 85.0)
        self.assertEqual(len(errors), 0)

    def test_openapi_validator_catches_missing_path_param(self):
        bad_spec = {
            "openapi": "3.1.0",
            "info": {"title": "Bad API", "version": "1.0.0"},
            "paths": {
                "/items/{item_id}": {
                    "get": {
                        "summary": "Get item",
                        "parameters": [],  # Missing item_id parameter definition!
                        "responses": {"200": {"description": "OK"}}
                    }
                }
            }
        }
        is_valid, score, errors, warnings = self.validator.validate(bad_spec)
        self.assertFalse(is_valid)
        self.assertTrue(any("uses URL variables" in e for e in errors))

    def test_security_auditor_flags_bola_and_broken_auth(self):
        vulnerable_endpoints = [
            {
                "path": "/users/{user_id}",
                "method": "GET",
                "auth_required": False,  # BOLA risk!
                "parameters": [{"name": "user_id", "in": "path"}]
            },
            {
                "path": "/users/records",
                "method": "DELETE",
                "auth_required": False,  # Broken auth risk on write!
                "parameters": []
            }
        ]
        report = self.auditor.audit(vulnerable_endpoints)
        self.assertLess(report["security_score"], 80.0)
        self.assertGreaterEqual(report["findings_count"], 2)


if __name__ == "__main__":
    unittest.main()
