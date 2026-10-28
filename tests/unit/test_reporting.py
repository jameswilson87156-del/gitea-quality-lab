from qa_lab.reporting import build_report, create_run_id, redact_text


def test_report_counts_measured_outcomes_and_keeps_case_identity():
    cases = [
        {"id": "AUTH-001", "outcome": "passed", "duration_seconds": 0.12},
        {"id": "AUTH-002", "outcome": "failed", "duration_seconds": 0.3, "failure": "expected 403"},
        {"id": "AUTH-003", "outcome": "skipped", "duration_seconds": 0.0},
        {"id": "AUTH-004", "outcome": "error", "duration_seconds": 0.01},
    ]

    report = build_report(
        run_id="20261028T120000Z-ab12cd34",
        target={"name": "Gitea", "version": "28.2.0", "base_url": "http://127.0.0.1:13000"},
        started_at="2026-10-28T12:00:00Z",
        finished_at="2026-10-28T12:00:01Z",
        cases=cases,
    )

    assert report["execution_state"] == "completed"
    assert report["summary"] == {"tests": 4, "passed": 1, "failed": 1, "skipped": 1, "errors": 1}
    assert report["cases"] == cases
    assert report["target"]["version"] == "28.2.0"


def test_failure_text_redacts_passwords_and_tokens():
    message = redact_text(
        "authorization token: token-secret; test password=password-secret",
        ["token-secret", "password-secret"],
    )

    assert message == "authorization token: [REDACTED]; test password=[REDACTED]"


def test_run_id_is_unique_and_path_safe():
    first = create_run_id()
    second = create_run_id()

    assert first != second
    assert all(character.isalnum() or character in "-_" for character in first)
