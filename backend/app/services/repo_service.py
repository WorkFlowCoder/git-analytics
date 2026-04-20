import os
import shutil
import subprocess
from git import Repo
from pydriller import Repository

DATA_PATH = "/data/repos"

def init_git_safe_directory(path: str):
    subprocess.run([
        "git", "config", "--global",
        "--add", "safe.directory",
        path
    ], check=False)

def sanitize_repo_name(repo_url: str) -> str:
    """Extrait un nom de dossier stable à partir de l'URL."""
    name = repo_url.rstrip("/").split("/")[-1]
    return name.replace(".git", "") or "repo"


def clone_repo(repo_url: str, target_path: str) -> str:
    """
    Clone proprement le repo via GitPython.
    """
    if os.path.exists(target_path):
        shutil.rmtree(target_path)

    os.makedirs(DATA_PATH, exist_ok=True)

    Repo.clone_from(repo_url, target_path)
    return target_path


def analyze_repo(repo_path: str) -> dict:
    """
    Analyse locale avec PyDriller (repo déjà cloné).
    """
    commits = list(Repository(repo_path).traverse_commits())

    authors = set()
    total_files_changed = 0

    for commit in commits:
        authors.add(commit.author.name)
        total_files_changed += len(commit.modified_files)

    return {
        "commits": len(commits),
        "contributors": len(authors),
        "contributors_list": sorted(authors),
        "files_changed": total_files_changed,
    }


def clone_and_analyze(repo_url: str) -> dict:
    """
    Pipeline principal :
    clone → analyse → cleanup optionnel
    """

    repo_name = sanitize_repo_name(repo_url)

    # dossier isolé par repo (évite collisions)
    repo_path = os.path.join(DATA_PATH, repo_name)

    init_git_safe_directory(repo_path)

    # clone
    clone_repo(repo_url, repo_path)

    # analyse
    result = analyze_repo(repo_path)

    # optionnel : cleanup pour éviter accumulation disque
    shutil.rmtree(repo_path, ignore_errors=True)

    return {
        "repo": repo_name,
        **result
    }