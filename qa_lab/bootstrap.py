import json
import secrets
import subprocess
from pathlib import Path

from qa_lab.compose import ROOT, compose_command


CREDENTIALS_FILE = ROOT / ".state" / "credentials.json"
USER_SPECS = {
    "admin": ("qa_admin", "qa-admin@example.invalid", True),
    "owner": ("qa_owner", "qa-owner@example.invalid", False),
    "guest": ("qa_guest", "qa-guest@example.invalid", False),
}


def run_gitea_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        compose_command("exec", "-T", "--user", "git", "gitea", "gitea", *args),
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def _ensure_user(username: str, password: str, email: str, admin: bool) -> None:
    create_args = [
        "admin",
        "user",
        "create",
        "--username",
        username,
        "--password",
        password,
        "--email",
        email,
        "--must-change-password=false",
    ]
    if admin:
        create_args.append("--admin")
    created = run_gitea_cli(*create_args)
    if created.returncode == 0:
        return

    reset = run_gitea_cli(
        "admin",
        "user",
        "change-password",
        "--username",
        username,
        "--password",
        password,
        "--must-change-password=false",
    )
    if reset.returncode != 0:
        raise RuntimeError(f"Could not prepare local test user '{username}'; Docker CLI details were suppressed.")


def ensure_test_users(credentials_file: Path = CREDENTIALS_FILE) -> dict[str, dict[str, str]]:
    """Create or reset only the named accounts in this isolated Gitea instance."""
    if credentials_file.exists():
        try:
            credentials = json.loads(credentials_file.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise RuntimeError("Local credentials file is unreadable; remove it only if you can reset this test instance.") from error
    else:
        credentials = {}

    for key, (username, email, is_admin) in USER_SPECS.items():
        existing = credentials.get(key, {})
        password = existing.get("password") if isinstance(existing, dict) else None
        if not isinstance(password, str) or len(password) < 20:
            password = secrets.token_urlsafe(32)
        credentials[key] = {"username": username, "email": email, "password": password}
        _ensure_user(username, password, email, is_admin)

    credentials_file.parent.mkdir(parents=True, exist_ok=True)
    credentials_file.write_text(json.dumps(credentials, indent=2) + "\n", encoding="utf-8")
    try:
        credentials_file.chmod(0o600)
    except OSError:
        pass
    return credentials
