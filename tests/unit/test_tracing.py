import json
import zipfile

from qa_lab.tracing import SafeTraceController


class FakeTracing:
    def __init__(self):
        self.started = []
        self.stopped = []

    def start(self, **kwargs):
        self.started.append(kwargs)

    def stop(self, **kwargs):
        self.stopped.append(kwargs)
        if "path" in kwargs:
            with zipfile.ZipFile(kwargs["path"], "w") as archive:
                archive.writestr(
                    "trace.network",
                    json.dumps(
                        {
                            "request": {
                                "headers": [
                                    {"name": "Cookie", "value": "gitea_session=SESSION_COOKIE_ABC"},
                                    {"name": "Authorization", "value": "token API_TOKEN_ABC"},
                                ]
                            },
                            "cookies": [{"name": "gitea_session", "value": "SESSION_COOKIE_ABC"}],
                            "body": "password=PASSWORD_ABC",
                        }
                    )
                    + "\n"
                    + json.dumps(
                        {"request": {"headers": [{"name": "Cookie", "value": "gitea_session=EXPIRED_COOKIE_XYZ"}]}}
                    )
                    + "\n",
                )


class FakeContext:
    def __init__(self):
        self.tracing = FakeTracing()

    def cookies(self):
        return [{"name": "gitea_session", "value": "SESSION_COOKIE_ABC"}]


def test_failure_before_authenticated_safe_point_does_not_save_trace(tmp_path):
    context = FakeContext()
    controller = SafeTraceController(context, tmp_path / "trace.zip")

    saved = controller.finish(failed=True)

    assert saved is False
    assert context.tracing.started == []
    assert context.tracing.stopped == []
    assert not (tmp_path / "trace.zip").exists()


def test_trace_is_started_only_when_test_declares_sensitive_login_complete(tmp_path):
    context = FakeContext()
    trace_path = tmp_path / "trace.zip"
    controller = SafeTraceController(context, trace_path)

    controller.start_after_login()
    saved = controller.finish(failed=True)

    assert saved is True
    assert context.tracing.started == [{"screenshots": True, "snapshots": True, "sources": True}]
    assert len(context.tracing.stopped) == 1
    assert "path" in context.tracing.stopped[0]
    assert trace_path.exists()


def test_failure_trace_redacts_cookie_authorization_and_password_secrets(tmp_path):
    context = FakeContext()
    trace_path = tmp_path / "trace.zip"
    controller = SafeTraceController(context, trace_path, secrets=["PASSWORD_ABC", "API_TOKEN_ABC"])

    controller.start_after_login()
    assert controller.finish(failed=True) is True

    with zipfile.ZipFile(trace_path) as archive:
        content = b"\n".join(archive.read(name) for name in archive.namelist())
    assert b"SESSION_COOKIE_ABC" not in content
    assert b"EXPIRED_COOKIE_XYZ" not in content
    assert b"PASSWORD_ABC" not in content
    assert b"API_TOKEN_ABC" not in content
    assert b"[REDACTED]" in content
    trace_records = [json.loads(line) for line in content.decode("utf-8").splitlines()]
    first = trace_records[0]
    assert isinstance(first["cookies"], list)
    assert first["cookies"][0]["value"] == "[REDACTED]"
    assert first["request"]["headers"][0]["value"] == "[REDACTED]"
    assert trace_records[1]["request"]["headers"][0]["value"] == "[REDACTED]"
    assert not list(tmp_path.glob("*.raw.zip"))


def test_passing_trace_is_discarded_after_safe_diagnostics(tmp_path):
    context = FakeContext()
    controller = SafeTraceController(context, tmp_path / "trace.zip")

    controller.start_after_login()
    saved = controller.finish(failed=False)

    assert saved is False
    assert context.tracing.stopped == [{}]
