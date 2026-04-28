from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def from_project_root(*parts: str) -> Path:
    return PROJECT_ROOT.joinpath(*parts)
