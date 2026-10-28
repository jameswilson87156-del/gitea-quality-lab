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


def pytest_sessionfinish(session, exitstatus):
    report_path = os.environ.get("GITEA_REPORT_PATH")
    if not report_path:
        return

    cases = []
    secrets = [
        os.environ.get(name, "")
        for name in (
            "GITEA_ADMIN_PASSWORD",
            "GITEA_OWNER_PASSWORD",
            "GITEA_GUEST_PASSWORD",
            "GITEA_API_TOKEN",
        )
    ]
    for item in session.items:
        result = getattr(item, "rep_call", None)
        if result is None:
            result = getattr(item, "rep_setup", None)
        outcome = result.outcome if result is not None else "error"
        outcome = "error" if outcome == "failed" and getattr(item, "rep_call", None) is None else outcome
        marker = item.get_closest_marker("case")
        case_id = marker.kwargs.get("id") if marker else None
        category = marker.kwargs.get("category") if marker else None
        failure = None
        if result is not None and outcome in {"failed", "error"}:
            failure = redact_text(str(getattr(result, "longreprtext", result.longrepr)), secrets)
        cases.append(
            {
                "id": case_id or item.nodeid,
                "category": category or "unclassified",
                "node_id": item.nodeid,
                "outcome": outcome,
                "duration_seconds": round(float(result.duration), 4) if result is not None else 0.0,
                "failure": failure,
            }
        )

    report = build_report(
        run_id=os.environ.get("GITEA_RUN_ID", "unassigned"),
        target={
            "name": "Gitea",
            "version": os.environ.get("GITEA_TARGET_VERSION", "unknown"),
            "base_url": os.environ.get("GITEA_BASE_URL", "http://127.0.0.1:13000"),
            "mode": "local-docker-compose",
        },
        started_at=getattr(session, "qa_started_at", _timestamp()),
        finished_at=_timestamp(),
        cases=cases,
    )
    path = Path(report_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
