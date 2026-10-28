from datetime import datetime, timezone
import uuid


OUTCOMES = {"passed", "failed", "skipped", "error"}


def create_run_id(now: datetime | None = None) -> str:
    moment = now or datetime.now(timezone.utc)
    stamp = moment.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"{stamp}-{uuid.uuid4().hex[:8]}"


def redact_text(value: str, secret_values: list[str]) -> str:
    redacted = value
    for secret in sorted((secret for secret in secret_values if secret), key=len, reverse=True):
        redacted = redacted.replace(secret, "[REDACTED]")
    return redacted


def build_report(
    run_id: str,
    target: dict[str, str],
    started_at: str,
    finished_at: str,
    cases: list[dict],
) -> dict:
    counts = {outcome: 0 for outcome in OUTCOMES}
    for case in cases:
        outcome = case.get("outcome", "error")
        counts[outcome if outcome in OUTCOMES else "error"] += 1
    return {
        "schema_version": 1,
        "run_id": run_id,
        "execution_state": "completed",
        "started_at": started_at,
        "finished_at": finished_at,
        "target": target,
        "summary": {
            "tests": len(cases),
            "passed": counts["passed"],
            "failed": counts["failed"],
            "skipped": counts["skipped"],
            "errors": counts["error"],
        },
        "cases": cases,
    }
