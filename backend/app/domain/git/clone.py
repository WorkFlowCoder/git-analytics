import os
import subprocess
from git import Repo

DATA_PATH = "/data/repos"


def ensure_data_path():
    os.makedirs(DATA_PATH, exist_ok=True)


def sanitize_repo_name(repo_url: str) -> str:
    return repo_url.rstrip("/").split("/")[-1].replace(".git", "")


def fix_git_safe_directory(path: str):
    subprocess.run(
        ["git", "config", "--global", "--add", "safe.directory", path],
        check=False
    )

def remove_if_exists(path: str):
    if os.path.exists(path):
        subprocess.run(["rm", "-rf", path], check=False)


def clone_repo(repo_url: str) -> str:
    """
    Clone repo et retourne le path local.
    Version safe + idempotente.
    """

    ensure_data_path()

    repo_name = sanitize_repo_name(repo_url)
    repo_path = os.path.join(DATA_PATH, repo_name)

    # si déjà présent → on reset proprement
    if os.path.exists(repo_path):
        remove_if_exists(repo_path)

    try:
        Repo.clone_from(
            repo_url,
            repo_path,
            multi_options=[
                "--no-single-branch",
                "--filter=blob:none",
                "--depth=200"
            ]
        )

        fix_git_safe_directory(repo_path)

        return repo_path

    except Exception as e:
        raise RuntimeError(f"Git clone failed for {repo_url}: {e}")