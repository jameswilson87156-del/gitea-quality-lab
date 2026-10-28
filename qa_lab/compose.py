from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROJECT_NAME = "gitea-quality-lab"


def compose_command(*args: str) -> list[str]:
    """Return a Compose command pinned to this project and its own file."""
    return [
        "docker",
        "compose",
        "--project-name",
        PROJECT_NAME,
        "--file",
        str(ROOT / "compose.yml"),
        *args,
    ]
