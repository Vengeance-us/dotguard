from __future__ import annotations
import subprocess
from pathlib import Path

def is_git_repo(path: Path) -> bool:
    result = subprocess.run(
        ["git", "rev-parse", "--is-inside-work-tree"],
        cwd=path if path.is_dir() else path.parent,
        capture_output=True, text=True,
    )
    return result.returncode == 0

def get_tracked_files(path: Path) -> list[str]:
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=path if path.is_dir() else path.parent,
        capture_output=True, text=True,
    )
    return result.stdout.splitlines() if result.returncode == 0 else []

def check_env_in_git(env_path: Path) -> str | None:
    if not is_git_repo(env_path):
        return None
    tracked = get_tracked_files(env_path)
    env_name = env_path.name
    if env_name in tracked or str(env_path) in tracked:
        return (
            f"{env_path} is tracked by git — your secrets may be exposed! "
            f"Run: git rm --cached {env_path} && echo '{env_path}' >> .gitignore"
        )
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        cwd=env_path.parent, capture_output=True, text=True,
    )
    staged = result.stdout.splitlines()
    if env_name in staged or str(env_path) in staged:
        return (
            f"{env_path} is staged for commit — your secrets are about to be exposed! "
            f"Run: git rm --cached {env_path} && echo '{env_path}' >> .gitignore"
        )
    return None
