# Local Acceptance Evidence

## Accepted end-to-end run

- Run ID: `20261028T125224Z-80e1fd0e`
- Date: 2026-10-28 UTC
- Target: Gitea `28.2.0`, `local-docker-compose`, `http://127.0.0.1:13000`
- Command: `.\.venv\Scripts\python.exe scripts/run.py`
- Exit code: `0`
- Result: 16 collected, 16 passed, 0 failed, 0 skipped, 0 errors
- The suite includes anonymous public/private repository access, denial at a private-repository boundary, regular-user repository/Issue creation, browser creation/comment/close flow, and persistence after restarting the dedicated Gitea container.

Evidence files:

- [`report.json`](runs/20261028T125224Z-80e1fd0e/report.json)
- [`junit.xml`](runs/20261028T125224Z-80e1fd0e/junit.xml)
- [`report.html`](runs/20261028T125224Z-80e1fd0e/report.html)
- [Chromium screenshot of the browser workflow](runs/20261028T125224Z-80e1fd0e/artifacts/20261028T125224Z-80e1fd0e-UI-001.png)

JSON and JUnit both report 16 tests, 16 passes, no failures, skips, or errors. The JSON case IDs are unique. The accepted run's report files were scanned against local password/token values; no matches were found. Since the run passed, it correctly contains no failure trace.

## Harness unit tests

- Command: `.\.venv\Scripts\python.exe -m pytest tests/unit -q`
- Exit code: `0`
- Result: 19 passed
- Coverage includes teardown accounting, setup-skip reporting, pre-reporter secret redaction, loopback target restriction, and cookie/header/NDJSON Trace sanitization.

## Failure-trace and report-secret diagnostic

Run `20261028T125412Z-76a418db` is a separate, intentional diagnostic, not part of the accepted end-to-end suite. It used a temporary browser test that logged in, enabled Trace, then raised an intentional failure containing the local admin password. A second temporary test skipped during setup to exercise pytest/JUnit compatibility. The temporary source was removed after the run.

- Pytest exit code: `1`, expected because `TRACE-PROBE-001` deliberately failed.
- Result: 2 tests, 0 passed, 1 failed, 1 skipped, 0 errors.
- JSON and JUnit totals agree.
- The password was absent from captured terminal output, JSON, JUnit, and HTML.
- A post-login Playwright Trace ZIP was generated; cookie, authorization, and credential fields were redacted and no raw trace remained.
- Before public release, the machine-specific absolute path in the diagnostic JUnit skip detail was replaced with its project-relative path; the case result and totals are unchanged.
- Command shape: `python -m pytest tests/test_security_probe_temp.py -ra --tb=short --junitxml=<run-dir>/junit.xml --html=<run-dir>/report.html --self-contained-html`; the test module was generated temporarily and removed afterward.

Evidence files:

- [`report.json`](runs/20261028T125412Z-76a418db/report.json)
- [`junit.xml`](runs/20261028T125412Z-76a418db/junit.xml)
- [`report.html`](runs/20261028T125412Z-76a418db/report.html)
- [Sanitized failure Trace](runs/20261028T125412Z-76a418db/artifacts/20261028T125412Z-76a418db-TRACE-PROBE-001-trace.zip)

This probe is intentionally reported as a failing diagnostic. Do not include it in the accepted-suite pass count.

## Environment checks

- `\.venv\Scripts\python.exe -m compileall -q qa_lab tests scripts` — exit `0`.
- `\.venv\Scripts\python.exe -m pip check` — exit `0`, no broken requirements.
- `docker compose --project-name gitea-quality-lab --file compose.yml ps` — Gitea `28.2.0` healthy on `127.0.0.1:13000`.

## CI status and boundaries

The public repository is [jameswilson87156-del/gitea-quality-lab](https://github.com/jameswilson87156-del/gitea-quality-lab). GitHub Actions run [40701222279](https://github.com/jameswilson87156-del/gitea-quality-lab/actions/runs/40701222279) completed successfully on `main` at commit `3460f5c4d7c97723aec3656814d6bee6d7086640`.

- Workflow/job: `Quality` / `local-gitea-quality`
- Runner: Ubuntu 24.04.5; Python 3.12.15
- Unit tests: 19 passed, 0 failed, 0 skipped; exit code 0
- Local Gitea API/browser/persistence suite: 16 passed, 0 failed, 0 skipped, 0 errors; exit code 0
- Report upload: succeeded; artifact [`gitea-quality-reports`](https://github.com/jameswilson87156-del/gitea-quality-lab/actions/runs/40701222279/artifacts/12821133970), retained by GitHub for 14 days
- Integration report run ID: `20261028T135804Z-e4646c3c`

The workflow uses an ephemeral local Gitea service in GitHub Actions. These results verify this repository's automated checks on the hosted runner; they do not represent a company's production system, production monitoring, production traffic, or production load. The recorded local acceptance and intentional failure diagnostic above remain separate from the GitHub Actions run.

## Report-integrity validator update

After adding JSON/JUnit cross-validation to `scripts/run.py`, the local checks were rerun on 2026-10-28:

- `\.venv\Scripts\python.exe -m pytest tests\unit -q` — exit `0`; 24 passed, 0 failed, 0 skipped. This includes five report-integrity checks for matching totals, run-ID mismatch, duplicate case IDs, JSON-summary mismatch, and JUnit mismatch.
- `\.venv\Scripts\python.exe scripts\run.py` — exit `0`; Gitea `28.2.0`; 16 passed, 0 failed, 0 skipped, 0 errors. The runner independently validated that JSON and JUnit both report 16 tests, 16 passed, and zero other outcomes.
- Local run ID: `20261028T144605Z-9971cee7`.
- JSON: [`report.json`](runs/20261028T144605Z-9971cee7/report.json); JUnit: [`junit.xml`](runs/20261028T144605Z-9971cee7/junit.xml); HTML: [`report.html`](runs/20261028T144605Z-9971cee7/report.html); Chromium evidence: [`UI screenshot`](runs/20261028T144605Z-9971cee7/artifacts/20261028T144605Z-9971cee7-UI-001.png).
- Hosted verification: [GitHub Actions run 40710451708](https://github.com/jameswilson87156-del/gitea-quality-lab/actions/runs/40710451708) on `feat/gitea-quality-lab`, commit `96baaa814f8c005451e54e9e967516814bde78f1`, completed successfully on Ubuntu 24.04.5 / Python 3.12.15. Unit tests: 24 passed; local Gitea API/browser/persistence: 16 passed, 0 failed/skipped/errors; the runner printed matching JSON/JUnit totals.
- CI integration Run ID: `20261028T145441Z-5318397a`. GitHub uploaded artifact [`gitea-quality-reports`](https://github.com/jameswilson87156-del/gitea-quality-lab/actions/runs/40710451708/artifacts/12825887164) (1,577,880 bytes, 14-day retention).
- These hosted results verify this repository's tests against an ephemeral local Gitea container. They do not represent a company's production system, user traffic, or production capacity. The separate Windows/Docker local run and its files above remain preserved.
