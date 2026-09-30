"""
Evaluation Metrics for API Documentation and Classical ML Predictive Analytics.
Syllabus Alignment: Unit 4 (Evaluation metrics like R², MAE, MSE, EDA, Missing values, Regression Models).
"""

import math
from typing import Any, Dict, List, Tuple


class APIDocEvaluator:
    """Evaluates the quality, consistency, and completeness of generated API documentation."""

    @staticmethod
    def evaluate(endpoints: List[Dict[str, Any]], spec: Dict[str, Any], audit_report: Dict[str, Any]) -> Dict[str, Any]:
        total_endpoints = len(endpoints)
        if total_endpoints == 0:
            return {"completeness_score": 0.0, "status": "NO_ENDPOINTS"}

        # 1. Endpoint Coverage
        documented_paths = spec.get("paths", {})
        documented_ops_count = sum(len(methods) for methods in documented_paths.values())
        endpoint_coverage = min(1.0, documented_ops_count / total_endpoints if total_endpoints else 0)

        # 2. Parameter Documentation Ratio
        total_params = 0
        documented_params = 0
        for ep in endpoints:
            for p in ep.get("parameters", []):
                total_params += 1
                if p.get("description"):
                    documented_params += 1
        param_coverage = documented_params / total_params if total_params > 0 else 1.0

        # 3. Response Schema Coverage
        total_responses = 0
        documented_responses = 0
        for ep in endpoints:
            for code, r in ep.get("responses", {}).items():
                total_responses += 1
                if r.get("description"):
                    documented_responses += 1
        response_coverage = documented_responses / total_responses if total_responses > 0 else 1.0

        # Overall Completeness Score (0 - 100)
        completeness = round(((endpoint_coverage * 0.4) + (param_coverage * 0.3) + (response_coverage * 0.3)) * 100, 1)

        return {
            "endpoint_count": total_endpoints,
            "documented_operations": documented_ops_count,
            "endpoint_coverage_pct": round(endpoint_coverage * 100, 1),
            "param_coverage_pct": round(param_coverage * 100, 1),
            "response_coverage_pct": round(response_coverage * 100, 1),
            "doc_completeness_score": completeness,
            "security_score": audit_report.get("security_score", 100.0),
            "overall_grade": "A+" if completeness >= 90 else ("A" if completeness >= 80 else "B")
        }


class PredictiveModelEvaluator:
    """
    Classical ML Evaluation & Modeling for API Response Time & Workload Prediction.
    Implements exploratory data analysis, imputation, linear regression, and metrics (R², MAE, MSE).
    Direct syllabus alignment: Unit 4.
    """

    @staticmethod
    def calculate_metrics(y_true: List[float], y_pred: List[float]) -> Dict[str, float]:
        """Calculates standard regression metrics: MAE, MSE, RMSE, R²."""
        n = len(y_true)
        if n == 0:
            return {"r2": 0.0, "mae": 0.0, "mse": 0.0, "rmse": 0.0}

        mae = sum(abs(t - p) for t, p in zip(y_true, y_pred)) / n
        mse = sum((t - p) ** 2 for t, p in zip(y_true, y_pred)) / n
        rmse = math.sqrt(mse)

        y_mean = sum(y_true) / n
        ss_tot = sum((t - y_mean) ** 2 for t in y_true)
        ss_res = sum((t - p) ** 2 for t, p in zip(y_true, y_pred))

        r2 = 1.0 - (ss_res / ss_tot) if ss_tot != 0 else 1.0

        return {
            "r2": round(r2, 4),
            "mae": round(mae, 4),
            "mse": round(mse, 4),
            "rmse": round(rmse, 4)
        }

    @staticmethod
    def train_linear_regression(X: List[float], y: List[float]) -> Tuple[float, float, Dict[str, float]]:
        """
        Trains an Ordinary Least Squares (OLS) Linear Regression model: y = slope * x + intercept.
        Returns: (slope, intercept, metrics)
        """
        n = len(X)
        if n <= 1:
            return 0.0, 0.0, {}

        # Impute missing values with mean
        x_clean = [sum(X) / n if val is None else val for val in X]
        y_clean = [sum(y) / n if val is None else val for val in y]

        mean_x = sum(x_clean) / n
        mean_y = sum(y_clean) / n

        numerator = sum((x - mean_x) * (y - mean_y) for x, y in zip(x_clean, y_clean))
        denominator = sum((x - mean_x) ** 2 for x in x_clean)

        slope = numerator / denominator if denominator != 0 else 0.0
        intercept = mean_y - (slope * mean_x)

        y_pred = [(slope * x) + intercept for x in x_clean]
        metrics = PredictiveModelEvaluator.calculate_metrics(y_clean, y_pred)

        return slope, intercept, metrics

    @staticmethod
    def run_sample_api_prediction() -> Dict[str, Any]:
        """Demonstrates dataset inspection, EDA, regression training, and metric comparison."""
        # Feature: Code complexity / parameter count
        # Target: Documentation generation latency (seconds) or API request latency (ms)
        param_counts = [2, 3, 5, 8, 12, 15, 20, 25, 30, 35]
        actual_latencies_ms = [45.2, 52.1, 78.4, 110.5, 160.2, 195.0, 260.8, 315.4, 380.0, 442.1]

        slope, intercept, metrics = PredictiveModelEvaluator.train_linear_regression(param_counts, actual_latencies_ms)

        return {
            "dataset": "API Parameter Complexity vs Documentation Synthesis Latency",
            "samples_count": len(param_counts),
            "model_type": "Linear Regression (OLS)",
            "slope": round(slope, 3),
            "intercept": round(intercept, 3),
            "formula": f"Latency(ms) = {round(slope, 2)} * (Params) + {round(intercept, 2)}",
            "metrics": metrics
        }
