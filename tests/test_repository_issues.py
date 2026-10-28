import pytest


@pytest.mark.case(id="REPO-001", category="repository")
def test_admin_creates_private_repository_and_reads_its_metadata(admin_client, private_repo):
    response = admin_client.get(f"/repos/{private_repo['full_name']}")

    assert response.status_code == 200
    assert response.json()["private"] is True
    assert response.json()["full_name"] == private_repo["full_name"]


@pytest.mark.case(id="PERM-003", category="authorization")
def test_guest_cannot_read_private_repository(guest_client, private_repo):
    response = guest_client.get(f"/repos/{private_repo['full_name']}")

    assert response.status_code == 404


@pytest.mark.case(id="ISSUE-001", category="issue-lifecycle")
def test_issue_comment_label_close_and_reopen_lifecycle(admin_client, private_repo):
    full_name = private_repo["full_name"]
    issue_response = admin_client.post(
        f"/repos/{full_name}/issues",
        json={"title": "Lifecycle regression scenario", "body": "Created by an isolated test run"},
    )
    assert issue_response.status_code == 201
    issue = issue_response.json()

    comment_response = admin_client.post(
        f"/repos/{full_name}/issues/{issue['number']}/comments",
        json={"body": "Automated comment evidence"},
    )
    assert comment_response.status_code == 201

    label_response = admin_client.post(
        f"/repos/{full_name}/labels",
        json={"name": "qa-triage", "color": "1f6feb", "description": "Created by this test run"},
    )
    assert label_response.status_code == 201
    label = label_response.json()
    assign_response = admin_client.post(
        f"/repos/{full_name}/issues/{issue['number']}/labels",
        json={"labels": [label["id"]]},
    )
    assert assign_response.status_code == 200

    comments = admin_client.get(f"/repos/{full_name}/issues/{issue['number']}/comments")
    assert comments.status_code == 200
    assert any(comment["body"] == "Automated comment evidence" for comment in comments.json())
    assert any(item["name"] == "qa-triage" for item in assign_response.json())

    closed = admin_client.patch(f"/repos/{full_name}/issues/{issue['number']}", json={"state": "closed"})
    assert closed.status_code == 201
    assert closed.json()["state"] == "closed"

    reopened = admin_client.patch(f"/repos/{full_name}/issues/{issue['number']}", json={"state": "open"})
    assert reopened.status_code == 201
    assert reopened.json()["state"] == "open"


@pytest.mark.case(id="ISSUE-002", category="input-validation")
def test_issue_without_required_title_returns_validation_error(admin_client, private_repo):
    response = admin_client.post(
        f"/repos/{private_repo['full_name']}/issues",
        json={"body": "The title field is intentionally missing"},
    )

    assert response.status_code in {400, 422}
    assert response.headers.get("content-type", "").startswith("application/json")


@pytest.mark.case(id="INPUT-001", category="input-validation")
def test_malformed_json_is_rejected_as_a_client_error(admin_client, private_repo):
    response = admin_client.post(
        f"/repos/{private_repo['full_name']}/issues",
        content="{ malformed-json",
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code in {400, 422}
