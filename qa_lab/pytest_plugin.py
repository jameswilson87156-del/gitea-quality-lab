from datetime import datetime, timezone
import json
import os
from pathlib import Path

import pytest

from qa_lab.reporting import build_report, redact_text


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def pytest_sessionstart(session):
    session.qa_started_at = _timestamp()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"rep_{report.when}", report)


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_logreport(report):
    """Remove local credentials before terminal, JUnit, and HTML plugins see a report."""
    secrets = _configured_secrets()
    longrepr = getattr(report, "longrepr", None)
    if isinstance(longrepr, tuple):
        report.longrepr = tuple(
            redact_text(value, secrets) if isinstance(value, str) else value
            for value in longrepr
        )
    elif longrepr is not None:
        report.longrepr = redact_text(str(longrepr), secrets)
    report.sections = [
        (redact_text(str(title), secrets), redact_text(str(content), secrets))
        for title, content in getattr(report, "sections", [])
    ]


def _configured_secrets() -> list[str]:
    return [
        value
        for name, value in os.environ.items()
        if name.startswith("GITEA_")
        and any(part in name for part in ("PASSWORD", "TOKEN", "SECRET"))
        and value
    ]


def pytest_sessionfinish(session, exitstatus):
    report_path = os.environ.get("GITEA_REPORT_PATH")
    if not report_path:
        return

    cases = []
    secrets = _configured_secrets()
    for item in session.items:
        setup = getattr(item, "rep_setup", None)
        call = getattr(item, "rep_call", None)
        teardown = getattr(item, "rep_teardown", None)
        failed_reports = [
            report for report in (setup, call, teardown)
            if report is not None and report.outcome == "failed"
        ]
        if call is not None and call.outcome == "failed":
            outcome = "failed"
        elif failed_reports:
            outcome = "error"
        elif call is None and setup is not None and setup.outcome == "skipped":
            outcome = "skipped"
        else:
            outcome = call.outcome if call is not None else "error"
        marker = item.get_closest_marker("case")
        case_id = marker.kwargs.get("id") if marker else None
        category = marker.kwargs.get("category") if marker else None
        failure = None
        if failed_reports:
            failure = "\n".join(
                f"[{report.when}] {getattr(report, 'longreprtext', getattr(report, 'longrepr', 'test phase failed'))}"
                for report in failed_reports
            )
            failure = redact_text(failure, secrets)
        elif outcome == "skipped":
            skip_report = call if call is not None else setup
            skip_detail = getattr(skip_report, "longreprtext", getattr(skip_report, "longrepr", "skipped"))
            failure = redact_text(str(skip_detail), secrets)
        phases = [report for report in (setup, call, teardown) if report is not None]
        cases.append(
            {
                "id": case_id or item.nodeid,
                "category": category or "unclassified",
                "node_id": item.nodeid,
                "outcome": outcome,
                "duration_seconds": round(sum(float(report.duration) for report in phases), 4),
                "failure": failure,
            }
        )

    report = build_report(
        run_id=os.environ.get("GITEA_RUN_ID", "unassigned"),
        target={
            "name": "Gitea",
            "version": os.environ.get("GITEA_TARGET_VERSION", "unknown"),
            "base_url": "http://127.0.0.1:13000",
            "mode": "local-docker-compose",
        },
        started_at=getattr(session, "qa_started_at", _timestamp()),
        finished_at=_timestamp(),
        cases=cases,
    )
    path = Path(report_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
