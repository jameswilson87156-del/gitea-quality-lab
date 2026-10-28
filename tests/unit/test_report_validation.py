import json
import xml.etree.ElementTree as ET

import pytest

from qa_lab.report_validation import ReportValidationError, validate_report_pair


RUN_ID = "20261028T140000Z-ab12cd34"


def write_artifacts(tmp_path, *, duplicate_id=False, summary_overrides=None, junit_outcomes=None):
    cases = [
        {"id": "AUTH-001", "outcome": "passed"},
        {"id": "AUTH-002", "outcome": "failed"},
        {"id": "AUTH-003", "outcome": "skipped"},
        {"id": "AUTH-004", "outcome": "error"},
    ]
    if duplicate_id:
        cases[1]["id"] = cases[0]["id"]
    summary = {"tests": 4, "passed": 1, "failed": 1, "skipped": 1, "errors": 1}
    summary.update(summary_overrides or {})
    json_path = tmp_path / "report.json"
    json_path.write_text(
        json.dumps({"run_id": RUN_ID, "summary": summary, "cases": cases}),
        encoding="utf-8",
    )

    outcomes = junit_outcomes or ["passed", "failed", "skipped", "error"]
    suites = ET.Element("testsuites")
    suite = ET.SubElement(suites, "testsuite")
    for index, outcome in enumerate(outcomes):
        testcase = ET.SubElement(suite, "testcase", name=f"case-{index}")
        if outcome in {"failed", "skipped", "error"}:
            junit_tag = {"failed": "failure", "skipped": "skipped", "error": "error"}[outcome]
            ET.SubElement(testcase, junit_tag)
    junit_path = tmp_path / "junit.xml"
    ET.ElementTree(suites).write(junit_path, encoding="utf-8", xml_declaration=True)
    return json_path, junit_path


def test_matching_reports_return_verified_run_totals(tmp_path):
    json_path, junit_path = write_artifacts(tmp_path)

    result = validate_report_pair(json_path, junit_path, RUN_ID)

    assert result == {
        "run_id": RUN_ID,
        "tests": 4,
        "passed": 1,
        "failed": 1,
        "skipped": 1,
        "errors": 1,
    }


def test_run_id_mismatch_is_rejected(tmp_path):
    json_path, junit_path = write_artifacts(tmp_path)

    with pytest.raises(ReportValidationError, match="run ID"):
        validate_report_pair(json_path, junit_path, "another-run")


def test_duplicate_case_ids_are_rejected(tmp_path):
    json_path, junit_path = write_artifacts(tmp_path, duplicate_id=True)

    with pytest.raises(ReportValidationError, match="Duplicate JSON case ID"):
        validate_report_pair(json_path, junit_path, RUN_ID)


def test_json_summary_must_match_case_outcomes(tmp_path):
    json_path, junit_path = write_artifacts(tmp_path, summary_overrides={"passed": 2})

    with pytest.raises(ReportValidationError, match="JSON summary counts"):
        validate_report_pair(json_path, junit_path, RUN_ID)


def test_junit_totals_must_match_json_cases(tmp_path):
    json_path, junit_path = write_artifacts(tmp_path, junit_outcomes=["passed"] * 4)

    with pytest.raises(ReportValidationError, match="JSON and JUnit totals differ"):
        validate_report_pair(json_path, junit_path, RUN_ID)
