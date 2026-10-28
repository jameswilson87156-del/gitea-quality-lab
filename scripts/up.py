from __future__ import annotations

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from qa_lab.bootstrap import ensure_test_users
from qa_lab.compose import ROOT, compose_command
from qa_lab.service import wait_for_gitea


def main() -> int:
    started = subprocess.run(
        compose_command("up", "-d", "--wait", "--wait-timeout", "150", "gitea"),
        cwd=ROOT,
        check=False,
    )
    if started.returncode != 0:
        print("Gitea startup failed. Review Docker Compose output; no credentials were printed.", file=sys.stderr)
        return started.returncode

    try:
        version = wait_for_gitea()
        ensure_test_users()
    except RuntimeError as error:
        print(str(error), file=sys.stderr)
        return 1

    print(f"Local Gitea {version} is ready at http://127.0.0.1:13000")
    print("Test accounts are stored in ignored .state/credentials.json; keep this instance local.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
