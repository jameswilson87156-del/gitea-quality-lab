from qa_lab.html_report import build_html_report


def sample_report():
    return {
        "run_id": "20261029T120000Z-a1b2c3d4",
        "execution_state": "completed",
        "started_at": "2026-10-29T12:00:00Z",
        "finished_at": "2026-10-29T12:00:02Z",
        "target": {
            "name": "Gitea",
            "version": "28.2.0",
            "base_url": "http://127.0.0.1:13000",
            "mode": "local-docker-compose",
        },
        "summary": {"tests": 2, "passed": 1, "failed": 1, "skipped": 0, "errors": 0},
        "cases": [
            {
                "id": "AUTH-001",
                "category": "authentication",
                "node_id": "tests/test_api_auth.py::test_version",
                "outcome": "passed",
                "duration_seconds": 0.25,
                "failure": None,
            },
            {
                "id": "INPUT-001",
                "category": "input-validation",
                "node_id": "tests/test_repository_issues.py::test_invalid_json",
                "outcome": "failed",
                "duration_seconds": 0.5,
                "failure": "Expected 400, received 500 <script>alert('x')</script>",
            },
        ],
    }


def test_html_report_uses_measured_totals_and_case_details():
    rendered = build_html_report(sample_report())

    assert "20261029T120000Z-a1b2c3d4" in rendered
    assert "28.2.0" in rendered
    assert '<strong class="ok">1</strong>' in rendered
    assert '<strong class="bad">1</strong>' in rendered
    assert "AUTH-001" in rendered
    assert "INPUT-001" in rendered
    assert "test_invalid_json" in rendered
    assert "Expected 400, received 500" in rendered


def test_html_report_escapes_failure_text_and_has_responsive_filters():
    rendered = build_html_report(sample_report())

    assert "<script>alert('x')</script>" not in rendered
    assert "&lt;script&gt;alert(&#x27;x&#x27;)&lt;/script&gt;" in rendered
    assert "aria-label=\"Search test cases\"" in rendered
    assert "@media(max-width:760px)" in rendered
    assert "data-outcome=\"failed\"" in rendered
