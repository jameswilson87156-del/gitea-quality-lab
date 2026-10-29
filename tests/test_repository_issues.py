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


@pytest.mark.case(id="REPO-002", category="authorization")
def test_regular_user_can_create_own_repository_and_issue(owner_client, owner_auth, run_id):
    repo_name = f"qa-owner-{run_id[-8:].lower()}"
    created_repo = owner_client.post(
        "/user/repos",
        json={"name": repo_name, "private": True, "auto_init": True},
    )
    assert created_repo.status_code == 201
    full_name = created_repo.json()["full_name"]

    created_issue = owner_client.post(
        f"/repos/{full_name}/issues",
        json={"title": "Regular user owns this Issue", "body": "Owner-level creation is allowed."},
    )

    assert created_issue.status_code == 201
    assert created_issue.json()["user"]["login"] == owner_auth[0]


@pytest.mark.case(id="ISSUE-003", category="issue-query")
def test_issue_list_filters_open_and_closed_state(admin_client, private_repo):
    full_name = private_repo["full_name"]
    created = admin_client.post(
        f"/repos/{full_name}/issues",
        json={"title": "Closed issue query regression", "body": "Filter by state."},
    )
    assert created.status_code == 201
    issue_number = created.json()["number"]

    closed = admin_client.patch(
        f"/repos/{full_name}/issues/{issue_number}", json={"state": "closed"}
    )
    assert closed.status_code == 201

    closed_issues = admin_client.get(
        f"/repos/{full_name}/issues", params={"state": "closed", "limit": 50}
    )
    open_issues = admin_client.get(
        f"/repos/{full_name}/issues", params={"state": "open", "limit": 50}
    )

    assert closed_issues.status_code == 200
    assert open_issues.status_code == 200
    assert issue_number in {issue["number"] for issue in closed_issues.json()}
    assert issue_number not in {issue["number"] for issue in open_issues.json()}


@pytest.mark.case(id="ISSUE-004", category="issue-query")
def test_issue_list_paginates_without_duplicates_or_missing_items(admin_client, private_repo):
    full_name = private_repo["full_name"]
    created_numbers = set()
    for index in range(3):
        response = admin_client.post(
            f"/repos/{full_name}/issues",
            json={"title": f"Pagination regression {index}", "body": "Page through results."},
        )
        assert response.status_code == 201
        created_numbers.add(response.json()["number"])

    page_one = admin_client.get(
        f"/repos/{full_name}/issues", params={"state": "all", "limit": 2, "page": 1}
    )
    page_two = admin_client.get(
        f"/repos/{full_name}/issues", params={"state": "all", "limit": 2, "page": 2}
    )

    assert page_one.status_code == page_two.status_code == 200
    first_numbers = [issue["number"] for issue in page_one.json()]
    second_numbers = [issue["number"] for issue in page_two.json()]
    assert len(first_numbers) == 2
    assert len(second_numbers) == 1
    assert set(first_numbers).isdisjoint(second_numbers)
    assert set(first_numbers + second_numbers) == created_numbers
