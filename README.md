# Gitea Quality Lab

[![Quality](https://github.com/jameswilson87156-del/gitea-quality-lab/actions/workflows/quality.yml/badge.svg?branch=main)](https://github.com/jameswilson87156-del/gitea-quality-lab/actions/workflows/quality.yml)

An independent black-box automation project for a locally hosted, pinned Gitea instance. It complements PromptOps Studio by demonstrating conventional system testing across REST APIs, authorization, browser workflows, and persisted data.

This repository tests the upstream Gitea product; it is not a Gitea fork. The measured evidence is from a local Docker Compose instance of Gitea 28.2.0 with SQLite. It does not represent a company's production system, production traffic, or production capacity.

## What is covered

- API identity, invalid credentials, admin-only access, anonymous public/private repository access, guest write denial at the private-repository boundary, regular-user repository creation, input validation, and Issue/comment/label lifecycle.
- Chromium login, repository creation, Issue creation, comment submission, and Issue closure.
- SQLite-backed repository and Issue persistence after restarting the Gitea container.
- Per-run JSON, JUnit XML, HTML, browser screenshot, and failure trace artifacts.
- A GitHub Actions workflow that runs the same local Compose and pytest process.

See [the test matrix](docs/test-matrix.md), [architecture](docs/architecture.md), and [observed test-harness issues](docs/defect-log.md).
The planned complementary upgrades for PromptOps are in [the Agent Eval roadmap](docs/agent-eval-upgrade-roadmap.md).

## Requirements

- Docker Desktop with Docker Compose v2, or Docker Engine with Compose v2.
- Python 3.12.
- About 4 GB of available Docker memory is sufficient for this single Gitea service; this project does not start a database container because it uses Gitea's SQLite backend.
- The local port `13000` must be available.

The web port binds to `127.0.0.1:13000`. The Compose project and named volume are `gitea-quality-lab`; they are separate from PromptOps and other Compose projects.

## Windows quick start

Run these commands from the repository directory in PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
$env:PLAYWRIGHT_BROWSERS_PATH = '0'
python -m playwright install --only-shell --no-remove chromium
python scripts/up.py
python scripts/run.py
```

The first startup creates local test users with random passwords and writes them to `.state/credentials.json`. That folder is ignored by Git. The test runner does not print credentials and always targets the fixed loopback URL in this repository.

## Linux / macOS quick start

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
export PLAYWRIGHT_BROWSERS_PATH=0
python -m playwright install --with-deps --only-shell chromium
python scripts/up.py
python scripts/run.py
```

`python scripts/run.py` starts or reuses only this Compose project, waits for the public version endpoint, prepares the three local test users, and runs the API/UI/persistence suite. It exits non-zero if a test fails, a JSON/JUnit report is missing, JSON totals do not match individual outcomes, JUnit totals disagree, the run ID is wrong, or a case ID is duplicated.

## Reports and artifacts

Each run writes to `reports/runs/<run_id>/`:

- `report.json`: run ID, Gitea version, local mode, measured case outcomes, durations, failure details, and totals.
- `junit.xml`: CI-compatible per-test report.
- `report.html`: project-owned responsive run report rendered from the validated JSON snapshot.
- `pytest-report.html`: upstream pytest-html diagnostic report.
- `artifacts/*.png`: actual Chromium screenshots.
- `artifacts/*-trace.zip`: failure trace only when tracing was enabled after successful login. Configured credentials and cookie/authorization values are redacted before publishing; raw trace archives are discarded. If sanitization fails, no trace is published.

Before returning, the runner cross-checks JSON totals against case outcomes and JUnit test cases, then renders the interactive HTML report from that validated snapshot. The accepted local verification and its generated reports are recorded in [the evidence log](reports/evidence.md).

The accepted local run is recorded in [reports/evidence.md](reports/evidence.md). Earlier iterative runs remain available in `reports/runs/`; their failures document issues found and fixed during development. Read `report.json` for the final run's actual counts; do not infer results from this README after code changes.

## Stop and reset

Stop the service while keeping its SQLite data:

```powershell
python scripts/stop.py
```

The command runs `docker compose down` for this project only and keeps the named data volume. To deliberately erase this project's Gitea data and start fresh, run the following only after confirming the project name and backing up anything you need:

```powershell
docker compose --project-name gitea-quality-lab --file compose.yml down --volumes
```

That reset removes the `gitea-quality-lab_gitea_data` volume and its local test users, repositories, and Issues. It does not target PromptOps volumes.

## Reproducibility and boundaries

- Gitea image is pinned to `docker.gitea.com/gitea:28.2.0`; Python dependencies are pinned in `requirements.txt`.
- Each test run gets a unique run ID and each generated repository uses that run ID, so reruns do not collide with prior data.
- The suite performs no paid model calls, no remote API calls, and no production or internet-facing testing.
- A test marked passed means the observed local Gitea behavior matched that case's assertion. It is not a claim that every Gitea feature is defect-free.
- GitHub Actions ran the unit and local Gitea integration suites successfully on the `feat/gitea-quality-lab` branch; see the [recorded evidence](reports/evidence.md) and [workflow run](https://github.com/jameswilson87156-del/gitea-quality-lab/actions/runs/40710451708).

## Resume-safe project description

> Built a Python/pytest quality automation project for Gitea 28.2.0 using Docker Compose, HTTPX, and Playwright; covered API authentication and authorization, repository and Issue workflows, a browser-based create/comment/close flow, pagination and state filters, and SQLite persistence after container restart. Generated run-scoped JSON/JUnit and responsive HTML reports with screenshots; the latest recorded local run passed 18 of 18 cases. This was a local open-source product test, not production-system experience.

See [resume positioning and limits](docs/resume-positioning.md) for wording that keeps the evidence boundary clear.

## Upstream references

- [Gitea release 28.2.0](https://github.com/go-gitea/gitea/releases/tag/v28.2.0)
- [Official Gitea Docker installation and SQLite example](https://docs.gitea.com/installation/install-with-docker/)
- [Gitea REST API](https://docs.gitea.com/api/)
- [Gitea license](https://github.com/go-gitea/gitea/blob/main/LICENSE)
