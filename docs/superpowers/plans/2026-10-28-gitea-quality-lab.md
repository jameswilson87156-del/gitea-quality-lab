# Gitea Quality Lab Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build an independent, reproducible local API/UI automation project that tests a pinned Gitea instance and emits truthful run evidence.

**Architecture:** Docker Compose runs Gitea 28.2.0 with SQLite in a project-specific named volume bound only to loopback. Python scripts bootstrap local-only test users, execute pytest against HTTP APIs and Chromium, capture artifacts, and emit JUnit, HTML, and JSON reports. A GitHub Actions workflow runs the same suite.

**Tech Stack:** Python 3.12, pytest, httpx, Playwright Python, pytest-html, Docker Compose v2.

**Spec:** `../../../../outputs/2026-10-28-gitea-quality-lab-design.md`

## Global Constraints

- Use `docker.gitea.com/gitea:28.2.0` and SQLite in a named volume scoped to `gitea-quality-lab`.
- Publish the web service only as `127.0.0.1:13000:3000`.
- Never target GitHub.com, an employer instance, or any remote service.
- Keep credentials in ignored local state; never print or commit them.
- Test data must use a per-run namespace; a run must not clean data belonging to another run.
- Clearly label results as local Gitea product testing, not production-system evidence.
- Preserve the existing PromptOps workspace, branch, files, containers, and volumes.

## Review Focus

- Gitea starts slowly or is already healthy but not ready for API requests: retry the public version endpoint with a bounded timeout.
- Local credentials are missing while the project volume already exists: bootstrap must reset only the dedicated test users without logging passwords.
- API authentication failures: do not leak token/password values in pytest failures or reports.
- Repeated runs: namespace repositories and artifact paths by run ID; do not collide with prior test resources.
- Service restart and browser failure: keep assertions and artifacts tied to the active run, and preserve the Compose volume.

---

### Task 1: Isolated Gitea runtime and local bootstrap

**Files:**
- Create: `compose.yml`
- Create: `requirements.txt`
- Create: `.gitignore`
- Create: `qa_lab/__init__.py`
- Create: `qa_lab/compose.py`
- Create: `qa_lab/bootstrap.py`
- Create: `scripts/up.py`
- Create: `scripts/stop.py`
- Test: `tests/unit/test_compose.py`
- Test: `tests/unit/test_bootstrap.py`

**Interfaces:**
- `qa_lab.compose.compose_command(*args: str) -> list[str]` returns a Docker Compose command scoped to this directory and project.
- `qa_lab.bootstrap.ensure_test_users() -> dict[str, str]` returns local credential values and persists them only under `.state/credentials.json`.
- `scripts/up.py` starts Gitea, waits for `/api/v1/version`, then ensures local admin/owner/guest accounts.

- [ ] Write unit tests for project-scoped Compose commands, generated credential storage, and duplicate-user password reset.
- [ ] Run `py -3.12 -m pytest tests/unit/test_compose.py tests/unit/test_bootstrap.py -q`; expected: FAIL because the modules are not implemented.
- [ ] Implement the Compose wrapper and idempotent user bootstrap. Capture Docker CLI output internally and never echo it on errors.
- [ ] Run the unit tests; expected: PASS.
- [ ] Run `py -3.12 scripts/up.py`; expected: only the `gitea-quality-lab` service starts, health endpoint returns 200, and generated credentials remain in ignored `.state/`.
- [ ] Commit the isolated runtime, bootstrap, and unit tests as `feat: add isolated Gitea runtime`.

### Task 2: Repeatable API suite and machine-readable report

**Files:**
- Create: `pytest.ini`
- Create: `tests/conftest.py`
- Create: `tests/test_api_auth.py`
- Create: `tests/test_repository_issues.py`
- Create: `qa_lab/reporting.py`
- Create: `scripts/run.py`
- Test: `tests/unit/test_reporting.py`

**Interfaces:**
- Fixtures expose `base_url`, `admin_auth`, `owner_auth`, `guest_auth`, `run_id`, and a function-scoped private repository.
- `qa_lab.reporting.build_report(run_id, target, cases, timestamps) -> dict` records measured pytest outcomes and metadata.
- `scripts/run.py` writes `reports/runs/<run_id>/report.json`, `junit.xml`, and `report.html`; the process exit code matches pytest.

- [ ] Write tests for report pass/fail/skip counts and secret redaction.
- [ ] Run `py -3.12 -m pytest tests/unit/test_reporting.py -q`; expected: FAIL before implementation.
- [ ] Implement measured per-case reporting and unique run-scoped repository names.
- [ ] Run unit tests; expected: PASS.
- [ ] Run the API suite against local Gitea; expected: real HTTP responses validate identity, invalid credentials, admin-only route denial, repository visibility, issue/comment lifecycle, and invalid payload behavior.
- [ ] Commit the API suite and report pipeline as `test: add repeatable Gitea API evaluation`.

### Task 3: Browser flow, trace artifacts, and restart persistence

**Files:**
- Create: `tests/test_browser.py`
- Modify: `tests/test_repository_issues.py`
- Modify: `tests/conftest.py`
- Modify: `scripts/run.py`

**Interfaces:**
- `browser_page` is a Chromium page with tracing enabled and a run-scoped artifact directory.
- A passing browser test saves a full-page screenshot; a failing browser test saves screenshot and Playwright trace.
- The persistence test restarts only the Gitea service through the project-scoped Compose command and verifies the same repository and issue remain readable.

- [ ] Write the browser login/issue assertion and restart-persistence test.
- [ ] Run those tests; expected: the new tests fail before their implementation/fixtures exist.
- [ ] Implement browser tracing, screenshots, bounded health wait, and container-restart verification without deleting the volume.
- [ ] Run the targeted tests; expected: real Gitea login and persisted issue pass.
- [ ] Run the entire API/UI suite; expected: pytest exit code 0 and report counts agree with JUnit.
- [ ] Commit the browser and persistence checks as `test: cover Gitea UI and restart persistence`.

### Task 4: CI, reproducibility documentation, and evidence audit

**Files:**
- Create: `README.md`
- Create: `docs/test-matrix.md`
- Create: `docs/defect-log.md`
- Create: `.github/workflows/quality.yml`
- Create: `LICENSE`
- Create: `reports/runs/<actual-run-id>/...`

- [ ] Document Windows and Linux setup, local-only boundaries, test matrix, report interpretation, start/stop commands, and evidence limitations.
- [ ] Add GitHub Actions steps for Python 3.12, Playwright Chromium, the same Compose/pytest runner, and always-uploaded reports.
- [ ] Run `py -3.12 -m pytest tests/unit -q` and `py -3.12 scripts/run.py`; expected: pass with actual JSON/JUnit/HTML and screenshot artifacts.
- [ ] Inspect the JSON report against JUnit and a live API query; expected: IDs, counts, run ID, service version, and outcomes agree.
- [ ] Inspect repository status and confirm no `.state` secrets, PromptOps files, or unrelated containers were changed.
- [ ] Commit CI, documentation, and nonsensitive evidence as `docs: document Gitea quality lab and evidence`.

## Self-Review

- Spec coverage: separate project and fixed upstream target are Task 1; API/auth/permissions/issues are Task 2; browser, trace, and volume persistence are Task 3; CI, reports, documentation, and scope boundaries are Task 4.
- Step granularity: each task has explicit test commands and expected outcomes; actual upstream behavior is verified against the running pinned service.
- Type consistency: Compose helpers, bootstrap credentials, report builder, and pytest fixtures have named interfaces above.
- Review focus: readiness, stale credentials, secret output, repeat runs, and restart failure evidence are exercised in unit/integration checks.
- Proportion: four tasks follow the four independent deliverables in the design; no real model, production target, or load-testing expansion is included.

