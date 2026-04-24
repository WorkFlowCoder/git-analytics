from app.domain.git.analyzer import analyze_repo
from app.domain.git.persistence import persist_to_db
from app.services.repo_service import sanitize_repo_name
from app.domain.git.tree import build_tree
from pathlib import Path

def analyze_repo_job(repo_path: str, repo_url: str, repo_id: int):
    """
    Job exécuté par le worker
    """
    data = analyze_repo(repo_path)
    tree = build_tree(Path(repo_path))
    #print(f"✅ Analysis complete for {repo_url}, persisting to DB...", flush=True)
    data["tree"] = tree
    persist_to_db(repo_id, data)
    #print(f"✅ Data persisted for {repo_url}", flush=True)
    data["repo_id"] = repo_id
    data["repo_url"] = repo_url

    repo_name = sanitize_repo_name(repo_url)

    return {
        "repo": repo_name,
        **data
    }