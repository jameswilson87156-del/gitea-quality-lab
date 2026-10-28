# Architecture

## Components

```text
scripts/run.py
  ├─ Docker Compose project: gitea-quality-lab
  │    └─ Gitea 28.2.0 → SQLite in gitea-quality-lab_gitea_data
  ├─ qa_lab/bootstrap.py → local qa_admin / qa_owner / qa_guest credentials
  └─ pytest
       ├─ HTTPX → Gitea REST API
       ├─ Playwright Chromium → Gitea web UI
       └─ qa_lab/pytest_plugin.py → JSON + JUnit + HTML + browser artifacts
```

## Isolation

- Only `127.0.0.1:13000` is published. The test target URL is fixed in `qa_lab/service.py`; there is no CLI or environment override for remote targets.
- Docker Compose is always invoked with project name `gitea-quality-lab` and the repository's own `compose.yml`.
- The named volume stores only this project's Gitea data. `scripts/stop.py` preserves it; the explicitly destructive reset uses this project's Compose project name.
- Test accounts are created or password-reset through Gitea's local admin CLI, running as the image's unprivileged `git` user. Their random credentials live only in ignored `.state/credentials.json`.

## Execution and evidence

1. The runner starts or reuses the dedicated container and waits on `/api/v1/version`, with bounded retries for startup disconnects.
2. It records the actual Gitea version and creates a unique run ID.
3. Pytest creates run-scoped private repositories, executes API cases, then runs the browser flow and container-restart persistence case.
4. A pytest plugin collects measured case outcomes and writes JSON. Pytest-html and JUnit are emitted by the same process.
5. Browser screenshots are saved per run. Tracing starts only after successful login; a failure before login produces a screenshot without a trace archive.

The recorded results distinguish the local target and mode from test outcomes. There is no remote model, production endpoint, performance claim, or invented result in this execution path.

## CI

GitHub Actions runs on Ubuntu 24.04, installs Python 3.12 and the same pinned dependencies, installs Playwright Chromium headless shell, and calls `python scripts/run.py`. The runner creates its own ephemeral local Gitea service and uploads run artifacts even on failure. The public repository's recorded run passed 19 unit tests and 16 integration cases; see [acceptance evidence](../reports/evidence.md).
