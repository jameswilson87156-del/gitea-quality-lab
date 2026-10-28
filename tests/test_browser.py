import re

import pytest
from playwright.sync_api import expect


@pytest.mark.case(id="UI-001", category="browser-workflow")
def test_admin_creates_repository_issue_comment_and_closes_it_in_browser(
    browser_page, browser_trace, base_url, admin_auth, admin_client, run_id
):
    username = admin_client.get("/user").json()["login"]
    repo_name = f"qa-ui-{run_id[-8:].lower()}"
    title = "Browser workflow issue from automated run"
    comment = "Comment posted through the browser workflow."
    page = browser_page
    page.goto(f"{base_url}/user/login", wait_until="domcontentloaded")
    page.locator("#user_name").fill(admin_auth[0])
    page.locator("#password").fill(admin_auth[1])
    page.get_by_role("button", name=re.compile("sign in", re.IGNORECASE)).click()
    page.wait_for_url(lambda url: "/user/login" not in url, timeout=15_000)
    browser_trace.start_after_login()

    page.goto(f"{base_url}/repo/create", wait_until="domcontentloaded")
    page.locator("#repo_name").fill(repo_name)
    page.get_by_role("button", name=re.compile("create repository", re.IGNORECASE)).click()
    page.wait_for_url(f"**/{username}/{repo_name}", timeout=15_000)

    page.goto(f"{base_url}/{username}/{repo_name}/issues/new", wait_until="domcontentloaded")
    page.locator("#issue_title").fill(title)
    page.get_by_placeholder("Leave a comment").fill("This Issue is created through the Gitea browser workflow.")
    page.get_by_role("button", name=re.compile("new issue|create issue", re.IGNORECASE)).click()
    page.wait_for_url(re.compile(rf".*/{re.escape(username)}/{re.escape(repo_name)}/issues/\d+"), timeout=15_000)
    expect(page.get_by_role("main").get_by_role("heading", level=1)).to_contain_text(title, timeout=10_000)

    page.get_by_placeholder("Leave a comment").fill(comment)
    page.get_by_role("button", name="Comment", exact=True).click()
    expect(page.locator("p[dir='auto']").filter(has_text=comment)).to_be_visible(timeout=10_000)

    page.get_by_role("button", name=re.compile("close issue", re.IGNORECASE)).click()
    expect(page.get_by_role("button", name=re.compile("reopen", re.IGNORECASE))).to_be_visible(timeout=10_000)
