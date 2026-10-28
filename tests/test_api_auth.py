import pytest


@pytest.mark.case(id="AUTH-001", category="authentication")
def test_public_version_endpoint_reports_pinned_gitea_release(base_url):
    import httpx

    response = httpx.get(f"{base_url}/api/v1/version", timeout=10)

    assert response.status_code == 200
    assert response.json()["version"].startswith("28.2.0")


@pytest.mark.case(id="AUTH-002", category="authentication")
def test_authenticated_user_endpoint_returns_admin_identity(admin_client, admin_auth):
    response = admin_client.get("/user")

    assert response.status_code == 200
    assert response.json()["login"] == admin_auth[0]


@pytest.mark.case(id="AUTH-003", category="authentication")
def test_invalid_token_is_rejected(base_url):
    import httpx

    response = httpx.get(
        f"{base_url}/api/v1/user",
        headers={"Authorization": "token invalid-token-for-negative-test"},
        timeout=10,
    )

    assert response.status_code == 401


@pytest.mark.case(id="PERM-001", category="authorization")
def test_regular_user_cannot_access_admin_user_api(owner_client):
    response = owner_client.get("/admin/users")

    assert response.status_code == 403


@pytest.mark.case(id="PERM-002", category="authorization")
def test_admin_can_list_users_and_test_accounts(admin_client, owner_auth, guest_auth):
    response = admin_client.get("/admin/users")

    assert response.status_code == 200
    usernames = {user["login"] for user in response.json()}
    assert owner_auth[0] in usernames
    assert guest_auth[0] in usernames
