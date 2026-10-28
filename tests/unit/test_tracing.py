from qa_lab.tracing import SafeTraceController


class FakeTracing:
    def __init__(self):
        self.started = []
        self.stopped = []

    def start(self, **kwargs):
        self.started.append(kwargs)

    def stop(self, **kwargs):
        self.stopped.append(kwargs)


class FakeContext:
    def __init__(self):
        self.tracing = FakeTracing()


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
    assert context.tracing.stopped == [{"path": str(trace_path)}]


def test_passing_trace_is_discarded_after_safe_diagnostics(tmp_path):
    context = FakeContext()
    controller = SafeTraceController(context, tmp_path / "trace.zip")

    controller.start_after_login()
    saved = controller.finish(failed=False)

    assert saved is False
    assert context.tracing.stopped == [{}]
