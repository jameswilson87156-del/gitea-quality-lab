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

## 2026-10-29 local end-to-end rerun

- Command: `.\.venv\Scripts\python.exe scripts/run.py`
- Target: pinned Gitea 28.2.0 at `127.0.0.1:13000`, local Compose/SQLite.
- Exit code: `0`; 16 tests, 16 passed, 0 failed, 0 skipped, 0 errors. Run ID: `20261029T021704Z-a5940ea1`.
- Runner independently cross-checked JSON/JUnit totals; all case IDs are unique.
- The test set covered authentication/authorization, public/private repository boundaries, Issue validation/lifecycle, Chromium create/comment/close workflow, and SQLite-backed repository/Issue persistence after restarting the dedicated Gitea container.
- Harness unit command `.\.venv\Scripts\python.exe -m pytest tests/unit -q` — exit `0`; 24 passed, 0 failed/skipped.
- Run artifacts: [`report.json`](runs/20261029T021704Z-a5940ea1/report.json), [`junit.xml`](runs/20261029T021704Z-a5940ea1/junit.xml), [`report.html`](runs/20261029T021704Z-a5940ea1/report.html), [Chromium screenshot](runs/20261029T021704Z-a5940ea1/artifacts/20261029T021704Z-a5940ea1-UI-001.png).
- The Gitea service was already running and remains available. These are local synthetic tests of the upstream open-source product; they do not represent company production systems, user traffic, or production capacity.

## Issue query coverage update — initial blocked attempt

- Added `ISSUE-003` for open/closed state filtering and `ISSUE-004` for two-page Issue listing with a small page size. Each case uses a fresh run-scoped private repository; assertions compare the exact test-created Issue IDs so unrelated historical Issues cannot satisfy them.
- Harness unit tests: `\.venv\Scripts\python.exe -m pytest tests/unit -q` — exit `0`; 24 passed, 0 failed, 0 skipped.
- Initial integration attempt: `\.venv\Scripts\python.exe scripts/run.py` — exit `1` before the suite started because Docker could not connect to `npipe:////./pipe/dockerDesktopLinuxEngine`; `http://127.0.0.1:13000/api/v1/version` was also unavailable. This initial attempt produced no integration report. Docker Desktop was started afterward and the cases were rerun successfully below.

## Issue query coverage acceptance run

- Run ID: `20261029T114725Z-15c81899`; target Gitea `28.2.0`, local Docker Compose/SQLite at `http://127.0.0.1:13000`.
- Command: `\.venv\Scripts\python.exe scripts\run.py` — exit code `0`; 18 tests, 18 passed, 0 failed, 0 skipped, 0 errors. The report validator confirmed JSON/JUnit totals agree.
- `ISSUE-003` passed: closing the created Issue makes it appear in `state=closed` and not in `state=open`.
- `ISSUE-004` passed: listing three run-scoped Issues across two pages (`limit=2`) returned two plus one, with no duplicate or missing IDs.
- Evidence: [`report.json`](runs/20261029T114725Z-15c81899/report.json), [`junit.xml`](runs/20261029T114725Z-15c81899/junit.xml), [`report.html`](runs/20261029T114725Z-15c81899/report.html), [Chromium screenshot](runs/20261029T114725Z-15c81899/artifacts/20261029T114725Z-15c81899-UI-001.png).
- Harness unit tests rerun: `\.venv\Scripts\python.exe -m pytest tests/unit -q` — exit code `0`; 24 passed, 0 failed, 0 skipped.
- These results cover the local synthetic suite against Gitea 28.2.0 only; they do not describe an employer's system, production traffic, or production capacity.

## Run report presentation and responsive verification — 2026-10-29

- Added a project-owned, self-contained HTML report rendered from the validated run-scoped JSON. It shows only observed case outcomes, category totals derived from those rows, search/outcome/category filters, and expandable case details. The upstream `pytest-html` output remains available as `pytest-report.html`.
- Latest local end-to-end run: `20261029T150955Z-4437d857`; command `\.venv\Scripts\python.exe scripts\run.py`; exit code `0`; Gitea 28.2.0; 18 passed, 0 failed, 0 skipped, 0 errors. JSON/JUnit validation succeeded.
- Harness unit command `\.venv\Scripts\python.exe -m pytest tests\unit -q` — exit code `0`; 27 passed, 0 failed, 0 skipped. The added Playwright browser test checks the custom report's search, outcome filter, failure detail expansion, and 390px viewport width.
- Dedicated report-page browser evidence at 1440×1000 and 390×844: 18 case rows, category counts rendered from the JSON snapshot, status and case search, expandable details, and no horizontal overflow. These two report-page screenshots were captured from run `20261029T144534Z-ec54abd9`: [desktop](runs/20261029T144534Z-ec54abd9/artifacts/report-desktop.png), [mobile](runs/20261029T144534Z-ec54abd9/artifacts/report-mobile.png). The newest run has a separate API/UI/persistence screenshot.
- Latest machine-readable evidence: [report.json](runs/20261029T150955Z-4437d857/report.json); [JUnit XML](runs/20261029T150955Z-4437d857/junit.xml); [project HTML report](runs/20261029T150955Z-4437d857/report.html); [pytest-html report](runs/20261029T150955Z-4437d857/pytest-report.html); [API/UI/persistence screenshot](runs/20261029T150955Z-4437d857/artifacts/20261029T150955Z-4437d857-UI-001.png).
- The result remains a local synthetic test of upstream Gitea on a dedicated instance. It is not production-system or load-capacity evidence.
