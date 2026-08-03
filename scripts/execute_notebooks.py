"""Execute every repository notebook without modifying it."""

from __future__ import annotations

import os
from pathlib import Path

import nbformat
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parents[1]
# Skip hidden directories (`.venv`, `.ipynb_checkpoints`) — CI creates the
# virtualenv inside the repo, and installed packages ship their own notebooks.
NOTEBOOKS = sorted(
    path
    for path in ROOT.rglob("*.ipynb")
    if not any(part.startswith(".") for part in path.relative_to(ROOT).parts)
)


def main() -> None:
    if not NOTEBOOKS:
        raise SystemExit("No notebooks found")

    old_cwd = Path.cwd()
    os.chdir(ROOT)
    try:
        for path in NOTEBOOKS:
            print(f"Executing {path.relative_to(ROOT)}")
            notebook = nbformat.read(path, as_version=4)
            NotebookClient(
                notebook,
                timeout=300,
                kernel_name="python3",
                resources={"metadata": {"path": str(ROOT)}},
            ).execute()
    finally:
        os.chdir(old_cwd)


if __name__ == "__main__":
    main()
