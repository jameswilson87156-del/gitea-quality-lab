from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from qa_lab.bootstrap import ensure_test_users
from qa_lab.compose import ROOT, compose_command
from qa_lab.reporting import create_run_id
from qa_lab.service import BASE_URL, wait_for_gitea


def main() -> int:
    started = subprocess.run(
        compose_command("up", "-d", "--wait", "--wait-timeout", "150", "gitea"),
        cwd=ROOT,
        check=False,
    )
    if started.returncode != 0:
        print("Gitea startup failed; the test suite was not executed.", file=sys.stderr)
        return started.returncode

    try:
        version = wait_for_gitea()
        credentials = ensure_test_users()
    except RuntimeError as error:
        print(str(error), file=sys.stderr)
        return 1

    run_id = create_run_id()
    run_dir = ROOT / "reports" / "runs" / run_id
    artifacts_dir = run_dir / "artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    json_report = run_dir / "report.json"

    env = os.environ.copy()
    env.update(
        {
            "GITEA_BASE_URL": BASE_URL,
            "GITEA_TARGET_VERSION": version,
            "GITEA_RUN_ID": run_id,
            "GITEA_REPORT_PATH": str(json_report),
            "GITEA_ARTIFACT_DIR": str(artifacts_dir),
            "PLAYWRIGHT_BROWSERS_PATH": "0",
        }
    )
    for key, account in credentials.items():
        env[f"GITEA_{key.upper()}_USERNAME"] = account["username"]
        env[f"GITEA_{key.upper()}_PASSWORD"] = account["password"]

    integration_tests = sorted((ROOT / "tests").glob("test_*.py"))
    if not integration_tests:
        print("No Gitea integration tests were found; refusing to report an empty run.", file=sys.stderr)
        return 2

    command = [
        sys.executable,
        "-m",
        "pytest",
        *(str(path.relative_to(ROOT)) for path in integration_tests),
        "-ra",
        "--tb=short",
        f"--junitxml={run_dir / 'junit.xml'}",
        f"--html={run_dir / 'report.html'}",
        "--self-contained-html",
    ]
    print(f"Running {len(integration_tests)} integration modules against local Gitea {version}.")
    print(f"Run ID: {run_id}")
    result = subprocess.run(command, cwd=ROOT, env=env, check=False)
    if not json_report.exists():
        print("Pytest did not produce the required JSON report.", file=sys.stderr)
        return result.returncode or 2
    print(f"JSON report: {json_report}")
    print(f"HTML report: {run_dir / 'report.html'}")
    print(f"JUnit report: {run_dir / 'junit.xml'}")
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
