import json
import time
from urllib.error import HTTPError, URLError
from urllib.request import urlopen


BASE_URL = "http://127.0.0.1:13000"


def wait_for_gitea(base_url: str = BASE_URL, timeout_seconds: int = 120) -> str:
    """Wait for the version API and return its reported Gitea version."""
    deadline = time.monotonic() + timeout_seconds
    last_problem = "not ready"
    while time.monotonic() < deadline:
        try:
            with urlopen(f"{base_url.rstrip('/')}/api/v1/version", timeout=3) as response:
                if response.status == 200:
                    body = json.loads(response.read().decode("utf-8"))
                    version = body.get("version")
                    if isinstance(version, str) and version:
                        return version
                    last_problem = "version response did not contain a version"
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as error:
            last_problem = type(error).__name__
        time.sleep(1)
    raise RuntimeError(f"Gitea did not become ready within {timeout_seconds}s ({last_problem})")
