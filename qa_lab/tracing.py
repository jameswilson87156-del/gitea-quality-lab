from __future__ import annotations

import json
import os
from pathlib import Path
import uuid
import zipfile

from qa_lab.reporting import redact_text


_SENSITIVE_FIELD_NAMES = {
    "authorization",
    "cookie",
    "cookies",
    "password",
    "set-cookie",
    "token",
    "secret",
}


def _is_sensitive_name(value: object) -> bool:
    return str(value).strip().lower().replace("_", "-") in _SENSITIVE_FIELD_NAMES


def _redact_sensitive_value(value):
    if isinstance(value, dict):
        return {
            key: "[REDACTED]" if str(key).strip().lower() == "value" or _is_sensitive_name(key)
            else _redact_sensitive_value(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [_redact_sensitive_value(item) for item in value]
    return "[REDACTED]" if isinstance(value, str) and value else value


def _redact_trace_data(value):
    if isinstance(value, dict):
        result = {}
        for key, item in value.items():
            normalized = str(key).strip().lower().replace("_", "-")
            if normalized == "cookies":
                result[key] = _redact_sensitive_value(item)
            elif _is_sensitive_name(key):
                result[key] = _redact_sensitive_value(item)
            else:
                result[key] = _redact_trace_data(item)
        if _is_sensitive_name(value.get("name")) and "value" in value:
            result["value"] = "[REDACTED]"
        return result
    if isinstance(value, list):
        return [_redact_trace_data(item) for item in value]
    return value


def _sanitize_trace_payload(payload: bytes, secrets: list[str]) -> bytes:
    try:
        decoded = payload.decode("utf-8")
    except UnicodeDecodeError:
        return redact_text(payload.decode("utf-8", errors="surrogateescape"), secrets).encode(
            "utf-8", errors="surrogateescape"
        )

    trailing_newline = decoded.endswith(("\n", "\r"))
    try:
        structured = json.loads(decoded)
    except json.JSONDecodeError:
        lines = decoded.splitlines()
        sanitized_lines = []
        parsed_any = False
        for line in lines:
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                sanitized_lines.append(line)
            else:
                parsed_any = True
                sanitized_lines.append(
                    json.dumps(_redact_trace_data(record), ensure_ascii=False, separators=(",", ":"))
                )
        safe_text = "\n".join(sanitized_lines) + ("\n" if trailing_newline else "") if parsed_any else decoded
    else:
        safe_text = json.dumps(_redact_trace_data(structured), ensure_ascii=False, separators=(",", ":"))
        if trailing_newline:
            safe_text += "\n"
    return redact_text(safe_text, secrets).encode("utf-8")


def sanitize_trace_archive(raw_path: Path, safe_path: Path, secrets: list[str]) -> None:
    """Rewrite a Playwright trace archive with credential-bearing fields removed."""
    safe_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(raw_path, "r") as source, zipfile.ZipFile(safe_path, "w", zipfile.ZIP_DEFLATED) as target:
        for entry in source.infolist():
            payload = source.read(entry.filename)
            safe_payload = _sanitize_trace_payload(payload, secrets)
            target.writestr(entry, safe_payload)

    with zipfile.ZipFile(safe_path, "r") as sanitized:
        for name in sanitized.namelist():
            payload = sanitized.read(name)
            if any(secret.encode("utf-8") in payload for secret in secrets if secret):
                raise ValueError("trace archive still contains a configured credential")


class SafeTraceController:
    """Capture a failure trace after login, then sanitize it before publication."""

    def __init__(self, context, trace_path: Path, secrets: list[str] | None = None):
        self.context = context
        self.trace_path = trace_path
        self.secrets = [secret for secret in (secrets or []) if secret]
        self.started = False

    def start_after_login(self) -> None:
        self.context.tracing.start(screenshots=True, snapshots=True, sources=True)
        self.started = True

    def finish(self, failed: bool) -> bool:
        if not self.started:
            return False
        if not failed:
            self.context.tracing.stop()
            return False

        self.trace_path.parent.mkdir(parents=True, exist_ok=True)
        raw_path = self.trace_path.with_name(f".{self.trace_path.name}.{uuid.uuid4().hex}.raw.zip")
        safe_path = self.trace_path.with_name(f".{self.trace_path.name}.{uuid.uuid4().hex}.safe.zip")
        secrets = list(self.secrets)
        try:
            for cookie in self.context.cookies():
                value = cookie.get("value") if isinstance(cookie, dict) else None
                if value:
                    secrets.append(str(value))
            self.context.tracing.stop(path=str(raw_path))
            sanitize_trace_archive(raw_path, safe_path, secrets)
            os.replace(safe_path, self.trace_path)
            return True
        except Exception:
            self.trace_path.unlink(missing_ok=True)
            return False
        finally:
            raw_path.unlink(missing_ok=True)
            safe_path.unlink(missing_ok=True)
