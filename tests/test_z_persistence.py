import subprocess

import httpx
import pytest

from qa_lab.compose import ROOT, compose_command
from qa_lab.service import wait_for_gitea


@pytest.mark.case(id="DATA-001", category="persistence")
def test_repository_and_issue_survive_gitea_container_restart(
    admin_auth, base_url, admin_client, private_repo
):
    full_name = private_repo["full_name"]
    title = "SQLite persistence after container restart"
    created = admin_client.post(
        f"/repos/{full_name}/issues",
        json={"title": title, "body": "The named volume must preserve this issue."},
    )
    assert created.status_code == 201
    issue_number = created.json()["number"]

    restarted = subprocess.run(
        compose_command("restart", "gitea"),
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert restarted.returncode == 0, "the isolated Gitea service restart failed"
    wait_for_gitea(base_url=base_url, timeout_seconds=150)

    with httpx.Client(base_url=f"{base_url}/api/v1", auth=admin_auth, timeout=15) as client:
        persisted_repo = client.get(f"/repos/{full_name}")
        persisted_issue = client.get(f"/repos/{full_name}/issues/{issue_number}")

    assert persisted_repo.status_code == 200
    assert persisted_repo.json()["full_name"] == full_name
    assert persisted_issue.status_code == 200
    assert persisted_issue.json()["title"] == title
    assert persisted_issue.json()["state"] == "open"
