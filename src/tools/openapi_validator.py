"""
OpenAPI 3.1.0 Specification Validator & Linter Guardrail Tool.
Syllabus Alignment: Unit 2 (Guardrails for boundaries) & Unit 4 (Evaluation & Validation).
"""

import re
from typing import Any, Dict, List, Tuple


class OpenAPIValidatorTool:
    """Validates and lints OpenAPI 3.1.0 JSON/Dict data against strict structural guardrails."""

    def validate(self, spec: Dict[str, Any]) -> Tuple[bool, float, List[str], List[str]]:
        """
        Validates the OpenAPI specification.
        Returns:
            (is_valid, quality_score, errors, warnings)
        """
        errors: List[str] = []
        warnings: List[str] = []

        if not isinstance(spec, dict):
            return False, 0.0, ["Specification root must be a JSON object/dictionary"], []

        # 1. Version Guardrail
        openapi_ver = spec.get("openapi", "")
        if not openapi_ver or not openapi_ver.startswith("3."):
            errors.append(f"Invalid or missing 'openapi' version: '{openapi_ver}'. Must be OpenAPI 3.x.x")

        # 2. Info Guardrail
        info = spec.get("info")
        if not info or not isinstance(info, dict):
            errors.append("Missing or invalid 'info' object.")
        else:
            if not info.get("title"):
                errors.append("info.title is required.")
            if not info.get("version"):
                errors.append("info.version is required.")
            if not info.get("description"):
                warnings.append("info.description is recommended for high-quality developer documentation.")

        # 3. Paths Guardrail
        paths = spec.get("paths")
        if not paths or not isinstance(paths, dict):
            errors.append("Missing or empty 'paths' object. An API specification must declare at least one path.")
        else:
            valid_methods = {"get", "post", "put", "delete", "patch", "options", "head", "trace"}
            for path_str, path_item in paths.items():
                if not path_str.startswith("/"):
                    errors.append(f"Path '{path_str}' must begin with a forward slash '/'.")

                # Extract declared URL path variables: /users/{user_id}
                url_vars = set(re.findall(r"\{([a-zA-Z0-9_]+)\}", path_str))

                if not isinstance(path_item, dict):
                    errors.append(f"Path item for '{path_str}' must be a dictionary.")
                    continue

                for method, op in path_item.items():
                    if method.lower() not in valid_methods:
                        continue

                    if not isinstance(op, dict):
                        errors.append(f"Operation {method.upper()} {path_str} must be an object.")
                        continue

                    # Summary / description check
                    if not op.get("summary") and not op.get("description"):
                        warnings.append(f"{method.upper()} {path_str} is missing a summary or description.")

                    # Responses check
                    responses = op.get("responses")
                    if not responses or not isinstance(responses, dict):
                        errors.append(f"Operation {method.upper()} {path_str} must declare at least one response.")
                    else:
                        has_success = any(code.startswith("2") for code in responses.keys())
                        if not has_success:
                            warnings.append(f"{method.upper()} {path_str} does not declare a 2xx success response code.")

                    # Path parameter alignment guardrail
                    declared_path_params = set()
                    params = op.get("parameters", [])
                    if isinstance(params, list):
                        for p in params:
                            if isinstance(p, dict) and p.get("in") == "path":
                                declared_path_params.add(p.get("name"))
                                if not p.get("required"):
                                    errors.append(f"Path parameter '{p.get('name')}' in {method.upper()} {path_str} must have required=true.")

                    missing_in_spec = url_vars - declared_path_params
                    if missing_in_spec:
                        errors.append(f"{method.upper()} {path_str} uses URL variables {missing_in_spec} not defined in parameters list.")

        # Compute Quality Score (0 to 100)
        penalty = (len(errors) * 15.0) + (len(warnings) * 4.0)
        score = max(0.0, round(100.0 - penalty, 1))
        is_valid = len(errors) == 0

        return is_valid, score, errors, warnings
