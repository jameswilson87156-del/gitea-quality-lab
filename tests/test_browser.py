import re

import pytest
from playwright.sync_api import expect


@pytest.mark.case(id="UI-001", category="browser-workflow")
def test_admin_signs_in_and_opens_an_issue_from_the_issue_list(
    browser_page, browser_trace, base_url, admin_auth, admin_client, private_repo
):
    title = "Browser workflow issue from automated run"
    created = admin_client.post(
        f"/repos/{private_repo['full_name']}/issues",
        json={"title": title, "body": "This issue is opened through the browser workflow test."},
    )
    assert created.status_code == 201

    page = browser_page
    page.goto(f"{base_url}/user/login", wait_until="domcontentloaded")
    page.locator("#user_name").fill(admin_auth[0])
    page.locator("#password").fill(admin_auth[1])
    page.get_by_role("button", name=re.compile("sign in", re.IGNORECASE)).click()
    page.wait_for_url(lambda url: "/user/login" not in url, timeout=15_000)
    browser_trace.start_after_login()

    page.goto(f"{base_url}/{private_repo['full_name']}/issues", wait_until="domcontentloaded")
    issue_link = page.get_by_role("link", name=title, exact=True)
    expect(issue_link).to_be_visible(timeout=10_000)
    issue_link.click()
    expect(page.get_by_role("main").get_by_role("heading", level=1)).to_contain_text(title, timeout=10_000)
