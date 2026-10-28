# Gitea Quality Lab

An independent black-box automation project for a locally hosted, pinned Gitea instance. It complements PromptOps Studio by demonstrating conventional system testing across REST APIs, authorization, browser workflows, and persisted data.

This repository tests the upstream Gitea product; it is not a Gitea fork. The measured evidence is from a local Docker Compose instance of Gitea 28.2.0 with SQLite. It does not represent a company's production system, production traffic, or production capacity.

## What is covered

- API identity, invalid credentials, admin-only access, repository visibility, input validation, and issue/comment/label lifecycle.
- Chromium login and opening an Issue from the repository Issue list.
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

`python scripts/run.py` starts or reuses only this Compose project, waits for the public version endpoint, prepares the three local test users, and runs the real API/UI/persistence suite. It exits non-zero if a test fails or if pytest does not produce the required JSON report.

## Reports and artifacts

Each run writes to `reports/runs/<run_id>/`:

- `report.json`: run ID, Gitea version, local mode, measured case outcomes, durations, failure details, and totals.
- `junit.xml`: CI-compatible per-test report.
- `report.html`: self-contained pytest HTML report.
- `artifacts/*.png`: actual Chromium screenshots.
- `artifacts/*-trace.zip`: failure trace only when tracing was enabled after successful login. Failures before login keep a screenshot but do not create a trace, so the login password cannot enter the trace.

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
- CI configuration is present, but remote GitHub Actions status is unverified because this project has not been pushed.

## Resume-safe project description

> Built a Python/pytest quality automation project for Gitea 28.2.0 using Docker Compose, HTTPX, and Playwright; covered API authentication and authorization, repository and Issue workflows, browser login, and SQLite persistence after container restart. Generated run-scoped JSON/JUnit/HTML reports and screenshots; the recorded local run passed 12 of 12 cases. This was a local open-source product test, not production-system experience.

See [resume positioning and limits](docs/resume-positioning.md) for wording that keeps the evidence boundary clear.

## Upstream references

- [Gitea release 28.2.0](https://github.com/go-gitea/gitea/releases/tag/v28.2.0)
- [Official Gitea Docker installation and SQLite example](https://docs.gitea.com/installation/install-with-docker/)
- [Gitea REST API](https://docs.gitea.com/api/)
- [Gitea license](https://github.com/go-gitea/gitea/blob/main/LICENSE)
