from playwright.sync_api import expect, sync_playwright

from qa_lab.html_report import build_html_report


def test_html_report_filters_expands_and_fits_mobile_viewport():
    report = {
        "run_id": "browser-check-001",
        "execution_state": "completed",
        "target": {"name": "Gitea", "version": "28.2.0", "mode": "local"},
        "summary": {"tests": 2, "passed": 1, "failed": 1, "errors": 0, "skipped": 0},
        "cases": [
            {
                "id": "AUTH-001",
                "category": "authentication",
                "node_id": "tests/test_auth.py::test_login",
                "outcome": "passed",
                "duration_seconds": 0.2,
                "failure": None,
            },
            {
                "id": "ISSUE-004",
                "category": "issue-query",
                "node_id": "tests/test_issues.py::test_pagination",
                "outcome": "failed",
                "duration_seconds": 0.4,
                "failure": "Expected three unique issues, received two.",
            },
        ],
    }

    with sync_playwright() as playwright:
        try:
            browser = playwright.chromium.launch()
        except Exception:
            browser = playwright.chromium.launch(channel="chrome")
        page = browser.new_page(viewport={"width": 1440, "height": 1000})
        page.set_content(build_html_report(report))

        rows = page.locator(".case-row")
        expect(rows).to_have_count(2)
        page.get_by_role("searchbox", name="Search test cases").fill("ISSUE-004")
        expect(page.locator(".case-row:visible")).to_have_count(1)
        page.get_by_label("Search test cases").fill("")
        page.get_by_label("Filter by outcome").select_option("failed")
        expect(page.locator(".case-row:visible")).to_have_count(1)
        expect(page.locator(".case-row:visible .case-id")).to_have_text("ISSUE-004")
        page.locator(".case-row:visible summary").click()
        expect(page.locator(".case-row:visible .case-detail")).to_contain_text(
            "Expected three unique issues, received two."
        )

        page.set_viewport_size({"width": 390, "height": 844})
        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
        browser.close()
