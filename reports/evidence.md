# Local Acceptance Evidence

## Accepted end-to-end run

- Run ID: `20261028T123203Z-10297b8d`
- Date: 2026-10-28 UTC
- Target: Gitea `28.2.0`, `local-docker-compose`, `http://127.0.0.1:13000`
- Command: `.\.venv\Scripts\python.exe scripts/run.py`
- Exit code: `0`
- Result: 12 collected, 12 passed, 0 failed, 0 skipped, 0 errors
- The persistence case restarted only `gitea-quality-lab-gitea-1`, then read the same repository and Issue from the named SQLite volume.

Evidence files:

- [`report.json`](runs/20261028T123203Z-10297b8d/report.json)
- [`junit.xml`](runs/20261028T123203Z-10297b8d/junit.xml)
- [`report.html`](runs/20261028T123203Z-10297b8d/report.html)
- [Chromium screenshot](runs/20261028T123203Z-10297b8d/artifacts/20261028T123203Z-10297b8d-test_admin_signs_in_and_opens_an_issue_from_the_issue_list.png)

JSON and JUnit totals were compared after the run: both reported 12 tests, 12 passes, no failures, skips, or errors. The JSON and report artifacts were scanned against the local credential file; no credential strings were found. The passing run produced no failure trace, as expected.

## Harness unit tests

- Command: `.\.venv\Scripts\python.exe -m pytest tests/unit -q`
- Exit code: `0`
- Result: 12 passed

## CI status

The workflow is configured in `.github/workflows/quality.yml`, but no remote Actions run is claimed. The project has not been pushed.
