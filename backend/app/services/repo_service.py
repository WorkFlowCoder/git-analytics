import os
import subprocess
from git import Repo
from threading import Lock

repo_lock = Lock()

from app.domain.git.analyzer import analyze_repo

DATA_PATH = "/data/repos"

def fix_git_safe_directory(path: str):
    subprocess.run(
        ["git", "config", "--global", "--add", "safe.directory", path],
        check=False
    )

def sanitize_repo_name(repo_url: str) -> str:
    return repo_url.rstrip("/").split("/")[-1].replace(".git", "")

def ensure_data_path():
    os.makedirs(DATA_PATH, exist_ok=True)

def force_remove(path: str):
    if os.path.exists(path):
        subprocess.run(["rm", "-rf", path], check=False)

def clone_repo(repo_url: str, repo_path: str):
    with repo_lock:
        force_remove(repo_path)
    os.makedirs(repo_path, exist_ok=True)
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


def clone_and_analyze(repo_url: str):
    ensure_data_path()

    repo_name = sanitize_repo_name(repo_url)
    repo_path = os.path.join(DATA_PATH, repo_name)

    # 1. clone
    clone_repo(repo_url, repo_path)

    # 2. analyse (déléguée au domain)
    analysis = analyze_repo(repo_path)

    # 3. réponse API propre
    return {
        "repo": repo_name,
        **analysis
    }