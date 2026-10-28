"""Cross-check run-scoped JSON results against pytest's JUnit XML output."""

from __future__ import annotations

import json
from pathlib import Path
import xml.etree.ElementTree as ET


class ReportValidationError(ValueError):
    """Raised when a test run's JSON and JUnit artifacts are incomplete or disagree."""


def validate_report_pair(
    json_path: Path,
    junit_path: Path,
    expected_run_id: str,
) -> dict[str, int | str]:
    try:
        report = json.loads(json_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ReportValidationError(f"Cannot read JSON run report: {error}") from error
    try:
        junit_root = ET.parse(junit_path).getroot()
    except (OSError, ET.ParseError) as error:
        raise ReportValidationError(f"Cannot read JUnit report: {error}") from error

    if not isinstance(report, dict):
        raise ReportValidationError("JSON run report must be an object.")
    if report.get("run_id") != expected_run_id:
        raise ReportValidationError("JSON run ID does not match the active run.")
    cases = report.get("cases")
    summary = report.get("summary")
    if not isinstance(cases, list) or not cases:
        raise ReportValidationError("JSON report has no measured test cases.")
    if not isinstance(summary, dict):
        raise ReportValidationError("JSON report has no summary object.")

    counts = {"passed": 0, "failed": 0, "skipped": 0, "errors": 0}
    case_ids: set[str] = set()
    for index, case in enumerate(cases):
        if not isinstance(case, dict):
            raise ReportValidationError(f"JSON case at index {index} is not an object.")
        case_id = case.get("id")
        if not isinstance(case_id, str) or not case_id.strip():
            raise ReportValidationError(f"JSON case at index {index} has no stable ID.")
        if case_id in case_ids:
            raise ReportValidationError(f"Duplicate JSON case ID: {case_id}")
        case_ids.add(case_id)
        outcome = case.get("outcome")
        if outcome not in {"passed", "failed", "skipped", "error"}:
            raise ReportValidationError(f"JSON case {case_id} has an unknown outcome.")
        counts["errors" if outcome == "error" else outcome] += 1

    json_totals = {
        "tests": len(cases),
        "passed": counts["passed"],
        "failed": counts["failed"],
        "skipped": counts["skipped"],
        "errors": counts["errors"],
    }
    if any(summary.get(key) != value for key, value in json_totals.items()):
        raise ReportValidationError("JSON summary counts do not match its case outcomes.")

    junit_cases = list(junit_root.iter("testcase"))
    junit_counts = {"tests": len(junit_cases), "passed": 0, "failed": 0, "skipped": 0, "errors": 0}
    for testcase in junit_cases:
        if testcase.find("error") is not None:
            junit_counts["errors"] += 1
        elif testcase.find("failure") is not None:
            junit_counts["failed"] += 1
        elif testcase.find("skipped") is not None:
            junit_counts["skipped"] += 1
        else:
            junit_counts["passed"] += 1
    if not junit_cases:
        raise ReportValidationError("JUnit report has no test cases.")
    if junit_counts != json_totals:
        raise ReportValidationError(
            f"JSON and JUnit totals differ: JSON={json_totals}; JUnit={junit_counts}."
        )

    return {"run_id": expected_run_id, **json_totals}
