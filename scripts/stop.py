import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from qa_lab.compose import ROOT, compose_command


if __name__ == "__main__":
    # Keep the named SQLite volume so the persistence test data remains available.
    raise SystemExit(subprocess.run(compose_command("down"), cwd=ROOT, check=False).returncode)
