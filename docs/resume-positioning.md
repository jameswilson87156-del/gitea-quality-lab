# Resume Positioning and Evidence Limits

## Gitea Quality Lab

Suggested project entry:

> **Gitea Quality Lab — API/UI automation testing**
>
> Built a local, repeatable test harness for Gitea 28.2.0 with Docker Compose, SQLite, Python, pytest, HTTPX, and Playwright. Automated API authentication/authorization, public/private repository access, Issue/comment/label lifecycle, a Chromium repository-to-Issue workflow, and post-restart persistence; emitted JSON/JUnit/HTML reports and browser screenshots. The recorded local run executed 16 cases: 16 passed, 0 failed, 0 skipped.

Evidence is available under `reports/runs/20261028T125224Z-80e1fd0e/`; the GitHub Actions run is linked from [acceptance evidence](../reports/evidence.md). Describe it as local open-source product testing and CI execution. Do not call it company project experience, production monitoring, production load, or a Gitea defect discovery project.

## PromptOps Studio

Position PromptOps as an AI Agent evaluation and test-platform project. Before using numeric claims in a resume, verify them against the current project test output and reports. Separate deterministic Mock Agent evidence from real-model results; the existing local order/refund service is a simulator, not a production integration.

## Interview explanation

- Explain the reason for choosing a real open-source target: exercise authentication, permissions, API and browser workflows, and persisted data without inventing access to a company system.
- Show the stable case IDs and how the same command creates a run ID and JUnit/HTML/JSON evidence.
- Demonstrate a meaningful negative case: an ordinary account is denied the admin endpoint or an unrelated user receives no access to a private repository.
- Explain how the restart case verifies persisted repository and Issue state.
- State clearly that one local passing run is proof that this suite executed, not proof of broad coverage or production readiness.
