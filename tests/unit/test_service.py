from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import socket
import threading

from qa_lab import service


def test_local_target_resolver_accepts_only_fixed_loopback(monkeypatch):
    assert service.resolve_base_url(None) == service.BASE_URL
    assert service.resolve_base_url("http://127.0.0.1:13000/") == service.BASE_URL

    for requested in (
        "https://example.com",
        "http://127.0.0.1:13001",
        "http://localhost:13000",
        "http://127.0.0.1:13000/path",
    ):
        try:
            service.resolve_base_url(requested)
        except ValueError as error:
            assert "fixed local target" in str(error)
        else:
            raise AssertionError(f"unexpected target accepted: {requested}")


def test_local_target_resolver_rejects_environment_override(monkeypatch):
    monkeypatch.setenv("GITEA_BASE_URL", "https://example.com")
    try:
        service.resolve_base_url_from_environment()
    except ValueError as error:
        assert "fixed local target" in str(error)
    else:
        raise AssertionError("external GITEA_BASE_URL override was accepted")


def test_wait_for_gitea_retries_a_real_connection_drop(monkeypatch):
    class FlakyHandler(BaseHTTPRequestHandler):
        attempts = 0

        def do_GET(self):
            type(self).attempts += 1
            if type(self).attempts == 1:
                self.connection.shutdown(socket.SHUT_RDWR)
                self.connection.close()
                return
            body = b'{"version":"28.2.0"}'
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, format, *args):
            return

    server = ThreadingHTTPServer(("127.0.0.1", 0), FlakyHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    monkeypatch.setattr(service.time, "sleep", lambda _seconds: None)
    try:
        version = service.wait_for_gitea(f"http://127.0.0.1:{server.server_port}", timeout_seconds=2)
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)

    assert version == "28.2.0"
    assert FlakyHandler.attempts == 2
