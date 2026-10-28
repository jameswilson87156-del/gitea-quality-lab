from pathlib import Path

from qa_lab.compose import PROJECT_NAME, ROOT, compose_command


def test_compose_command_is_scoped_to_this_project_and_file():
    command = compose_command("up", "-d", "--wait")

    assert command[:5] == [
        "docker",
        "compose",
        "--project-name",
        PROJECT_NAME,
        "--file",
    ]
    assert Path(command[5]) == ROOT / "compose.yml"
    assert command[6:] == ["up", "-d", "--wait"]
    assert PROJECT_NAME == "gitea-quality-lab"
