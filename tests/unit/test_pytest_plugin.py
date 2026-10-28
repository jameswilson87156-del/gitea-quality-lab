import json
from types import SimpleNamespace

from qa_lab.pytest_plugin import pytest_runtest_logreport, pytest_sessionfinish


def test_teardown_error_is_not_reported_as_a_pass(tmp_path, monkeypatch):
    report_path = tmp_path / "report.json"
    monkeypatch.setenv("GITEA_REPORT_PATH", str(report_path))
    monkeypatch.setenv("GITEA_RUN_ID", "teardown-error-run")

    class Item:
        nodeid = "tests/test_sample.py::test_artifact_teardown"

        def __init__(self):
            self.rep_setup = SimpleNamespace(outcome="passed", when="setup", duration=0.01)
            self.rep_call = SimpleNamespace(outcome="passed", when="call", duration=0.2)
            self.rep_teardown = SimpleNamespace(
                outcome="failed",
                when="teardown",
                duration=0.03,
                longreprtext="artifact capture failed",
            )

        def get_closest_marker(self, _name):
            return None

    session = SimpleNamespace(
        items=[Item()],
        qa_started_at="2026-10-28T12:00:00Z",
    )

    pytest_sessionfinish(session, exitstatus=1)

    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["summary"] == {"tests": 1, "passed": 0, "failed": 0, "skipped": 0, "errors": 1}
    assert report["cases"][0]["outcome"] == "error"
    assert report["cases"][0]["failure"].startswith("[teardown]")
    assert "artifact capture failed" in report["cases"][0]["failure"]
    assert report["cases"][0]["duration_seconds"] == 0.24


def test_failure_report_redacts_secrets_before_reporters_receive_it(monkeypatch):
    secret = "SYNTHETIC_PASSWORD_12345"
    monkeypatch.setenv("GITEA_ADMIN_PASSWORD", secret)
    report = SimpleNamespace(
        outcome="failed",
        when="call",
        longrepr=f'AssertionError: page.fill("{secret}") timed out',
        sections=[("Captured stdout", f"request body included {secret}")],
    )
    pytest_runtest_logreport(report)

    assert secret not in str(report.longrepr)
    assert secret not in str(report.sections)
    assert "[REDACTED]" in str(report.longrepr)
    assert "[REDACTED]" in str(report.sections)


def test_skip_report_keeps_pytest_tuple_shape_and_redacts_reason(monkeypatch):
    secret = "SYNTHETIC_SKIP_SECRET_9876"
    monkeypatch.setenv("GITEA_ADMIN_PASSWORD", secret)
    report = SimpleNamespace(
        outcome="skipped",
        when="setup",
        longrepr=("test_sample.py", 12, f"Skipped: {secret}"),
        sections=[],
    )

    pytest_runtest_logreport(report)

    assert isinstance(report.longrepr, tuple)
    assert report.longrepr[0:2] == ("test_sample.py", 12)
    assert secret not in str(report.longrepr)
    assert "[REDACTED]" in report.longrepr[2]


def test_setup_skip_is_reported_as_skipped_not_error(tmp_path, monkeypatch):
    report_path = tmp_path / "report.json"
    monkeypatch.setenv("GITEA_REPORT_PATH", str(report_path))
    monkeypatch.setenv("GITEA_RUN_ID", "setup-skip-run")

    class Item:
        nodeid = "tests/test_sample.py::test_marked_skip"
        rep_setup = SimpleNamespace(
            outcome="skipped",
            when="setup",
            duration=0.01,
            longrepr=("tests/test_sample.py", 5, "Skipped: platform condition"),
        )

        def get_closest_marker(self, _name):
            return None

    session = SimpleNamespace(items=[Item()], qa_started_at="2026-10-28T12:00:00Z")
    pytest_sessionfinish(session, exitstatus=0)

    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["summary"] == {"tests": 1, "passed": 0, "failed": 0, "skipped": 1, "errors": 0}
    assert report["cases"][0]["outcome"] == "skipped"
    assert "platform condition" in report["cases"][0]["failure"]
