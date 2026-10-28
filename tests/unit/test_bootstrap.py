import json
import subprocess

from qa_lab import bootstrap
from qa_lab.compose import compose_command


def test_ensure_test_users_creates_local_credentials_and_admin_users(tmp_path, monkeypatch):
    calls = []

    def fake_cli(*args):
        calls.append(args)
        return subprocess.CompletedProcess(args, 0, stdout="created", stderr="")

    monkeypatch.setattr(bootstrap, "run_gitea_cli", fake_cli)
    credential_file = tmp_path / "credentials.json"

    credentials = bootstrap.ensure_test_users(credential_file)

    persisted = json.loads(credential_file.read_text(encoding="utf-8"))
    assert credentials == persisted
    assert set(credentials) == {"admin", "owner", "guest"}
    assert all(credentials[key]["password"] for key in credentials)
    assert len(calls) == 3
    assert all(call[:3] == ("admin", "user", "create") for call in calls)
    assert "--admin" in calls[0]
    assert "--admin" not in calls[1]
    assert "--admin" not in calls[2]


def test_existing_users_are_password_reset_without_echoing_cli_errors(tmp_path, monkeypatch):
    calls = []

    def fake_cli(*args):
        calls.append(args)
        if args[2] == "create":
            return subprocess.CompletedProcess(args, 1, stdout="", stderr="duplicate user secret-leak-check")
        return subprocess.CompletedProcess(args, 0, stdout="updated", stderr="")

    monkeypatch.setattr(bootstrap, "run_gitea_cli", fake_cli)
    credential_file = tmp_path / "credentials.json"

    credentials = bootstrap.ensure_test_users(credential_file)

    assert len(calls) == 6
    assert all(calls[index + 1][:3] == ("admin", "user", "change-password") for index in (0, 2, 4))
    assert "secret-leak-check" not in str(credentials)
    assert credential_file.exists()


def test_bootstrap_failure_does_not_include_password_or_cli_output(tmp_path, monkeypatch):
    def fail_cli(*args):
        return subprocess.CompletedProcess(args, 1, stdout="token-secret", stderr="password-secret")

    monkeypatch.setattr(bootstrap, "run_gitea_cli", fail_cli)

    try:
        bootstrap.ensure_test_users(tmp_path / "credentials.json")
    except RuntimeError as error:
        assert "token-secret" not in str(error)
        assert "password-secret" not in str(error)
    else:
        raise AssertionError("bootstrap should fail when both create and password reset fail")


def test_gitea_cli_runs_as_the_unprivileged_container_user(monkeypatch):
    captured = {}

    def fake_run(command, **kwargs):
        captured["command"] = command
        return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

    monkeypatch.setattr(bootstrap.subprocess, "run", fake_run)

    bootstrap.run_gitea_cli("admin", "user", "list")

    assert captured["command"] == compose_command(
        "exec", "-T", "--user", "git", "gitea", "gitea", "admin", "user", "list"
    )
