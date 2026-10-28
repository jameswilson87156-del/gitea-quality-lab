from pathlib import Path


class SafeTraceController:
    """Capture a failure trace only after a test declares sensitive login done."""

    def __init__(self, context, trace_path: Path):
        self.context = context
        self.trace_path = trace_path
        self.started = False

    def start_after_login(self) -> None:
        self.context.tracing.start(screenshots=True, snapshots=True, sources=True)
        self.started = True

    def finish(self, failed: bool) -> bool:
        if not self.started:
            return False
        if failed:
            self.context.tracing.stop(path=str(self.trace_path))
            return True
        self.context.tracing.stop()
        return False
